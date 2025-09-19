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
# 检查是否需要自动切换到数据可视化页签
if 'switch_to_viz' in st.session_state and st.session_state.switch_to_viz:
    # 清除切换标记
    del st.session_state.switch_to_viz
    # 设置默认选中的标签页为数据可视化（索引3）
    st.session_state.selected_tab = 3
    # 强制更新radio选择器的状态
    st.session_state.tab_selector = "📈 数据可视化"
    # 显示自动切换提示
    st.info("🎯 已自动切换到数据可视化页面，图表正在生成中...")

# 创建标签页，根据session_state选择默认标签页
selected_tab_index = st.session_state.get('selected_tab', 0)
tab_names = ["📁 数据上传", "📊 数据摘要", "🎯 目标生成", "📈 数据可视化", "✏️ 图表编辑", "🎨 智能推荐"]

# 使用radio来模拟标签页切换
# 如果session_state中已经有tab_selector的值，使用它；否则使用索引
if "tab_selector" in st.session_state:
    # 确保session_state中的值在tab_names中
    if st.session_state.tab_selector in tab_names:
        default_index = tab_names.index(st.session_state.tab_selector)
    else:
        default_index = selected_tab_index
else:
    default_index = selected_tab_index

selected_tab_name = st.radio(
    "选择功能页面",
    tab_names,
    index=default_index,
    horizontal=True,
    key="tab_selector"
)

# 更新选中的标签页索引
new_tab_index = tab_names.index(selected_tab_name)
if new_tab_index != selected_tab_index:
    st.session_state.selected_tab = new_tab_index
    st.rerun()

# 根据选中的标签页显示对应内容
if selected_tab_name == "📁 数据上传":
    st.header("📁 上传数据文件")
    
    uploaded_file = st.file_uploader(
        "选择数据文件",
        type=["csv", "xlsx", "xls"],
        help="请上传CSV或Excel格式的数据文件"
    )
    
    if uploaded_file is not None:
        try:
            # 根据文件扩展名选择读取方法
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
            
            # 保存数据到session state
            st.session_state.data = df
            st.session_state.filename = uploaded_file.name
            
            # 同时保存文件到lida/web/files/data目录，供LIDA库使用
            import os
            data_folder = os.path.join(os.path.dirname(__file__), "lida/web/files/data")
            os.makedirs(data_folder, exist_ok=True)
            file_path = os.path.join(data_folder, uploaded_file.name)
            
            # 根据文件类型保存
            if file_extension == 'csv':
                df.to_csv(file_path, index=False, encoding='utf-8')
            else:  # Excel文件转换为CSV保存
                csv_filename = uploaded_file.name.rsplit('.', 1)[0] + '.csv'
                csv_path = os.path.join(data_folder, csv_filename)
                df.to_csv(csv_path, index=False, encoding='utf-8')
                st.session_state.filename = csv_filename  # 更新文件名为CSV格式
            
        except Exception as e:
            st.error(f"❌ 文件读取失败: {e}")
            st.info("💡 提示：如果是Excel文件，请确保文件格式正确且没有密码保护")
    
    # 显示已上传的数据（如果存在）
    if 'data' in st.session_state and 'filename' in st.session_state:
        st.subheader("📊 当前已上传的数据")
        st.info(f"📁 文件名: {st.session_state.filename}")
        st.info(f"📏 数据形状: {st.session_state.data.shape}")
        
        # 显示数据预览
        st.subheader("📋 数据预览")
        st.dataframe(st.session_state.data.head(10))
        
        # 提供清除数据的选项
        if st.button("🗑️ 清除当前数据", type="secondary"):
            if 'data' in st.session_state:
                del st.session_state.data
            if 'filename' in st.session_state:
                del st.session_state.filename
            if 'summary' in st.session_state:
                del st.session_state.summary
            if 'generated_goals' in st.session_state:
                del st.session_state.generated_goals
            if 'current_charts' in st.session_state:
                del st.session_state.current_charts
            st.success("✅ 数据已清除，请重新上传文件")
            st.rerun()

