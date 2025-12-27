'use client';

import { useState, useEffect } from 'react';
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface AnalyticsData {
    pomodoroSessions: number;
    tasksCompleted: number;
    focusMinutes: number;
    productivityScore: number;
    dailyData: Array<{
        date: string;
        tasks: number;
        pomodoros: number;
        focusTime: number;
    }>;
    tasksByCategory: Array<{
        name: string;
        value: number;
    }>;
}

export default function AnalyticsDashboard() {
    const [analytics, setAnalytics] = useState<AnalyticsData>({
        pomodoroSessions: 0,
        tasksCompleted: 0,
        focusMinutes: 0,
        productivityScore: 0,
        dailyData: [],
        tasksByCategory: []
    });
    const [timeRange, setTimeRange] = useState<'week' | 'month' | 'year'>('week');

    useEffect(() => {
        loadAnalytics();
    }, [timeRange]);

    const loadAnalytics = () => {
        // Load from localStorage
        const pomodoroData = JSON.parse(localStorage.getItem('friday_pomodoro_history') || '[]');
        const taskData = JSON.parse(localStorage.getItem('friday_task_analytics') || '[]');

        // Calculate stats
        const sessions = pomodoroData.length;
        const focusMinutes = sessions * 25;
        const tasksCompleted = taskData.filter((t: any) => t.status === 'done').length;
        const productivityScore = Math.min(100, Math.round((sessions * 10 + tasksCompleted * 5) / 2));

        // Generate daily data for charts
        const dailyData = generateDailyData(timeRange);

        // Tasks by category
        const categories = taskData.reduce((acc: any, task: any) => {
            const cat = task.category || 'general';
            acc[cat] = (acc[cat] || 0) + 1;
            return acc;
        }, {});

        const tasksByCategory = Object.entries(categories).map(([name, value]) => ({
            name,
            value: value as number
        }));

        setAnalytics({
            pomodoroSessions: sessions,
            tasksCompleted,
            focusMinutes,
            productivityScore,
            dailyData,
            tasksByCategory
        });
    };

    const generateDailyData = (range: string) => {
        const days = range === 'week' ? 7 : range === 'month' ? 30 : 365;
        const data = [];
        const today = new Date();

        for (let i = days - 1; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);

            data.push({
                date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                tasks: Math.floor(Math.random() * 5), // Replace with actual data
                pomodoros: Math.floor(Math.random() * 4),
                focusTime: Math.floor(Math.random() * 120)
            });
        }

        return data;
    };

    const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white">Productivity Analytics</h2>
                <div className="flex gap-2">
                    {(['week', 'month', 'year'] as const).map((range) => (
                        <button
                            key={range}
                            onClick={() => setTimeRange(range)}
                            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${timeRange === range
                                ? 'bg-blue-500 text-white'
                                : 'bg-white/[0.04] text-gray-400 hover:bg-white/[0.08]'
                                }`}
                        >
                            {range.charAt(0).toUpperCase() + range.slice(1)}
                        </button>
                    ))}
                </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="glass-card p-5 border-blue-500/20">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                            <span className="text-2xl"></span>
                        </div>
                        <div>
                            <div className="text-xs text-gray-400">Pomodoro Sessions</div>
                            <div className="text-2xl font-bold text-white">{analytics.pomodoroSessions}</div>
                        </div>
                    </div>
                </div>

                <div className="glass-card p-5 border-green-500/20">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                            <span className="text-2xl"></span>
                        </div>
                        <div>
                            <div className="text-xs text-gray-400">Tasks Completed</div>
                            <div className="text-2xl font-bold text-white">{analytics.tasksCompleted}</div>
                        </div>
                    </div>
                </div>

                <div className="glass-card p-5 border-purple-500/20">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                            <span className="text-2xl">⏱</span>
                        </div>
                        <div>
                            <div className="text-xs text-gray-400">Focus Time</div>
                            <div className="text-2xl font-bold text-white">{analytics.focusMinutes}m</div>
                        </div>
                    </div>
                </div>

                <div className="glass-card p-5 border-yellow-500/20">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 rounded-lg bg-yellow-500/10 flex items-center justify-center">
                            <span className="text-2xl"></span>
                        </div>
                        <div>
                            <div className="text-xs text-gray-400">Productivity Score</div>
                            <div className="text-2xl font-bold text-white">{analytics.productivityScore}</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Activity Over Time */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Activity Over Time</h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <AreaChart data={analytics.dailyData}>
                            <defs>
                                <linearGradient id="colorTasks" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                </linearGradient>
                                <linearGradient id="colorPomodoros" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                            <XAxis dataKey="date" stroke="#666" style={{ fontSize: '12px' }} />
                            <YAxis stroke="#666" />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#111', border: '1px solid #333', borderRadius: '8px' }}
                                labelStyle={{ color: '#999' }}
                            />
                            <Area type="monotone" dataKey="tasks" stroke="#3b82f6" fillOpacity={1} fill="url(#colorTasks)" name="Tasks" />
                            <Area type="monotone" dataKey="pomodoros" stroke="#8b5cf6" fillOpacity={1} fill="url(#colorPomodoros)" name="Pomodoros" />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>

                {/* Tasks by Category */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Tasks by Category</h3>
                    {analytics.tasksByCategory.length > 0 ? (
                        <ResponsiveContainer width="100%" height={250}>
                            <PieChart>
                                <Pie
                                    data={analytics.tasksByCategory}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                                    outerRadius={80}
                                    fill="#8884d8"
                                    dataKey="value"
                                >
                                    {analytics.tasksByCategory.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#111', border: '1px solid #333', borderRadius: '8px' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="h-64 flex items-center justify-center text-gray-500">
                            No task data yet
                        </div>
                    )}
                </div>
            </div>

            {/* Insights */}
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4"> Insights</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
                        <div className="text-sm text-blue-300 mb-1">Best Day</div>
                        <div className="text-lg font-semibold text-white">
                            {analytics.dailyData.length > 0
                                ? analytics.dailyData.reduce((max, day) => day.tasks > max.tasks ? day : max).date
                                : 'N/A'}
                        </div>
                    </div>
                    <div className="p-4 rounded-lg bg-purple-500/10 border border-purple-500/20">
                        <div className="text-sm text-purple-300 mb-1">Avg Tasks/Day</div>
                        <div className="text-lg font-semibold text-white">
                            {analytics.dailyData.length > 0
                                ? (analytics.dailyData.reduce((sum, day) => sum + day.tasks, 0) / analytics.dailyData.length).toFixed(1)
                                : '0'}
                        </div>
                    </div>
                    <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
                        <div className="text-sm text-green-300 mb-1">Total Focus Hours</div>
                        <div className="text-lg font-semibold text-white">
                            {(analytics.focusMinutes / 60).toFixed(1)}h
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
