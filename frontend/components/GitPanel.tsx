'use client';

import { useState, useEffect } from 'react';
import config from '@/config/api';

export default function GitPanel() {
    const [status, setStatus] = useState<any>(null);
    const [diff, setDiff] = useState('');
    const [commitMessage, setCommitMessage] = useState('');
    const [log, setLog] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadStatus();
        loadLog();
    }, []);

    const loadStatus = async () => {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/git/status`);
            const data = await response.json();
            setStatus(data);
        } catch (error) {
            console.error('Status error:', error);
        }
    };

    const loadDiff = async (staged = false) => {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/git/diff?staged=${staged}`);
            const data = await response.json();
            if (data.success) {
                setDiff(data.diff);
            }
        } catch (error) {
            console.error('Diff error:', error);
        }
    };

    const loadLog = async () => {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/git/log?max_count=10`);
            const data = await response.json();
            if (data.success) {
                setLog(data.log);
            }
        } catch (error) {
            console.error('Log error:', error);
        }
    };

    const stageAll = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/git/stage`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ files: null })
            });
            const data = await response.json();
            if (data.success) {
                loadStatus();
                alert('All changes staged');
            }
        } catch (error) {
            console.error('Stage error:', error);
        } finally {
            setLoading(false);
        }
    };

    const commit = async () => {
        if (!commitMessage && commitMessage !== 'auto') return;

        setLoading(true);
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/git/commit`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: commitMessage })
            });
            const data = await response.json();
            if (data.success) {
                alert(`Committed: ${data.commit_hash}\nMessage: ${data.message}`);
                setCommitMessage('');
                loadStatus();
                loadLog();
            }
        } catch (error) {
            console.error('Commit error:', error);
        } finally {
            setLoading(false);
        }
    };

    const push = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/git/push`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
            const data = await response.json();
            if (data.success) {
                alert('Pushed to remote!');
                loadStatus();
            }
        } catch (error) {
            console.error('Push error:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white">🔀 Git Integration</h2>

            {/* Status */}
            {status && !status.error && (
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Status</h3>
                    <div className="space-y-3">
                        <div className="flex items-center gap-2">
                            <span className="text-sm text-gray-400">Branch:</span>
                            <span className="text-white font-semibold">{status.branch}</span>
                            {status.ahead > 0 && <span className="text-green-400 text-xs">↑{status.ahead}</span>}
                            {status.behind > 0 && <span className="text-red-400 text-xs">↓{status.behind}</span>}
                        </div>

                        {status.modified && status.modified.length > 0 && (
                            <div>
                                <div className="text-sm text-yellow-400 mb-1">Modified ({status.modified.length}):</div>
                                {status.modified.map((file: string, idx: number) => (
                                    <div key={idx} className="text-xs text-gray-300 ml-4">• {file}</div>
                                ))}
                            </div>
                        )}

                        {status.staged && status.staged.length > 0 && (
                            <div>
                                <div className="text-sm text-green-400 mb-1">Staged ({status.staged.length}):</div>
                                {status.staged.map((file: string, idx: number) => (
                                    <div key={idx} className="text-xs text-gray-300 ml-4">• {file}</div>
                                ))}
                            </div>
                        )}

                        {status.untracked && status.untracked.length > 0 && (
                            <div>
                                <div className="text-sm text-red-400 mb-1">Untracked ({status.untracked.length}):</div>
                                {status.untracked.map((file: string, idx: number) => (
                                    <div key={idx} className="text-xs text-gray-300 ml-4">• {file}</div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Actions */}
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Actions</h3>
                <div className="space-y-3">
                    <div className="flex gap-3">
                        <button onClick={stageAll} disabled={loading} className="px-4 py-2 rounded-lg bg-yellow-500 hover:bg-yellow-600 text-white text-sm disabled:opacity-50">
                            Stage All
                        </button>
                        <button onClick={() => loadDiff(false)} className="px-4 py-2 rounded-lg bg-blue-500 hover:bg-blue-600 text-white text-sm">
                            View Diff
                        </button>
                        <button onClick={() => loadDiff(true)} className="px-4 py-2 rounded-lg bg-purple-500 hover:bg-purple-600 text-white text-sm">
                            View Staged
                        </button>
                    </div>

                    <div className="flex gap-3">
                        <input
                            type="text"
                            value={commitMessage}
                            onChange={(e) => setCommitMessage(e.target.value)}
                            placeholder="Commit message (or 'auto' for AI)"
                            className="flex-1 px-4 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white focus:outline-none focus:border-green-500/30"
                        />
                        <button onClick={commit} disabled={loading || !commitMessage} className="px-6 py-2 rounded-lg bg-green-500 hover:bg-green-600 text-white font-semibold disabled:opacity-50">
                            Commit
                        </button>
                    </div>

                    <button onClick={push} disabled={loading} className="w-full py-2 rounded-lg bg-blue-500 hover:bg-blue-600 text-white font-semibold disabled:opacity-50">
                        Push to Remote
                    </button>
                </div>
            </div>

            {/* Diff */}
            {diff && (
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Diff</h3>
                    <pre className="text-xs text-gray-300 whitespace-pre-wrap bg-black/40 p-4 rounded border border-white/[0.05] max-h-64 overflow-y-auto scrollbar-dark">
                        {diff}
                    </pre>
                </div>
            )}

            {/* Commit Log */}
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Recent Commits</h3>
                <div className="space-y-2">
                    {log.map((commit, idx) => (
                        <div key={idx} className="p-3 rounded-lg bg-white/[0.02] border border-white/[0.05]">
                            <div className="flex items-center justify-between mb-1">
                                <span className="text-xs font-mono text-blue-400">{commit.hash}</span>
                                <span className="text-xs text-gray-500">{new Date(commit.date).toLocaleDateString()}</span>
                            </div>
                            <div className="text-sm text-white">{commit.message}</div>
                            <div className="text-xs text-gray-500 mt-1">{commit.author}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
