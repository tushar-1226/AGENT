'use client';

import { useState } from 'react';
import Editor from '@monaco-editor/react';
import config from '@/config/api';

export default function CodeAssistant() {
    const [code, setCode] = useState('// Write or paste your code here\n\n');
    const [language, setLanguage] = useState('javascript');
    const [output, setOutput] = useState('');
    const [loading, setLoading] = useState(false);
    const [mode, setMode] = useState<'debug' | 'test' | 'refactor' | 'explain'>('explain');

    const analyzeCode = async () => {
        if (!code.trim()) return;

        setLoading(true);
        setOutput('');

        try {
            // Use Gemini via WebSocket for code analysis
            const prompts = {
                debug: `Analyze this ${language} code for bugs and errors:\n\n${code}\n\nProvide:\n1. Potential bugs\n2. Error explanations\n3. Fixes`,
                test: `Generate unit tests for this ${language} code:\n\n${code}\n\nProvide comprehensive test cases.`,
                refactor: `Suggest refactoring improvements for this ${language} code:\n\n${code}\n\nFocus on:\n1. Performance\n2. Readability\n3. Best practices`,
                explain: `Explain this ${language} code in detail:\n\n${code}\n\nProvide:\n1. What it does\n2. How it works\n3. Key concepts`
            };

            const response = await fetch(`${config.apiBaseUrl}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: prompts[mode] })
            });

            const data = await response.json();
            setOutput(data.response || 'No response from AI');
        } catch (error) {
            setOutput('Error analyzing code: ' + error);
        } finally {
            setLoading(false);
        }
    };

    const languages = [
        'javascript', 'typescript', 'python', 'java', 'cpp', 'csharp',
        'go', 'rust', 'php', 'ruby', 'swift', 'kotlin'
    ];

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-white">Code Assistant</h2>
                <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="px-4 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white focus:outline-none focus:border-blue-500/30"
                >
                    {languages.map(lang => (
                        <option key={lang} value={lang}>{lang.toUpperCase()}</option>
                    ))}
                </select>
            </div>

            {/* Mode Selector */}
            <div className="flex gap-2">
                {(['explain', 'debug', 'test', 'refactor'] as const).map((m) => (
                    <button
                        key={m}
                        onClick={() => setMode(m)}
                        className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${mode === m
                            ? 'bg-blue-500 text-white'
                            : 'bg-white/[0.04] text-gray-400 hover:bg-white/[0.08]'
                            }`}
                    >
                        {m === 'explain' && '📖'} {m === 'debug' && '🐛'} {m === 'test' && '🧪'} {m === 'refactor' && '♻️'}
                        {' '}{m.charAt(0).toUpperCase() + m.slice(1)}
                    </button>
                ))}
            </div>

            {/* Editor */}
            <div className="glass-card p-4 border-blue-500/20">
                <div className="rounded-lg overflow-hidden border border-white/[0.08]">
                    <Editor
                        height="400px"
                        language={language}
                        value={code}
                        onChange={(value) => setCode(value || '')}
                        theme="vs-dark"
                        options={{
                            minimap: { enabled: false },
                            fontSize: 14,
                            lineNumbers: 'on',
                            roundedSelection: true,
                            scrollBeyondLastLine: false,
                            automaticLayout: true,
                            tabSize: 2,
                        }}
                    />
                </div>

                <button
                    onClick={analyzeCode}
                    disabled={loading}
                    className="w-full mt-4 py-3 rounded-lg bg-blue-500 hover:bg-blue-600 text-white font-semibold transition-all disabled:opacity-50"
                >
                    {loading ? 'Analyzing...' : `${mode.charAt(0).toUpperCase() + mode.slice(1)} Code`}
                </button>
            </div>

            {/* Output */}
            {output && (
                <div className="glass-card p-6 border-green-500/20">
                    <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                        <span>✨</span> AI Analysis
                    </h3>
                    <div className="prose prose-invert max-w-none">
                        <pre className="text-sm text-gray-300 whitespace-pre-wrap bg-white/[0.02] p-4 rounded-lg border border-white/[0.05]">
                            {output}
                        </pre>
                    </div>
                </div>
            )}

            {/* Quick Actions */}
            <div className="grid grid-cols-2 gap-3">
                <button
                    onClick={() => setCode('// Write or paste your code here\n\n')}
                    className="py-2 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-gray-300 text-sm transition-all"
                >
                    Clear Code
                </button>
                <button
                    onClick={() => navigator.clipboard.writeText(code)}
                    className="py-2 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-gray-300 text-sm transition-all"
                >
                    Copy Code
                </button>
            </div>

            {/* Tips */}
            <div className="glass-card p-4 bg-blue-500/5 border-blue-500/20">
                <div className="text-sm text-blue-300">
                    <strong> Tips:</strong>
                    <ul className="mt-2 space-y-1 text-xs text-gray-400">
                        <li>• <strong>Explain:</strong> Understand what code does</li>
                        <li>• <strong>Debug:</strong> Find and fix bugs</li>
                        <li>• <strong>Test:</strong> Generate unit tests</li>
                        <li>• <strong>Refactor:</strong> Improve code quality</li>
                    </ul>
                </div>
            </div>
        </div>
    );
}
