import ReactECharts from 'echarts-for-react'
import { useState, useEffect } from 'react'

function EvolutionTreeChart() {
  const [treeData, setTreeData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/data/evolution_tree.json')
      .then(res => res.json())
      .then(data => {
        setTreeData(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('加载演化树数据失败:', err)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '50px', color: '#94a3b8' }}>加载中...</div>
  }

  if (!treeData) {
    return <div style={{ textAlign: 'center', padding: '50px', color: '#ef4444' }}>数据加载失败</div>
  }

  const option = {
    title: {
      text: '交互式技术演化树',
      subtext: '从基础模型到具体创新的演化路径（可拖拽缩放，点击展开/折叠）',
      left: 'center',
      textStyle: {
        color: '#e2e8f0',
        fontSize: 24,
        fontWeight: 'bold'
      },
      subtextStyle: {
        color: '#94a3b8',
        fontSize: 14
      }
    },
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove',
      backgroundColor: 'rgba(30, 41, 59, 0.98)',
      borderColor: '#3b82f6',
      borderWidth: 2,
      padding: 15,
      textStyle: {
        color: '#e2e8f0',
        fontSize: 13
      },
      formatter: (params) => {
        const data = params.data
        
        // 根节点
        if (data.name === treeData.name) {
          return `<div style="font-size: 16px; font-weight: bold; color: #3b82f6;">${data.name}</div>`
        }
        
        // 叶子节点（具体模型）- 显示详细信息
        if (data.attributes) {
          const attrs = data.attributes
          // 限制描述长度，避免超出
          const maxDescLength = 150
          let desc = attrs.desc || ''
          if (desc.length > maxDescLength) {
            desc = desc.substring(0, maxDescLength) + '...'
          }
          
          return `
            <div style="max-width: 350px; word-wrap: break-word; white-space: normal;">
              <div style="font-size: 14px; font-weight: bold; color: #3b82f6; margin-bottom: 8px; word-break: break-word;">
                ${data.name}
              </div>
              <div style="margin-bottom: 6px; color: #94a3b8;">
                <span style="color: #10b981;">📅 ${attrs.year}</span> | 
                <span style="color: #f59e0b;">📋 ${attrs.type}</span>
              </div>
              <div style="margin-bottom: 6px; padding: 8px; background: rgba(59, 130, 246, 0.1); border-radius: 4px;">
                <div style="font-size: 11px; color: #8b5cf6; margin-bottom: 4px;">创新机制：</div>
                <div style="font-size: 11px; color: #e2e8f0; word-break: break-word;">${attrs.topic}</div>
              </div>
              <div style="font-size: 11px; line-height: 1.5; color: #cbd5e1; word-break: break-word;">
                ${desc}
              </div>
            </div>
          `
        }
        
        // 中间节点（基础模型或一级主题）
        return `
          <div style="font-size: 14px; font-weight: bold; color: #8b5cf6;">
            ${data.name}
          </div>
          <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
            ${data.children ? data.children.length + ' 个子节点' : ''}
          </div>
        `
      }
    },
    series: [
      {
        type: 'tree',
        data: [treeData],
        top: '10%',
        left: '5%',
        bottom: '5%',
        right: '20%',
        symbolSize: (value, params) => {
          // 根据层级设置不同大小
          if (params.data.name === treeData.name) return 40  // 根节点
          if (params.data.attributes) return 10  // 叶子节点
          if (params.data.symbolSize) return params.data.symbolSize  // 自定义大小
          return 15  // 默认中间节点
        },
        label: {
          position: 'right',
          verticalAlign: 'middle',
          align: 'left',
          fontSize: 11,
          color: '#e2e8f0',
          distance: 8
        },
        leaves: {
          label: {
            position: 'right',
            verticalAlign: 'middle',
            align: 'left',
            fontSize: 10,
            color: '#cbd5e1'
          }
        },
        emphasis: {
          focus: 'descendant',
          itemStyle: {
            borderColor: '#3b82f6',
            borderWidth: 2,
            shadowBlur: 10,
            shadowColor: 'rgba(59, 130, 246, 0.5)'
          },
          label: {
            fontSize: 13,
            fontWeight: 'bold',
            color: '#3b82f6'
          }
        },
        expandAndCollapse: true,
        animationDuration: 550,
        animationDurationUpdate: 750,
        initialTreeDepth: 2,  // 初始只展开2层
        orient: 'LR',  // 从左到右
        layout: 'orthogonal',  // 正交布局
        lineStyle: {
          color: '#475569',
          width: 1.5,
          curveness: 0.5
        },
        itemStyle: {
          borderWidth: 1.5,
          borderColor: '#334155'
        },
        roam: true  // 允许缩放和平移
      }
    ],
    backgroundColor: 'transparent'
  }

  return (
    <ReactECharts
      option={option}
      style={{ height: '800px', width: '100%' }}
      opts={{ renderer: 'canvas' }}
    />
  )
}

export default EvolutionTreeChart

