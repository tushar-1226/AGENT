'use client';

import { useState, useEffect } from 'react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import config from '@/config/api';

interface SystemStats {
    cpu: {
        percent: number;
        per_core: number[];
        cores: number;
        frequency: {
            current: number;
            min: number;
            max: number;
        };
    };
    memory: {
        percent: number;
        total_gb: number;
        used_gb: number;
        available_gb: number;
    };
    disk: {
        percent: number;
        total_gb: number;
        used_gb: number;
        free_gb: number;
    };
    network: {
        bytes_sent: number;
        bytes_recv: number;
    };
}

interface SystemStatsModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function SystemStatsModal({ isOpen, onClose }: SystemStatsModalProps) {
    const [stats, setStats] = useState<SystemStats | null>(null);
    const [history, setHistory] = useState<any[]>([]);

    useEffect(() => {
        if (!isOpen) return;

        const fetchStats = async () => {
            try {
                const response = await fetch(`${config.apiBaseUrl}/api/system/stats`);
                const data = await response.json();
                setStats(data);

                // Add to history for charts
                setHistory(prev => {
                    const newHistory = [...prev, {
                        time: new Date().toLocaleTimeString(),
                        cpu: data.cpu.percent,
                        memory: data.memory.percent,
                        disk: data.disk.percent
                    }];
                    // Keep last 20 data points
                    return newHistory.slice(-20);
                });
            } catch (error) {
                console.error('Failed to fetch system stats:', error);
            }
        };

        // Initial fetch
        fetchStats();

        // Poll every 2 seconds
        const interval = setInterval(fetchStats, 2000);

        return () => clearInterval(interval);
    }, [isOpen]);

    if (!isOpen) return null;

