// App Component with Routing
import { Routes, Route } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import AgentsPage from './pages/Agents'
import ResourcesPage from './pages/Resources'
import CostPage from './pages/Cost'
import SecurityPage from './pages/Security'
import Layout from './components/Layout'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/agents" element={<AgentsPage />} />
        <Route path="/resources" element={<ResourcesPage />} />
        <Route path="/cost" element={<CostPage />} />
        <Route path="/security" element={<SecurityPage />} />
      </Routes>
    </Layout>
  )
}

export default App