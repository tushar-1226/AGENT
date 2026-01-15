'use client';

import { useState } from 'react';

interface DocsModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function DocsModal({ isOpen, onClose }: DocsModalProps) {
    const [activeTab, setActiveTab] = useState<'getting-started' | 'features' | 'api'>('getting-started');

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <div className="w-full max-w-5xl max-h-[90vh] glass-card overflow-hidden flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-white/[0.08]">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center">

                        </div>
                        <h2 className="text-2xl font-bold text-white">Documentation</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="w-8 h-8 rounded-lg hover:bg-white/[0.08] flex items-center justify-center text-gray-400 hover:text-white transition-colors"
                    >
                        ✕
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex gap-1 px-6 pt-4 border-b border-white/[0.08]">
                    <button
                        onClick={() => setActiveTab('getting-started')}
                        className={`px-4 py-2 rounded-t-lg font-medium transition-all ${activeTab === 'getting-started'
                            ? 'bg-blue-500/20 text-blue-400 border-b-2 border-blue-500'
                            : 'text-gray-400 hover:text-white hover:bg-white/[0.04]'
                            }`}
                    >
                        Getting Started
                    </button>
                    <button
                        onClick={() => setActiveTab('features')}
                        className={`px-4 py-2 rounded-t-lg font-medium transition-all ${activeTab === 'features'
                            ? 'bg-blue-500/20 text-blue-400 border-b-2 border-blue-500'
                            : 'text-gray-400 hover:text-white hover:bg-white/[0.04]'
                            }`}
                    >
                        Features
                    </button>
                    <button
                        onClick={() => setActiveTab('api')}
                        className={`px-4 py-2 rounded-t-lg font-medium transition-all ${activeTab === 'api'
                            ? 'bg-blue-500/20 text-blue-400 border-b-2 border-blue-500'
                            : 'text-gray-400 hover:text-white hover:bg-white/[0.04]'
                            }`}
                    >
                        API Reference
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 scrollbar-dark">
                    {activeTab === 'getting-started' && <GettingStarted />}
                    {activeTab === 'features' && <Features />}
                    {activeTab === 'api' && <APIReference />}
                </div>
            </div>
        </div>
    );
}

