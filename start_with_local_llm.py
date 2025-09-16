#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIDA 本地LLM启动脚本
无需OpenAI API密钥，使用本地大语言模型

使用方法:
1. python start_with_local_llm.py --model huggingface
2. python start_with_local_llm.py --model ollama
3. python start_with_local_llm.py --model vllm

作者: AI助手
日期: 2024
"""

import os
import sys
import argparse
import uvicorn
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def setup_local_model(model_type):
    """
    根据模型类型设置本地LLM
    
    Args:
        model_type (str): 模型类型 ('huggingface', 'ollama', 'vllm')
    
    Returns:
        Manager: 配置好的LIDA管理器
    """
    from lida import Manager, llm
    
    print(f"🤖 正在配置 {model_type} 本地模型...")
    
    try:
        if model_type == "huggingface":
            # 使用轻量级的HuggingFace模型
            print("使用HuggingFace模型: microsoft/DialoGPT-medium")
            text_gen = llm(
                provider="hf",
                model="microsoft/DialoGPT-medium",
                device_map="auto"
            )
            
        elif model_type == "ollama":
            # 使用Ollama服务器
            print("连接到Ollama服务器 (localhost:11434)")
            model_details = [{
                'name': "llama2",
                'max_tokens': 2048,
                'model': {
                    'provider': 'openai',
                    'parameters': {'model': "llama2"}
                }
            }]
            
            text_gen = llm(
                provider="openai",
                api_base="http://localhost:11434/v1",
                api_key="ollama",
                models=model_details
            )
            
        elif model_type == "vllm":
            # 使用vLLM服务器
            print("连接到vLLM服务器 (localhost:8000)")
            model_details = [{
                'name': "microsoft/DialoGPT-medium",
                'max_tokens': 2596,
                'model': {
                    'provider': 'openai',
                    'parameters': {'model': "microsoft/DialoGPT-medium"}
                }
            }]
            
            text_gen = llm(
                provider="openai",
                api_base="http://localhost:8000/v1",
                api_key="EMPTY",
                models=model_details
            )
            
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        # 创建LIDA管理器
        lida_manager = Manager(text_gen=text_gen)
        print(f"✅ {model_type} 模型配置成功！")
        
        return lida_manager
        
    except Exception as e:
        print(f"❌ {model_type} 模型配置失败: {e}")
        print("\n可能的解决方案:")
        
        if model_type == "huggingface":
            print("1. 安装依赖: pip install transformers torch")
            print("2. 确保有足够的GPU/CPU内存")
            print("3. 检查网络连接（首次下载模型需要）")
            
        elif model_type == "ollama":
            print("1. 安装Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
            print("2. 启动服务: ollama serve")
            print("3. 下载模型: ollama pull llama2")
            
        elif model_type == "vllm":
            print("1. 安装vLLM: pip install vllm")
            print("2. 启动服务器: python -m vllm.entrypoints.openai.api_server --model microsoft/DialoGPT-medium")
            
        return None

def create_local_app(lida_manager):
    """
    创建使用本地模型的FastAPI应用
    
    Args:
        lida_manager (Manager): 配置好的LIDA管理器
    
    Returns:
        FastAPI: 配置好的应用实例
    """
    import json
    import logging
    import requests
    from fastapi import FastAPI, UploadFile
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware
    import traceback
    
    from lida.datamodel import (
        GoalWebRequest, SummaryUrlRequest, TextGenerationConfig, 
        VisualizeWebRequest, InfographicsRequest
    )
    
    # 创建应用
    app = FastAPI(title="LIDA Local LLM")
    logger = logging.getLogger("lida")
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 创建API路由
    api = FastAPI(root_path="/api")
    app.mount("/api", api)
    
    # 设置静态文件目录
    root_file_path = os.path.dirname(os.path.abspath(__file__))
    static_folder_root = os.path.join(root_file_path, "lida/web/ui")
    files_static_root = os.path.join(root_file_path, "lida/web/files/")
    data_folder = os.path.join(root_file_path, "lida/web/files/data")
    
    # 创建必要的目录
    os.makedirs(data_folder, exist_ok=True)
    os.makedirs(files_static_root, exist_ok=True)
    
    # 挂载静态文件
    if os.path.exists(static_folder_root):
        app.mount("/", StaticFiles(directory=static_folder_root, html=True), name="ui")
    api.mount("/files", StaticFiles(directory=files_static_root, html=True), name="files")
    
    @api.post("/summarize")
    async def upload_file(file: UploadFile):
        """上传文件并返回数据摘要"""
        allowed_types = [
            "text/csv", 
            "application/vnd.ms-excel", 
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            "application/json"
        ]
        
        if file.content_type not in allowed_types:
            return {
                "status": False,
                "message": f"不支持的文件类型 ({file.content_type})。支持的类型: csv, excel, json"
            }
        
        try:
            # 保存文件
            file_location = os.path.join(data_folder, file.filename)
            with open(file_location, "wb+") as file_object:
                file_object.write(file.file.read())
            
            # 生成摘要（使用基础摘要，不依赖LLM）
            print(f"正在处理文件: {file.filename}")
            summary = lida_manager.summarize(
                data=file_location,
                file_name=file.filename,
                summary_method="default"  # 使用基础摘要
            )
            
            return {
                "status": True, 
                "summary": summary, 
                "data_filename": file.filename
            }
            
        except Exception as exception_error:
            logger.error(f"处理文件时出错: {str(exception_error)}")
            return {
                "status": False, 
                "message": f"处理文件时出错: {str(exception_error)}"
            }
    
    @api.post("/goal")
    async def generate_goal(req: GoalWebRequest):
        """根据数据摘要生成可视化目标"""
        try:
            textgen_config = req.textgen_config if req.textgen_config else TextGenerationConfig()
            goals = lida_manager.goals(req.summary, n=req.n, textgen_config=textgen_config)
            return {
                "status": True, 
                "data": goals,
                "message": f"成功生成 {len(goals)} 个目标"
            }
        except Exception as exception_error:
            logger.error(f"生成目标时出错: {str(exception_error)}")
            return {
                "status": False,
                "message": f"生成目标时出错: {exception_error}"
            }
    
    @api.post("/visualize")
    async def visualize_data(req: VisualizeWebRequest):
        """根据目标生成可视化图表"""
        try:
            charts = lida_manager.visualize(
                summary=req.summary,
                goal=req.goal,
                textgen_config=req.textgen_config if req.textgen_config else TextGenerationConfig(),
                library=req.library, 
                return_error=True
            )
            
            if len(charts) == 0:
                return {"status": False, "message": "未生成任何图表"}
                
            return {
                "status": True, 
                "charts": charts,
                "message": "成功生成图表"
            }
            
        except Exception as exception_error:
            logger.error(f"生成可视化时出错: {str(exception_error)}")
            return {
                "status": False,
                "message": f"生成可视化时出错: {str(exception_error)}"
            }
    
    @api.get("/health")
    async def health_check():
        """健康检查接口"""
        return {
            "status": "healthy",
            "model_type": "local_llm",
            "message": "LIDA本地模型服务正常运行"
        }
    
    return app

def main():
    """
    主函数：解析命令行参数并启动服务
    """
    parser = argparse.ArgumentParser(description="LIDA 本地LLM启动工具")
    parser.add_argument(
        "--model", 
        choices=["huggingface", "ollama", "vllm"],
        default="huggingface",
        help="选择本地模型类型 (默认: huggingface)"
    )
    parser.add_argument(
        "--host", 
        default="127.0.0.1",
        help="服务器地址 (默认: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", 
        type=int,
        default=8080,
        help="服务器端口 (默认: 8080)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true",
        help="启用自动重载"
    )
    
    args = parser.parse_args()
    
    print("🚀 LIDA 本地LLM启动工具")
    print("=" * 50)
    print(f"模型类型: {args.model}")
    print(f"服务地址: http://{args.host}:{args.port}")
    print("=" * 50)
    
    # 配置本地模型
    lida_manager = setup_local_model(args.model)
    if not lida_manager:
        print("❌ 本地模型配置失败，退出程序")
        sys.exit(1)
    
    # 创建应用
    app = create_local_app(lida_manager)
    
    print(f"\n🌐 启动Web服务器...")
    print(f"访问地址: http://{args.host}:{args.port}")
    print("按 Ctrl+C 停止服务")
    
    try:
        # 启动服务器
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            reload=args.reload
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动服务时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()