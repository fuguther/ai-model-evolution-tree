import ReactECharts from 'echarts-for-react'

// 定义颜色方案
const COLORS = [
  '#3b82f6', // 蓝色 - 架构与拓扑创新
  '#8b5cf6', // 紫色 - 生成与分布创新
  '#ec4899', // 粉色 - 训练范式与学习策略创新
  '#10b981', // 绿色 - 决策与搜索创新
  '#f59e0b', // 橙色 - 时序与动态创新
  '#06b6d4', // 青色 - 特定几何/结构创新
]

function EvolutionStackChart({ data }) {
  const option = {
    title: {
      text: data.title,
      left: 'center',
      textStyle: {
        color: '#e2e8f0',
        fontSize: 20,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      },
      backgroundColor: 'rgba(30, 41, 59, 0.95)',
      borderColor: '#3b82f6',
      borderWidth: 1,
      textStyle: {
        color: '#e2e8f0'
      }
    },
    legend: {
      data: data.series.map(s => s.name),
      top: 40,
      textStyle: {
        color: '#94a3b8'
      },
      itemGap: 20
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.categories,
      axisLabel: {
        color: '#94a3b8',
        fontSize: 12
      },
      axisLine: {
        lineStyle: {
          color: '#334155'
        }
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#94a3b8',
        fontSize: 12
      },
      axisLine: {
        lineStyle: {
          color: '#334155'
        }
      },
      splitLine: {
        lineStyle: {
          color: '#1e293b',
          type: 'dashed'
        }
      }
    },
    dataZoom: [
      {
        type: 'slider',
        show: true,
        xAxisIndex: [0],
        bottom: 10,
        height: 20,
        handleStyle: {
          color: '#3b82f6'
        },
        textStyle: {
          color: '#94a3b8'
        },
        borderColor: '#334155'
      },
      {
        type: 'inside',
        xAxisIndex: [0],
        start: 50,
        end: 100
      }
    ],
    series: data.series.map((series, index) => ({
      ...series,
      itemStyle: {
        color: COLORS[index % COLORS.length]
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            {
              offset: 0,
              color: COLORS[index % COLORS.length]
            },
            {
              offset: 1,
              color: COLORS[index % COLORS.length] + '40' // 添加透明度
            }
          ]
        }
      }
    })),
    backgroundColor: 'transparent'
  }

  return (
    <ReactECharts
      option={option}
      style={{ height: '500px', width: '100%' }}
      opts={{ renderer: 'svg' }}
    />
  )
}

export default EvolutionStackChart

