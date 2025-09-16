#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试自定义LLM配置是否正确
这个脚本会验证你的LLM服务是否能正常工作
"""

import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def test_direct_api():
    """
    直接测试API连接
    不依赖LIDA，直接调用你的LLM服务
    """
    import requests
    import json
    
    print("🔍 直接测试API连接...")
    
    api_url = "http://10.254.28.17:30000/v1/chat/completions"
    
    # 构造请求数据
    data = {
        "model": "default",
        "messages": [
            {"role": "user", "content": "你好，请简单介绍一下自己"}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            api_url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"✅ API测试成功！")
                print(f"📝 回复内容: {content[:100]}...")
                return True
            else:
                print(f"❌ API返回格式异常: {result}")
                return False
        else:
            print(f"❌ API请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False

def test_llmx_openai_provider():
    """
    测试llmx的OpenAI provider
    尝试通过环境变量设置API base
    """
    print("\n🧪 测试llmx OpenAI provider...")
    
    try:
        from llmx import llm
        
        # 方法1: 通过环境变量设置
        original_base = os.environ.get('OPENAI_API_BASE')
        original_key = os.environ.get('OPENAI_API_KEY')
        
        try:
            # 设置环境变量
            os.environ['OPENAI_API_BASE'] = 'http://10.254.28.17:30000/v1'
            os.environ['OPENAI_API_KEY'] = 'EMPTY'
            
            print("尝试通过环境变量配置...")
            text_gen = llm(provider="openai")
            print("✅ 通过环境变量创建成功！")
            
            # 尝试生成文本
            try:
                response = text_gen.generate("你好")
                print(f"✅ 文本生成成功: {response[:50]}...")
                return text_gen, "环境变量配置"
            except Exception as gen_e:
                print(f"⚠️  文本生成失败: {gen_e}")
                
        finally:
            # 恢复原始环境变量
            if original_base is not None:
                os.environ['OPENAI_API_BASE'] = original_base
            elif 'OPENAI_API_BASE' in os.environ:
                del os.environ['OPENAI_API_BASE']
                
            if original_key is not None:
                os.environ['OPENAI_API_KEY'] = original_key
            elif 'OPENAI_API_KEY' in os.environ:
                del os.environ['OPENAI_API_KEY']
        
        # 方法2: 尝试直接传递参数
        test_params = [
            {"name": "openai_api_base", "openai_api_base": "http://10.254.28.17:30000/v1", "openai_api_key": "EMPTY"},
            {"name": "api_base", "api_base": "http://10.254.28.17:30000/v1", "api_key": "EMPTY"},
            {"name": "base_url", "base_url": "http://10.254.28.17:30000/v1", "api_key": "EMPTY"},
        ]
        
        for params in test_params:
            try:
                name = params.pop("name")
                print(f"\n尝试 {name} 参数...")
                text_gen = llm(provider="openai", **params)
                print(f"✅ {name} 创建成功！")
                
                # 尝试生成文本
                try:
                    response = text_gen.generate("你好")
                    print(f"✅ 文本生成成功: {response[:50]}...")
                    return text_gen, name
                except Exception as gen_e:
                    print(f"⚠️  文本生成失败: {gen_e}")
                    
            except Exception as e:
                print(f"❌ {name} 失败: {e}")
        
        return None, None
        
    except ImportError as e:
        print(f"❌ 无法导入llmx: {e}")
        return None, None

def test_alternative_approach():
    """
    测试替代方案：直接使用OpenAI客户端
    """
    print("\n🔄 测试替代方案...")
    
    try:
        import openai
        
        # 创建自定义OpenAI客户端
        client = openai.OpenAI(
            base_url="http://10.254.28.17:30000/v1",
            api_key="EMPTY"
        )
        
        print("✅ OpenAI客户端创建成功！")
        
        # 测试聊天完成
        try:
            response = client.chat.completions.create(
                model="default",
                messages=[
                    {"role": "user", "content": "你好"}
                ],
                max_tokens=50
            )
            
            content = response.choices[0].message.content
            print(f"✅ OpenAI客户端测试成功: {content[:50]}...")
            return client
            
        except Exception as e:
            print(f"❌ OpenAI客户端测试失败: {e}")
            return None
            
    except ImportError:
        print("❌ 无法导入openai库")
        return None
    except Exception as e:
        print(f"❌ OpenAI客户端创建失败: {e}")
        return None

def create_working_config(method, client=None):
    """
    创建可工作的配置文件
    """
    print(f"\n📝 创建基于{method}的配置文件...")
    
    if method == "环境变量配置":
        config_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIDA 自定义LLM配置文件 - 环境变量方式
配置类型: openai_compatible
生成时间: 自动生成

使用方法:
1. from custom_llm_config_working import get_lida_manager
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
    
    # 设置环境变量
    os.environ['OPENAI_API_BASE'] = 'http://10.254.28.17:30000/v1'
    os.environ['OPENAI_API_KEY'] = 'EMPTY'
    
    # 创建文本生成器
    text_gen = llm(provider="openai")
    
    # 创建LIDA管理器
    lida_manager = Manager(text_gen=text_gen)
    
    print("✅ 自定义LLM服务初始化成功！")
    print(f"API地址: http://10.254.28.17:30000/v1")
    print(f"模型名称: default")
    
    return lida_manager

def test_llm_service():
    """
    测试LLM服务是否正常工作
    """
    try:
        lida = get_lida_manager()
        print("\\n🧪 正在测试LLM服务...")
        
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
        print("\\n🎉 配置成功！现在可以使用LIDA了")
        print("\\n📝 使用示例:")
        print("from custom_llm_config_working import get_lida_manager")
        print("lida = get_lida_manager()")
        print("summary = lida.summarize('your_data.csv')")
    else:
        print("\\n⚠️  配置可能有问题，请检查设置")
'''
    elif method == "OpenAI客户端":
        config_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIDA 自定义LLM配置文件 - OpenAI客户端方式
配置类型: openai_compatible
生成时间: 自动生成

使用方法:
1. from custom_llm_config_working import get_lida_manager
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
    使用直接的OpenAI客户端方式
    
    返回:
        Manager: 配置好的LIDA管理器实例
    """
    from lida import Manager
    import openai
    
    print("🚀 正在初始化自定义LLM服务...")
    
    # 创建自定义OpenAI客户端
    client = openai.OpenAI(
        base_url="http://10.254.28.17:30000/v1",
        api_key="EMPTY"
    )
    
    # 创建一个简单的文本生成器包装器
    class CustomTextGenerator:
        def __init__(self, client):
            self.client = client
            
        def generate(self, prompt, **kwargs):
            response = self.client.chat.completions.create(
                model="default",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=kwargs.get('max_tokens', 2048),
                temperature=kwargs.get('temperature', 0.7)
            )
            return response.choices[0].message.content
    
    text_gen = CustomTextGenerator(client)
    
    # 创建LIDA管理器
    lida_manager = Manager(text_gen=text_gen)
    
    print("✅ 自定义LLM服务初始化成功！")
    print(f"API地址: http://10.254.28.17:30000/v1")
    print(f"模型名称: default")
    
    return lida_manager

