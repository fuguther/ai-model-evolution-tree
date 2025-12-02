import ReactECharts from 'echarts-for-react'

function InfluenceBarChart({ data }) {
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
      axisPointer: {
        type: 'shadow'
      },
      backgroundColor: 'rgba(30, 41, 59, 0.95)',
      borderColor: '#3b82f6',
      borderWidth: 1,
      textStyle: {
        color: '#e2e8f0'
      },
      formatter: (params) => {
        const param = params[0]
        return `${param.name}<br/>引用次数: ${param.value}`
      }
    },
    grid: {
      left: '25%',
      right: '5%',
      bottom: '10%',
      top: '15%',
      containLabel: false
    },
    xAxis: {
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
    yAxis: {
      type: 'category',
      data: data.categories,
      axisLabel: {
        color: '#94a3b8',
        fontSize: 11,
        interval: 0
      },
      axisLine: {
        lineStyle: {
          color: '#334155'
        }
      }
    },
    series: [
      {
        type: 'bar',
        data: data.values.map((value, index) => ({
          value: value,
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 1,
              y2: 0,
              colorStops: [
                {
                  offset: 0,
                  color: '#3b82f6'
                },
                {
                  offset: 1,
                  color: '#8b5cf6'
                }
              ]
            }
          }
        })),
        label: {
          show: true,
          position: 'right',
          color: '#e2e8f0',
          fontSize: 11
        }
      }
    ],
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

export default InfluenceBarChart

