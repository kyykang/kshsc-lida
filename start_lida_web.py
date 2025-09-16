#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIDA Web界面启动脚本
使用你配置好的自定义LLM服务

这个脚本会启动LIDA的Web界面，你可以通过浏览器访问来进行数据可视化
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def start_lida_web():
    """
    启动LIDA Web界面
    使用自定义LLM配置
    """
    try:
        # 导入必要的模块
        from custom_llm_config_working import get_lida_manager
        import streamlit as st
        
        print("🚀 正在启动LIDA Web界面...")
        print("📍 使用自定义LLM服务: http://10.254.28.17:30000")
        
        # 获取配置好的LIDA管理器
        lida = get_lida_manager()
        
        print("✅ LIDA管理器初始化成功！")
        print("🌐 正在启动Web服务器...")
        print("\n📝 启动后请在浏览器中访问显示的地址")
        print("💡 通常是: http://localhost:8501")
        print("\n⚠️  要停止服务器，请按 Ctrl+C")
        
        # 启动Streamlit应用
        # 这里需要创建一个简单的Streamlit应用
        create_streamlit_app()
        
        # 运行Streamlit
        os.system("streamlit run lida_app.py --server.port 8501")
        
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("\n可能需要安装Streamlit:")
        print("python3 -m pip install streamlit")
        return False
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

def create_streamlit_app():
    """
    创建一个简单的Streamlit应用文件
    """
    app_content = '''import streamlit as st
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
        """
        1. 上传CSV数据文件
        2. 查看数据摘要
        3. 生成可视化图表
        4. 下载结果
        """
    )

# 主要内容区域
tab1, tab2, tab3 = st.tabs(["📁 数据上传", "📊 数据摘要", "📈 可视化"])

with tab1:
    st.header("📁 上传数据文件")
    
    uploaded_file = st.file_uploader(
        "选择CSV文件",
        type=["csv"],
        help="请上传CSV格式的数据文件"
    )
    
    if uploaded_file is not None:
        try:
            # 读取数据
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ 文件上传成功！数据形状: {df.shape}")
            
            # 显示数据预览
            st.subheader("📋 数据预览")
            st.dataframe(df.head(10))
            
            # 保存到session state
            st.session_state.data = df
            st.session_state.filename = uploaded_file.name
            
        except Exception as e:
            st.error(f"❌ 文件读取失败: {e}")

with tab2:
    st.header("📊 数据摘要")
    
    if 'data' in st.session_state:
        if st.button("🔍 生成数据摘要", type="primary"):
            try:
                with st.spinner("正在分析数据..."):
                    # 获取LIDA管理器
                    lida = get_lida_manager()
                    
                    # 生成摘要
                    summary = lida.summarize(st.session_state.data)
                    
                    st.success("✅ 数据摘要生成成功！")
                    
                    # 显示摘要信息
                    st.subheader("📋 数据集信息")
                    st.write(f"**文件名:** {st.session_state.filename}")
                    st.write(f"**数据形状:** {summary.shape}")
                    st.write(f"**列数:** {len(summary.columns)}")
                    
                    # 显示列信息
                    st.subheader("📊 列信息")
                    for col in summary.columns:
                        st.write(f"- **{col.column_name}** ({col.column_type}): {col.column_description}")
                    
                    # 保存摘要到session state
                    st.session_state.summary = summary
                    
            except Exception as e:
                st.error(f"❌ 摘要生成失败: {e}")
    else:
        st.info("请先在'数据上传'标签页中上传数据文件")

with tab3:
    st.header("📈 数据可视化")
    
    if 'summary' in st.session_state:
        # 可视化目标输入
        goal = st.text_area(
            "📝 描述你想要的可视化",
            placeholder="例如: 显示各个类别的销售额分布",
            help="用自然语言描述你想要创建的图表"
        )
        
        if st.button("🎨 生成可视化", type="primary") and goal:
            try:
                with st.spinner("正在生成可视化..."):
                    # 获取LIDA管理器
                    lida = get_lida_manager()
                    
                    # 生成可视化
                    charts = lida.visualize(
                        summary=st.session_state.summary,
                        goal=goal,
                        library="matplotlib"
                    )
                    
                    if charts:
                        st.success(f"✅ 生成了 {len(charts)} 个可视化方案！")
                        
                        # 显示图表
                        for i, chart in enumerate(charts):
                            st.subheader(f"📊 方案 {i+1}")
                            
                            # 显示代码
                            with st.expander("查看生成的代码"):
                                st.code(chart.code, language="python")
                            
                            # 执行并显示图表
                            try:
                                exec(chart.code)
                                st.pyplot()
                            except Exception as exec_e:
                                st.error(f"图表执行失败: {exec_e}")
                    else:
                        st.warning("未能生成可视化方案，请尝试调整描述")
                        
            except Exception as e:
                st.error(f"❌ 可视化生成失败: {e}")
    else:
        st.info("请先生成数据摘要")

# 页脚
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🤖 由 LIDA + 自定义LLM 驱动 | 📊 智能数据可视化助手</p>
    </div>
    """,
    unsafe_allow_html=True
)
'''
    
    try:
        with open('lida_app.py', 'w', encoding='utf-8') as f:
            f.write(app_content)
        print("✅ Streamlit应用文件创建成功: lida_app.py")
        return True
    except Exception as e:
        print(f"❌ 创建Streamlit应用失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 LIDA Web界面启动器")
    print("=" * 30)
    
    # 检查依赖
    try:
        import streamlit
        print("✅ Streamlit已安装")
    except ImportError:
        print("❌ 需要安装Streamlit")
        print("运行: python3 -m pip install streamlit")
        sys.exit(1)
    
    # 启动Web界面
    start_lida_web()