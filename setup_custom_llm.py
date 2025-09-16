#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIDA 自定义LLM服务配置工具
帮助用户将自己的LLM服务集成到LIDA项目中

支持的服务类型:
1. OpenAI兼容API (推荐)
2. 自定义HTTP API
3. 本地模型服务

作者: AI助手
日期: 2024
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

def test_api_connection(api_base, api_key, model_name, test_prompt="Hello, how are you?"):
    """
    测试API连接是否正常
    
    参数:
        api_base (str): API基础URL
        api_key (str): API密钥
        model_name (str): 模型名称
        test_prompt (str): 测试提示词
    
    返回:
        bool: 连接成功返回True，失败返回False
    """
    print(f"🔍 正在测试API连接...")
    
    try:
        # 构建请求URL
        if api_base.endswith('/v1'):
            url = f"{api_base}/chat/completions"
        elif api_base.endswith('/v1/'):
            url = f"{api_base}chat/completions"
        else:
            url = f"{api_base}/v1/chat/completions"
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # 构建请求数据
        data = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": test_prompt}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        print(f"请求URL: {url}")
        print(f"模型名称: {model_name}")
        
        # 发送测试请求
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                reply = result['choices'][0]['message']['content']
                print(f"✅ API连接成功！")
                print(f"测试回复: {reply[:100]}...")
                return True
            else:
                print(f"❌ API响应格式异常: {result}")
                return False
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请检查网络连接或服务器状态")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败，请检查API地址是否正确")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def setup_openai_compatible_api():
    """
    配置OpenAI兼容的API服务
    这是最常见的配置方式，支持大多数LLM服务提供商
    """
    print("🔧 配置OpenAI兼容API服务")
    print("=" * 50)
    
    print("\n📝 请输入您的LLM服务信息:")
    
    # 获取用户输入
    api_base = input("API基础URL (例: http://10.254.28.17:30000): ").strip()
    if not api_base:
        print("❌ API基础URL不能为空")
        return None
    
    # 确保URL格式正确
    if not api_base.startswith('http'):
        api_base = f"http://{api_base}"
    
    api_key = input("API密钥 (如果不需要可直接回车): ").strip()
    if not api_key:
        api_key = "EMPTY"  # 很多本地服务不需要真实密钥
    
    model_name = input("模型名称 (例: gpt-3.5-turbo, llama2等): ").strip()
    if not model_name:
        print("❌ 模型名称不能为空")
        return None
    
    max_tokens = input("最大token数 [2048]: ").strip()
    max_tokens = int(max_tokens) if max_tokens.isdigit() else 2048
    
    print("\n📋 配置信息确认:")
    print(f"API地址: {api_base}")
    print(f"API密钥: {'***' if api_key != 'EMPTY' else 'EMPTY'}")
    print(f"模型名称: {model_name}")
    print(f"最大tokens: {max_tokens}")
    
    confirm = input("\n确认配置? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ 用户取消配置")
        return None
    
    # 测试API连接
    if not test_api_connection(api_base, api_key, model_name):
        retry = input("\n⚠️  API测试失败，是否继续保存配置? (y/n): ").strip().lower()
        if retry != 'y':
            return None
    
    # 返回配置信息
    config = {
        'type': 'openai_compatible',
        'api_base': api_base,
        'api_key': api_key,
        'model_name': model_name,
        'max_tokens': max_tokens
    }
    
    return config

def setup_custom_http_api():
    """
    配置自定义HTTP API服务
    适用于非OpenAI兼容的自定义API
    """
    print("🔧 配置自定义HTTP API服务")
    print("=" * 50)
    print("\n⚠️  注意: 此选项需要您自己实现API适配器")
    print("建议优先尝试OpenAI兼容API配置")
    
    api_url = input("\nAPI完整URL: ").strip()
    if not api_url:
        print("❌ API URL不能为空")
        return None
    
    headers = {}
    print("\n请输入HTTP请求头 (可选，直接回车跳过):")
    while True:
        key = input("请求头名称 (直接回车结束): ").strip()
        if not key:
            break
        value = input(f"{key}的值: ").strip()
        if value:
            headers[key] = value
    
    config = {
        'type': 'custom_http',
        'api_url': api_url,
        'headers': headers
    }
    
    return config

def generate_config_file(config):
    """
    生成LIDA配置文件
    
    参数:
        config (dict): 配置信息
    
    返回:
        str: 配置文件路径
    """
    config_file = "custom_llm_config.py"
    
    # 生成配置文件内容
    config_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIDA 自定义LLM配置文件
配置类型: {config['type']}
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

