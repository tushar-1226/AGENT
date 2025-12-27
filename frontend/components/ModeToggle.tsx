'use client';

import { useState, useEffect } from 'react';
import config from '@/config/api';

type LLMMode = 'local' | 'cloud' | 'hybrid';

interface ModeToggleProps {
    onModeChange?: (mode: LLMMode) => void;
}

export default function ModeToggle({ onModeChange }: ModeToggleProps) {
    const [currentMode, setCurrentMode] = useState<LLMMode>('hybrid');
    const [isOpen, setIsOpen] = useState(false);
    const [loading, setLoading] = useState(false);

    // Fetch current mode on mount
    useEffect(() => {
        fetchCurrentMode();
    }, []);

    const fetchCurrentMode = async () => {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/llm/get-mode`);
            const data = await response.json();
            if (data.success) {
                setCurrentMode(data.mode);
            }
        } catch (error) {
            console.error('Error fetching mode:', error);
        }
    };

    const handleModeChange = async (mode: LLMMode) => {
        setLoading(true);
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/llm/set-mode`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode })
            });

            const data = await response.json();

            if (data.success) {
                setCurrentMode(mode);
                setIsOpen(false);
                onModeChange?.(mode);

                // Show success toast
                window.dispatchEvent(new CustomEvent('showToast', {
                    detail: {
                        message: `Mode switched to ${mode.charAt(0).toUpperCase() + mode.slice(1)}`,
                        type: 'success'
                    }
                }));
            } else {
                console.error('Failed to set mode:', data.error);

                // Show error toast with helpful message
                let errorMessage = data.error || 'Failed to set mode';
                if (mode === 'local' && errorMessage.includes('not available')) {
                    errorMessage = 'Local mode unavailable. Please install and start Ollama first.';
                }

                window.dispatchEvent(new CustomEvent('showToast', {
                    detail: {
                        message: errorMessage,
                        type: 'error'
                    }
                }));
            }
        } catch (error) {
            console.error('Error setting mode:', error);
            window.dispatchEvent(new CustomEvent('showToast', {
                detail: {
                    message: 'Network error. Please check if backend is running.',
                    type: 'error'
                }
            }));
        } finally {
            setLoading(false);
        }
    };

    const modes = [
        {
            id: 'local' as LLMMode,
            name: 'Local Only',
            icon: '💻',
            description: 'All queries use local models',
            color: 'from-green-500/10 to-emerald-500/10 border-green-500/30'
        },
        {
            id: 'hybrid' as LLMMode,
            name: 'Hybrid',
            icon: '🔄',
            description: 'Smart routing (recommended)',
            color: 'from-blue-500/10 to-purple-500/10 border-blue-500/30'
        },
        {
            id: 'cloud' as LLMMode,
            name: 'Cloud Only',
            icon: '🌐',
            description: 'All queries use Gemini',
            color: 'from-purple-500/10 to-pink-500/10 border-purple-500/30'
        }
    ];

    const currentModeInfo = modes.find(m => m.id === currentMode) || modes[1];

    return (
        <div className="relative">
            {/* Mode Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg bg-gradient-to-r ${currentModeInfo.color} hover:opacity-80 transition-all duration-200`}
                title={`Current mode: ${currentModeInfo.name}`}
            >
                <span className="text-lg">{currentModeInfo.icon}</span>
                <span className="text-sm font-medium text-white hidden sm:inline">
                    {currentModeInfo.name}
                </span>
                <svg
                    className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </button>

            {/* Dropdown Menu */}
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <div
                        className="fixed inset-0 z-40"
                        onClick={() => setIsOpen(false)}
                    />

                    {/* Menu */}
                    <div className="absolute right-0 mt-2 w-72 bg-[#1a1a1a] border border-white/10 rounded-lg shadow-2xl z-50 overflow-hidden">
                        <div className="p-3 border-b border-white/10">
                            <h3 className="text-sm font-semibold text-white">LLM Mode</h3>
                            <p className="text-xs text-gray-400 mt-1">Choose how queries are processed</p>
                        </div>

                        <div className="p-2">
                            {modes.map((mode) => (
                                <button
                                    key={mode.id}
                                    onClick={() => handleModeChange(mode.id)}
                                    disabled={loading}
                                    className={`w-full flex items-start gap-3 p-3 rounded-lg transition-all duration-200 ${currentMode === mode.id
                                        ? 'bg-blue-500/20 border border-blue-500/50'
                                        : 'hover:bg-white/5 border border-transparent'
                                        } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                                >
                                    <span className="text-2xl">{mode.icon}</span>
                                    <div className="flex-1 text-left">
                                        <div className="flex items-center gap-2">
                                            <span className="text-sm font-medium text-white">{mode.name}</span>
                                            {currentMode === mode.id && (
                                                <span className="px-2 py-0.5 text-xs font-medium bg-blue-500 text-white rounded">
                                                    Active
                                                </span>
                                            )}
                                        </div>
                                        <p className="text-xs text-gray-400 mt-1">{mode.description}</p>
                                    </div>
                                </button>
                            ))}
                        </div>

                        <div className="p-3 bg-white/5 border-t border-white/10">
                            <div className="flex items-start gap-2 text-xs text-gray-400">
                                <span>ℹ️</span>
                                <div>
                                    <p className="font-medium text-white mb-1">Mode Details:</p>
                                    <ul className="space-y-1">
                                        <li>💻 <strong>Local:</strong> Private, fast, no API costs</li>
                                        <li>🔄 <strong>Hybrid:</strong> Best of both worlds</li>
                                        <li>🌐 <strong>Cloud:</strong> Most capable</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
