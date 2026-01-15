'use client';

import { useState, useEffect } from 'react';

interface CPUInfo {
  physical_cores: number;
  total_cores: number;
  usage_percent: number;
  per_core_usage: number[];
  current_frequency: number;
  max_frequency: number;
  load_average: number[];
}

interface MemoryInfo {
  total: number;
  used: number;
  available: number;
  percent: number;
  swap_total: number;
  swap_used: number;
  swap_percent: number;
}

interface DiskInfo {
  device: string;
  mountpoint: string;
  filesystem: string;
  total: number;
  used: number;
  free: number;
  percent: number;
}

interface NetworkInfo {
  bytes_sent: number;
  bytes_received: number;
  packets_sent: number;
  packets_received: number;
  errors_in: number;
  errors_out: number;
}

interface ProcessInfo {
  total_processes: number;
  top_processes: Array<{
    pid: number;
    name: string;
    cpu_percent: number;
    memory_percent: number;
  }>;
}

interface SystemInfo {
  os: string;
  os_version: string;
  os_architecture: string;
  hostname: string;
  python_version: string;
  boot_time: string;
  uptime_formatted: string;
}

interface SystemStats {
  timestamp: string;
  system: SystemInfo;
  cpu: CPUInfo;
  memory: MemoryInfo;
  disks: DiskInfo[];
  network: NetworkInfo;
  processes: ProcessInfo;
  temperature: any;
  battery: any;
}

