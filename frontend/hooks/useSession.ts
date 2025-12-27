import { useState, useEffect, useCallback } from 'react';
import config from '@/config/api';

interface Session {
    id: string;
    name: string;
    created_at: string;
    updated_at: string;
    message_count: number;
    messages?: Message[];
}

interface Message {
    id: number;
    session_id: string;
    type: 'user' | 'gemini';
    content: string;
    timestamp: string;
    metadata?: any;
}

interface UseSessionReturn {
    sessions: Session[];
    currentSession: Session | null;
    messages: Message[];
    loading: boolean;
    error: string | null;
    createSession: (name?: string) => Promise<Session | null>;
    loadSession: (sessionId: string) => Promise<void>;
    deleteSession: (sessionId: string) => Promise<boolean>;
    renameSession: (sessionId: string, name: string) => Promise<boolean>;
    addMessage: (type: 'user' | 'gemini', content: string, metadata?: any) => Promise<void>;
    refreshSessions: () => Promise<void>;
}

export function useSession(): UseSessionReturn {
    const [sessions, setSessions] = useState<Session[]>([]);
    const [currentSession, setCurrentSession] = useState<Session | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Load all sessions on mount (deferred for better initial load performance)
    useEffect(() => {
        // Defer session loading to allow page to render first
        const timer = setTimeout(() => {
            refreshSessions();
        }, 1000);

        return () => clearTimeout(timer);
    }, []);

    const refreshSessions = useCallback(async () => {
        const abortController = new AbortController();

        try {
            setLoading(true);
            const response = await fetch(`${config.apiBaseUrl}/api/sessions`, {
                signal: abortController.signal
            });
            const data = await response.json();

            if (data.success) {
                setSessions(data.sessions);
                // Don't auto-load first session to reduce initial API calls
                // User can manually select a session when needed
            }
        } catch (err: any) {
            if (err.name === 'AbortError') {
                console.log('Session fetch aborted');
                return;
            }
            setError('Failed to load sessions');
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, []);

    const createSession = useCallback(async (name?: string): Promise<Session | null> => {
        try {
            setLoading(true);
            const response = await fetch(`${config.apiBaseUrl}/api/sessions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });

            const data = await response.json();

            if (data.success) {
                const newSession = data.session;
                setSessions(prev => [newSession, ...prev]);
                setCurrentSession(newSession);
                setMessages([]);

                // Store in localStorage
                localStorage.setItem('friday_current_session', newSession.id);

                return newSession;
            }

            return null;
        } catch (err: any) {
            setError('Failed to create session');
            console.error(err);
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    const loadSession = useCallback(async (sessionId: string) => {
        const abortController = new AbortController();

        try {
            setLoading(true);
            const response = await fetch(`${config.apiBaseUrl}/api/sessions/${sessionId}`, {
                signal: abortController.signal
            });
            const data = await response.json();

            if (data.success) {
                setCurrentSession(data.session);
                setMessages(data.session.messages || []);

                // Store in localStorage
                localStorage.setItem('friday_current_session', sessionId);
            }
        } catch (err: any) {
            if (err.name === 'AbortError') {
                console.log('Session load aborted');
                return;
            }
            setError('Failed to load session');
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, []);

    const deleteSession = useCallback(async (sessionId: string): Promise<boolean> => {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/sessions/${sessionId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                setSessions(prev => prev.filter(s => s.id !== sessionId));

                // If deleting current session, clear it
                if (currentSession?.id === sessionId) {
                    setCurrentSession(null);
                    setMessages([]);
                    localStorage.removeItem('friday_current_session');
                }

                return true;
            }

            return false;
        } catch (err) {
            setError('Failed to delete session');
            console.error(err);
            return false;
        }
    }, [currentSession]);

    const renameSession = useCallback(async (sessionId: string, name: string): Promise<boolean> => {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/sessions/${sessionId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });

            const data = await response.json();

            if (data.success) {
                setSessions(prev => prev.map(s =>
                    s.id === sessionId ? { ...s, name } : s
                ));

                if (currentSession?.id === sessionId) {
                    setCurrentSession(prev => prev ? { ...prev, name } : null);
                }

                return true;
            }

            return false;
        } catch (err) {
            setError('Failed to rename session');
            console.error(err);
            return false;
        }
    }, [currentSession]);

    const addMessage = useCallback(async (type: 'user' | 'gemini', content: string, metadata?: any) => {
        let sessionId: string;

        if (!currentSession) {
            // Create a new session if none exists
            const newSession = await createSession();
            if (!newSession) return;
            sessionId = newSession.id;
        } else {
            sessionId = currentSession.id;
        }

        try {
            const response = await fetch(`${config.apiBaseUrl}/api/sessions/${sessionId}/messages`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type, content, metadata })
            });

            const data = await response.json();

            if (data.success) {
                const newMessage = data.message;
                setMessages(prev => [...prev, newMessage]);

                // Update session message count
                setSessions(prev => prev.map(s =>
                    s.id === sessionId
                        ? { ...s, message_count: s.message_count + 1, updated_at: newMessage.timestamp }
                        : s
                ));
            }
        } catch (err) {
            console.error('Failed to add message:', err);
        }
    }, [currentSession, createSession]);

    return {
        sessions,
        currentSession,
        messages,
        loading,
        error,
        createSession,
        loadSession,
        deleteSession,
        renameSession,
        addMessage,
        refreshSessions
    };
}
