'use client';

import { useState, useEffect } from 'react';
import config from '@/config/api';

interface Task {
    id: string;
    title: string;
    description: string;
    priority: 'low' | 'medium' | 'high';
    status: 'pending' | 'in_progress' | 'done';
    due_date: string | null;
    category: string;
    created_at: string;
    updated_at: string;
}

interface TaskStats {
    total: number;
    pending: number;
    in_progress: number;
    done: number;
    overdue: number;
    by_category: Record<string, number>;
    by_priority: Record<string, number>;
}

export default function TaskManager() {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [stats, setStats] = useState<TaskStats | null>(null);
    const [input, setInput] = useState('');
    const [filter, setFilter] = useState<'all' | 'pending' | 'in_progress' | 'done'>('all');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadTasks();
    }, [filter]);

    const loadTasks = async () => {
        try {
            const statusParam = filter !== 'all' ? `?status=${filter}` : '';
            const response = await fetch(`${config.apiBaseUrl}/api/tasks${statusParam}`);
            const data = await response.json();
            if (data.success) {
                setTasks(data.tasks);
                setStats(data.stats);
            }
        } catch (error) {
            console.error('Failed to load tasks:', error);
        }
    };

    const createTask = async () => {
        if (!input.trim()) return;

        setLoading(true);
        try {
            // Parse natural language
            const parseResponse = await fetch(`${config.apiBaseUrl}/api/tasks/parse`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: input })
            });
            const parseData = await parseResponse.json();

            if (parseData.success) {
                // Create task
                const createResponse = await fetch(`${config.apiBaseUrl}/api/tasks`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(parseData.parsed)
                });
                const createData = await createResponse.json();

                if (createData.success) {
                    setInput('');
                    loadTasks();
                }
            }
        } catch (error) {
            console.error('Failed to create task:', error);
        } finally {
            setLoading(false);
        }
    };

    const updateTaskStatus = async (taskId: string, status: string) => {
        try {
            await fetch(`${config.apiBaseUrl}/api/tasks/${taskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status })
            });
            loadTasks();
        } catch (error) {
            console.error('Failed to update task:', error);
        }
    };

    const deleteTask = async (taskId: string) => {
        try {
            await fetch(`${config.apiBaseUrl}/api/tasks/${taskId}`, {
                method: 'DELETE'
            });
            loadTasks();
        } catch (error) {
            console.error('Failed to delete task:', error);
        }
    };

    const getPriorityColor = (priority: string) => {
        switch (priority) {
            case 'high': return 'text-red-400 bg-red-500/10 border-red-500/30';
            case 'medium': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30';
            case 'low': return 'text-green-400 bg-green-500/10 border-green-500/30';
            default: return 'text-gray-400 bg-gray-500/10 border-gray-500/30';
        }
    };

    const formatDate = (dateString: string | null) => {
        if (!dateString) return null;
        const date = new Date(dateString);
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);

        if (date.toDateString() === today.toDateString()) return 'Today';
        if (date.toDateString() === tomorrow.toDateString()) return 'Tomorrow';
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    };

    return (
        <div className="space-y-6">
            {/* Header with Stats */}
            {stats && (
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                    <div className="glass-card p-4 text-center">
                        <div className="text-2xl font-bold text-white">{stats.total}</div>
                        <div className="text-xs text-gray-400">Total</div>
                    </div>
                    <div className="glass-card p-4 text-center border-yellow-500/20">
                        <div className="text-2xl font-bold text-yellow-400">{stats.pending}</div>
                        <div className="text-xs text-gray-400">Pending</div>
                    </div>
                    <div className="glass-card p-4 text-center border-blue-500/20">
                        <div className="text-2xl font-bold text-blue-400">{stats.in_progress}</div>
                        <div className="text-xs text-gray-400">In Progress</div>
                    </div>
                    <div className="glass-card p-4 text-center border-green-500/20">
                        <div className="text-2xl font-bold text-green-400">{stats.done}</div>
                        <div className="text-xs text-gray-400">Done</div>
                    </div>
                    <div className="glass-card p-4 text-center border-red-500/20">
                        <div className="text-2xl font-bold text-red-400">{stats.overdue}</div>
                        <div className="text-xs text-gray-400">Overdue</div>
                    </div>
                </div>
            )}

            {/* Input */}
            <div className="glass-card p-4">
                <div className="flex gap-3">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && createTask()}
                        placeholder="Add task... (e.g., 'Buy milk tomorrow' or 'Fix urgent bug')"
                        className="flex-1 px-4 py-3 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/30"
                    />
                    <button
                        onClick={createTask}
                        disabled={loading}
                        className="px-6 py-3 rounded-lg bg-blue-500 hover:bg-blue-600 text-white font-semibold transition-all disabled:opacity-50"
                    >
                        {loading ? 'Adding...' : 'Add Task'}
                    </button>
                </div>
                <div className="mt-2 text-xs text-gray-500">
                    💡 Try: "Deploy website tomorrow", "Call John urgent", "Learn React next week"
                </div>
            </div>

            {/* Filters */}
            <div className="flex gap-2">
                {(['all', 'pending', 'in_progress', 'done'] as const).map((f) => (
                    <button
                        key={f}
                        onClick={() => setFilter(f)}
                        className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${filter === f
                                ? 'bg-blue-500 text-white'
                                : 'bg-white/[0.04] text-gray-400 hover:bg-white/[0.08]'
                            }`}
                    >
                        {f.replace('_', ' ').toUpperCase()}
                    </button>
                ))}
            </div>

            {/* Tasks List */}
            <div className="space-y-3">
                {tasks.length === 0 ? (
                    <div className="glass-card p-8 text-center text-gray-500">
                        No tasks yet. Add one above!
                    </div>
                ) : (
                    tasks.map((task) => (
                        <div
                            key={task.id}
                            className={`glass-card p-4 ${task.status === 'done' ? 'opacity-60' : ''
                                }`}
                        >
                            <div className="flex items-start gap-3">
                                {/* Checkbox */}
                                <button
                                    onClick={() => updateTaskStatus(task.id, task.status === 'done' ? 'pending' : 'done')}
                                    className={`mt-1 w-5 h-5 rounded border-2 flex items-center justify-center transition-all ${task.status === 'done'
                                            ? 'bg-green-500 border-green-500'
                                            : 'border-white/[0.2] hover:border-white/[0.4]'
                                        }`}
                                >
                                    {task.status === 'done' && (
                                        <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                        </svg>
                                    )}
                                </button>

                                {/* Content */}
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                        <h3 className={`text-sm font-semibold ${task.status === 'done' ? 'line-through text-gray-500' : 'text-white'}`}>
                                            {task.title}
                                        </h3>
                                        <span className={`text-xs px-2 py-0.5 rounded-full border ${getPriorityColor(task.priority)}`}>
                                            {task.priority}
                                        </span>
                                        {task.category && (
                                            <span className="text-xs px-2 py-0.5 rounded-full bg-white/[0.05] text-gray-400">
                                                {task.category}
                                            </span>
                                        )}
                                    </div>
                                    {task.description && (
                                        <p className="text-xs text-gray-400 mb-2">{task.description}</p>
                                    )}
                                    <div className="flex items-center gap-3 text-xs text-gray-500">
                                        {task.due_date && (
                                            <span className="flex items-center gap-1">
                                                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                                </svg>
                                                {formatDate(task.due_date)}
                                            </span>
                                        )}
                                    </div>
                                </div>

                                {/* Actions */}
                                <div className="flex gap-1">
                                    {task.status !== 'in_progress' && task.status !== 'done' && (
                                        <button
                                            onClick={() => updateTaskStatus(task.id, 'in_progress')}
                                            className="p-2 rounded-lg hover:bg-blue-500/20 text-blue-400 transition-all"
                                            title="Start"
                                        >
                                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                        </button>
                                    )}
                                    <button
                                        onClick={() => deleteTask(task.id)}
                                        className="p-2 rounded-lg hover:bg-red-500/20 text-red-400 transition-all"
                                        title="Delete"
                                    >
                                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