elif selected_tab_name == "📊 数据摘要":
    st.header("📊 数据摘要")
    
    if 'data' in st.session_state:
        # 显示已生成的摘要（如果存在）
        if 'summary' in st.session_state:
            st.success("✅ 数据摘要已生成！")
            
            # 显示摘要信息
            st.subheader("📋 数据集信息")
            st.write(f"**文件名:** {st.session_state.filename}")
            st.write(f"**数据形状:** {st.session_state.data.shape}")
            st.write(f"**列数:** {len(st.session_state.summary.field_names)}")
            
            # 显示数据集描述
            if st.session_state.summary.dataset_description:
                st.write(f"**数据集描述:** {st.session_state.summary.dataset_description}")
            
            # 显示字段信息
            st.subheader("📊 列信息")
            fields = st.session_state.summary.fields or []
            for field in fields:
                column_name = field.get('column', 'Unknown')
                properties = field.get('properties', {})
                dtype = properties.get('dtype', 'Unknown')
                description = properties.get('description', '无描述')
                samples = properties.get('samples', [])
                
                st.write(f"- **{column_name}** ({dtype}): {description}")
                if samples:
                    st.write(f"  示例值: {', '.join(map(str, samples[:3]))}")
            
            # 提供重新生成选项
            if st.button("🔄 重新生成数据摘要", type="secondary"):
                try:
                    with st.spinner("正在重新分析数据..."):
                        # 获取LIDA管理器
                        lida = get_lida_manager()
                        
                        # 生成数据摘要
                        summary = lida.summarize(
                            data=st.session_state.data,
                            file_name=st.session_state.filename
                        )
                        
                        # 保存摘要到session state
                        st.session_state.summary = summary
                        st.success("✅ 数据摘要重新生成成功！")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ 摘要重新生成失败: {e}")
        else:
            # 首次生成摘要
            if st.button("🔍 生成数据摘要", type="primary"):
                try:
                    with st.spinner("正在分析数据..."):
                        # 获取LIDA管理器
                        lida = get_lida_manager()
                        
                        # 生成数据摘要
                        summary = lida.summarize(
                            data=st.session_state.data,
                            file_name=st.session_state.filename
                        )
                        
                        # 保存摘要到session state
                        st.session_state.summary = summary
                        st.success("✅ 数据摘要生成成功！")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ 摘要生成失败: {e}")
    else:
        st.info("请先在'数据上传'标签页中上传数据文件")

elif selected_tab_name == "🎯 目标生成":
    st.header("🎯 AI目标生成")
    st.markdown("让AI帮你想想可以画什么图表！")
    
    if 'summary' in st.session_state:
        # 角色选择
        persona_options = {
            "数据分析师": "data analyst",
            "业务经理": "business manager", 
            "CEO": "ceo",
            "市场营销专员": "marketing specialist",
            "财务分析师": "financial analyst",
            "产品经理": "product manager"
        }
        
        selected_persona = st.selectbox(
            "🎭 选择分析角色",
            options=list(persona_options.keys()),
            help="不同角色会生成不同视角的分析目标"
        )
        
        # 目标数量选择
        goal_count = st.slider(
            "📊 生成目标数量",
            min_value=3,
            max_value=8,
            value=5,
            help="选择要生成多少个可视化目标"
        )
        
        if st.button("🎯 生成可视化目标", type="primary"):
            try:
                with st.spinner("AI正在分析数据并生成目标..."):
                    # 获取LIDA管理器
                    lida = get_lida_manager()
                    
                    # 导入配置类
                    from lida.datamodel import TextGenerationConfig
                    
                    # 生成目标
                    goals = lida.goals(
                        summary=st.session_state.summary,
                        n=goal_count,
                        persona=persona_options[selected_persona],
                        textgen_config=TextGenerationConfig(n=1, temperature=0.3)
                    )
                    
                    if goals:
                        st.success(f"✅ 生成了 {len(goals)} 个可视化目标！")
                        
                        # 保存生成的目标
                        st.session_state.generated_goals = goals
                    else:
                        st.warning("未能生成目标，请重试")
                        
            except Exception as e:
                st.error(f"❌ 目标生成失败: {e}")
        
        # 显示已保存的目标（无论是刚生成的还是之前保存的）
        if 'generated_goals' in st.session_state and st.session_state.generated_goals:
            st.subheader("📋 已生成的可视化目标")
            goals = st.session_state.generated_goals
            
            for i, goal in enumerate(goals):
                with st.expander(f"🎯 目标 {i+1}: {goal.question}", expanded=True):
                    st.write(f"**问题:** {goal.question}")
                    st.write(f"**可视化建议:** {goal.visualization}")
                    st.write(f"**分析理由:** {goal.rationale}")
                    
                    # 快速生成按钮
                    if st.button(f"🚀 立即生成此图表", key=f"generate_{i}"):
                        # 设置标记，表示需要切换到数据可视化页签并生成图表
                        st.session_state.auto_generate_goal = goal.question
                        st.session_state.switch_to_viz = True
                        # 立即重新运行页面以触发切换
                        st.rerun()
    else:
        st.info("请先生成数据摘要")