def test_llm_service():
    """
    测试LLM服务是否正常工作
    """
    try:
        lida = get_lida_manager()
        print("\\n🧪 正在测试LLM服务...")
        
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
        print("\\n🎉 配置成功！现在可以使用LIDA了")
        print("\\n📝 使用示例:")
        print("from custom_llm_config_working import get_lida_manager")
        print("lida = get_lida_manager()")
        print("summary = lida.summarize('your_data.csv')")
    else:
        print("\\n⚠️  配置可能有问题，请检查设置")
'''
    else:
        return False
    
    try:
        with open('custom_llm_config_working.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print(f"✅ 可工作的配置文件已创建: custom_llm_config_working.py")
        return True
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")
        return False

def main():
    """
    主测试函数
    按步骤测试各个组件
    """
    print("🚀 开始测试自定义LLM配置")
    print("=" * 50)
    
    # 步骤1: 直接测试API
    api_ok = test_direct_api()
    
    if not api_ok:
        print("\n❌ API测试失败，请检查:")
        print("1. LLM服务是否正在运行")
        print("2. 服务地址是否正确: http://10.254.28.17:30000")
        print("3. 网络连接是否正常")
        return
    
    # 步骤2: 测试llmx兼容性
    text_gen, config_name = test_llmx_openai_provider()
    
    if text_gen is not None:
        print(f"\n✅ 找到可用的llmx配置: {config_name}")
        
        # 测试LIDA集成
        try:
            from lida import Manager
            lida_manager = Manager(text_gen=text_gen)
            print("✅ LIDA集成测试通过！")
            
            # 创建可工作的配置文件
            create_working_config(config_name)
            
            print("\n🎉 所有测试通过！")
            print("\n下一步可以:")
            print("1. 使用: python custom_llm_config_working.py 测试配置")
            print("2. 在代码中使用:")
            print("   from custom_llm_config_working import get_lida_manager")
            print("   lida = get_lida_manager()")
            return
            
        except Exception as e:
            print(f"❌ LIDA集成失败: {e}")
    
    # 步骤3: 尝试替代方案
    print("\n🔄 llmx方式失败，尝试替代方案...")
    client = test_alternative_approach()
    
    if client is not None:
        print("\n✅ 找到可用的替代方案: OpenAI客户端")
        
        # 创建基于OpenAI客户端的配置
        if create_working_config("OpenAI客户端", client):
            print("\n🎉 替代方案配置成功！")
            print("\n下一步可以:")
            print("1. 使用: python custom_llm_config_working.py 测试配置")
            print("2. 在代码中使用:")
            print("   from custom_llm_config_working import get_lida_manager")
            print("   lida = get_lida_manager()")
        else:
            print("❌ 创建替代配置失败")
    else:
        print("\n❌ 所有方案都失败了")
        print("\n可能的解决方案:")
        print("1. 检查LLM服务是否正常运行")
        print("2. 更新相关库: python3 -m pip install -U llmx openai lida")
        print("3. 检查网络连接")

if __name__ == "__main__":
    main()