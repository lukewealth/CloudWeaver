// Agent Dashboard Component
import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  ServerIcon, 
  ShieldCheckIcon, 
  CurrencyDollarIcon, 
  BoltIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline'
import { motion } from 'framer-motion'
import axios from 'axios'

interface AgentStatus {
  name: string
  status: 'running' | 'paused' | 'error'
  lastHeartbeat: string
  tasksCompleted: number
  activeTasks: number
}

interface ResourceMetrics {
  totalResources: number
  optimizedCount: number
  savingsThisMonth: number
  securityIssues: number
  pendingActions: number
}

export default function Dashboard() {
  const { data: agents, isLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => {
      const res = await axios.get('/api/agents/status')
      return res.data as AgentStatus[]
    },
    refetchInterval: 30000,
  })

  const { data: metrics } = useQuery({
    queryKey: ['metrics'],
    queryFn: async () => {
      const res = await axios.get('/api/dashboard/metrics')
      return res.data as ResourceMetrics
    },
    refetchInterval: 60000,
  })

  const agentCards = [
    { 
      name: 'CostOptimizer', 
      icon: CurrencyDollarIcon, 
      color: 'bg-green-500',
      description: 'Financial governance & waste detection'
    },
    { 
      name: 'SecurityAuditor', 
      icon: ShieldCheckIcon, 
      color: 'bg-blue-500',
      description: 'Continuous security scanning'
    },
    { 
      name: 'AutoScaler', 
      icon: BoltIcon, 
      color: 'bg-yellow-500',
      description: 'Predictive scaling & optimization'
    },
    { 
      name: 'IncidentResponder', 
      icon: ExclamationTriangleIcon, 
      color: 'bg-red-500',
      description: 'Auto-remediation & RCA'
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <ServerIcon className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">CloudWeaver</h1>
                <p className="text-sm text-gray-500">Multi-Agent Cloud Orchestrator</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-2 text-sm text-green-600">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                All systems operational
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Monthly Savings"
            value={`$${metrics?.savingsThisMonth?.toLocaleString() || '0'}`}
            trend="+23%"
            trendUp={true}
          />
          <MetricCard
            title="Resources Managed"
            value={metrics?.totalResources?.toString() || '0'}
            trend="+12"
            trendUp={true}
          />
          <MetricCard
            title="Security Issues"
            value={metrics?.securityIssues?.toString() || '0'}
            trend="-5"
            trendUp={false}
            danger={metrics?.securityIssues > 0}
          />
          <MetricCard
            title="Pending Actions"
            value={metrics?.pendingActions?.toString() || '0'}
          />
        </div>

        {/* Agent Status Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {agentCards.map((agent, idx) => (
            <motion.div
              key={agent.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-lg ${agent.color} bg-opacity-10`}>
                  <agent.icon className={`h-6 w-6 ${agent.color.replace('bg-', 'text-')}`} />
                </div>
                <span className="flex h-2 w-2 rounded-full bg-green-500" />
              </div>
              <h3 className="font-semibold text-gray-900">{agent.name}</h3>
              <p className="text-sm text-gray-500 mt-1">{agent.description}</p>
              <div className="mt-4 pt-4 border-t border-gray-100">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Tasks Today</span>
                  <span className="font-medium">{agents?.[idx]?.tasksCompleted || 0}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </main>
    </div>
  )
}

function MetricCard({ 
  title, 
  value, 
  trend, 
  trendUp, 
  danger 
}: { 
  title: string
  value: string
  trend?: string
  trendUp?: boolean
  danger?: boolean 
}) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <p className="text-sm font-medium text-gray-600">{title}</p>
      <div className="mt-2 flex items-baseline gap-2">
        <p className="text-3xl font-bold text-gray-900">{value}</p>
        {trend && (
          <span className={`text-sm font-medium ${
            danger ? 'text-red-600' : 
            trendUp ? 'text-green-600' : 'text-red-600'
          }`}>
            {trend}
          </span>
        )}
      </div>
    </div>
  )
}