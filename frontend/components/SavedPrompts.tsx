'use client';

import { useState, useEffect } from 'react';

interface Prompt {
    id: string;
    title: string;
    content: string;
    category: string;
}

interface SavedPromptsProps {
    onSelectPrompt: (prompt: string) => void;
}

export default function SavedPrompts({ onSelectPrompt }: SavedPromptsProps) {
    const [prompts, setPrompts] = useState<Prompt[]>([
        {
            id: '1',
            title: 'Code Review',
            content: 'Review this code and suggest improvements for performance and readability:',
            category: 'coding'
        },
        {
            id: '2',
            title: 'Explain Like I\'m 5',
            content: 'Explain the following concept in simple terms as if I\'m 5 years old:',
            category: 'learning'
        },
        {
            id: '3',
            title: 'Bug Fix Helper',
            content: 'Help me debug this error. Here\'s the error message and relevant code:',
            category: 'coding'
        },
        {
            id: '4',
            title: 'Email Draft',
            content: 'Help me draft a professional email about:',
            category: 'writing'
        },
        {
            id: '5',
            title: 'Meeting Summary',
            content: 'Summarize the key points and action items from this meeting:',
            category: 'productivity'
        }
    ]);

    const [newPrompt, setNewPrompt] = useState({ title: '', content: '', category: 'general' });
    const [isAdding, setIsAdding] = useState(false);

    const addPrompt = () => {
        if (newPrompt.title && newPrompt.content) {
            setPrompts([...prompts, { ...newPrompt, id: Date.now().toString() }]);
            setNewPrompt({ title: '', content: '', category: 'general' });
            setIsAdding(false);

            // Save to localStorage
            localStorage.setItem('friday_prompts', JSON.stringify([...prompts, { ...newPrompt, id: Date.now().toString() }]));
        }
    };

    const deletePrompt = (id: string) => {
        const updated = prompts.filter(p => p.id !== id);
        setPrompts(updated);
        localStorage.setItem('friday_prompts', JSON.stringify(updated));
    };

    // Load from localStorage
    useEffect(() => {
        const saved = localStorage.getItem('friday_prompts');
        if (saved) {
            try {
                setPrompts(JSON.parse(saved));
            } catch (e) {
                console.error('Failed to load prompts');
            }
        }
    }, []);

    const categories = ['coding', 'writing', 'learning', 'productivity', 'general'];

    return (
        <div className="p-4 space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-white">Saved Prompts</h3>
                <button
                    onClick={() => setIsAdding(!isAdding)}
                    className="p-1.5 rounded-lg hover:bg-white/[0.04] transition-colors"
                >
                    <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                </button>
            </div>

            {/* Add New Prompt */}
            {isAdding && (
                <div className="glass-card p-3 space-y-2">
                    <input
                        type="text"
                        placeholder="Prompt title..."
                        value={newPrompt.title}
                        onChange={(e) => setNewPrompt({ ...newPrompt, title: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white text-sm focus:outline-none focus:border-blue-500/30"
                    />
                    <textarea
                        placeholder="Prompt content..."
                        value={newPrompt.content}
                        onChange={(e) => setNewPrompt({ ...newPrompt, content: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white text-sm focus:outline-none focus:border-blue-500/30 resize-none"
                        rows={3}
                    />
                    <select
                        value={newPrompt.category}
                        onChange={(e) => setNewPrompt({ ...newPrompt, category: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white text-sm focus:outline-none focus:border-blue-500/30"
                    >
                        {categories.map(cat => (
                            <option key={cat} value={cat}>{cat}</option>
                        ))}
                    </select>
                    <div className="flex gap-2">
                        <button
                            onClick={addPrompt}
                            className="flex-1 py-2 rounded-lg bg-blue-500 hover:bg-blue-600 text-white text-sm font-semibold"
                        >
                            Save
                        </button>
                        <button
                            onClick={() => setIsAdding(false)}
                            className="px-4 py-2 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-white text-sm"
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            )}

            {/* Prompts List */}
            <div className="space-y-2 max-h-96 overflow-y-auto scrollbar-dark">
                {prompts.map((prompt) => (
                    <div
                        key={prompt.id}
                        className="group glass-card p-3 hover:border-blue-500/30 transition-all cursor-pointer"
                        onClick={() => onSelectPrompt(prompt.content)}
                    >
                        <div className="flex items-start justify-between">
                            <div className="flex-1">
                                <div className="flex items-center gap-2">
                                    <h4 className="text-sm font-semibold text-white">{prompt.title}</h4>
                                    <span className="text-xs px-2 py-0.5 rounded-full bg-white/[0.05] text-gray-400">
                                        {prompt.category}
                                    </span>
                                </div>
                                <p className="text-xs text-gray-400 mt-1 line-clamp-2">{prompt.content}</p>
                            </div>
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    deletePrompt(prompt.id);
                                }}
                                className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-500/20 transition-all"
                            >
                                <svg className="w-4 h-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
