# AI创新机制仪表板

基于React + ECharts的交互式数据可视化仪表板，展示AI创新机制的演化趋势和关系网络。

## 功能特性

- 📊 **一级主题演化图** - 堆叠面积图展示6大创新类别的年度变化
- 📈 **创新性质演化图** - 折线图展示Model/Variant/AdapterModel的趋势
- 📉 **模型影响力图** - 柱状图展示Top 15基础模型的引用次数
- 🌊 **桑基流向图** - 展示基础模型到创新类别的映射关系

## 技术栈

- React 18
- ECharts 5 (echarts-for-react)
- Vite
- CSS3 (深色主题，渐变效果)

## 快速开始

### 安装依赖

```bash
cd dashboard
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

## 项目结构

```
dashboard/
├── public/
│   └── data/
│       └── dashboard_data.json    # 图表数据
├── src/
│   ├── components/
│   │   ├── charts/                 # 图表组件
│   │   │   ├── EvolutionStackChart.jsx
│   │   │   ├── NatureLineChart.jsx
│   │   │   ├── InfluenceBarChart.jsx
│   │   │   └── RelationSankey.jsx
│   │   └── DashboardLayout.jsx    # 布局组件
│   ├── App.jsx                     # 主应用
│   ├── main.jsx                    # 入口文件
│   └── index.css                   # 全局样式
├── index.html
├── package.json
└── vite.config.js
```

## 图表说明

### 1. 一级主题演化（堆叠面积图）
- 展示2012-2024年间6大创新类别的演化趋势
- 支持时间轴缩放（DataZoom）
- 鼠标悬停查看详细数据

### 2. 创新性质演化（折线图）
- 展示Model、Variant、AdapterModel三种类型的趋势
- 平滑曲线，清晰展示增长模式

### 3. 模型影响力（柱状图）
- Top 15基础模型的引用次数排名
- 渐变色彩，直观展示影响力差异

### 4. 桑基流向图
- 展示10个基础模型与6个创新类别的映射关系
- 节点颜色区分：蓝色=基础模型，其他颜色=创新类别
- 流量大小反映关联强度

## 数据更新

如需更新数据：
1. 更新 `public/data/dashboard_data.json`
2. 刷新页面即可看到新数据

数据由 `generate_dashboard_data.py` 脚本生成。

## 浏览器支持

- Chrome (推荐)
- Firefox
- Safari
- Edge

## 开发说明

- 使用深色主题，适合长时间查看
- 响应式设计，支持不同屏幕尺寸
- SVG渲染，图表清晰可缩放
- 交互式提示，鼠标悬停显示详细信息

