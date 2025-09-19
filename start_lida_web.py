#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIDA Web应用启动器
使用自定义LLM服务的Streamlit应用
"""

import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def start_lida_web():
    """
    启动LIDA Web应用
    """
    print("🚀 正在启动LIDA Web应用...")
    
    try:
        # 创建Streamlit应用文件
        create_streamlit_app()
        
        # 启动Streamlit服务
        import subprocess
        
        # 设置环境变量
        env = os.environ.copy()
        env['STREAMLIT_SERVER_HEADLESS'] = 'true'
        
        # 启动命令
        cmd = [
            sys.executable, '-m', 'streamlit', 'run', 
            'temp_lida_app.py', 
            '--server.port', '8501',
            '--server.address', '0.0.0.0'
        ]
        
        print("📊 启动Streamlit服务...")
        print(f"🌐 访问地址: http://localhost:8501")
        
        # 启动服务
        subprocess.run(cmd, env=env)
        
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def create_streamlit_app():
    """
    创建一个简单的Streamlit应用文件
    """
    app_content = """import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from custom_llm_config_working import get_lida_manager

# 页面配置
st.set_page_config(
    page_title="LIDA - 数据可视化助手",
    page_icon="📊",
    layout="wide"
)

# 标题
st.title("📊 LIDA - 智能数据可视化")
st.markdown("使用自定义LLM服务进行数据分析和可视化")

# 侧边栏信息
with st.sidebar:
    st.header("🔧 配置信息")
    st.info(
        "**LLM服务地址:** http://10.254.28.17:30000\\n"
        "**模型名称:** default\\n"
        "**配置状态:** ✅ 已连接"
    )
    
    st.header("📝 使用说明")
    st.markdown(
        '''
        1. 上传CSV数据文件
        2. 查看数据摘要
        3. 生成可视化图表
        4. 下载结果
        '''
    )

# 主要内容区域
tab1, tab2, tab3 = st.tabs(["📁 数据上传", "📊 数据摘要", "📈 可视化"])

with tab1:
    st.header("📁 数据上传")
    
    uploaded_file = st.file_uploader(
        "选择CSV文件",
        type=['csv'],
        help="上传您的数据文件进行分析"
    )
    
    if uploaded_file is not None:
        # 读取并显示数据
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ 成功上传文件: {uploaded_file.name}")
        
        # 数据预览
        st.subheader("📋 数据预览")
        st.dataframe(df.head(), use_container_width=True)
        
        # 数据基本信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("数据行数", len(df))
        with col2:
            st.metric("数据列数", len(df.columns))
        with col3:
            st.metric("数据大小", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
        
        # 存储数据到session state
        st.session_state['uploaded_data'] = df

with tab2:
    st.header("📊 数据摘要")
    
    if 'uploaded_data' in st.session_state:
        df = st.session_state['uploaded_data']
        
        if st.button("🔍 生成数据摘要", type="primary"):
            with st.spinner("正在分析数据..."):
                try:
                    # 获取LIDA管理器
                    lida_manager = get_lida_manager()
                    
                    if lida_manager:
                        # 将DataFrame转换为字符串格式
                        data_str = df.to_csv(index=False)
                        
                        # 生成数据摘要
                        summary = lida_manager.summarize(data_str, summary_method="default")
                        
                        if summary:
                            st.success("✅ 数据摘要生成成功")
                            
                            # 显示摘要信息
                            st.subheader("📈 数据集概览")
                            if hasattr(summary, 'dataset_description') and summary.dataset_description:
                                st.write(f"**数据描述**: {summary.dataset_description}")
                            
                            # 字段信息
                            if hasattr(summary, 'fields') and summary.fields:
                                st.subheader("📋 字段信息")
                                fields_data = []
                                for field in summary.fields:
                                    fields_data.append({
                                        "字段名": field.column,
                                        "数据类型": field.dtype,
                                        "描述": getattr(field, 'description', ''),
                                    })
                                
                                fields_df = pd.DataFrame(fields_data)
                                st.dataframe(fields_df, use_container_width=True)
                            
                            # 存储摘要
                            st.session_state['summary'] = summary
                            st.session_state['data_str'] = data_str
                        else:
                            st.error("❌ 未能生成数据摘要")
                    else:
                        st.error("❌ 无法连接到LLM服务")
                        
                except Exception as e:
                    st.error(f"❌ 数据摘要生成失败: {e}")
    else:
        st.info("请先在"数据上传"标签页上传CSV文件")

with tab3:
    st.header("📈 智能可视化")
    
    if 'summary' in st.session_state:
        # 可视化描述输入
        viz_description = st.text_area(
            "描述您想要的可视化",
            placeholder="例如：显示各类别的销售额分布的柱状图",
            help="用自然语言描述您想要生成的图表类型和内容"
        )
        
        if st.button("🎯 生成可视化", type="primary") and viz_description:
            with st.spinner("正在生成可视化..."):
                try:
                    lida_manager = get_lida_manager()
                    
                    if lida_manager:
                        # 生成可视化方案
                        goals = lida_manager.goals(st.session_state['summary'], n=3)
                        
                        if goals:
                            st.success("✅ 可视化方案生成成功")
                            
                            # 显示生成的目标
                            st.subheader("🎯 推荐的可视化方案")
                            for i, goal in enumerate(goals):
                                with st.expander(f"方案 {i+1}: {goal.question}", expanded=(i==0)):
                                    st.write(f"**可视化类型**: {goal.visualization}")
                                    st.write(f"**基本原理**: {goal.rationale}")
                        else:
                            st.warning("未能生成可视化方案，请尝试调整描述")
                    else:
                        st.error("❌ 无法连接到LLM服务")
                        
                except Exception as e:
                    st.error(f"❌ 可视化生成失败: {e}")
    else:
        st.info("请先生成数据摘要")

# 页脚
st.markdown("---")
st.markdown(
    '''
    <div style='text-align: center; color: #666;'>
        <p>🤖 由 LIDA + 自定义LLM 驱动 | 📊 智能数据可视化助手</p>
    </div>
    ''',
    unsafe_allow_html=True
)
"""
    
    # 写入临时应用文件
    with open('temp_lida_app.py', 'w', encoding='utf-8') as f:
        f.write(app_content)
    
    print("✅ Streamlit应用文件创建成功")

if __name__ == "__main__":
    start_lida_web()