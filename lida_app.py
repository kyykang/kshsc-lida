import streamlit as st
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
        "**LLM服务地址:** http://10.254.28.17:30000\n"
        "**模型名称:** default\n"
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
        "选择数据文件",
        type=["csv", "xlsx", "xls"],
        help="请上传CSV或Excel格式的数据文件"
    )
    
    if uploaded_file is not None:
        try:
            # 根据文件扩展名选择读取方式
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'csv':
                # 读取CSV文件
                df = pd.read_csv(uploaded_file)
            elif file_extension in ['xlsx', 'xls']:
                # 读取Excel文件
                df = pd.read_excel(uploaded_file, engine='openpyxl' if file_extension == 'xlsx' else None)
            else:
                st.error("❌ 不支持的文件格式")
                st.stop()
            
            st.success(f"✅ 文件上传成功！数据形状: {df.shape}")
            
            # 显示数据预览
            st.subheader("📋 数据预览")
            st.dataframe(df.head(10))
            
            # 保存到session state
            st.session_state.data = df
            st.session_state.filename = uploaded_file.name
            
        except Exception as e:
            st.error(f"❌ 文件读取失败: {e}")
            st.info("💡 提示：如果是Excel文件，请确保文件格式正确且没有密码保护")

with tab2:
    st.header("📊 数据摘要")
    
    if 'data' in st.session_state:
        if st.button("🔍 生成数据摘要", type="primary"):
            try:
                with st.spinner("正在分析数据..."):
                    # 获取LIDA管理器
                    lida = get_lida_manager()
                    
                    # 生成摘要 - 传递文件名以确保summary对象包含file_name属性
                    summary = lida.summarize(
                        data=st.session_state.data,
                        file_name=st.session_state.filename
                    )
                    
                    st.success("✅ 数据摘要生成成功！")
                    
                    # 显示摘要信息
                    st.subheader("📋 数据集信息")
                    st.write(f"**文件名:** {st.session_state.filename}")
                    st.write(f"**数据形状:** {st.session_state.data.shape}")
                    st.write(f"**列数:** {len(summary.field_names)}")
                    
                    # 显示数据集描述（如果有）
                    if summary.dataset_description:
                        st.write(f"**数据集描述:** {summary.dataset_description}")
                    
                    # 显示列信息
                    st.subheader("📊 列信息")
                    fields = summary.fields or []
                    for field in fields:
                        column_name = field.get('column', 'Unknown')
                        properties = field.get('properties', {})
                        dtype = properties.get('dtype', 'Unknown')
                        description = properties.get('description', '无描述')
                        samples = properties.get('samples', [])
                        
                        st.write(f"- **{column_name}** ({dtype}): {description}")
                        if samples:
                            st.write(f"  示例值: {', '.join(map(str, samples[:3]))}")
                    
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
                    
                    # 导入TextGenerationConfig
                    from lida.datamodel import TextGenerationConfig
                    
                    # 生成可视化 - 传递数据参数
                    charts = lida.visualize(
                        summary=st.session_state.summary,
                        goal=goal,
                        textgen_config=TextGenerationConfig(n=1, temperature=0),
                        library="matplotlib",
                        data=st.session_state.data
                    )
                    
                    if charts:
                        st.success(f"✅ 生成了 {len(charts)} 个可视化方案！")
                        
                        # 显示图表
                        for i, chart in enumerate(charts):
                            st.subheader(f"📊 方案 {i+1}")
                            
                            # 显示代码
                            with st.expander("查看生成的代码"):
                                st.code(chart.code, language="python")
                            
                            # 显示图表 - LIDA已经执行过代码并生成了图表
                            try:
                                if chart.status and chart.raster:
                                    # 显示base64编码的图片
                                    import base64
                                    from io import BytesIO
                                    from PIL import Image
                                    
                                    # 解码base64图片数据
                                    image_data = base64.b64decode(chart.raster)
                                    image = Image.open(BytesIO(image_data))
                                    
                                    # 在Streamlit中显示图片
                                    st.image(image, caption=f"方案 {i+1}")
                                elif chart.error:
                                    # 显示错误信息
                                    st.error(f"图表生成失败: {chart.error.get('message', '未知错误')}")
                                    if 'traceback' in chart.error:
                                        with st.expander("查看详细错误信息"):
                                            st.code(chart.error['traceback'], language="text")
                                else:
                                    st.warning("图表生成成功但没有返回图片数据")
                            except Exception as display_e:
                                st.error(f"图表显示失败: {display_e}")
                                # 显示生成的代码以便调试
                                with st.expander("查看生成的代码（调试用）"):
                                    st.code(chart.code, language="python")
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