elif selected_tab_name == "📈 数据可视化":
    st.header("📈 数据可视化")
    
    if 'summary' in st.session_state:
        # 检查是否有自动生成的目标
        default_goal = ""
        if 'auto_generate_goal' in st.session_state:
            default_goal = st.session_state.auto_generate_goal
            # 自动触发生成
            auto_generate = True
        else:
            auto_generate = False
        
        goal = st.text_area(
            "🎯 描述你想要的图表",
            value=default_goal,
            placeholder="例如：显示各月份销售额的柱状图",
            help="用自然语言描述你想要创建的图表"
        )
        
        # 如果是自动生成模式或用户点击按钮，则生成图表
        if (auto_generate and goal) or (st.button("🎨 生成可视化", type="primary") and goal):
            # 清除自动生成标记
            if 'auto_generate_goal' in st.session_state:
                del st.session_state.auto_generate_goal
            try:
                with st.spinner("正在生成可视化..."):
                    # 获取LIDA管理器
                    lida = get_lida_manager()
                    
                    # 导入配置类
                    from lida.datamodel import TextGenerationConfig
                    
                    # 生成可视化
                    charts = lida.visualize(
                        summary=st.session_state.summary,
                        goal=goal,
                        textgen_config=TextGenerationConfig(n=1, temperature=0),
                        library="matplotlib",
                        data=st.session_state.data
                    )
                    
                    if charts:
                        st.success(f"✅ 生成了 {len(charts)} 个可视化方案！")
                        
                        # 保存当前图表和目标，用于编辑功能
                        st.session_state.current_charts = charts
                        st.session_state.current_goal = goal
                        
                        # 显示生成的图表
                        for i, chart in enumerate(charts):
                            st.subheader(f"📊 方案 {i+1}")
                            
                            # 显示代码
                            with st.expander("查看生成的代码"):
                                st.code(chart.code, language="python")
                            
                            # 显示图表
                            try:
                                if chart.status and chart.raster:
                                    # 导入必要的库
                                    import base64
                                    from io import BytesIO
                                    from PIL import Image
                                    
                                    # 解码base64图片数据
                                    image_data = base64.b64decode(chart.raster)
                                    image = Image.open(BytesIO(image_data))
                                    
                                    # 显示图表图片
                                    st.image(image, caption=f"方案 {i+1}", use_container_width=True)
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
                                # 显示调试信息
                                with st.expander("查看生成的代码（调试用）"):
                                    st.code(chart.code, language="python")
                    else:
                        st.warning("未能生成可视化方案，请尝试调整描述")
                        
            except Exception as e:
                st.error(f"❌ 可视化生成失败: {e}")
    else:
        st.info("请先生成数据摘要")

elif selected_tab_name == "✏️ 图表编辑":
    st.header("✏️ 图表编辑")
    st.markdown("用自然语言修改你的图表！")
    
    if 'current_charts' in st.session_state and st.session_state.current_charts:
        # 选择要编辑的图表
        chart_options = [f"方案 {i+1}" for i in range(len(st.session_state.current_charts))]
        selected_chart_idx = st.selectbox(
            "📊 选择要编辑的图表",
            options=range(len(chart_options)),
            format_func=lambda x: chart_options[x]
        )
        
        # 显示当前图表
        current_chart = st.session_state.current_charts[selected_chart_idx]
        st.subheader("📊 当前图表")
        
        # 显示当前图表
        try:
            if current_chart.status and current_chart.raster:
                import base64
                from io import BytesIO
                from PIL import Image
                
                image_data = base64.b64decode(current_chart.raster)
                image = Image.open(BytesIO(image_data))
                st.image(image, caption="当前图表", use_container_width=True)
        except Exception as e:
            st.error(f"图表显示失败: {e}")
        
        # 编辑指令输入
        st.subheader("✏️ 编辑指令")
        edit_instructions = st.text_area(
            "📝 描述你想要的修改",
            placeholder="例如：\n- 改成柱状图\n- 颜色改成蓝色\n- 添加标题'销售数据分析'\n- 调整字体大小",
            help="用自然语言描述你想要的修改，可以写多条指令"
        )
        
        if st.button("✏️ 应用修改", type="primary") and edit_instructions:
            try:
                with st.spinner("正在修改图表..."):
                    # 获取LIDA管理器
                    lida = get_lida_manager()
                    
                    # 设置数据到管理器中 - 这是关键修复
                    lida.data = st.session_state.data
                    
                    # 导入配置类
                    from lida.datamodel import TextGenerationConfig
                    
                    # 将指令分割成列表
                    instructions_list = [inst.strip() for inst in edit_instructions.split('\n') if inst.strip()]
                    
                    # 编辑图表 - 添加data参数和return_error参数以获得更好的错误处理
                    edited_charts = lida.edit(
                        code=current_chart.code,
                        summary=st.session_state.summary,
                        instructions=instructions_list,
                        library="matplotlib",
                        textgen_config=TextGenerationConfig(n=1, temperature=0),
                        return_error=True
                    )
                    
                    if edited_charts:
                        st.success("✅ 图表修改成功！")
                        
                        # 显示修改后的图表
                        for i, edited_chart in enumerate(edited_charts):
                            st.subheader(f"✨ 修改后的图表 {i+1}")
                            
                            # 显示修改后的代码
                            with st.expander("查看修改后的代码"):
                                st.code(edited_chart.code, language="python")
                            
                            # 显示修改后的图表
                            try:
                                if edited_chart.status and edited_chart.raster:
                                    import base64
                                    from io import BytesIO
                                    from PIL import Image
                                    
                                    image_data = base64.b64decode(edited_chart.raster)
                                    image = Image.open(BytesIO(image_data))
                                    st.image(image, caption=f"修改后的图表 {i+1}")
                                elif edited_chart.error:
                                    st.error(f"图表修改失败: {edited_chart.error.get('message', '未知错误')}")
                                    if 'traceback' in edited_chart.error:
                                        with st.expander("查看详细错误信息"):
                                            st.code(edited_chart.error['traceback'], language="text")
                            except Exception as display_e:
                                st.error(f"修改后图表显示失败: {display_e}")
                    else:
                        st.warning("图表修改失败，请尝试调整指令")
                        
            except Exception as e:
                st.error(f"❌ 图表编辑失败: {e}")
    else:
        st.info("请先在'数据可视化'标签页中生成图表")

