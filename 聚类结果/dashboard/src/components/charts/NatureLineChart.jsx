import ReactECharts from 'echarts-for-react'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b']

function NatureLineChart({ data }) {
  const option = {
    title: {
      text: data.title,
      left: 'center',
      textStyle: {
        color: '#e2e8f0',
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
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
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.categories,
      axisLabel: {
        color: '#94a3b8',
        fontSize: 11
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
        fontSize: 11
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
    series: data.series.map((series, index) => ({
      ...series,
      lineStyle: {
        width: 3,
        color: COLORS[index % COLORS.length]
      },
      itemStyle: {
        color: COLORS[index % COLORS.length]
      },
      symbol: 'circle',
      symbolSize: 6
    })),
    backgroundColor: 'transparent'
  }

  return (
    <ReactECharts
      option={option}
      style={{ height: '400px', width: '100%' }}
      opts={{ renderer: 'svg' }}
    />
  )
}

export default NatureLineChart

