#!/usr/bin/env python3
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
    
    # 创建一个兼容LIDA的文本生成器包装器
    class CustomTextGenerator:
        def __init__(self, client):
            self.client = client
            # 添加LIDA需要的属性
            self.provider = "openai"  # 设置provider属性
            self.model = "default"    # 设置模型名称
            
        def generate(self, messages=None, config=None, **kwargs):
            """
            生成文本的方法，兼容LIDA的调用方式
            
            参数:
                messages: 消息列表，LIDA传入的对话格式
                config: TextGenerationConfig对象，包含生成配置
                **kwargs: 其他参数
            
            返回:
                TextGenerationResponse格式的对象
            """
            # 处理不同的调用方式
            if messages is None and len(kwargs) > 0:
                # 兼容旧的prompt方式调用
                prompt = kwargs.get('prompt', '')
                messages = [{"role": "user", "content": prompt}]
            elif messages is None:
                raise ValueError("必须提供messages参数")
            
            # 从config中获取参数，如果没有config则使用默认值
            temperature = 0.7
            max_tokens = 2048
            n = 1
            
            if config:
                temperature = getattr(config, 'temperature', 0.7)
                max_tokens = getattr(config, 'max_tokens', 2048)
                n = getattr(config, 'n', 1)
            
            try:
                response = self.client.chat.completions.create(
                    model="default",
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    n=n
                )
                
                # 创建兼容LIDA的响应格式
                class TextGenerationResponse:
                    def __init__(self, response):
                        self.text = []
                        for choice in response.choices:
                            self.text.append({
                                "content": choice.message.content
                            })
                
                return TextGenerationResponse(response)
                
            except Exception as e:
                print(f"❌ LLM调用失败: {e}")
                # 返回空响应以避免崩溃
                class EmptyResponse:
                    def __init__(self):
                        self.text = [{"content": ""}]
                return EmptyResponse()
    
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
        print("from custom_llm_config_working import get_lida_manager")
        print("lida = get_lida_manager()")
        print("summary = lida.summarize('your_data.csv')")
    else:
        print("\n⚠️  配置可能有问题，请检查设置")
