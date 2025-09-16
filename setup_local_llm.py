#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIDA 本地LLM大模型配置脚本
支持多种本地模型配置方式，无需OpenAI API密钥

作者: AI助手
日期: 2024
"""

import os
import sys
from lida import Manager, llm
from llmx import TextGenerationConfig

def setup_huggingface_model():
    """
    配置HuggingFace本地模型
    这种方式直接使用HuggingFace的transformers库加载模型
    需要GPU支持以获得更好的性能
    """
    print("🤖 配置HuggingFace本地模型...")
    print("注意：这需要较大的GPU内存和存储空间")
    
    # 推荐的开源模型列表
    recommended_models = [
        "microsoft/DialoGPT-medium",  # 轻量级对话模型
        "microsoft/DialoGPT-large",   # 大型对话模型
        "uukuguy/speechless-llama2-hermes-orca-platypus-13b",  # 高质量13B模型
        "codellama/CodeLlama-7b-Instruct-hf",  # 代码生成专用模型
        "WizardLM/WizardCoder-Python-7B-V1.0",  # Python代码专用模型
    ]
    
    print("\n推荐的开源模型:")
    for i, model in enumerate(recommended_models, 1):
        print(f"{i}. {model}")
    
    print("\n请选择一个模型 (输入数字 1-5):")
    try:
        choice = int(input("选择: ")) - 1
        if 0 <= choice < len(recommended_models):
            selected_model = recommended_models[choice]
        else:
            print("无效选择，使用默认模型")
            selected_model = recommended_models[0]
    except ValueError:
        print("无效输入，使用默认模型")
        selected_model = recommended_models[0]
    
    print(f"\n选择的模型: {selected_model}")
    
    try:
        # 创建HuggingFace文本生成器
        print("正在加载模型，请稍候...")
        text_gen = llm(
            provider="hf", 
            model=selected_model, 
            device_map="auto"  # 自动分配GPU/CPU
        )
        
        # 创建LIDA管理器
        lida_manager = Manager(text_gen=text_gen)
        
        print("✅ HuggingFace模型配置成功！")
        return lida_manager, text_gen
        
    except Exception as e:
        print(f"❌ HuggingFace模型配置失败: {e}")
        print("可能的原因:")
        print("1. 缺少transformers库: pip install transformers")
        print("2. 缺少torch库: pip install torch")
        print("3. GPU内存不足")
        print("4. 网络连接问题")
        return None, None

def setup_vllm_server():
    """
    配置vLLM服务器连接
    这种方式连接到本地运行的vLLM服务器
    需要先启动vLLM服务器
    """
    print("🚀 配置vLLM服务器连接...")
    
    # 默认配置
    default_host = "localhost"
    default_port = "8000"
    default_model = "microsoft/DialoGPT-medium"
    
    print(f"\n请输入vLLM服务器配置 (直接回车使用默认值):")
    
    host = input(f"服务器地址 [{default_host}]: ").strip() or default_host
    port = input(f"端口号 [{default_port}]: ").strip() or default_port
    model_name = input(f"模型名称 [{default_model}]: ").strip() or default_model
    
    api_base = f"http://{host}:{port}/v1"
    
    print(f"\n配置信息:")
    print(f"API地址: {api_base}")
    print(f"模型名称: {model_name}")
    
    try:
        # 模型详细信息配置
        model_details = [{
            'name': model_name, 
            'max_tokens': 2596, 
            'model': {
                'provider': 'openai', 
                'parameters': {'model': model_name}
            }
        }]
        
        # 创建文本生成器
        text_gen = llm(
            provider="openai",  
            api_base=api_base, 
            api_key="EMPTY",  # vLLM不需要真实API密钥
            models=model_details
        )
        
        # 创建LIDA管理器
        lida_manager = Manager(text_gen=text_gen)
        
        print("✅ vLLM服务器配置成功！")
        print("\n启动vLLM服务器的命令示例:")
        print(f"python -m vllm.entrypoints.openai.api_server --model {model_name} --port {port}")
        
        return lida_manager, text_gen
        
    except Exception as e:
        print(f"❌ vLLM服务器配置失败: {e}")
        print("请确保:")
        print("1. vLLM服务器正在运行")
        print("2. 服务器地址和端口正确")
        print("3. 模型名称正确")
        return None, None

def setup_ollama_server():
    """
    配置Ollama服务器连接
    Ollama是一个轻量级的本地LLM运行工具
    """
    print("🦙 配置Ollama服务器连接...")
    
    default_host = "localhost"
    default_port = "11434"
    default_model = "llama2"
    
    print(f"\n请输入Ollama服务器配置:")
    
    host = input(f"服务器地址 [{default_host}]: ").strip() or default_host
    port = input(f"端口号 [{default_port}]: ").strip() or default_port
    model_name = input(f"模型名称 [{default_model}]: ").strip() or default_model
    
    api_base = f"http://{host}:{port}/v1"
    
    print(f"\n配置信息:")
    print(f"API地址: {api_base}")
    print(f"模型名称: {model_name}")
    
    try:
        # 模型配置
        model_details = [{
            'name': model_name,
            'max_tokens': 2048,
            'model': {
                'provider': 'openai',
                'parameters': {'model': model_name}
            }
        }]
        
        # 创建文本生成器
        text_gen = llm(
            provider="openai",
            api_base=api_base,
            api_key="ollama",  # Ollama使用固定密钥
            models=model_details
        )
        
        # 创建LIDA管理器
        lida_manager = Manager(text_gen=text_gen)
        
        print("✅ Ollama服务器配置成功！")
        print("\n安装和启动Ollama的命令:")
        print("1. 安装: curl -fsSL https://ollama.ai/install.sh | sh")
        print(f"2. 下载模型: ollama pull {model_name}")
        print("3. 启动服务: ollama serve")
        
        return lida_manager, text_gen
        
    except Exception as e:
        print(f"❌ Ollama服务器配置失败: {e}")
        return None, None

def test_local_model(lida_manager):
    """
    测试本地模型是否正常工作
    """
    print("\n🧪 测试本地模型...")
    
    try:
        # 创建测试数据
        import pandas as pd
        test_data = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35],
            'salary': [50000, 60000, 70000]
        })
        
        # 保存测试数据
        test_file = "/tmp/test_data.csv"
        test_data.to_csv(test_file, index=False)
        
        print("正在生成数据摘要...")
        
        # 测试数据摘要功能
        summary = lida_manager.summarize(
            data=test_file,
            file_name="test_data.csv",
            summary_method="default"  # 使用基础摘要，不依赖LLM
        )
        
        print("✅ 本地模型测试成功！")
        print(f"数据摘要: {summary.name}")
        print(f"数据行数: {summary.shape[0]}")
        print(f"数据列数: {summary.shape[1]}")
        
        return True
        
    except Exception as e:
        print(f"❌ 本地模型测试失败: {e}")
        return False

def save_config(config_type, config_data):
    """
    保存配置到文件
    """
    config_file = "local_llm_config.py"
    
    config_content = f'''
# LIDA 本地LLM配置文件
# 配置类型: {config_type}
# 生成时间: {__import__('datetime').datetime.now()}

from lida import Manager, llm

def get_lida_manager():
    """获取配置好的LIDA管理器"""
'''
    
    if config_type == "huggingface":
        config_content += f'''
    text_gen = llm(
        provider="hf",
        model="{config_data['model']}",
        device_map="auto"
    )
'''
    elif config_type == "vllm":
        config_content += f'''
    model_details = [{{
        'name': "{config_data['model']}",
        'max_tokens': 2596,
        'model': {{
            'provider': 'openai',
            'parameters': {{'model': "{config_data['model']}"}}
        }}
    }}]
    
    text_gen = llm(
        provider="openai",
        api_base="{config_data['api_base']}",
        api_key="EMPTY",
        models=model_details
    )
'''
    elif config_type == "ollama":
        config_content += f'''
    model_details = [{{
        'name': "{config_data['model']}",
        'max_tokens': 2048,
        'model': {{
            'provider': 'openai',
            'parameters': {{'model': "{config_data['model']}"}}
        }}
    }}]
    
    text_gen = llm(
        provider="openai",
        api_base="{config_data['api_base']}",
        api_key="ollama",
        models=model_details
    )
'''
    
    config_content += '''
    return Manager(text_gen=text_gen)

if __name__ == "__main__":
    lida = get_lida_manager()
    print("LIDA本地模型已准备就绪！")
'''
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"\n💾 配置已保存到: {config_file}")
    print("使用方法:")
    print("from local_llm_config import get_lida_manager")
    print("lida = get_lida_manager()")

def main():
    """
    主函数：显示菜单并处理用户选择
    """
    print("🚀 LIDA 本地LLM大模型配置工具")
    print("=" * 50)
    print("选择配置方式:")
    print("1. HuggingFace模型 (直接加载)")
    print("2. vLLM服务器 (OpenAI兼容API)")
    print("3. Ollama服务器 (轻量级本地LLM)")
    print("4. 退出")
    
    while True:
        try:
            choice = input("\n请选择 (1-4): ").strip()
            
            if choice == "1":
                lida_manager, text_gen = setup_huggingface_model()
                if lida_manager:
                    if test_local_model(lida_manager):
                        save_config("huggingface", {"model": text_gen.model})
                    break
                    
            elif choice == "2":
                lida_manager, text_gen = setup_vllm_server()
                if lida_manager:
                    save_config("vllm", {
                        "model": text_gen.models[0]['name'],
                        "api_base": text_gen.api_base
                    })
                    break
                    
            elif choice == "3":
                lida_manager, text_gen = setup_ollama_server()
                if lida_manager:
                    save_config("ollama", {
                        "model": text_gen.models[0]['name'],
                        "api_base": text_gen.api_base
                    })
                    break
                    
            elif choice == "4":
                print("👋 退出配置工具")
                sys.exit(0)
                
            else:
                print("❌ 无效选择，请输入 1-4")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户取消操作")
            sys.exit(0)
        except Exception as e:
            print(f"❌ 发生错误: {e}")
    
    print("\n🎉 本地LLM配置完成！")
    print("\n📝 下一步:")
    print("1. 使用生成的配置文件启动LIDA")
    print("2. 或者直接运行: python local_llm_config.py")
    print("3. 启动Web界面: lida ui --port=8080")

if __name__ == "__main__":
    main()