function GettingStarted() {
    return (
        <div className="space-y-6 text-gray-300">
            <div>
                <h3 className="text-xl font-bold text-white mb-3">Welcome to F.R.I.D.A.Y. Agent!</h3>
                <p className="text-gray-400 leading-relaxed">
                    Your AI-powered development platform with 19 revolutionary features. Let's get you started!
                </p>
            </div>

            <div className="glass-card p-5 border-green-500/20 bg-green-500/5">
                <h4 className="text-lg font-semibold text-green-400 mb-3">Quick Start (5 minutes)</h4>
                <div className="space-y-3">
                    <div className="flex gap-3">
                        <span className="flex-shrink-0 w-6 h-6 rounded-full bg-green-500/20 text-green-400 flex items-center justify-center text-sm font-bold">1</span>
                        <div>
                            <div className="font-medium text-white">Start Chatting</div>
                            <div className="text-sm text-gray-400">Type your question in the chat box and press Enter</div>
                        </div>
                    </div>
                    <div className="flex gap-3">
                        <span className="flex-shrink-0 w-6 h-6 rounded-full bg-green-500/20 text-green-400 flex items-center justify-center text-sm font-bold">2</span>
                        <div>
                            <div className="font-medium text-white">Explore Tools</div>
                            <div className="text-sm text-gray-400">Click "Tools" in header → Try Tasks, Pomodoro, Calculator</div>
                        </div>
                    </div>
                    <div className="flex gap-3">
                        <span className="flex-shrink-0 w-6 h-6 rounded-full bg-green-500/20 text-green-400 flex items-center justify-center text-sm font-bold">3</span>
                        <div>
                            <div className="font-medium text-white">Code Assistant</div>
                            <div className="text-sm text-gray-400">Click "Code" → Paste code → Select mode (Explain/Debug/Test)</div>
                        </div>
                    </div>
                </div>
            </div>

            <div>
                <h4 className="text-lg font-semibold text-white mb-3">Try These Examples</h4>
                <div className="space-y-2">
                    <div className="p-3 rounded-lg bg-white/[0.02] border border-white/[0.05]">
                        <div className="text-sm font-mono text-blue-400">"Create a task: Deploy website tomorrow urgent"</div>
                        <div className="text-xs text-gray-500 mt-1">→ AI parses and creates high-priority task</div>
                    </div>
                    <div className="p-3 rounded-lg bg-white/[0.02] border border-white/[0.05]">
                        <div className="text-sm font-mono text-blue-400">"Show me AAPL stock price"</div>
                        <div className="text-xs text-gray-500 mt-1">→ Real-time stock data (no API key needed!)</div>
                    </div>
                    <div className="p-3 rounded-lg bg-white/[0.02] border border-white/[0.05]">
                        <div className="text-sm font-mono text-blue-400">"Explain this code: [paste code]"</div>
                        <div className="text-xs text-gray-500 mt-1">→ AI explains what the code does</div>
                    </div>
                </div>
            </div>

            <div>
                <h4 className="text-lg font-semibold text-white mb-3">Advanced Setup (Optional)</h4>
                <div className="space-y-3">
                    <div className="p-4 rounded-lg bg-white/[0.02] border border-white/[0.05]">
                        <div className="font-medium text-white mb-2">Install Optional Features</div>
                        <pre className="text-xs bg-black/40 p-3 rounded border border-white/[0.05] overflow-x-auto">
                            <code className="text-green-400">cd backend{'\n'}pip install chromadb gitpython sqlalchemy playwright</code>
                        </pre>
                        <div className="text-xs text-gray-500 mt-2">Enables: RAG, Git, Database, Browser automation</div>
                    </div>
                    <div className="p-4 rounded-lg bg-white/[0.02] border border-white/[0.05]">
                        <div className="font-medium text-white mb-2">🔑 Add API Keys (Optional)</div>
                        <div className="text-sm text-gray-400">Add to <code className="text-blue-400">backend/.env</code>:</div>
                        <pre className="text-xs bg-black/40 p-3 rounded border border-white/[0.05] mt-2">
                            <code className="text-gray-300">OPENWEATHER_API_KEY=your_key{'\n'}NEWS_API_KEY=your_key</code>
                        </pre>
                    </div>
                </div>
            </div>

            <div className="glass-card p-5 border-blue-500/20 bg-blue-500/5">
                <h4 className="text-lg font-semibold text-blue-400 mb-2">Pro Tips</h4>
                <ul className="space-y-2 text-sm">
                    <li className="flex gap-2"><span>•</span><span>Use voice control: Click microphone icon or say "Hey Friday"</span></li>
                    <li className="flex gap-2"><span>•</span><span>Split-screen: Click "Split" to work with multiple tools</span></li>
                    <li className="flex gap-2"><span>•</span><span>Analytics: Track your productivity with charts and insights</span></li>
                    <li className="flex gap-2"><span>•</span><span>Save prompts: Sidebar → Prompts → Save frequently used prompts</span></li>
                </ul>
            </div>
        </div>
    );
}

