'use client';

import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import AuthModal from './AuthModal';

type ConnectionStatus = 'connected' | 'disconnected' | 'connecting' | 'error';

interface SidebarProps {
    isOpen: boolean;
    onToggle: () => void;
    connectionStatus?: ConnectionStatus;
    user?: { name: string; email: string } | null;
    onAuthSuccess?: (userData: { email: string; name: string }) => void;
}

export default function NavigationSidebar({
    isOpen,
    onToggle,
    connectionStatus = 'disconnected',
    user: initialUser,
    onAuthSuccess
}: SidebarProps) {
    const router = useRouter();
    const [hovering, setHovering] = useState(false);
    const [showAuthModal, setShowAuthModal] = useState(false);
    const [user, setUser] = useState(initialUser);

    useEffect(() => {
        // Check if user is logged in
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }
    }, []);

    useEffect(() => {
        setUser(initialUser);
    }, [initialUser]);

    const handleLogout = () => {
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        setUser(null);
        if (typeof window !== 'undefined') {
            window.dispatchEvent(new CustomEvent('showToast', {
                detail: { message: 'Logged out successfully', type: 'success' }
            }));
        }
    };

    const handleAuthSuccess = (userData: { email: string; name: string }) => {
        setUser(userData);
        onAuthSuccess?.(userData);
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

    const menuItems = [
        {
            icon: (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
            ),
            label: 'Home',
            route: '/'
        },
        {
            icon: (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
            ),
            label: 'Docs',
            route: '/documentation'
        },
        {
            icon: (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-3zM14 13a1 1 0 011-1h4a1  1 0 011 1v6a1 1 0 01-1 1h-4a1 1 0 01-1-1v-6z" />
                </svg>
            ),
            label: 'Dashboard',
            route: '/dashboard'
        },
        {
            icon: (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
            ),
            label: 'System',
            route: '/system'
        },
        {
            icon: (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
            ),
            label: 'Tools',
            route: '/quick-actions'
        },
        {
            icon: (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
            ),
            label: 'Analytics',
            route: '/analytics'
        },
        {
            icon: (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
            ),
            label: 'Code',
            route: '/code'
        },
        {
            icon: (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
            ),
            label: 'Chat',
            route: '/chat-history'
        },
        {
            icon: (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
            ),
            label: 'Projects',
            route: '/projects'
        },
    ];

    return (
        <>
            {/* Modern Rail Sidebar - Always Visible */}
            <aside
                onMouseEnter={() => setHovering(true)}
                onMouseLeave={() => setHovering(false)}
                className={`fixed left-0 top-0 h-full bg-[#0a0a0a]/95 backdrop-blur-md border-r border-gray-800/50 z-50 transition-all duration-300 ease-in-out ${hovering ? 'w-56' : 'w-20'
                    }`}
            >
                {/* Logo + Connection Status Section */}
                <div className={`p-4 border-b border-gray-800/50 ${hovering ? '' : 'flex flex-col items-center gap-3'}`}>
                    {/* Logo */}
                    <div className={`flex items-center gap-3 mb-2 ${hovering ? 'justify-start' : 'justify-center'}`}>
                        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center relative">
                            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                            </svg>
                            {/* Status dot on logo */}
                            <div className={`absolute -top-1 -right-1 w-3 h-3 rounded-full ${statusColors[connectionStatus]} border-2 border-[#0a0a0a]`} />
                        </div>
                        <span
                            className={`text-lg font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent transition-all duration-300 ${hovering ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4 w-0'
                                }`}
                        >
                            F.R.I.D.A.Y.
                        </span>
                    </div>

                    {/* Connection Status (when expanded) */}
                    {hovering && (
                        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-gray-700/50">
                            <div className={`w-2 h-2 rounded-full ${statusColors[connectionStatus]}`} />
                            <span className="text-xs text-gray-400">{statusText[connectionStatus]}</span>
                        </div>
                    )}
                </div>

                {/* Navigation Items */}
                <nav className="px-2 py-3 space-y-1 overflow-y-auto scrollbar-dark" style={{ maxHeight: 'calc(100vh - 240px)' }}>
                    {menuItems.map((item, idx) => (
                        <button
                            key={idx}
                            onClick={() => router.push(item.route)}
                            className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg text-gray-400 hover:text-white hover:bg-gradient-to-r hover:from-blue-600/20 hover:to-purple-600/20 border border-transparent hover:border-blue-500/30 transition-all group relative ${hovering ? 'justify-start' : 'just ify-center'
                                }`}
                            title={!hovering ? item.label : undefined}
                        >
                            <span className="flex-shrink-0 text-gray-400 group-hover:text-blue-400 transition-colors">
                                {item.icon}
                            </span>
                            <span
                                className={`text-sm font-medium whitespace-nowrap transition-all duration-300 ${hovering ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4 w-0 overflow-hidden'
                                    }`}
                            >
                                {item.label}
                            </span>

                            {/* Tooltip for collapsed state */}
                            {!hovering && (
                                <div className="absolute left-full ml-2 px-3 py-1.5 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50 border border-gray-700">
                                    {item.label}
                                    <div className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-gray-900"></div>
                                </div>
                            )}
                        </button>
                    ))}
                </nav>

                {/* User Profile + Settings at Bottom */}
                <div className={`absolute bottom-0 left-0 right-0 p-2 border-t border-gray-800/50 bg-[#0a0a0a]/95`}>
                    {user ? (
                        <>
                            {/* User Profile */}
                            <div className={`flex items-center gap-3 px-3 py-2.5 rounded-lg bg-white/5 border border-gray-700/50 mb-2 ${hovering ? '' : 'justify-center'
                                }`}>
                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-semibold text-xs flex-shrink-0">
                                    {getInitials(user.name)}
                                </div>
                                {hovering && (
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium text-white truncate">{user.name}</p>
                                        <p className="text-xs text-gray-400 truncate">{user.email}</p>
                                    </div>
                                )}
                            </div>

                            {/* Logout Button (when expanded) */}
                            {hovering && (
                                <button
                                    onClick={handleLogout}
                                    className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-gray-400 hover:text-red-400 hover:bg-red-500/10 border border-transparent hover:border-red-500/30 transition-all text-sm"
                                >
                                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                                    </svg>
                                    <span>Logout</span>
                                </button>
                            )}
                        </>
                    ) : (
                        <button
                            onClick={() => setShowAuthModal(true)}
                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white transition-all ${hovering ? 'justify-start' : 'justify-center'
                                }`}
                        >
                            <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                            {hovering && <span className="text-sm font-medium">Login</span>}
                        </button>
                    )}

                    {/* Settings */}
                    <button
                        onClick={() => router.push('/settings')}
                        className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-all group relative mt-2 ${hovering ? 'justify-start' : 'justify-center'
                            }`}
                        title={!hovering ? 'Settings' : undefined}
                    >
                        <span className="flex-shrink-0">
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                        </span>
                        <span
                            className={`text-sm font-medium whitespace-nowrap transition-all duration-300 ${hovering ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4 w-0 overflow-hidden'
                                }`}
                        >
                            Settings
                        </span>

                        {/* Tooltip for collapsed state */}
                        {!hovering && (
                            <div className="absolute left-full ml-2 px-3 py-1.5 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50 border border-gray-700">
                                Settings
                                <div className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-gray-900"></div>
                            </div>
                        )}
                    </button>
                </div>

                {/* Expansion Indicator */}
                <div className={`absolute top-1/2 -translate-y-1/2 -right-3 transition-opacity duration-300 ${hovering ? 'opacity-0' : 'opacity-100'}`}>
                    <div className="w-6 h-12 bg-gradient-to-r from-transparent via-blue-500/20 to-transparent flex items-center justify-center">
                        <svg className="w-3 h-3 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                    </div>
                </div>
            </aside>

            {/* Auth Modal */}
            <AuthModal
                isOpen={showAuthModal}
                onClose={() => setShowAuthModal(false)}
                onAuthSuccess={handleAuthSuccess}
            />
        </>
    );
}
