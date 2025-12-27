'use client';

import { useState, useEffect, useRef } from 'react';
import VoiceControl from './VoiceControl';
import FileUpload from './FileUpload';
import MarkdownRenderer from './MarkdownRenderer';
import config from '@/config/api';

interface Message {
    id: string;
    type: 'user' | 'gemini';
    content: string;
    timestamp: Date;
    used_model?: 'local' | 'cloud';
    complexity?: 'simple' | 'medium' | 'complex';
}

interface Model {
    id: string;
    name: string;
    description: string;
    size: string;
    type: string;
    icon: string;
    installed: boolean;
    active: boolean;
}

interface HeroSectionProps {
    onSendCommand: (command: string) => void;
    isProcessing?: boolean;
    response?: string;
    isListening?: boolean;
    isSpeaking?: boolean;
    onToggleListening?: () => void;
    voiceSupported?: boolean;
    onFileAnalyzed?: (analysis: string, fileInfo: any) => void;
    onModelChange?: (model: Model | null) => void;
}

export default function HeroSection({
    onSendCommand,
    isProcessing = false,
    response = '',
    isListening = false,
    isSpeaking = false,
    onToggleListening = () => { },
    voiceSupported = false,
    onFileAnalyzed = () => { },
    onModelChange = () => { }
}: HeroSectionProps) {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState<Message[]>([]);
    const [lastUserMessage, setLastUserMessage] = useState('');
    const [showWelcome, setShowWelcome] = useState(true);
    const [models, setModels] = useState<Model[]>([]);
    const [currentModel, setCurrentModel] = useState<Model | null>(null);
    const [showModelSelector, setShowModelSelector] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLTextAreaElement>(null);
    const modelSelectorRef = useRef<HTMLDivElement>(null);

    // Fetch available models on mount
    useEffect(() => {
        fetchModels();
    }, []);

    // Close model selector when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (modelSelectorRef.current && !modelSelectorRef.current.contains(event.target as Node)) {
                setShowModelSelector(false);
            }
        };

        if (showModelSelector) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [showModelSelector]);

    // Scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Add Gemini response when it arrives
    useEffect(() => {
        if (response && lastUserMessage) {
            setMessages(prev => [
                ...prev,
                {
                    id: Date.now().toString(),
                    type: 'gemini',
                    content: response,
                    timestamp: new Date()
                }
            ]);
            setLastUserMessage('');
            setShowWelcome(false);
        }
    }, [response]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (input.trim() && !isProcessing) {
            // Add user message
            const userMessage: Message = {
                id: Date.now().toString(),
                type: 'user',
                content: input,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, userMessage]);
            setLastUserMessage(input);
            setShowWelcome(false);

            onSendCommand(input);
            setInput('');
        }
    };

    const fetchModels = async () => {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/local-llm/available-models`);
            const data = await response.json();

            if (data.success) {
                setModels(data.models);
                // Set current active model
                const activeModel = data.models.find((m: Model) => m.active);
                if (activeModel) {
                    setCurrentModel(activeModel);
                    onModelChange(activeModel);
                }
            }
        } catch (error) {
            console.error('Error fetching models:', error);
            window.dispatchEvent(new CustomEvent('showToast', {
                detail: {
                    message: 'Failed to fetch models. Check backend connection.',
                    type: 'error'
                }
            }));
        }
    };

    const selectModel = async (modelId: string) => {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/local-llm/select-model`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model_id: modelId })
            });

            const data = await response.json();

            if (data.success) {
                setCurrentModel(data.model);
                onModelChange(data.model);
                // Refresh models list to update active status
                await fetchModels();
                setShowModelSelector(false);

                // Show success toast
                window.dispatchEvent(new CustomEvent('showToast', {
                    detail: {
                        message: `Switched to ${data.model.name}`,
                        type: 'success'
                    }
                }));
            } else {
                // Show error toast
                window.dispatchEvent(new CustomEvent('showToast', {
                    detail: {
                        message: data.error || 'Failed to select model',
                        type: 'error'
                    }
                }));
            }
        } catch (error) {
            console.error('Error selecting model:', error);
            window.dispatchEvent(new CustomEvent('showToast', {
                detail: {
                    message: 'Network error. Please check if backend is running.',
                    type: 'error'
                }
            }));
        }
    };

    const handleQuickAction = (action: string) => {
        setInput(action);
        inputRef.current?.focus();
    };

    const clearConversation = () => {
        setMessages([]);
        setInput('');
        setShowWelcome(true);
        setLastUserMessage('');
    };

    const quickActions = [
        'Create image',
        'Create video',
        'Write anything',
        'Help me learn',
        'Boost my day'
    ];

    return (
        <div className="flex-1 flex flex-col h-full">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto scrollbar-dark">
                {showWelcome && messages.length === 0 ? (
                    /* Welcome Screen - Gemini Style */
                    <div className="flex flex-col items-center justify-center min-h-[70vh] px-6">
                        {/* Greeting */}
                        <div className="mb-12 text-center">
                            <div className="flex items-center justify-center gap-2 mb-4">
                                <svg className="w-6 h-6 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                                </svg>
                                <h1 className="text-3xl font-normal text-gray-300">
                                    Hi Tushar
                                </h1>
                            </div>
                            <p className="text-4xl font-light text-white">
                                Fast is now powered by 3 Flash. Try it
                                <svg className="inline-block w-8 h-8 ml-2 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                                </svg>
                            </p>
                        </div>

                        {/* Search Input - Large Centered */}
                        <div className="w-full max-w-3xl mb-8">
                            <form onSubmit={handleSubmit} className="relative">
                                <div className="relative rounded-full bg-[#1e1e1e] border border-gray-700 hover:border-gray-600 focus-within:border-gray-500 transition-all">
                                    <textarea
                                        ref={inputRef}
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        onKeyDown={(e) => {
                                            if (e.key === 'Enter' && !e.shiftKey) {
                                                e.preventDefault();
                                                handleSubmit(e);
                                            }
                                        }}
                                        placeholder="Ask F.R.I.D.A.Y. 3"
                                        className="w-full px-6 py-4 pr-32 bg-transparent text-white text-base resize-none focus:outline-none placeholder-gray-500"
                                        rows={1}
                                        style={{ maxHeight: '200px' }}
                                    />

                                    {/* Right side controls */}
                                    <div className="absolute right-3 bottom-3 flex items-center gap-2">
                                        {/* Model Selector */}
                                        <div className="relative" ref={modelSelectorRef}>
                                            <button
                                                type="button"
                                                onClick={() => setShowModelSelector(!showModelSelector)}
                                                className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-white/5 transition-colors text-gray-400 hover:text-white border border-gray-700 hover:border-gray-600"
                                                title="Select AI Model"
                                            >
                                                <span className="text-sm">{currentModel?.icon || '🤖'}</span>
                                                <span className="text-xs font-medium">{currentModel?.name || 'Select Model'}</span>
                                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                                </svg>
                                            </button>

                                            {/* Dropdown Menu */}
                                            {showModelSelector && (
                                                <div className="absolute bottom-full right-0 mb-2 w-80 max-h-96 overflow-y-auto bg-[#1e1e1e] border border-gray-700 rounded-lg shadow-2xl z-50 scrollbar-dark">
                                                    <div className="p-3 border-b border-gray-700">
                                                        <h3 className="text-sm font-semibold text-white">Select AI Model</h3>
                                                        <p className="text-xs text-gray-400 mt-1">Choose your preferred language model</p>
                                                    </div>
                                                    <div className="p-2">
                                                        {models.length === 0 ? (
                                                            <div className="text-center py-8 text-gray-400 text-sm">
                                                                <p>No models available</p>
                                                                <p className="text-xs mt-2">Install Ollama to use local models</p>
                                                            </div>
                                                        ) : (
                                                            models.map((model) => (
                                                                <button
                                                                    key={model.id}
                                                                    onClick={() => selectModel(model.id)}
                                                                    className={`w-full text-left p-3 rounded-lg transition-all mb-2 ${model.active
                                                                        ? 'bg-blue-600/20 border border-blue-500/50'
                                                                        : 'hover:bg-white/5 border border-transparent'
                                                                        }`}
                                                                >
                                                                    <div className="flex items-start gap-3">
                                                                        <span className="text-2xl">{model.icon}</span>
                                                                        <div className="flex-1 min-w-0">
                                                                            <div className="flex items-center gap-2">
                                                                                <h4 className="text-sm font-medium text-white truncate">
                                                                                    {model.name}
                                                                                </h4>
                                                                                {model.active && (
                                                                                    <span className="flex-shrink-0 px-2 py-0.5 text-xs bg-blue-500 text-white rounded-full">
                                                                                        Active
                                                                                    </span>
                                                                                )}
                                                                                {!model.installed && (
                                                                                    <span className="flex-shrink-0 px-2 py-0.5 text-xs bg-yellow-500/20 text-yellow-400 rounded-full border border-yellow-500/30">
                                                                                        Not Installed
                                                                                    </span>
                                                                                )}
                                                                            </div>
                                                                            <p className="text-xs text-gray-400 mt-1 line-clamp-2">
                                                                                {model.description}
                                                                            </p>
                                                                            <div className="flex items-center gap-3 mt-2">
                                                                                <span className="text-xs text-gray-500">
                                                                                    {model.size}
                                                                                </span>
                                                                                <span className={`text-xs px-2 py-0.5 rounded ${model.type === 'coding'
                                                                                    ? 'bg-purple-500/20 text-purple-300'
                                                                                    : 'bg-green-500/20 text-green-300'
                                                                                    }`}>
                                                                                    {model.type}
                                                                                </span>
                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                </button>
                                                            ))
                                                        )}
                                                    </div>
                                                </div>
                                            )}
                                        </div>

                                        {/* Voice Control */}
                                        {voiceSupported && (
                                            <button
                                                type="button"
                                                onClick={onToggleListening}
                                                className={`p-2 rounded-lg transition-colors ${isListening
                                                    ? 'bg-red-500 text-white'
                                                    : 'hover:bg-white/5 text-gray-400 hover:text-white'
                                                    }`}
                                                title="Voice input"
                                            >
                                                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                                                </svg>
                                            </button>
                                        )}

                                        {/* Submit Button */}
                                        <button
                                            type="submit"
                                            disabled={!input.trim() || isProcessing}
                                            className="p-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed transition-colors text-white"
                                        >
                                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            </form>
                        </div>

                        {/* Quick Action Chips */}
                        <div className="flex flex-wrap gap-3 justify-center max-w-2xl">
                            {quickActions.map((action, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => handleQuickAction(action)}
                                    className="px-5 py-2.5 rounded-full bg-[#1e1e1e] hover:bg-[#2a2a2a] border border-gray-700 hover:border-gray-600 text-gray-300 hover:text-white text-sm transition-all"
                                >
                                    {action}
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    /* Chat Messages */
                    <div className="max-w-4xl mx-auto px-6 py-8 space-y-8">
                        {/* Clear Conversation Button */}
                        <div className="flex justify-end mb-4">
                            <button
                                onClick={clearConversation}
                                className="group flex items-center gap-2 px-4 py-2 rounded-full bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 hover:border-red-500/50 transition-all"
                                title="Clear conversation"
                            >
                                <svg className="w-4 h-4 text-red-400 group-hover:text-red-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                                <span className="text-sm text-red-400 group-hover:text-red-300 font-medium">Clear Chat</span>
                            </button>
                        </div>

                        {messages.map((message) => (
                            <div key={message.id} className="space-y-4">
                                {message.type === 'user' ? (
                                    <div className="flex justify-end">
                                        <div className="max-w-[80%] bg-blue-600 text-white rounded-2xl px-5 py-3">
                                            <p className="text-sm leading-relaxed">{message.content}</p>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="flex gap-4">
                                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                                            <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                                                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                                            </svg>
                                        </div>
                                        <div className="flex-1 max-w-[80%]">
                                            {/* Model Badge for AI responses */}
                                            {message.used_model && (
                                                <div className="flex items-center gap-2 mb-2">
                                                    <span className={`px-2 py-0.5 text-xs font-medium rounded ${message.used_model === 'local'
                                                        ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                                                        : 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                                                        }`}>
                                                        {message.used_model === 'local' ? '💻 Local' : '🌐 Cloud'}
                                                    </span>
                                                    {message.complexity && (
                                                        <span className="px-2 py-0.5 text-xs text-gray-400 bg-white/5 rounded">
                                                            {message.complexity}
                                                        </span>
                                                    )}
                                                </div>
                                            )}
                                            <MarkdownRenderer content={message.content} />
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}

                        {isProcessing && (
                            <div className="flex gap-4">
                                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                                        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                                    </svg>
                                </div>
                                <div className="flex gap-1">
                                    <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                    <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                    <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                )}
            </div>

            {/* Bottom Input (when chatting) */}
            {!showWelcome && messages.length > 0 && (
                <div className="border-t border-gray-800 bg-black/40 backdrop-blur-sm">
                    <div className="max-w-4xl mx-auto px-6 py-4">
                        <form onSubmit={handleSubmit} className="relative">
                            <div className="relative rounded-2xl bg-[#1e1e1e] border border-gray-700 hover:border-gray-600 focus-within:border-gray-500 transition-all">
                                <textarea
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter' && !e.shiftKey) {
                                            e.preventDefault();
                                            handleSubmit(e);
                                        }
                                    }}
                                    placeholder="Ask a follow-up..."
                                    className="w-full px-5 py-3 pr-24 bg-transparent text-white text-sm resize-none focus:outline-none placeholder-gray-500"
                                    rows={1}
                                    style={{ maxHeight: '150px' }}
                                />

                                <div className="absolute right-2 bottom-2 flex items-center gap-1">
                                    {voiceSupported && (
                                        <button
                                            type="button"
                                            onClick={onToggleListening}
                                            className={`p-2 rounded-lg transition-colors ${isListening
                                                ? 'bg-red-500 text-white'
                                                : 'hover:bg-white/5 text-gray-400 hover:text-white'
                                                }`}
                                        >
                                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                                            </svg>
                                        </button>
                                    )}
                                    <button
                                        type="submit"
                                        disabled={!input.trim() || isProcessing}
                                        className="p-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed transition-colors text-white"
                                    >
                                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Hidden components for functionality */}
            <div className="hidden">
                <FileUpload onFileAnalyzed={onFileAnalyzed} />
            </div>
        </div>
    );
}