function Features() {
    const features = [
        {
            category: "Revolutionary Features",
            items: [
                { name: "RAG Document Intelligence", desc: "Upload codebase for AI-powered semantic search" },
                { name: "Integrated Terminal", desc: "Execute commands directly from chat" },
                { name: "Git Integration", desc: "Full version control with AI commit messages" },
                { name: "Database Query Builder", desc: "Natural language to SQL conversion" },
                { name: "Screenshot to Code", desc: "Convert UI mockups to React components" },
                { name: "Browser Automation", desc: "Playwright-powered E2E testing" },
                { name: "Learning Path Generator", desc: "Personalized education curriculum" },
            ]
        },
        {
            category: "Core Features",
            items: [
                { name: "Smart Code Assistant", desc: "Monaco editor with 4 analysis modes" },
                { name: "AI Task Management", desc: "Natural language task parsing" },
                { name: "Productivity Analytics", desc: "Charts, insights, productivity scoring" },
                { name: "Split-Screen Mode", desc: "Work with multiple tools simultaneously" },
                { name: "System Monitoring", desc: "Real-time CPU, RAM, disk stats" },
                { name: "Weather/News/Stock APIs", desc: "Live data feeds" },
                { name: "Voice Control", desc: "Speech-to-text and text-to-speech" },
                { name: "File Upload & Analysis", desc: "Image and PDF processing" },
            ]
        }
    ];

    return (
        <div className="space-y-6">
            {features.map((category, idx) => (
                <div key={idx}>
                    <h3 className="text-xl font-bold text-white mb-4">{category.category}</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {category.items.map((feature, fidx) => (
                            <div key={fidx} className="glass-card p-4 border-blue-500/10 hover:border-blue-500/30 transition-all">
                                <div className="font-semibold text-white mb-1">{feature.name}</div>
                                <div className="text-sm text-gray-400">{feature.desc}</div>
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
}

function APIReference() {
    const endpoints = [
        {
            category: "RAG Document Intelligence",
            endpoints: [
                { method: "POST", path: "/api/rag/upload-directory", desc: "Upload codebase" },
                { method: "POST", path: "/api/rag/query", desc: "Semantic search" },
                { method: "GET", path: "/api/rag/stats", desc: "Database statistics" },
            ]
        },
        {
            category: "Integrated Terminal",
            endpoints: [
                { method: "POST", path: "/api/terminal/create", desc: "Create session" },
                { method: "POST", path: "/api/terminal/execute", desc: "Run command" },
                { method: "GET", path: "/api/terminal/sessions", desc: "List sessions" },
            ]
        },
        {
            category: "Git Integration",
            endpoints: [
                { method: "GET", path: "/api/git/status", desc: "Repository status" },
                { method: "POST", path: "/api/git/commit", desc: "Create commit (use 'auto' for AI message)" },
                { method: "POST", path: "/api/git/push", desc: "Push to remote" },
            ]
        },
        {
            category: "Task Management",
            endpoints: [
                { method: "POST", path: "/api/tasks/parse", desc: "Parse natural language task" },
                { method: "GET", path: "/api/tasks", desc: "List all tasks" },
                { method: "PUT", path: "/api/tasks/{id}", desc: "Update task" },
            ]
        },
    ];

    return (
        <div className="space-y-6">
            <div className="glass-card p-5 border-blue-500/20 bg-blue-500/5">
                <div className="font-semibold text-blue-400 mb-2">📖 Full API Documentation</div>
                <div className="text-sm text-gray-400">
                    Visit <a href="http://localhost:8000/docs" target="_blank" className="text-blue-400 hover:text-blue-300 underline">http://localhost:8000/docs</a> for interactive API documentation
                </div>
            </div>

            {endpoints.map((category, idx) => (
                <div key={idx}>
                    <h3 className="text-lg font-bold text-white mb-3">{category.category}</h3>
                    <div className="space-y-2">
                        {category.endpoints.map((endpoint, eidx) => (
                            <div key={eidx} className="p-3 rounded-lg bg-white/[0.02] border border-white/[0.05] hover:border-blue-500/30 transition-all">
                                <div className="flex items-center gap-3 mb-1">
                                    <span className={`px-2 py-0.5 rounded text-xs font-mono font-bold ${endpoint.method === 'GET' ? 'bg-green-500/20 text-green-400' :
                                        endpoint.method === 'POST' ? 'bg-blue-500/20 text-blue-400' :
                                            endpoint.method === 'PUT' ? 'bg-yellow-500/20 text-yellow-400' :
                                                'bg-red-500/20 text-red-400'
                                        }`}>
                                        {endpoint.method}
                                    </span>
                                    <code className="text-sm text-blue-400 font-mono">{endpoint.path}</code>
                                </div>
                                <div className="text-sm text-gray-400 ml-16">{endpoint.desc}</div>
                            </div>
                        ))}
                    </div>
                </div>
            ))}

            <div className="glass-card p-5 border-purple-500/20 bg-purple-500/5">
                <div className="font-semibold text-purple-400 mb-2">Example Usage</div>
                <pre className="text-xs bg-black/40 p-3 rounded border border-white/[0.05] overflow-x-auto">
                    <code className="text-gray-300">{`curl -X POST http://localhost:8000/api/rag/query \\
  -H "Content-Type: application/json" \\
  -d '{"query": "How does authentication work?"}'`}</code>
                </pre>
            </div>
        </div>
    );
}
