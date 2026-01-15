'use client';

import { useState, useEffect } from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface ApiCallStats {
  total_calls: number;
  status_breakdown: {
    success?: number;
    client_error?: number;
    server_error?: number;
  };
  avg_response_time: number;
  top_endpoints: Array<{ endpoint: string; count: number }>;
  calls_over_time: Array<{ time: string; count: number }>;
  time_period_hours: number;
}

interface UserActivityStats {
  total_activities: number;
  active_users: number;
  top_actions: Array<{ action: string; count: number }>;
  activity_over_time: Array<{ time: string; count: number }>;
  time_period_hours: number;
}

interface ErrorStats {
  total_errors: number;
  errors_by_type: Array<{ error: string; count: number }>;
  recent_errors: Array<any>;
  time_period_hours: number;
}

interface QualityMetrics {
  success_rate: number;
  avg_response_time: number;
  error_rate: number;
  uptime: number;
}

interface CompleteAnalytics {
  timestamp: string;
  api_calls: ApiCallStats;
  user_activity: UserActivityStats;
  errors: ErrorStats;
  performance: {
    avg_metrics: Array<any>;
    time_period_hours: number;
  };
}

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<CompleteAnalytics | null>(null);
  const [quality, setQuality] = useState<QualityMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(24);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchAnalytics = async () => {
    try {
      const [analyticsRes, qualityRes] = await Promise.all([
        fetch(`http://localhost:8000/api/analytics/complete?hours=${timeRange}`),
        fetch(`http://localhost:8000/api/analytics/quality`)
      ]);

      const analyticsData = await analyticsRes.json();
      const qualityData = await qualityRes.json();

      setAnalytics(analyticsData);
      setQuality(qualityData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();

    if (autoRefresh) {
      const interval = setInterval(fetchAnalytics, 30000); // Refresh every 30 seconds
      return () => clearInterval(interval);
    }
  }, [timeRange, autoRefresh]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <div className="text-white text-2xl">Loading Analytics...</div>
      </div>
    );
  }

  if (!analytics || !quality) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <div className="text-white text-2xl">Failed to load analytics</div>
      </div>
    );
  }

  const successCalls = analytics.api_calls.status_breakdown.success || 0;
  const clientErrors = analytics.api_calls.status_breakdown.client_error || 0;
  const serverErrors = analytics.api_calls.status_breakdown.server_error || 0;
  const totalErrors = clientErrors + serverErrors;

  // Chart configurations
  const hourlyCallsData = {
    labels: analytics.api_calls.calls_over_time.map(h => {
      const date = new Date(h.time);
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }),
    datasets: [
      {
        label: 'API Calls',
        data: analytics.api_calls.calls_over_time.map(h => h.count),
        borderColor: 'rgb(147, 51, 234)',
        backgroundColor: 'rgba(147, 51, 234, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const statusDistributionData = {
    labels: ['Success', 'Client Errors', 'Server Errors'],
    datasets: [
      {
        data: [successCalls, clientErrors, serverErrors],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(234, 179, 8, 0.8)',
          'rgba(239, 68, 68, 0.8)',
        ],
      },
    ],
  };

  const topEndpointsData = {
    labels: analytics.api_calls.top_endpoints.map(e => e.endpoint.split('/').pop() || e.endpoint),
    datasets: [
      {
        label: 'Calls',
        data: analytics.api_calls.top_endpoints.map(e => e.count),
        backgroundColor: 'rgba(147, 51, 234, 0.8)',
      },
    ],
  };

  const userActivityData = {
    labels: analytics.user_activity.activity_over_time.map(h => {
      const date = new Date(h.time);
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }),
    datasets: [
      {
        label: 'User Actions',
        data: analytics.user_activity.activity_over_time.map(h => h.count),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-4">Analytics Dashboard</h1>
          <div className="flex gap-4 items-center">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(Number(e.target.value))}
              className="bg-gray-800 text-white px-4 py-2 rounded-lg border border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value={1}>Last 1 Hour</option>
              <option value={6}>Last 6 Hours</option>
              <option value={24}>Last 24 Hours</option>
              <option value={168}>Last 7 Days</option>
            </select>

            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-4 py-2 rounded-lg font-semibold transition ${
                autoRefresh
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-700 text-gray-300'
              }`}
            >
              Auto Refresh: {autoRefresh ? 'ON' : 'OFF'}
            </button>

            <button
              onClick={fetchAnalytics}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-purple-700 transition"
            >
              Refresh Now
            </button>
          </div>
        </div>

        {/* Quality Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl p-6 text-white shadow-lg">
            <h3 className="text-sm font-semibold mb-2 opacity-90">Success Rate</h3>
            <p className="text-4xl font-bold">{quality.success_rate.toFixed(1)}%</p>
            <p className="text-sm mt-2 opacity-75">
              {successCalls} / {analytics.api_calls.total_calls} calls
            </p>
          </div>

          <div className="bg-gradient-to-br from-green-600 to-green-800 rounded-xl p-6 text-white shadow-lg">
            <h3 className="text-sm font-semibold mb-2 opacity-90">Avg Response Time</h3>
            <p className="text-4xl font-bold">{quality.avg_response_time.toFixed(0)}ms</p>
            <p className="text-sm mt-2 opacity-75">
              {analytics.api_calls.total_calls} requests tracked
            </p>
          </div>

          <div className="bg-gradient-to-br from-yellow-600 to-yellow-800 rounded-xl p-6 text-white shadow-lg">
            <h3 className="text-sm font-semibold mb-2 opacity-90">Error Rate</h3>
            <p className="text-4xl font-bold">{quality.error_rate.toFixed(1)}%</p>
            <p className="text-sm mt-2 opacity-75">
              {totalErrors} total errors
            </p>
          </div>

          <div className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-xl p-6 text-white shadow-lg">
            <h3 className="text-sm font-semibold mb-2 opacity-90">System Uptime</h3>
            <p className="text-4xl font-bold">{quality.uptime.toFixed(2)}%</p>
            <p className="text-sm mt-2 opacity-75">Last 7 days</p>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* API Calls Over Time */}
          <div className="bg-gray-800 rounded-xl p-6 border border-purple-500 shadow-lg">
            <h3 className="text-xl font-bold text-white mb-4">API Calls Over Time</h3>
            <Line
              data={hourlyCallsData}
              options={{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                  legend: { labels: { color: 'white' } },
                },
                scales: {
                  x: { ticks: { color: 'white' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                  y: { ticks: { color: 'white' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                },
              }}
            />
          </div>

          {/* Status Distribution */}
          <div className="bg-gray-800 rounded-xl p-6 border border-purple-500 shadow-lg">
            <h3 className="text-xl font-bold text-white mb-4">Status Distribution</h3>
            <div className="flex justify-center">
              <div style={{ maxWidth: '300px', maxHeight: '300px' }}>
                <Doughnut
                  data={statusDistributionData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                      legend: { labels: { color: 'white' } },
                    },
                  }}
                />
              </div>
            </div>
          </div>

          {/* Top Endpoints */}
          <div className="bg-gray-800 rounded-xl p-6 border border-purple-500 shadow-lg">
            <h3 className="text-xl font-bold text-white mb-4">Top Endpoints</h3>
            <Bar
              data={topEndpointsData}
              options={{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                  legend: { display: false },
                },
                scales: {
                  x: { ticks: { color: 'white' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                  y: { ticks: { color: 'white' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                },
              }}
            />
          </div>

          {/* User Activity */}
          <div className="bg-gray-800 rounded-xl p-6 border border-purple-500 shadow-lg">
            <h3 className="text-xl font-bold text-white mb-4">User Activity</h3>
            <Line
              data={userActivityData}
              options={{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                  legend: { labels: { color: 'white' } },
                },
                scales: {
                  x: { ticks: { color: 'white' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                  y: { ticks: { color: 'white' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                },
              }}
            />
          </div>
        </div>

        {/* Error Tracking */}
        {analytics.errors.total_errors > 0 && (
          <div className="bg-gray-800 rounded-xl p-6 border border-red-500 shadow-lg mb-8">
            <h3 className="text-xl font-bold text-white mb-4">Error Tracking</h3>

            {analytics.errors.errors_by_type.length > 0 && (
              <div>
                <h4 className="text-lg font-semibold text-white mb-3">Error Types</h4>
                <div className="space-y-2">
                  {analytics.errors.errors_by_type.slice(0, 5).map((error, index) => (
                    <div key={index} className="bg-gray-700 rounded-lg p-3">
                      <div className="flex justify-between items-center">
                        <span className="text-red-400 font-mono text-sm">{error.error}</span>
                        <span className="text-white font-semibold">{error.count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
        {/* Additional Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Actions */}
          <div className="bg-gray-800 rounded-xl p-6 border border-purple-500 shadow-lg">
            <h3 className="text-xl font-bold text-white mb-4">Top User Actions</h3>
            <div className="space-y-2">
              {analytics.user_activity.top_actions.slice(0, 10).map((action, index) => (
                <div key={index} className="bg-gray-700 rounded-lg p-3 flex justify-between items-center">
                  <span className="text-white">{action.action}</span>
                  <span className="text-purple-400 font-semibold">{action.count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Status Code Breakdown */}
          <div className="bg-gray-800 rounded-xl p-6 border border-purple-500 shadow-lg">
            <h3 className="text-xl font-bold text-white mb-4">Status Breakdown</h3>
            <div className="space-y-2">
              <div className="bg-gray-700 rounded-lg p-3 flex justify-between items-center">
                <span className="text-green-400 font-semibold">Success (2xx)</span>
                <span className="text-white font-semibold">{successCalls}</span>
              </div>
              <div className="bg-gray-700 rounded-lg p-3 flex justify-between items-center">
                <span className="text-yellow-400 font-semibold">Client Error (4xx)</span>
                <span className="text-white font-semibold">{clientErrors}</span>
              </div>
              <div className="bg-gray-700 rounded-lg p-3 flex justify-between items-center">
                <span className="text-red-400 font-semibold">Server Error (5xx)</span>
                <span className="text-white font-semibold">{serverErrors}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