export default function SystemPage() {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(3000);

  const fetchSystemStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/system/complete');
      const data = await response.json();
      setStats(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch system stats:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSystemStats();
  }, []);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchSystemStats, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval]);

  const getStatusColor = (percent: number) => {
    if (percent < 50) return 'text-green-400';
    if (percent < 75) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getProgressBarColor = (percent: number) => {
    if (percent < 50) return 'bg-green-500';
    if (percent < 75) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] text-white flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-gray-400">Loading system information...</p>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] text-white flex items-center justify-center">
        <p className="text-red-400">Failed to load system information</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">System Monitor</h1>
            <p className="text-gray-400">Real-time system performance and statistics</p>
          </div>
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="w-4 h-4"
              />
              Auto-refresh
            </label>
            <select
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              className="px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm"
              disabled={!autoRefresh}
            >
              <option value={1000}>1s</option>
              <option value={3000}>3s</option>
              <option value={5000}>5s</option>
              <option value={10000}>10s</option>
            </select>
            <button
              onClick={fetchSystemStats}
              className="px-4 py-2 bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors text-sm"
            >
              Refresh Now
            </button>
          </div>
        </div>

        {/* System Info */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">System Information</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-gray-400 text-sm">Operating System</p>
              <p className="font-semibold">{stats.system.os} {stats.system.os_version}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Architecture</p>
              <p className="font-semibold">{stats.system.os_architecture}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Hostname</p>
              <p className="font-semibold">{stats.system.hostname}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Uptime</p>
              <p className="font-semibold">{stats.system.uptime_formatted}</p>
            </div>
          </div>
        </div>

        {/* CPU Info */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold">CPU Usage</h2>
            <span className={`text-3xl font-bold ${getStatusColor(stats.cpu.usage_percent)}`}>
              {stats.cpu.usage_percent}%
            </span>
          </div>

          <div className="mb-4">
            <div className="w-full bg-white/10 rounded-full h-4 overflow-hidden">
              <div
                className={`h-full ${getProgressBarColor(stats.cpu.usage_percent)} transition-all duration-500`}
                style={{ width: `${stats.cpu.usage_percent}%` }}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div>
              <p className="text-gray-400 text-sm">Physical Cores</p>
              <p className="font-semibold">{stats.cpu.physical_cores}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Total Cores</p>
              <p className="font-semibold">{stats.cpu.total_cores}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Current Frequency</p>
              <p className="font-semibold">{stats.cpu.current_frequency} MHz</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Max Frequency</p>
              <p className="font-semibold">{stats.cpu.max_frequency} MHz</p>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-3">Per-Core Usage</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
              {stats.cpu.per_core_usage.map((usage, index) => (
                <div key={index} className="text-center">
                  <div className="mb-1">
                    <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
                      <div
                        className={`h-full ${getProgressBarColor(usage)}`}
                        style={{ width: `${usage}%` }}
                      />
                    </div>
                  </div>
                  <p className="text-xs text-gray-400">Core {index}</p>
                  <p className={`text-sm font-semibold ${getStatusColor(usage)}`}>{usage}%</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Memory Info */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold">Memory Usage</h2>
            <span className={`text-3xl font-bold ${getStatusColor(stats.memory.percent)}`}>
              {stats.memory.percent}%
            </span>
          </div>

          <div className="mb-4">
            <div className="w-full bg-white/10 rounded-full h-4 overflow-hidden">
              <div
                className={`h-full ${getProgressBarColor(stats.memory.percent)} transition-all duration-500`}
                style={{ width: `${stats.memory.percent}%` }}
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 mb-4">
            <div>
              <p className="text-gray-400 text-sm">Total</p>
              <p className="font-semibold">{stats.memory.total} GB</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Used</p>
              <p className="font-semibold">{stats.memory.used} GB</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Available</p>
              <p className="font-semibold">{stats.memory.available} GB</p>
            </div>
          </div>

          {stats.memory.swap_total > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-3">Swap Memory</h3>
              <div className="mb-2">
                <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden">
                  <div
                    className={`h-full ${getProgressBarColor(stats.memory.swap_percent)}`}
                    style={{ width: `${stats.memory.swap_percent}%` }}
                  />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-gray-400 text-sm">Total</p>
                  <p className="font-semibold">{stats.memory.swap_total} GB</p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm">Used</p>
                  <p className="font-semibold">{stats.memory.swap_used} GB</p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm">Usage</p>
                  <p className={`font-semibold ${getStatusColor(stats.memory.swap_percent)}`}>
                    {stats.memory.swap_percent}%
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Disk Info */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">Disk Usage</h2>
          <div className="space-y-4">
            {stats.disks.map((disk, index) => (
              <div key={index} className="border-b border-white/10 pb-4 last:border-0">
                <div className="flex justify-between items-center mb-2">
                  <div>
                    <p className="font-semibold">{disk.mountpoint}</p>
                    <p className="text-sm text-gray-400">{disk.device} ({disk.filesystem})</p>
                  </div>
                  <span className={`text-xl font-bold ${getStatusColor(disk.percent)}`}>
                    {disk.percent}%
                  </span>
                </div>
                <div className="mb-2">
                  <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden">
                    <div
                      className={`h-full ${getProgressBarColor(disk.percent)}`}
                      style={{ width: `${disk.percent}%` }}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-gray-400">Total</p>
                    <p className="font-semibold">{disk.total} GB</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Used</p>
                    <p className="font-semibold">{disk.used} GB</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Free</p>
                    <p className="font-semibold">{disk.free} GB</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Network Info */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">Network Statistics</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-gray-400 text-sm">Data Sent</p>
              <p className="font-semibold">{stats.network.bytes_sent} GB</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Data Received</p>
              <p className="font-semibold">{stats.network.bytes_received} GB</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Packets Sent</p>
              <p className="font-semibold">{stats.network.packets_sent.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Packets Received</p>
              <p className="font-semibold">{stats.network.packets_received.toLocaleString()}</p>
            </div>
          </div>
        </div>

        {/* Process Info */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold">Top Processes</h2>
            <span className="text-gray-400">Total: {stats.processes.total_processes}</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-2 px-3">PID</th>
                  <th className="text-left py-2 px-3">Name</th>
                  <th className="text-right py-2 px-3">CPU %</th>
                  <th className="text-right py-2 px-3">Memory %</th>
                </tr>
              </thead>
              <tbody>
                {stats.processes.top_processes.map((proc, index) => (
                  <tr key={index} className="border-b border-white/5 hover:bg-white/5">
                    <td className="py-2 px-3 font-mono text-sm">{proc.pid}</td>
                    <td className="py-2 px-3">{proc.name}</td>
                    <td className={`py-2 px-3 text-right font-semibold ${getStatusColor(proc.cpu_percent)}`}>
                      {proc.cpu_percent}%
                    </td>
                    <td className={`py-2 px-3 text-right font-semibold ${getStatusColor(proc.memory_percent)}`}>
                      {proc.memory_percent}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-6 text-center text-sm text-gray-500">
          Last updated: {new Date(stats.timestamp).toLocaleString()}
        </div>
      </div>
    </div>
  );
}