    return (
        <>
            {/* Overlay */}
            <div
                className="fixed inset-0 bg-black/60 z-50 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
                <div
                    className="glass-card w-full max-w-6xl max-h-[90vh] overflow-y-auto pointer-events-auto scrollbar-dark"
                    onClick={(e) => e.stopPropagation()}
                >
                    {/* Header */}
                    <div className="flex items-center justify-between p-6 border-b border-white/[0.08]">
                        <div>
                            <h2 className="text-2xl font-bold text-white">System Monitor</h2>
                            <p className="text-sm text-gray-400 mt-1">Real-time performance metrics</p>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-2 rounded-lg hover:bg-white/[0.04] transition-colors"
                        >
                            <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    {/* Content */}
                    {stats && (
                        <div className="p-6 space-y-6">
                            {/* Quick Stats Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                {/* CPU Card */}
                                <div className="glass-card p-5 border-blue-500/20">
                                    <div className="flex items-center justify-between mb-3">
                                        <h3 className="text-sm font-semibold text-gray-300">CPU Usage</h3>
                                        <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                                            <svg className="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                                            </svg>
                                        </div>
                                    </div>
                                    <div className="text-3xl font-bold text-white mb-1">{stats.cpu.percent.toFixed(1)}%</div>
                                    <div className="text-xs text-gray-500">{stats.cpu.cores} cores @ {stats.cpu.frequency.current.toFixed(0)} MHz</div>

                                    {/* Progress bar */}
                                    <div className="mt-4 h-2 bg-white/[0.05] rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all duration-500"
                                            style={{ width: `${stats.cpu.percent}%` }}
                                        />
                                    </div>
                                </div>

                                {/* Memory Card */}
                                <div className="glass-card p-5 border-purple-500/20">
                                    <div className="flex items-center justify-between mb-3">
                                        <h3 className="text-sm font-semibold text-gray-300">Memory Usage</h3>
                                        <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                                            <svg className="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                                            </svg>
                                        </div>
                                    </div>
                                    <div className="text-3xl font-bold text-white mb-1">{stats.memory.percent.toFixed(1)}%</div>
                                    <div className="text-xs text-gray-500">{stats.memory.used_gb} / {stats.memory.total_gb} GB</div>

                                    <div className="mt-4 h-2 bg-white/[0.05] rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
                                            style={{ width: `${stats.memory.percent}%` }}
                                        />
                                    </div>
                                </div>

                                {/* Disk Card */}
                                <div className="glass-card p-5 border-green-500/20">
                                    <div className="flex items-center justify-between mb-3">
                                        <h3 className="text-sm font-semibold text-gray-300">Disk Usage</h3>
                                        <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                                            <svg className="w-5 h-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                                            </svg>
                                        </div>
                                    </div>
                                    <div className="text-3xl font-bold text-white mb-1">{stats.disk.percent.toFixed(1)}%</div>
                                    <div className="text-xs text-gray-500">{stats.disk.used_gb} / {stats.disk.total_gb} GB</div>

                                    <div className="mt-4 h-2 bg-white/[0.05] rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-green-500 to-emerald-500 transition-all duration-500"
                                            style={{ width: `${stats.disk.percent}%` }}
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Charts */}
                            {history.length > 1 && (
                                <div className="glass-card p-6">
                                    <h3 className="text-lg font-semibold text-white mb-4">Performance History</h3>
                                    <div className="h-64">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <AreaChart data={history}>
                                                <defs>
                                                    <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                                                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                                    </linearGradient>
                                                    <linearGradient id="colorMemory" x1="0" y1="0" x2="0" y2="1">
                                                        <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3} />
                                                        <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
                                                    </linearGradient>
                                                    <linearGradient id="colorDisk" x1="0" y1="0" x2="0" y2="1">
                                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                                    </linearGradient>
                                                </defs>
                                                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                                <XAxis dataKey="time" stroke="#666" />
                                                <YAxis stroke="#666" domain={[0, 100]} />
                                                <Tooltip
                                                    contentStyle={{ backgroundColor: '#111', border: '1px solid #333', borderRadius: '8px' }}
                                                    labelStyle={{ color: '#999' }}
                                                />
                                                <Area type="monotone" dataKey="cpu" stroke="#3b82f6" fillOpacity={1} fill="url(#colorCpu)" name="CPU %" />
                                                <Area type="monotone" dataKey="memory" stroke="#a855f7" fillOpacity={1} fill="url(#colorMemory)" name="Memory %" />
                                                <Area type="monotone" dataKey="disk" stroke="#10b981" fillOpacity={1} fill="url(#colorDisk)" name="Disk %" />
                                            </AreaChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>
                            )}

                            {/* Detailed Stats */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {/* CPU Cores */}
                                <div className="glass-card p-5">
                                    <h3 className="text-sm font-semibold text-white mb-4">CPU Cores</h3>
                                    <div className="space-y-3">
                                        {stats.cpu.per_core.map((usage, index) => (
                                            <div key={index}>
                                                <div className="flex justify-between text-xs mb-1">
                                                    <span className="text-gray-400">Core {index + 1}</span>
                                                    <span className="text-white">{usage.toFixed(1)}%</span>
                                                </div>
                                                <div className="h-1.5 bg-white/[0.05] rounded-full overflow-hidden">
                                                    <div
                                                        className="h-full bg-gradient-to-r from-blue-500 to-cyan-500"
                                                        style={{ width: `${usage}%` }}
                                                    />
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Network */}
                                <div className="glass-card p-5">
                                    <h3 className="text-sm font-semibold text-white mb-4">Network Activity</h3>
                                    <div className="space-y-4">
                                        <div>
                                            <div className="flex items-center gap-2 mb-1">
                                                <svg className="w-4 h-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 11l5-5m0 0l5 5m-5-5v12" />
                                                </svg>
                                                <span className="text-xs text-gray-400">Sent</span>
                                            </div>
                                            <div className="text-lg font-semibold text-white">
                                                {(stats.network.bytes_sent / (1024 ** 3)).toFixed(2)} GB
                                            </div>
                                        </div>
                                        <div>
                                            <div className="flex items-center gap-2 mb-1">
                                                <svg className="w-4 h-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 13l-5 5m0 0l-5-5m5 5V6" />
                                                </svg>
                                                <span className="text-xs text-gray-400">Received</span>
                                            </div>
                                            <div className="text-lg font-semibold text-white">
                                                {(stats.network.bytes_recv / (1024 ** 3)).toFixed(2)} GB
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}
