'use client';

import { useState, useEffect } from 'react';
import AuthModal from './AuthModal';
import ModeToggle from './ModeToggle';

type ConnectionStatus = 'connected' | 'disconnected' | 'connecting' | 'error';

interface Model {
    id: string;
    name: string;
    icon: string;
}

interface HeaderProps {
    connectionStatus?: ConnectionStatus;
    currentModel?: Model | null;
}

export default function Header({
    connectionStatus = 'disconnected',
    currentModel = null
}: HeaderProps) {
    const [showAuthModal, setShowAuthModal] = useState(false);
    const [user, setUser] = useState<{ email: string; name: string } | null>(null);

    useEffect(() => {
        // Check if user is logged in
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }
    }, []);

    const handleAuthSuccess = (userData: { email: string; name: string }) => {
        setUser(userData);
    };

    const handleLogout = () => {
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        setUser(null);
        window.dispatchEvent(new CustomEvent('showToast', {
            detail: { message: 'Logged out successfully', type: 'success' }
        }));
    };

    const getInitials = (name: string) => {
        return name
            .split(' ')
            .map(n => n[0])
            .join('')
            .toUpperCase()
            .slice(0, 2);
    };

    const statusColors = {
        connected: 'bg-emerald-500',
        connecting: 'bg-yellow-500 animate-pulse',
        disconnected: 'bg-gray-500',
        error: 'bg-red-500',
    };

    const statusText = {
        connected: 'Connected',
        connecting: 'Connecting...',
        disconnected: 'Offline',
        error: 'Error',
    };

    return (
        <header className="sticky top-0 z-50 border-b border-white/[0.06] backdrop-blur-xl bg-black/80 shadow-lg">
            <div className="max-w-7xl mx-auto px-8 py-5 flex items-center justify-between">
                {/* Left: Minimal AI Bot Icon + Title */}
                <div className="flex items-center gap-3.5">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500/90 to-blue-600/90 flex items-center justify-center shadow-lg shadow-blue-500/20">
                        <svg
                            className="w-5 h-5 text-white"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            viewBox="0 0 24 24"
                        >
                            <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
                        </svg>
                    </div>
                    <div>
                        <h1 className="text-[1.125rem] font-semibold text-white tracking-tight">
                            AI Copilot
                        </h1>
                        <div className="flex items-center gap-2 mt-0.5">
                            <div className={`w-1.5 h-1.5 rounded-full ${statusColors[connectionStatus]}`} />
                            <span className="text-xs text-gray-400">{statusText[connectionStatus]}</span>
                        </div>
                    </div>
                </div>

                {/* Center: Current Model Indicator */}
                {currentModel && (
                    <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/30">
                        <span className="text-lg">{currentModel.icon}</span>
                        <div className="flex flex-col">
                            <span className="text-xs text-gray-400 font-medium">Active Model</span>
                            <span className="text-sm text-white font-semibold">{currentModel.name}</span>
                        </div>
                    </div>
                )}

                {/* Mode Toggle */}
                <ModeToggle />

                {/* Right: User Profile/Login */}
                <div className="flex items-center gap-3">
                    {user ? (
                        <div className="flex items-center gap-3">
                            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-semibold text-xs shadow-lg shadow-purple-500/20">
                                    {getInitials(user.name)}
                                </div>
                                <span className="text-sm font-medium text-gray-300 hidden sm:inline">{user.name}</span>
                            </div>
                            <button
                                onClick={handleLogout}
                                className="px-3 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08] hover:bg-white/[0.08] hover:border-red-500/30 transition-all duration-200 text-gray-300 hover:text-red-400"
                                title="Logout"
                            >
                                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                                </svg>
                            </button>
                        </div>
                    ) : (
                        <button
                            onClick={() => setShowAuthModal(true)}
                            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08] hover:bg-white/[0.08] hover:border-blue-500/30 transition-all duration-200"
                            title="Login"
                        >
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-semibold text-sm shadow-lg shadow-purple-500/20">
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                </svg>
                            </div>
                            <span className="text-sm font-medium text-gray-300 hidden sm:inline">Login</span>
                        </button>
                    )}
                </div>
            </div>

            {/* Auth Modal */}
            <AuthModal
                isOpen={showAuthModal}
                onClose={() => setShowAuthModal(false)}
                onAuthSuccess={handleAuthSuccess}
            />
        </header>
    );
}
