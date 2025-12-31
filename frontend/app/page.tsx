'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import Header from '@/components/Header';
import HeroSection from '@/components/HeroSection';
import EnhancedSidebar from '@/components/EnhancedSidebar';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useVoice } from '@/hooks/useVoice';
import { useSession } from '@/hooks/useSession';
import config from '@/config/api';

// Lazy load modal components to reduce initial bundle size
const SystemStatsModal = dynamic(() => import('@/components/SystemStatsModal'), {
    ssr: false,
    loading: () => null
});
const ProductivityHub = dynamic(() => import('@/components/ProductivityHub'), {
    ssr: false,
    loading: () => null
});
const AnalyticsDashboard = dynamic(() => import('@/components/AnalyticsDashboard'), {
    ssr: false,
    loading: () => null
});
const CodeAssistant = dynamic(() => import('@/components/CodeAssistant'), {
    ssr: false,
    loading: () => null
});
const SplitScreen = dynamic(() => import('@/components/SplitScreen'), {
    ssr: false,
    loading: () => null
});
const DocsModal = dynamic(() => import('@/components/DocsModal'), {
    ssr: false,
    loading: () => null
});

export default function Home() {
    const { status, lastMessage, sendMessage } = useWebSocket();
    const [commandResponse, setCommandResponse] = useState<string>('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [systemStatsOpen, setSystemStatsOpen] = useState(false);
    const [productivityOpen, setProductivityOpen] = useState(false);
    const [analyticsOpen, setAnalyticsOpen] = useState(false);
    const [codeAssistantOpen, setCodeAssistantOpen] = useState(false);
    const [splitScreenOpen, setSplitScreenOpen] = useState(false);
    const [docsOpen, setDocsOpen] = useState(false);
    const [currentModel, setCurrentModel] = useState<{ id: string; name: string; icon: string } | null>(null);

    // Voice integration
    const {
        isListening,
        isSupported: voiceSupported,
        transcript,
        startListening,
        stopListening,
        speak,
        isSpeaking,
        timeRemaining
    } = useVoice();

    // Session management
    const {
        sessions,
        currentSession,
        messages,
        createSession,
        loadSession,
        deleteSession,
        renameSession,
        addMessage
    } = useSession();

    // Handle incoming WebSocket messages
    useEffect(() => {
        if (lastMessage) {
            console.log(' Received:', lastMessage);

            if (lastMessage.type === 'command_result') {
                const response = lastMessage.result?.response || 'Command executed';
                setCommandResponse(response);
                setIsProcessing(false);

                // Speak response if voice is enabled
                if (voiceSupported) {
                    speak(response);
                }

                // Save to session
                addMessage('gemini', response);
            } else if (lastMessage.type === 'connected') {
                console.log(' Connected to backend:', lastMessage.message);
            }
        }
    }, [lastMessage, voiceSupported, speak, addMessage]);

    // Handle voice transcript
    useEffect(() => {
        if (transcript && !isListening) {
            console.log('Processing voice command:', transcript);
            // Auto-send voice command
            sendCommand(transcript);
        }
    }, [transcript, isListening]);

    const sendCommand = async (commandText: string) => {
        if (!commandText.trim()) return;

        setIsProcessing(true);
        setCommandResponse('');

        // Save user message to session
        await addMessage('user', commandText);

        try {
            // Try WebSocket first
            if (status === 'connected') {
                const sent = sendMessage({
                    type: 'command',
                    text: commandText,
                });

                if (sent) {
                    console.log(' Sent via WebSocket:', commandText);
                    return;
                }
            }

            // Fallback to HTTP API
            console.log(' Using HTTP API...');
            const response = await fetch(config.endpoints.command, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: commandText }),
            });

            const result = await response.json();
            console.log(' Command result:', result);
            const responseText = result.response || 'Command executed';
            setCommandResponse(responseText);
            setIsProcessing(false);

            // Speak response
            if (voiceSupported) {
                speak(responseText);
            }

            // Save response to session
            await addMessage('gemini', responseText);
        } catch (error) {
            console.error(' Error sending command:', error);
            const errorMsg = 'Failed to execute command. Is the backend running?';
            setCommandResponse(errorMsg);
            setIsProcessing(false);

            await addMessage('gemini', errorMsg);
        }
    };

    const handleFileAnalyzed = async (analysis: string, fileInfo: any) => {
        // Add file analysis to chat
        const message = ` File: ${fileInfo.fileName}\n\n${analysis}`;
        await addMessage('gemini', message, { fileInfo });
        setCommandResponse(analysis);

        // Speak analysis
        if (voiceSupported) {
            speak(analysis);
        }
    };

    const handlePromptSelect = (prompt: string) => {
        sendCommand(prompt);
    };

    const toggleVoiceListening = () => {
        if (isListening) {
            stopListening();
        } else {
            startListening();
        }
    };

    return (
        <div className="min-h-screen bg-[#0a0a0a]">
            {/* Enhanced Sidebar with Tabs */}
            <EnhancedSidebar
                sessions={sessions}
                currentSessionId={currentSession?.id || null}
                onSelectSession={loadSession}
                onCreateSession={() => createSession()}
                onDeleteSession={deleteSession}
                onRenameSession={renameSession}
                isOpen={sidebarOpen}
                onToggle={() => setSidebarOpen(!sidebarOpen)}
                onSelectPrompt={handlePromptSelect}
            />

            <Header
                connectionStatus={status}
                currentModel={currentModel}
            />

            {/* System Stats Modal */}
            <SystemStatsModal
                isOpen={systemStatsOpen}
                onClose={() => setSystemStatsOpen(false)}
            />

            {/* Productivity Hub Modal */}
            <ProductivityHub
                isOpen={productivityOpen}
                onClose={() => setProductivityOpen(false)}
            />

            {/* Analytics Modal */}
            {analyticsOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" onClick={() => setAnalyticsOpen(false)}>
                    <div className="glass-card w-full max-w-6xl max-h-[90vh] overflow-y-auto p-6 scrollbar-dark" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-2xl font-bold text-white">Analytics</h2>
                            <button onClick={() => setAnalyticsOpen(false)} className="p-2 rounded-lg hover:bg-white/[0.04]">
                                <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                        <AnalyticsDashboard />
                    </div>
                </div>
            )}

            {/* Code Assistant Modal */}
            {codeAssistantOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" onClick={() => setCodeAssistantOpen(false)}>
                    <div className="glass-card w-full max-w-6xl max-h-[90vh] overflow-y-auto p-6 scrollbar-dark" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-2xl font-bold text-white">Code Assistant</h2>
                            <button onClick={() => setCodeAssistantOpen(false)} className="p-2 rounded-lg hover:bg-white/[0.04]">
                                <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                        <CodeAssistant />
                    </div>
                </div>
            )}

            {/* Documentation Modal */}
            <DocsModal
                isOpen={docsOpen}
                onClose={() => setDocsOpen(false)}
            />

            {/* Split Screen */}
            <SplitScreen
                isActive={splitScreenOpen}
                onClose={() => setSplitScreenOpen(false)}
                leftContent="chat"
                rightContent="code"
                chatComponent={
                    <HeroSection
                        onSendCommand={sendCommand}
                        response={commandResponse}
                        isProcessing={isProcessing}
                        voiceSupported={voiceSupported}
                        isListening={isListening}
                        isSpeaking={isSpeaking}
                        onToggleListening={toggleVoiceListening}
                        onFileAnalyzed={handleFileAnalyzed}
                        timeRemaining={timeRemaining}
                    />
                }
            />

            <main className="flex-1 flex flex-col overflow-hidden">
                <HeroSection
                    onSendCommand={sendCommand}
                    isProcessing={isProcessing}
                    response={commandResponse}
                    isListening={isListening}
                    isSpeaking={isSpeaking}
                    transcript={transcript}
                    onToggleListening={toggleVoiceListening}
                    voiceSupported={voiceSupported}
                    onFileAnalyzed={handleFileAnalyzed}
                    onModelChange={setCurrentModel}
                    timeRemaining={timeRemaining}
                />
            </main>

            {/* Connection Status Indicator */}
            {status !== 'connected' && (
                <div className="fixed bottom-6 right-6 z-50">
                    <div className="glass-card px-5 py-3 border-yellow-500/30 bg-yellow-500/5">
                        <div className="flex items-center gap-3">
                            <div className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse" />
                            <span className="text-sm text-yellow-200 font-medium">
                                {status === 'connecting' ? 'Connecting to backend...' :
                                    status === 'error' ? 'Backend connection failed' :
                                        'Backend disconnected'}
                            </span>
                        </div>
                    </div>
                </div>
            )}

            {/* Voice Status Indicator */}
            {isListening && (
                <div className="fixed bottom-6 left-6 z-50">
                    <div className="glass-card px-5 py-3 border-red-500/30 bg-red-500/10">
                        <div className="flex items-center gap-3">
                            <div className="w-2 h-2 rounded-full bg-red-400 animate-pulse" />
                            <span className="text-sm text-red-200 font-medium">
                                Listening...
                            </span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
