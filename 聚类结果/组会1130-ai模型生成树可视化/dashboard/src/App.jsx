import { useState, useEffect } from 'react'
import DashboardLayout from './components/DashboardLayout'
import './App.css'

function App() {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('/data/dashboard_data.json')
      .then(res => res.json())
      .then(data => {
        setDashboardData(data)
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>正在加载数据...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>加载错误</h2>
        <p>{error}</p>
      </div>
    )
  }

  if (!dashboardData) {
    return (
      <div className="error-container">
        <h2>数据未找到</h2>
      </div>
    )
  }

  return <DashboardLayout data={dashboardData} />
}

export default App

