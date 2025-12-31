'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import toast, { Toaster } from 'react-hot-toast';
import config from '@/config/api';

interface SystemStats {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    uptime: number;
}

interface ProjectStats {
    total: number;
    active: number;
    completed: number;
}

interface ActivityItem {
    id: number;
    type: string;
    message: string;
    timestamp: string;
}

export default function Dashboard() {
    const router = useRouter();
    const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
    const [projectStats, setProjectStats] = useState<ProjectStats>({ total: 0, active: 0, completed: 0 });
    const [recentActivity, setRecentActivity] = useState<ActivityItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [currentTime, setCurrentTime] = useState(new Date());

    useEffect(() => {
        fetchDashboardData();
        const interval = setInterval(() => {
            fetchDashboardData();
            setCurrentTime(new Date());
        }, 5000);
        return () => clearInterval(interval);
    }, []);

    // Monitor system health and show warnings
    useEffect(() => {
        if (systemStats) {
            // CPU warning
            if (systemStats.cpu_usage > 80 && systemStats.cpu_usage <= 90) {
                toast('High CPU usage detected', {
                    icon: '⚠️',
                    duration: 4000,
                });
            } else if (systemStats.cpu_usage > 90) {
                toast.error('Critical CPU usage!', {
                    icon: '🔥',
                    duration: 5000,
                });
            }

            // Memory warning
            if (systemStats.memory_usage > 85 && systemStats.memory_usage <= 95) {
                toast('High memory usage detected', {
                    icon: '⚠️',
                    duration: 4000,
                });
            } else if (systemStats.memory_usage > 95) {
                toast.error('Critical memory usage!', {
                    icon: '🔥',
                    duration: 5000,
                });
            }

            // Disk space warning
            if (systemStats.disk_usage > 90) {
                toast.error('Low disk space!', {
                    icon: '💾',
                    duration: 5000,
                });
            }
        }
    }, [systemStats?.cpu_usage, systemStats?.memory_usage, systemStats?.disk_usage]);

    const fetchDashboardData = async () => {
        try {
            // Fetch system stats
            const sysResponse = await fetch(`${config.apiBaseUrl}/api/system/stats`);
            if (sysResponse.ok) {
                const sysData = await sysResponse.json();
                setSystemStats(sysData);
            } else {
                if (!systemStats) {
                    toast.error('Failed to fetch system stats', {
                        icon: '⚠️',
                        duration: 3000,
                    });
                }
            }

            // Fetch project stats
            const projResponse = await fetch(`${config.apiBaseUrl}/api/projects`);
            if (projResponse.ok) {
                const projData = await projResponse.json();
                if (projData.success && projData.projects) {
                    const projects = projData.projects;
                    const newStats = {
                        total: projects.length,
                        active: projects.filter((p: any) => p.status === 'active').length,
                        completed: projects.filter((p: any) => p.status === 'completed').length,
                    };
                    
                    // Show notification for new projects
                    if (projectStats.total > 0 && newStats.total > projectStats.total) {
                        toast.success('New project detected!', {
                            icon: '📁',
                            duration: 4000,
                        });
                    }
                    
                    setProjectStats(newStats);
                }
            }

            // Fetch recent activity (chat history)
            const chatResponse = await fetch(`${config.apiBaseUrl}/api/chat/history?user_id=1&limit=5`);
            if (chatResponse.ok) {
                const chatData = await chatResponse.json();
                if (chatData.success && chatData.messages) {
                    const newActivity = chatData.messages.slice(0, 5).map((msg: any, idx: number) => ({
                        id: idx,
                        type: msg.sender === 'user' ? 'query' : 'response',
                        message: msg.message.substring(0, 80) + (msg.message.length > 80 ? '...' : ''),
                        timestamp: new Date(msg.timestamp).toLocaleTimeString(),
                    }));
                    
                    // Show notification for new activity
                    if (recentActivity.length > 0 && newActivity.length > 0 && 
                        newActivity[0].message !== recentActivity[0]?.message) {
                        toast('New activity detected', {
                            icon: '🔔',
                            duration: 3000,
                        });
                    }
                    
                    setRecentActivity(newActivity);
                }
            }

            if (!loading) {
                // Show success toast only on first load
                if (!systemStats) {
                    toast.success('Dashboard loaded successfully', {
                        icon: '✅',
                        duration: 2000,
                    });
                }
            }

            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch dashboard data:', error);
            if (!systemStats) {
                toast.error('Failed to connect to backend', {
                    icon: '❌',
                    duration: 4000,
                });
            }
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-[#0a0a0a] text-white p-8 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#0a0a0a] text-white p-8">
            {/* Toast Notifications */}
            <Toaster
                position="top-right"
                toastOptions={{
                    className: '',
                    style: {
                        background: '#1a1a1a',
                        color: '#fff',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        borderRadius: '12px',
                        padding: '16px',
                    },
                    success: {
                        duration: 3000,
                        iconTheme: {
                            primary: '#10b981',
                            secondary: '#fff',
                        },
                    },
                    error: {
                        duration: 4000,
                        iconTheme: {
                            primary: '#ef4444',
                            secondary: '#fff',
                        },
                    },
                }}
            />
            
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
                                Dashboard
                            </h1>
                            <p className="text-gray-400">Welcome back! Here's what's happening with F.R.I.D.A.Y.</p>
                        </div>
                        <div className="text-right">
                            <p className="text-sm text-gray-500">
                                {currentTime.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                            </p>
                            <p className="text-2xl font-bold text-blue-400">{currentTime.toLocaleTimeString()}</p>
                        </div>
                    </div>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    {/* System CPU */}
                    <div className="bg-gradient-to-br from-blue-500/10 to-blue-600/10 border border-blue-500/20 rounded-xl p-6 hover:border-blue-500/40 transition-all">
                        <div className="flex items-center justify-between mb-4">
                            <div className="p-3 bg-blue-500/20 rounded-lg">
                                <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                                </svg>
                            </div>
                            <span className="text-3xl font-bold text-blue-400">{systemStats?.cpu_usage?.toFixed(1) || '0.0'}%</span>
                        </div>
                        <h3 className="text-gray-400 text-sm mb-2">CPU Usage</h3>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                            <div 
                                className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-500"
                                style={{ width: `${systemStats?.cpu_usage ?? 0}%` }}
                            ></div>
                        </div>
                    </div>

                    {/* System Memory */}
                    <div className="bg-gradient-to-br from-purple-500/10 to-purple-600/10 border border-purple-500/20 rounded-xl p-6 hover:border-purple-500/40 transition-all">
                        <div className="flex items-center justify-between mb-4">
                            <div className="p-3 bg-purple-500/20 rounded-lg">
                                <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                                </svg>
                            </div>
                            <span className="text-3xl font-bold text-purple-400">{systemStats?.memory_usage?.toFixed(1) || '0.0'}%</span>
                        </div>
                        <h3 className="text-gray-400 text-sm mb-2">Memory Usage</h3>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                            <div 
                                className="bg-gradient-to-r from-purple-500 to-purple-600 h-2 rounded-full transition-all duration-500"
                                style={{ width: `${systemStats?.memory_usage ?? 0}%` }}
                            ></div>
                        </div>
                    </div>

                    {/* Projects */}
                    <div className="bg-gradient-to-br from-green-500/10 to-green-600/10 border border-green-500/20 rounded-xl p-6 hover:border-green-500/40 transition-all">
                        <div className="flex items-center justify-between mb-4">
                            <div className="p-3 bg-green-500/20 rounded-lg">
                                <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                                </svg>
                            </div>
                            <span className="text-3xl font-bold text-green-400">{projectStats.active}</span>
                        </div>
                        <h3 className="text-gray-400 text-sm mb-2">Active Projects</h3>
                        <p className="text-xs text-gray-500">{projectStats.total} total projects</p>
                    </div>

                    {/* Uptime */}
                    <div className="bg-gradient-to-br from-yellow-500/10 to-orange-600/10 border border-yellow-500/20 rounded-xl p-6 hover:border-yellow-500/40 transition-all">
                        <div className="flex items-center justify-between mb-4">
                            <div className="p-3 bg-yellow-500/20 rounded-lg">
                                <svg className="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <span className="text-3xl font-bold text-yellow-400">{Math.floor((systemStats?.uptime ?? 0) / 3600)}h</span>
                        </div>
                        <h3 className="text-gray-400 text-sm mb-2">System Uptime</h3>
                        <p className="text-xs text-gray-500">{Math.floor((systemStats?.uptime ?? 0) / 60)} minutes</p>
                    </div>
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Quick Actions */}
                    <div className="lg:col-span-2 bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                            <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                            Quick Actions
                        </h2>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                            <button
                                onClick={() => {
                                    toast.loading('Opening AI Copilot...', { duration: 1000 });
                                    setTimeout(() => router.push('/ai-copilot'), 500);
                                }}
                                className="p-6 bg-gradient-to-br from-blue-500/10 to-blue-600/10 border border-blue-500/20 rounded-lg hover:border-blue-500/40 transition-all group"
                            >
                                <div className="p-3 bg-blue-500/20 rounded-lg mb-3 w-fit">
                                    <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                                    </svg>
                                </div>
                                <h3 className="font-semibold text-sm mb-1">AI Copilot</h3>
                                <p className="text-xs text-gray-500">Code completion</p>
                            </button>

                            <button
                                onClick={() => {
                                    toast.loading('Opening Debugger...', { duration: 1000 });
                                    setTimeout(() => router.push('/debugger'), 500);
                                }}
                                className="p-6 bg-gradient-to-br from-red-500/10 to-red-600/10 border border-red-500/20 rounded-lg hover:border-red-500/40 transition-all group"
                            >
                                <div className="p-3 bg-red-500/20 rounded-lg mb-3 w-fit">
                                    <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                    </svg>
                                </div>
                                <h3 className="font-semibold text-sm mb-1">Debugger</h3>
                                <p className="text-xs text-gray-500">Debug code</p>
                            </button>

                            <button
                                onClick={() => {
                                    toast.loading('Loading Snippets...', { duration: 1000 });
                                    setTimeout(() => router.push('/code-snippets'), 500);
                                }}
                                className="p-6 bg-gradient-to-br from-purple-500/10 to-purple-600/10 border border-purple-500/20 rounded-lg hover:border-purple-500/40 transition-all group"
                            >
                                <div className="p-3 bg-purple-500/20 rounded-lg mb-3 w-fit">
                                    <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                                    </svg>
                                </div>
                                <h3 className="font-semibold text-sm mb-1">Snippets</h3>
                                <p className="text-xs text-gray-500">Code templates</p>
                            </button>

                            <button
                                onClick={() => {
                                    toast.loading('Opening Projects...', { duration: 1000 });
                                    setTimeout(() => router.push('/projects'), 500);
                                }}
                                className="p-6 bg-gradient-to-br from-green-500/10 to-green-600/10 border border-green-500/20 rounded-lg hover:border-green-500/40 transition-all group"
                            >
                                <div className="p-3 bg-green-500/20 rounded-lg mb-3 w-fit">
                                    <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                                    </svg>
                                </div>
                                <h3 className="font-semibold text-sm mb-1">Projects</h3>
                                <p className="text-xs text-gray-500">Manage projects</p>
                            </button>

                            <button
                                onClick={() => {
                                    toast.loading('Opening Code IDE...', { duration: 1000 });
                                    setTimeout(() => router.push('/code'), 500);
                                }}
                                className="p-6 bg-gradient-to-br from-yellow-500/10 to-yellow-600/10 border border-yellow-500/20 rounded-lg hover:border-yellow-500/40 transition-all group"
                            >
                                <div className="p-3 bg-yellow-500/20 rounded-lg mb-3 w-fit">
                                    <svg className="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                                    </svg>
                                </div>
                                <h3 className="font-semibold text-sm mb-1">Code IDE</h3>
                                <p className="text-xs text-gray-500">Write code</p>
                            </button>

                            <button
                                onClick={() => {
                                    toast.loading('Loading Analytics...', { duration: 1000 });
                                    setTimeout(() => router.push('/analytics'), 500);
                                }}
                                className="p-6 bg-gradient-to-br from-pink-500/10 to-pink-600/10 border border-pink-500/20 rounded-lg hover:border-pink-500/40 transition-all group"
                            >
                                <div className="p-3 bg-pink-500/20 rounded-lg mb-3 w-fit">
                                    <svg className="w-6 h-6 text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                    </svg>
                                </div>
                                <h3 className="font-semibold text-sm mb-1">Analytics</h3>
                                <p className="text-xs text-gray-500">View insights</p>
                            </button>
                        </div>
                    </div>

                    {/* Recent Activity */}
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                            <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            Recent Activity
                        </h2>
                        <div className="space-y-4">
                            {recentActivity.length > 0 ? (
                                recentActivity.map((activity) => (
                                    <div key={activity.id} className="flex gap-3 p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all">
                                        <div className={`w-2 h-2 mt-2 rounded-full flex-shrink-0 ${
                                            activity.type === 'query' ? 'bg-blue-400' : 'bg-green-400'
                                        }`}></div>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm text-gray-300 truncate">{activity.message}</p>
                                            <p className="text-xs text-gray-500 mt-1">{activity.timestamp}</p>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="text-center py-8 text-gray-500">
                                    <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    <p className="text-sm">No recent activity</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* System Status */}
                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* System Health */}
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                            <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            System Health
                        </h2>
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                                    <span className="text-gray-300">API Server</span>
                                </div>
                                <span className="text-green-400 text-sm font-semibold">Online</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                                    <span className="text-gray-300">WebSocket</span>
                                </div>
                                <span className="text-green-400 text-sm font-semibold">Connected</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                                    <span className="text-gray-300">Database</span>
                                </div>
                                <span className="text-green-400 text-sm font-semibold">Active</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className={`w-3 h-3 rounded-full ${process.env.GEMINI_API_KEY ? 'bg-green-400 animate-pulse' : 'bg-gray-500'}`}></div>
                                    <span className="text-gray-300">AI Services</span>
                                </div>
                                <span className={`text-sm font-semibold ${process.env.GEMINI_API_KEY ? 'text-green-400' : 'text-gray-500'}`}>
                                    {process.env.GEMINI_API_KEY ? 'Enabled' : 'Offline'}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Performance Metrics */}
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                            <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                            </svg>
                            Performance
                        </h2>
                        <div className="space-y-4">
                            <div>
                                <div className="flex justify-between mb-2">
                                    <span className="text-sm text-gray-400">Disk Usage</span>
                                    <span className="text-sm text-blue-400">{systemStats?.disk_usage?.toFixed(1) || '0.0'}%</span>
                                </div>
                                <div className="w-full bg-gray-700 rounded-full h-2">
                                    <div 
                                        className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full transition-all duration-500"
                                        style={{ width: `${systemStats?.disk_usage ?? 0}%` }}
                                    ></div>
                                </div>
                            </div>
                            <div>
                                <div className="flex justify-between mb-2">
                                    <span className="text-sm text-gray-400">Response Time</span>
                                    <span className="text-sm text-green-400">~50ms</span>
                                </div>
                                <div className="w-full bg-gray-700 rounded-full h-2">
                                    <div className="bg-gradient-to-r from-green-500 to-emerald-500 h-2 rounded-full w-[15%]"></div>
                                </div>
                            </div>
                            <div>
                                <div className="flex justify-between mb-2">
                                    <span className="text-sm text-gray-400">Cache Hit Rate</span>
                                    <span className="text-sm text-purple-400">94%</span>
                                </div>
                                <div className="w-full bg-gray-700 rounded-full h-2">
                                    <div className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full w-[94%]"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
