#!/usr/bin/env python3
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
        
        print("
🌐 启动Web服务器...")
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
        print(f"❌ 导入错误: {e}")
        print("请确保已正确配置custom_llm_config.py")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
