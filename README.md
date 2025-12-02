# AI 模型生长树项目

## 📋 项目简介

本项目用于分析和可视化 AI 模型的演化树，包括论文数据处理、聚类分析和交互式可视化。

## 📁 项目结构

```
.
├── 模型生长树代码/          # 数据处理和提取
│   ├── pipeline/           # 数据提取管道
│   ├── requirements.txt    # Python 依赖
│   └── env.example         # 环境变量模板
├── 聚类结果/                # 聚类分析和可视化
│   ├── dashboard/          # 前端可视化界面
│   └── generate_*.py       # 数据生成脚本
└── README.md               # 本文件
```

## 🚀 快速开始

### 前置要求

- Python 3.8+ 
- Node.js 16+ 和 npm
- Git

### 1. 安装依赖

#### macOS / Linux

```bash
# Python 依赖
cd 模型生长树代码
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Node.js 依赖（用于前端）
cd 聚类结果/dashboard
npm install
```

#### Windows

```powershell
# Python 依赖
cd 模型生长树代码
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Node.js 依赖（用于前端）
cd 聚类结果\dashboard
npm install
```

### 2. 配置环境变量

#### macOS / Linux

```bash
cd 模型生长树代码
cp env.example .env
# 编辑 .env 文件，填入你的 API 密钥
```

#### Windows

```powershell
cd 模型生长树代码
copy env.example .env
# 编辑 .env 文件，填入你的 API 密钥
```

### 3. 运行项目

#### macOS / Linux

```bash
# 数据处理
cd 模型生长树代码/pipeline
python3 extract.py --in your_data.xlsx

# 启动前端
cd 聚类结果/dashboard
npm run dev
```

#### Windows

```powershell
# 数据处理
cd 模型生长树代码\pipeline
python extract.py --in your_data.xlsx

# 启动前端
cd 聚类结果\dashboard
npm run dev
```

## 📝 贡献指南

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

[添加你的许可证信息]

## 👥 贡献者

[添加贡献者信息]
