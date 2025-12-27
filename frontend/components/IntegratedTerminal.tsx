'use client';

import { useState, useEffect } from 'react';
import config from '@/config/api';

export default function IntegratedTerminal() {
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [command, setCommand] = useState('');
    const [output, setOutput] = useState<string[]>([]);
    const [cwd, setCwd] = useState('~');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        createSession();
    }, []);

    const createSession = async () => {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/terminal/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
            const data = await response.json();
            if (data.success) {
                setSessionId(data.session_id);
                setOutput(['Terminal session created. Type commands below.']);
            }
        } catch (error) {
            setOutput(['Error creating terminal session']);
        }
    };

    const executeCommand = async () => {
        if (!command.trim() || !sessionId) return;

        setLoading(true);
        setOutput(prev => [...prev, `$ ${command}`]);

        try {
            const response = await fetch(`${config.apiBaseUrl}/api/terminal/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, command })
            });
            const data = await response.json();

            if (data.success) {
                setOutput(prev => [...prev, data.output || '']);
                if (data.cwd) setCwd(data.cwd);
            } else if (data.requires_confirmation) {
                const confirmed = confirm(`${data.error}\n\nDo you want to proceed?`);
                if (confirmed) {
                    // Re-execute with force flag
                    const forceResponse = await fetch(`${config.apiBaseUrl}/api/terminal/execute`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ session_id: sessionId, command, force: true })
                    });
                    const forceData = await forceResponse.json();
                    setOutput(prev => [...prev, forceData.output || forceData.error]);
                }
            } else {
                setOutput(prev => [...prev, `Error: ${data.error}`]);
            }
        } catch (error) {
            setOutput(prev => [...prev, `Error: ${error}`]);
        } finally {
            setLoading(false);
            setCommand('');
        }
    };

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-white">Integrated Terminal</h2>
                <div className="text-sm text-gray-400">CWD: {cwd}</div>
            </div>

            {/* Terminal Output */}
            <div className="glass-card p-4 bg-black/40 border-green-500/20">
                <div className="font-mono text-sm space-y-1 max-h-96 overflow-y-auto scrollbar-dark">
                    {output.map((line, idx) => (
                        <div key={idx} className={line.startsWith('$') ? 'text-green-400' : 'text-gray-300'}>
                            {line}
                        </div>
                    ))}
                </div>
            </div>

            {/* Command Input */}
            <div className="flex gap-3">
                <div className="flex-1 flex items-center gap-2 px-4 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                    <span className="text-green-400 font-mono">$</span>
                    <input
                        type="text"
                        value={command}
                        onChange={(e) => setCommand(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && executeCommand()}
                        placeholder="Enter command..."
                        className="flex-1 bg-transparent text-white font-mono focus:outline-none"
                        disabled={loading}
                    />
                </div>
                <button
                    onClick={executeCommand}
                    disabled={loading || !command.trim()}
                    className="px-6 py-2 rounded-lg bg-green-500 hover:bg-green-600 text-white font-semibold disabled:opacity-50"
                >
                    {loading ? 'Running...' : 'Execute'}
                </button>
            </div>

            {/* Quick Commands */}
            <div className="flex gap-2 flex-wrap">
                {['ls -la', 'git status', 'npm install', 'python --version'].map(cmd => (
                    <button
                        key={cmd}
                        onClick={() => setCommand(cmd)}
                        className="px-3 py-1 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-xs text-gray-300 font-mono"
                    >
                        {cmd}
                    </button>
                ))}
            </div>
        </div>
    );
}