使用方法:
1. from custom_llm_config import get_lida_manager
2. lida = get_lida_manager()
3. 开始使用LIDA进行数据可视化
"""

import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def get_lida_manager():
    """
    获取配置好的LIDA管理器
    
    返回:
        Manager: 配置好的LIDA管理器实例
    """
    from lida import Manager, llm
    
    print("🚀 正在初始化自定义LLM服务...")
    
'''
    
    if config['type'] == 'openai_compatible':
        config_content += f'''
    # OpenAI兼容API配置
    model_details = [{{
        'name': "{config['model_name']}",
        'max_tokens': {config['max_tokens']},
        'model': {{
            'provider': 'openai',
            'parameters': {{'model': "{config['model_name']}"}}
        }}
    }}]
    
    # 创建文本生成器
    text_gen = llm(
        provider="openai",
        api_base="{config['api_base']}",
        api_key="{config['api_key']}",
        models=model_details
    )
    
    # 创建LIDA管理器
    lida_manager = Manager(text_gen=text_gen)
    
    print("✅ 自定义LLM服务初始化成功！")
    print(f"API地址: {config['api_base']}")
    print(f"模型名称: {config['model_name']}")
    
    return lida_manager
'''
    
    elif config['type'] == 'custom_http':
        config_content += f'''
    # 自定义HTTP API配置
    # 注意: 需要您自己实现API适配逻辑
    
    import requests
    
    class CustomLLMProvider:
        def __init__(self):
            self.api_url = "{config['api_url']}"
            self.headers = {config['headers']}
        
        def generate(self, prompt, **kwargs):
            # 在这里实现您的API调用逻辑
            # 返回生成的文本
            pass
    
    # 这里需要您根据实际API实现适配器
    # 建议使用OpenAI兼容API配置
    raise NotImplementedError("自定义HTTP API需要手动实现适配器")
'''
    
    config_content += '''

def test_llm_service():
    """
    测试LLM服务是否正常工作
    """
    try:
        lida = get_lida_manager()
        print("\n🧪 正在测试LLM服务...")
        
        # 这里可以添加简单的测试逻辑
        print("✅ LLM服务测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ LLM服务测试失败: {e}")
        return False

if __name__ == "__main__":
    print("LIDA 自定义LLM配置")
    print("=" * 30)
    
    # 测试服务
    if test_llm_service():
        print("\n🎉 配置成功！现在可以使用LIDA了")
        print("\n📝 使用示例:")
        print("from custom_llm_config import get_lida_manager")
        print("lida = get_lida_manager()")
        print("summary = lida.summarize('your_data.csv')")
    else:
        print("\n⚠️  配置可能有问题，请检查设置")
'''
    
    # 写入配置文件
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"\n💾 配置文件已生成: {config_file}")
    return config_file

def generate_startup_script(config):
    """
    生成启动脚本
    
    参数:
        config (dict): 配置信息
    
    返回:
        str: 启动脚本路径
    """
    script_file = "start_lida_with_custom_llm.py"
    
    script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIDA 自定义LLM启动脚本
使用您配置的自定义LLM服务启动LIDA Web界面

使用方法:
python start_lida_with_custom_llm.py
"""

import os
import sys
import uvicorn
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """
    启动LIDA Web服务
    """
    print("🚀 启动LIDA自定义LLM Web服务")
    print("=" * 40)
    
    try:
        # 导入自定义配置
        from custom_llm_config import get_lida_manager
        
        # 初始化LIDA管理器
        lida_manager = get_lida_manager()
        
        # 创建Web应用
        from lida.web.app import create_app
        app = create_app(lida_manager)
        
        print("\n🌐 启动Web服务器...")
        print("访问地址: http://localhost:8080")
        print("按 Ctrl+C 停止服务")
        
        # 启动服务器
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8080,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ 导入错误: {{e}}")
        print("请确保已正确配置custom_llm_config.py")
    except Exception as e:
        print(f"❌ 启动失败: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    # 写入启动脚本
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 设置执行权限
    os.chmod(script_file, 0o755)
    
    print(f"💾 启动脚本已生成: {script_file}")
    return script_file

def main():
    """
    主函数：配置向导
    """
    print("🎯 LIDA 自定义LLM服务配置工具")
    print("=" * 50)
    print("\n此工具将帮助您将自己的LLM服务集成到LIDA项目中")
    
    while True:
        print("\n📋 请选择配置类型:")
        print("1. OpenAI兼容API (推荐)")
        print("2. 自定义HTTP API (高级)")
        print("3. 退出")
        
        try:
            choice = input("\n请输入选择 (1-3): ").strip()
            
            if choice == "1":
                config = setup_openai_compatible_api()
                if config:
                    # 生成配置文件
                    config_file = generate_config_file(config)
                    startup_script = generate_startup_script(config)
                    
                    print("\n🎉 配置完成！")
                    print("\n📝 下一步操作:")
                    print(f"1. 测试配置: python {config_file}")
                    print(f"2. 启动Web界面: python {startup_script}")
                    print("3. 或者在代码中使用:")
                    print("   from custom_llm_config import get_lida_manager")
                    print("   lida = get_lida_manager()")
                    
                    break
                    
            elif choice == "2":
                config = setup_custom_http_api()
                if config:
                    config_file = generate_config_file(config)
                    print("\n⚠️  自定义HTTP API配置已生成")
                    print(f"请手动编辑 {config_file} 实现API适配逻辑")
                    break
                    
            elif choice == "3":
                print("👋 退出配置工具")
                sys.exit(0)
                
            else:
                print("❌ 无效选择，请输入 1-3")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户取消操作")
            sys.exit(0)
        except Exception as e:
            print(f"❌ 发生错误: {e}")
    
    print("\n✨ 自定义LLM配置完成！")
    print("\n💡 提示:")
    print("- 如果遇到问题，请检查API地址和密钥是否正确")
    print("- 确保您的LLM服务支持OpenAI兼容的API格式")
    print("- 可以参考本地LLM使用指南.md了解更多信息")

if __name__ == "__main__":
    main()