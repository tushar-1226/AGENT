'use client';

import { useState } from 'react';

interface Session {
    id: string;
    name: string;
    created_at: string;
    updated_at: string;
    message_count: number;
}

interface ChatSidebarProps {
    sessions: Session[];
    currentSessionId: string | null;
    onSelectSession: (sessionId: string) => void;
    onCreateSession: () => void;
    onDeleteSession: (sessionId: string) => void;
    onRenameSession: (sessionId: string, name: string) => void;
    isOpen: boolean;
    onToggle: () => void;
}

export default function ChatSidebar({
    sessions,
    currentSessionId,
    onSelectSession,
    onCreateSession,
    onDeleteSession,
    onRenameSession,
    isOpen,
    onToggle
}: ChatSidebarProps) {
    const [editingId, setEditingId] = useState<string | null>(null);
    const [editName, setEditName] = useState('');

    const handleStartEdit = (session: Session) => {
        setEditingId(session.id);
        setEditName(session.name);
    };

    const handleSaveEdit = (sessionId: string) => {
        if (editName.trim()) {
            onRenameSession(sessionId, editName.trim());
        }
        setEditingId(null);
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (days === 0) return 'Today';
        if (days === 1) return 'Yesterday';
        if (days < 7) return `${days} days ago`;
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    };

    return (
        <>
            {/* Overlay */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-40 lg:hidden"
                    onClick={onToggle}
                />
            )}

            {/* Sidebar */}
            <div
                className={`fixed top-0 left-0 h-full w-80 bg-[#0d0d0d] border-r border-white/[0.08] z-50 transform transition-transform duration-300 ${isOpen ? 'translate-x-0' : '-translate-x-full'
                    }`}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-white/[0.08]">
                    <h2 className="text-lg font-semibold text-white">Chat History</h2>
                    <button
                        onClick={onToggle}
                        className="p-2 rounded-lg hover:bg-white/[0.04] transition-colors"
                    >
                        <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* New Chat Button */}
                <div className="p-4">
                    <button
                        onClick={onCreateSession}
                        className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 text-white font-medium hover:shadow-lg hover:shadow-blue-500/30 transition-all duration-200"
                    >
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        New Chat
                    </button>
                </div>

                {/* Sessions List */}
                <div className="flex-1 overflow-y-auto scrollbar-dark px-4 pb-4">
                    {sessions.length === 0 ? (
                        <div className="text-center text-gray-500 mt-8">
                            <p className="text-sm">No chat history yet</p>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {sessions.map((session) => (
                                <div
                                    key={session.id}
                                    className={`group relative rounded-xl p-3 cursor-pointer transition-all duration-200 ${currentSessionId === session.id
                                            ? 'bg-blue-500/10 border border-blue-500/30'
                                            : 'bg-white/[0.02] border border-white/[0.05] hover:bg-white/[0.04] hover:border-white/[0.1]'
                                        }`}
                                    onClick={() => onSelectSession(session.id)}
                                >
                                    {/* Session Info */}
                                    {editingId === session.id ? (
                                        <input
                                            type="text"
                                            value={editName}
                                            onChange={(e) => setEditName(e.target.value)}
                                            onBlur={() => handleSaveEdit(session.id)}
                                            onKeyDown={(e) => {
                                                if (e.key === 'Enter') handleSaveEdit(session.id);
                                                if (e.key === 'Escape') setEditingId(null);
                                            }}
                                            className="w-full bg-transparent text-white text-sm font-medium outline-none border-b border-blue-500"
                                            autoFocus
                                            onClick={(e) => e.stopPropagation()}
                                        />
                                    ) : (
                                        <h3 className="text-sm font-medium text-white truncate pr-16">
                                            {session.name}
                                        </h3>
                                    )}

                                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                                        <span>{formatDate(session.updated_at)}</span>
                                        <span>•</span>
                                        <span>{session.message_count} messages</span>
                                    </div>

                                    {/* Actions */}
                                    <div className="absolute top-3 right-3 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleStartEdit(session);
                                            }}
                                            className="p-1.5 rounded-lg hover:bg-white/[0.1] transition-colors"
                                            title="Rename"
                                        >
                                            <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                            </svg>
                                        </button>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                onDeleteSession(session.id);
                                            }}
                                            className="p-1.5 rounded-lg hover:bg-red-500/20 transition-colors"
                                            title="Delete"
                                        >
                                            <svg className="w-4 h-4 text-gray-400 hover:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Toggle Button (when sidebar is closed) */}
            {!isOpen && (
                <button
                    onClick={onToggle}
                    className="fixed top-4 left-4 z-30 p-3 rounded-xl bg-white/[0.04] border border-white/[0.08] hover:bg-white/[0.08] hover:border-blue-500/30 transition-all duration-200"
                    title="Open chat history"
                >
                    <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                    </svg>
                </button>
            )}
        </>
    );
}