elif selected_tab_name == "🎨 智能推荐":
    st.header("🎨 智能推荐")
    st.markdown("AI为你推荐最适合的图表类型！")
    
    if 'summary' in st.session_state:
        # 推荐数量选择
        recommend_count = st.slider(
            "📊 推荐图表数量",
            min_value=2,
            max_value=6,
            value=3,
            help="选择要推荐多少种图表类型"
        )
        
        if st.button("🎨 获取智能推荐", type="primary"):
            try:
                with st.spinner("AI正在分析数据特征并生成推荐..."):
                    # 获取LIDA管理器
                    lida = get_lida_manager()
                    
                    # 导入配置类
                    from lida.datamodel import TextGenerationConfig
                    
                    # 获取推荐
                    recommendations = lida.recommend(
                        summary=st.session_state.summary,
                        n=recommend_count,
                        textgen_config=TextGenerationConfig(n=1, temperature=0.2)
                    )
                    
                    if recommendations:
                        st.success(f"✅ 生成了 {len(recommendations)} 个推荐方案！")
                        
                        # 显示推荐结果
                        for i, rec in enumerate(recommendations):
                            with st.expander(f"🎨 推荐 {i+1}: {rec.question}", expanded=True):
                                st.write(f"**推荐问题:** {rec.question}")
                                st.write(f"**可视化类型:** {rec.visualization}")
                                st.write(f"**推荐理由:** {rec.rationale}")
                                
                                # 生成推荐图表按钮
                                col1, col2 = st.columns([1, 1])
                                with col1:
                                    if st.button(f"🚀 生成此推荐图表", key=f"rec_generate_{i}"):
                                        try:
                                            with st.spinner("正在生成推荐图表..."):
                                                # 直接生成推荐的图表
                                                charts = lida.visualize(
                                                    summary=st.session_state.summary,
                                                    goal=rec.question,
                                                    textgen_config=TextGenerationConfig(n=1, temperature=0),
                                                    library="matplotlib",
                                                    data=st.session_state.data
                                                )
                                                
                                                if charts and charts[0].status and charts[0].raster:
                                                    import base64
                                                    from io import BytesIO
                                                    from PIL import Image
                                                    
                                                    image_data = base64.b64decode(charts[0].raster)
                                                    image = Image.open(BytesIO(image_data))
                                                    st.image(image, caption=f"推荐图表 {i+1}")
                                                else:
                                                    st.error("推荐图表生成失败")
                                        except Exception as gen_e:
                                            st.error(f"生成推荐图表失败: {gen_e}")
                    else:
                        st.warning("未能生成推荐，请重试")
                        
            except Exception as e:
                st.error(f"❌ 智能推荐失败: {e}")
    else:
        st.info("请先生成数据摘要")

# 页脚
st.markdown("---")
st.markdown("🚀 **LIDA智能数据可视化** - 让数据分析变得更简单！")
