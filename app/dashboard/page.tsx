'use client';

import { useState } from 'react';
import Link from 'next/link';
import AuthProtection from '@/components/AuthProtection';
import { 
  ArrowLeft, 
  BarChart3, 
  Activity,
  FileText,
  MessageSquare,
  TrendingUp
} from 'lucide-react';

function DashboardPageContent() {
  const [timeRange, setTimeRange] = useState('7d');

  // Mock usage data
  const usageStats = {
    totalQueries: 1247,
    totalTokens: 89543,
    documentsAnalyzed: 23,
    avgResponseTime: '1.2s'
  };

  // Mock chart data for token consumption
  const chartData = [
    { day: 'Mon', tokens: 8500 },
    { day: 'Tue', tokens: 12300 },
    { day: 'Wed', tokens: 9800 },
    { day: 'Thu', tokens: 15200 },
    { day: 'Fri', tokens: 11400 },
    { day: 'Sat', tokens: 6700 },
    { day: 'Sun', tokens: 8900 }
  ];

  const maxTokens = Math.max(...chartData.map(d => d.tokens));

  // Mock usage logs
  const usageLogs = [
    {
      id: 1,
      timestamp: '2024-07-11 14:23:45',
      action: 'Document Analysis',
      document: 'Smith v. Johnson Appeal.pdf',
      tokens: 1250,
      responseTime: '2.1s',
      status: 'completed'
    },
    {
      id: 2,
      timestamp: '2024-07-11 14:18:32',
      action: 'AI Query',
      document: 'Contract Review - Tech Merger.pdf',
      tokens: 890,
      responseTime: '1.8s',
      status: 'completed'
    },
    {
      id: 3,
      timestamp: '2024-07-11 14:15:21',
      action: 'Brief Generation',
      document: 'Employment Law Research.pdf',
      tokens: 2100,
      responseTime: '3.2s',
      status: 'completed'
    },
    {
      id: 4,
      timestamp: '2024-07-11 14:08:17',
      action: 'Document Upload',
      document: 'Motion to Dismiss Brief.pdf',
      tokens: 0,
      responseTime: '0.5s',
      status: 'completed'
    },
    {
      id: 5,
      timestamp: '2024-07-11 13:45:33',
      action: 'AI Query',
      document: 'Real Estate Closing Docs.pdf',
      tokens: 1350,
      responseTime: '1.9s',
      status: 'completed'
    },
    {
      id: 6,
      timestamp: '2024-07-11 13:22:18',
      action: 'Document Analysis',
      document: 'Criminal Defense Strategy.pdf',
      tokens: 1680,
      responseTime: '2.5s',
      status: 'completed'
    }
  ];

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'Document Analysis':
        return <FileText className="w-4 h-4 text-blue-500" />;
      case 'AI Query':
        return <MessageSquare className="w-4 h-4 text-green-500" />;
      case 'Brief Generation':
        return <FileText className="w-4 h-4 text-purple-500" />;
      case 'Document Upload':
        return <Activity className="w-4 h-4 text-gray-500" />;
      default:
        return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link 
                href="/app" 
                className="p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Back to dashboard"
              >
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div className="flex items-center space-x-2">
                <BarChart3 className="w-6 h-6 text-gray-600 dark:text-gray-300" />
                <h1 className="text-xl font-semibold text-gray-900 dark:text-white">Usage Dashboard</h1>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <select 
                value={timeRange} 
                onChange={(e) => setTimeRange(e.target.value)}
                className="bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
              >
                <option value="24h">Last 24 hours</option>
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
              </select>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
            <div className="flex items-center">
              <MessageSquare className="w-8 h-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Queries</p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">{usageStats.totalQueries.toLocaleString()}</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
            <div className="flex items-center">
              <Activity className="w-8 h-8 text-green-500" />
              <div className="ml-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Tokens</p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">{usageStats.totalTokens.toLocaleString()}</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
            <div className="flex items-center">
              <FileText className="w-8 h-8 text-purple-500" />
              <div className="ml-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Documents</p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">{usageStats.documentsAnalyzed}</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
            <div className="flex items-center">
              <TrendingUp className="w-8 h-8 text-orange-500" />
              <div className="ml-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Avg Response</p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">{usageStats.avgResponseTime}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Token Consumption Chart */}
          <div className="lg:col-span-1">
            <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Token Consumption</h2>
              <div className="space-y-4">
                {chartData.map((item) => (
                  <div key={item.day} className="flex items-center space-x-3">
                    <div className="w-8 text-sm text-gray-600 dark:text-gray-400">{item.day}</div>
                    <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        style={{width: `${(item.tokens / maxTokens) * 100}%`}}
                      ></div>
                    </div>
                    <div className="w-12 text-right text-sm text-gray-900 dark:text-white">
                      {(item.tokens / 1000).toFixed(1)}k
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Usage Logs Table */}
          <div className="lg:col-span-2">
            <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Activity</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <th className="text-left py-2 px-1 text-sm font-medium text-gray-600 dark:text-gray-400">Time</th>
                      <th className="text-left py-2 px-1 text-sm font-medium text-gray-600 dark:text-gray-400">Action</th>
                      <th className="text-left py-2 px-1 text-sm font-medium text-gray-600 dark:text-gray-400">Document</th>
                      <th className="text-left py-2 px-1 text-sm font-medium text-gray-600 dark:text-gray-400">Tokens</th>
                      <th className="text-left py-2 px-1 text-sm font-medium text-gray-600 dark:text-gray-400">Response</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                    {usageLogs.map((log) => (
                      <tr key={log.id} className="hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors">
                        <td className="py-3 px-1 text-sm text-gray-600 dark:text-gray-400">
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </td>
                        <td className="py-3 px-1">
                          <div className="flex items-center space-x-2">
                            {getActionIcon(log.action)}
                            <span className="text-sm text-gray-900 dark:text-white">{log.action}</span>
                          </div>
                        </td>
                        <td className="py-3 px-1 text-sm text-gray-900 dark:text-white max-w-48 truncate">
                          {log.document}
                        </td>
                        <td className="py-3 px-1 text-sm text-gray-600 dark:text-gray-400">
                          {log.tokens > 0 ? log.tokens.toLocaleString() : '-'}
                        </td>
                        <td className="py-3 px-1 text-sm text-gray-600 dark:text-gray-400">
                          {log.responseTime}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <AuthProtection>
      <DashboardPageContent />
    </AuthProtection>
  );
}