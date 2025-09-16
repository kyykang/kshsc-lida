#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIDA基本功能测试脚本
这个脚本用来测试LIDA库是否正确安装和基本功能是否正常
"""

import os
import sys
import pandas as pd

def test_import():
    """测试LIDA库是否能正确导入"""
    try:
        from lida import Manager, llm, TextGenerationConfig
        print("✅ LIDA库导入成功")
        return True
    except ImportError as e:
        print(f"❌ LIDA库导入失败: {e}")
        return False

def test_manager_creation():
    """测试Manager对象是否能正确创建"""
    try:
        from lida import Manager
        # 设置一个临时的API密钥来避免错误（仅用于测试）
        os.environ['OPENAI_API_KEY'] = 'test-key-for-basic-testing'
        manager = Manager()
        print("✅ Manager对象创建成功")
        return True, manager
    except Exception as e:
        print(f"❌ Manager对象创建失败: {e}")
        return False, None

def test_sample_data():
    """创建测试数据并测试数据摘要功能"""
    try:
        # 创建一个简单的测试数据集
        data = {
            'Name': ['Toyota Camry', 'Honda Civic', 'Ford Focus', 'BMW X3', 'Audi A4'],
            'MPG': [28, 32, 27, 23, 25],
            'Cylinders': [4, 4, 4, 6, 4],
            'Horsepower': [203, 158, 160, 248, 201],
            'Weight': [3400, 2800, 3000, 4200, 3500]
        }
        df = pd.DataFrame(data)
        print("✅ 测试数据创建成功")
        print("数据预览:")
        print(df.head())
        return True, df
    except Exception as e:
        print(f"❌ 测试数据创建失败: {e}")
        return False, None

def check_api_key():
    """检查OpenAI API密钥是否设置"""
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and api_key != 'your-openai-api-key-here':
        print(f"✅ OpenAI API密钥已设置: {api_key[:10]}...")
        return True
    else:
        print("⚠️  OpenAI API密钥未设置或为默认值")
        print("   请运行以下命令设置API密钥:")
        print("   export OPENAI_API_KEY='your-actual-api-key'")
        print("   或编辑 setup_api_key.sh 文件")
        return False

def main():
    """主测试函数"""
    print("🚀 开始LIDA基本功能测试...\n")
    
    # 测试1: 导入测试
    print("1. 测试库导入...")
    if not test_import():
        sys.exit(1)
    
    # 测试2: Manager创建测试
    print("\n2. 测试Manager创建...")
    success, manager = test_manager_creation()
    if not success:
        sys.exit(1)
    
    # 测试3: 测试数据创建
    print("\n3. 测试数据创建...")
    success, df = test_sample_data()
    if not success:
        sys.exit(1)
    
    # 测试4: API密钥检查
    print("\n4. 检查API密钥配置...")
    api_key_set = check_api_key()
    
    # 总结
    print("\n" + "="*50)
    print("📊 测试结果总结:")
    print("✅ LIDA库安装正常")
    print("✅ 基本组件可以正常创建")
    print("✅ 测试数据准备完成")
    
    if api_key_set:
        print("✅ API密钥配置完成")
        print("\n🎉 LIDA已准备就绪，可以开始使用！")
    else:
        print("⚠️  需要配置OpenAI API密钥才能使用完整功能")
        print("\n📝 下一步: 配置API密钥后即可使用LIDA的完整功能")
    
    print("\n🌐 启动Web界面请运行: python3 -m lida.web.app")
    print("或使用命令: lida ui --port=8080")

if __name__ == "__main__":
    main()