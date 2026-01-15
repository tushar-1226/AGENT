'use client';

import { useState } from 'react';
import config from '@/config/api';

interface TODO {
    type: string;
    text: string;
    file: string;
    line: number;
    code_snippet: string;
    priority: string;
    created_at: string;
}

interface TodoStats {
    total: number;
    by_type: Record<string, number>;
    by_priority: Record<string, number>;
    by_file: Record<string, number>;
}

export default function TodoTrackerPage() {
    const [todos, setTodos] = useState<TODO[]>([]);
    const [stats, setStats] = useState<TodoStats | null>(null);
    const [loading, setLoading] = useState(false);
    const [projectPath, setProjectPath] = useState('.');
    const [filterType, setFilterType] = useState<string>('all');
    const [searchQuery, setSearchQuery] = useState('');

    const scanTodos = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/devtools/todos/scan`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: projectPath })
            });

            const data = await response.json();
            if (data.success) {
                setTodos(data.todos);
                setStats(data.stats);
            }
        } catch (error) {
            console.error('Failed to scan TODOs:', error);
        }
        setLoading(false);
    };

    const filterTodos = () => {
        if (searchQuery) {
            return todos.filter(todo =>
                todo.text.toLowerCase().includes(searchQuery.toLowerCase()) ||
                todo.file.toLowerCase().includes(searchQuery.toLowerCase())
            );
        }

        if (filterType === 'all') return todos;
        if (filterType === 'high') return todos.filter(t => t.priority === 'high');
        if (filterType === 'medium') return todos.filter(t => t.priority === 'medium');
        if (filterType === 'low') return todos.filter(t => t.priority === 'low');
        return todos.filter(t => t.type === filterType);
    };

    const getPriorityColor = (priority: string) => {
        switch (priority) {
            case 'high': return 'bg-red-600';
            case 'medium': return 'bg-yellow-600';
            case 'low': return 'bg-blue-600';
            default: return 'bg-gray-600';
        }
    };

    const filteredTodos = filterTodos();

    return (
        <div className="min-h-screen bg-[#0a0a0a] text-white p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
                        📝 TODO/FIXME Tracker
                    </h1>
                    <p className="text-gray-400">
                        Scan your codebase for TODO, FIXME, HACK, NOTE, XXX, and BUG comments
                    </p>
                </div>

                {/* Controls */}
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 mb-6">
                    <div className="flex gap-4 items-end">
                        <div className="flex-1">
                            <label className="block text-sm mb-2 text-gray-400">Project Path</label>
                            <input
                                type="text"
                                value={projectPath}
                                onChange={(e) => setProjectPath(e.target.value)}
                                className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="."
                            />
                        </div>
                        <button
                            onClick={scanTodos}
                            disabled={loading}
                            className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50"
                        >
                            {loading ? 'Scanning...' : 'Scan Project'}
                        </button>
                    </div>
                </div>

                {/* Stats */}
                {stats && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                        <div className="bg-gradient-to-br from-blue-600/20 to-blue-600/5 border border-blue-500/30 rounded-lg p-6">
                            <div className="text-3xl font-bold">{stats.total}</div>
                            <div className="text-sm text-gray-400">Total TODOs</div>
                        </div>

                        {Object.entries(stats.by_priority).map(([priority, count]) => (
                            <div
                                key={priority}
                                className={`bg-gradient-to-br ${priority === 'high' ? 'from-red-600/20 to-red-600/5 border-red-500/30' :
                                        priority === 'medium' ? 'from-yellow-600/20 to-yellow-600/5 border-yellow-500/30' :
                                            'from-blue-600/20 to-blue-600/5 border-blue-500/30'
                                    } border rounded-lg p-6`}
                            >
                                <div className="text-3xl font-bold">{count}</div>
                                <div className="text-sm text-gray-400 capitalize">{priority} Priority</div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Filters */}
                {todos.length > 0 && (
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4 mb-6">
                        <div className="flex gap-4 items-center flex-wrap">
                            <div className="flex-1 min-w-[200px]">
                                <input
                                    type="text"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="Search TODOs..."
                                />
                            </div>

                            <div className="flex gap-2">
                                {['all', 'high', 'medium', 'low', 'TODO', 'FIXME', 'HACK', 'BUG'].map((filter) => (
                                    <button
                                        key={filter}
                                        onClick={() => setFilterType(filter)}
                                        className={`px-4 py-2 rounded-lg font-medium transition-all ${filterType === filter
                                                ? 'bg-blue-600 text-white'
                                                : 'bg-white/5 text-gray-400 hover:bg-white/10'
                                            }`}
                                    >
                                        {filter.toUpperCase()}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* Results */}
                <div className="space-y-3">
                    {loading ? (
                        <div className="text-center py-12">
                            <div className="inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                            <p className="text-gray-400 mt-4">Scanning codebase...</p>
                        </div>
                    ) : filteredTodos.length === 0 && todos.length === 0 ? (
                        <div className="text-center py-12">
                            <p className="text-gray-400 text-lg">No TODOs found. Click "Scan Project" to start.</p>
                        </div>
                    ) : filteredTodos.length === 0 ? (
                        <div className="text-center py-12">
                            <p className="text-gray-400 text-lg">No TODOs match your filter.</p>
                        </div>
                    ) : (
                        filteredTodos.map((todo, index) => (
                            <div
                                key={index}
                                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4 hover:bg-white/10 transition-all"
                            >
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-2">
                                            <span className={`px-2 py-1 rounded text-xs font-semibold ${getPriorityColor(todo.priority)}`}>
                                                {todo.type}
                                            </span>
                                            <span className="text-gray-400 text-sm">
                                                {todo.file}:{todo.line}
                                            </span>
                                        </div>

                                        <p className="text-white mb-2">{todo.text}</p>

                                        <pre className="bg-black/50 border border-white/10 rounded p-3 text-sm overflow-x-auto">
                                            <code className="text-gray-300">{todo.code_snippet}</code>
                                        </pre>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>

                {/* Summary footer */}
                {filteredTodos.length > 0 && (
                    <div className="mt-6 text-center text-gray-400">
                        Showing {filteredTodos.length} of {todos.length} TODOs
                    </div>
                )}
            </div>
        </div>
    );
}
