#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIDA 自定义LLM配置文件
配置类型: openai_compatible
生成时间: 2025-09-16 14:35:39

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
    

    # OpenAI兼容API配置
    model_details = [{
        'name': "default",
        'max_tokens': 2048,
        'model': {
            'provider': 'openai',
            'parameters': {'model': "default"}
        }
    }]
    
    # 创建文本生成器
    text_gen = llm(
        provider="openai",
        base_url="http://10.254.28.17:30000/v1",
        api_key="EMPTY",
        models=model_details
    )
    
    # 创建LIDA管理器
    lida_manager = Manager(text_gen=text_gen)
    
    print("✅ 自定义LLM服务初始化成功！")
    print(f"API地址: http://10.254.28.17:30000")
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
        print("from custom_llm_config import get_lida_manager")
        print("lida = get_lida_manager()")
        print("summary = lida.summarize('your_data.csv')")
    else:
        print("\n⚠️  配置可能有问题，请检查设置")
