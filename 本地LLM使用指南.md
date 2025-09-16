# LIDA 本地LLM大模型使用指南

## 📖 概述

本指南将帮助你配置和使用本地大语言模型（LLM）来运行LIDA，无需OpenAI API密钥，完全免费使用！

## 🎯 优势

✅ **完全免费** - 无需付费API密钥  
✅ **数据隐私** - 数据不会发送到外部服务器  
✅ **离线使用** - 配置完成后可离线运行  
✅ **自定义控制** - 可以选择适合的模型大小和性能  

## 🚀 快速开始

### 方法一：使用配置工具（推荐新手）

```bash
# 进入LIDA目录
cd lida-main

# 运行配置工具
python setup_local_llm.py
```

按照提示选择配置方式，工具会自动帮你完成配置。

### 方法二：使用启动脚本（推荐有经验用户）

```bash
# 使用HuggingFace模型（推荐）
python start_with_local_llm.py --model huggingface

# 使用Ollama模型
python start_with_local_llm.py --model ollama

# 使用vLLM服务器
python start_with_local_llm.py --model vllm
```

## 🤖 支持的本地模型类型

### 1. HuggingFace 模型（推荐新手）

**优点：**
- 配置简单，一键启动
- 模型质量高
- 社区支持好

**缺点：**
- 首次下载模型需要时间
- 需要较多内存

**推荐模型：**
- `microsoft/DialoGPT-medium` - 轻量级，适合入门
- `microsoft/DialoGPT-large` - 效果更好，需要更多内存
- `codellama/CodeLlama-7b-Instruct-hf` - 专门用于代码生成

**使用方法：**
```python
from lida import Manager, llm

# 创建HuggingFace文本生成器
text_gen = llm(
    provider="hf",
    model="microsoft/DialoGPT-medium",
    device_map="auto"  # 自动分配GPU/CPU
)

# 创建LIDA管理器
lida = Manager(text_gen=text_gen)
```

### 2. Ollama 服务器（推荐日常使用）

**优点：**
- 轻量级，资源占用少
- 启动快速
- 支持多种开源模型

**缺点：**
- 需要单独安装Ollama
- 需要手动管理模型

**安装步骤：**
```bash
# 1. 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. 启动Ollama服务
ollama serve

# 3. 下载模型（新开终端窗口）
ollama pull llama2        # 基础模型
ollama pull codellama     # 代码专用模型
ollama pull mistral       # 高性能模型
```

**使用方法：**
```python
from lida import Manager, llm

# 配置Ollama连接
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

lida = Manager(text_gen=text_gen)
```

### 3. vLLM 服务器（推荐高性能需求）

**优点：**
- 高性能推理
- 支持批量处理
- OpenAI兼容API

**缺点：**
- 配置相对复杂
- 需要较好的硬件

**安装步骤：**
```bash
# 1. 安装vLLM
pip install vllm

# 2. 启动vLLM服务器
python -m vllm.entrypoints.openai.api_server \
    --model microsoft/DialoGPT-medium \
    --port 8000
```

**使用方法：**
```python
from lida import Manager, llm

# 配置vLLM连接
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

lida = Manager(text_gen=text_gen)
```

## 💻 系统要求

### 最低配置
- **内存：** 8GB RAM
- **存储：** 10GB 可用空间
- **Python：** 3.9+

### 推荐配置
- **内存：** 16GB+ RAM
- **显卡：** NVIDIA GPU（可选，加速推理）
- **存储：** 20GB+ 可用空间
- **网络：** 首次下载模型需要稳定网络

## 🛠️ 安装依赖

```bash
# 基础依赖
pip install -U lida llmx

# HuggingFace支持
pip install transformers torch

# GPU支持（可选）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# vLLM支持（可选）
pip install vllm
```

## 📝 使用示例

### 完整的数据可视化流程

```python
from lida import Manager, llm
import pandas as pd

# 1. 配置本地模型
text_gen = llm(
    provider="hf",
    model="microsoft/DialoGPT-medium",
    device_map="auto"
)

lida = Manager(text_gen=text_gen)

# 2. 准备数据
data = pd.DataFrame({
    'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    'sales': [100, 120, 140, 110, 160],
    'profit': [20, 25, 30, 22, 35]
})
data.to_csv('sales_data.csv', index=False)

# 3. 生成数据摘要
summary = lida.summarize(
    data='sales_data.csv',
    file_name='sales_data.csv',
    summary_method='default'  # 使用基础摘要，不依赖LLM
)

print(f"数据摘要: {summary.name}")
print(f"行数: {summary.shape[0]}, 列数: {summary.shape[1]}")

# 4. 生成可视化目标（需要LLM）
try:
    goals = lida.goals(summary, n=3)
    print(f"生成了 {len(goals)} 个可视化目标")
    
    # 5. 生成图表
    if goals:
        charts = lida.visualize(
            summary=summary,
            goal=goals[0],
            library='matplotlib'
        )
        print(f"生成了 {len(charts)} 个图表")
except Exception as e:
    print(f"LLM功能出错: {e}")
    print("可以使用基础摘要功能，但需要手动创建可视化目标")
```

### 启动Web界面

```bash
# 使用本地模型启动Web界面
python start_with_local_llm.py --model huggingface --port 8080

# 然后在浏览器中访问
# http://localhost:8080
```

## 🔧 故障排除

### 常见问题

**Q: 模型下载很慢或失败？**
A: 
- 检查网络连接
- 使用国内镜像：`export HF_ENDPOINT=https://hf-mirror.com`
- 尝试更小的模型

**Q: 内存不足错误？**
A:
- 使用更小的模型（如DialoGPT-medium而不是large）
- 关闭其他占用内存的程序
- 使用CPU而不是GPU：`device_map="cpu"`

**Q: Ollama连接失败？**
A:
- 确保Ollama服务正在运行：`ollama serve`
- 检查端口是否被占用
- 确认模型已下载：`ollama list`

**Q: 生成的图表质量不好？**
A:
- 尝试使用更大的模型
- 调整温度参数：`TextGenerationConfig(temperature=0.7)`
- 使用专门的代码生成模型（如CodeLlama）

### 性能优化建议

1. **使用GPU加速**
   ```python
   # 确保安装了CUDA版本的PyTorch
   text_gen = llm(
       provider="hf",
       model="microsoft/DialoGPT-medium",
       device_map="cuda"  # 强制使用GPU
   )
   ```

2. **调整模型参数**
   ```python
   from lida.datamodel import TextGenerationConfig
   
   config = TextGenerationConfig(
       temperature=0.3,    # 降低随机性
       max_tokens=1000,    # 限制输出长度
       n=1                 # 只生成一个结果
   )
   ```

3. **使用缓存**
   ```python
   config = TextGenerationConfig(use_cache=True)
   goals = lida.goals(summary, textgen_config=config)
   ```

## 🎉 总结

通过本指南，你现在可以：

1. ✅ 选择适合的本地LLM模型
2. ✅ 配置和启动本地模型服务
3. ✅ 使用LIDA进行数据可视化
4. ✅ 解决常见问题和优化性能

**推荐学习路径：**
1. 新手：从HuggingFace模型开始
2. 进阶：尝试Ollama获得更好的性能
3. 高级：使用vLLM进行生产环境部署

**下一步：**
- 尝试不同的模型和参数
- 探索LIDA的高级功能
- 集成到你的数据分析工作流中

祝你使用愉快！🚀