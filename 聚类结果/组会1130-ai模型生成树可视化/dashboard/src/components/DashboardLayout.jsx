import EvolutionStackChart from './charts/EvolutionStackChart'
import NatureLineChart from './charts/NatureLineChart'
import InfluenceBarChart from './charts/InfluenceBarChart'
import RelationSankey from './charts/RelationSankey'
import EvolutionTreeChart from './charts/EvolutionTreeChart'
import './DashboardLayout.css'

function DashboardLayout({ data }) {
  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>AI创新机制仪表板</h1>
        <p>基于44个核心创新机制的数据可视化分析</p>
      </header>

      <div className="dashboard-grid">
        {/* 第一行：左侧堆叠面积图（2/3宽度），右侧柱状图（1/3宽度） */}
        <div className="chart-card chart-wide">
          <EvolutionStackChart data={data.evolution_l1} />
        </div>
        <div className="chart-card chart-narrow">
          <InfluenceBarChart data={data.model_influence} />
        </div>

        {/* 第二行：左侧折线图（1/3宽度），右侧桑基图（2/3宽度） */}
        <div className="chart-card chart-narrow">
          <NatureLineChart data={data.evolution_nature} />
        </div>
        <div className="chart-card chart-wide">
          <RelationSankey data={data.sankey_flow} />
        </div>

        {/* 第三行：技术演化树（全宽） */}
        <div className="chart-card chart-full">
          <EvolutionTreeChart />
        </div>
      </div>
    </div>
  )
}

export default DashboardLayout

