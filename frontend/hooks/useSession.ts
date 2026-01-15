'use client';

import { useState, useEffect, useCallback } from 'react';

export interface Message {
    id: string;
    role: 'user' | 'gemini';
    content: string;
    timestamp: number;
    metadata?: any;
}

export interface Session {
    id: string;
    name: string;
    createdAt: number;
    updatedAt: number;
    messageIds: string[];
}

const STORAGE_KEYS = {
    SESSIONS: 'friday_sessions',
    MESSAGES: 'friday_messages',
    CURRENT_SESSION: 'friday_current_session',
};

export function useSession() {
    const [sessions, setSessions] = useState<Session[]>([]);
    const [currentSession, setCurrentSession] = useState<Session | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);

    // Load sessions from localStorage on mount
    useEffect(() => {
        const loadedSessions = loadSessions();
        setSessions(loadedSessions);

        const currentSessionId = localStorage.getItem(STORAGE_KEYS.CURRENT_SESSION);
        if (currentSessionId) {
            const session = loadedSessions.find(s => s.id === currentSessionId);
            if (session) {
                setCurrentSession(session);
                loadMessagesForSession(session.id);
            } else {
                // Create default session if none exists
                createDefaultSession();
            }
        } else if (loadedSessions.length === 0) {
            createDefaultSession();
        }
    }, []);

    const loadSessions = (): Session[] => {
        try {
            const stored = localStorage.getItem(STORAGE_KEYS.SESSIONS);
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error('Failed to load sessions:', error);
            return [];
        }
    };

    const saveSessions = (sessionsToSave: Session[]) => {
        try {
            localStorage.setItem(STORAGE_KEYS.SESSIONS, JSON.stringify(sessionsToSave));
        } catch (error) {
            console.error('Failed to save sessions:', error);
        }
    };

    const loadMessagesForSession = (sessionId: string) => {
        try {
            const stored = localStorage.getItem(STORAGE_KEYS.MESSAGES);
            const allMessages: Message[] = stored ? JSON.parse(stored) : [];

            const session = sessions.find(s => s.id === sessionId);
            if (session) {
                const sessionMessages = allMessages.filter(m =>
                    session.messageIds.includes(m.id)
                );
                setMessages(sessionMessages);
            }
        } catch (error) {
            console.error('Failed to load messages:', error);
            setMessages([]);
        }
    };

    const saveMessage = (message: Message) => {
        try {
            const stored = localStorage.getItem(STORAGE_KEYS.MESSAGES);
            const allMessages: Message[] = stored ? JSON.parse(stored) : [];
            allMessages.push(message);
            localStorage.setItem(STORAGE_KEYS.MESSAGES, JSON.stringify(allMessages));
        } catch (error) {
            console.error('Failed to save message:', error);
        }
    };

    const createDefaultSession = () => {
        const newSession: Session = {
            id: `session_${Date.now()}`,
            name: 'New Chat',
            createdAt: Date.now(),
            updatedAt: Date.now(),
            messageIds: [],
        };

        const updatedSessions = [newSession];
        setSessions(updatedSessions);
        setCurrentSession(newSession);
        setMessages([]);
        saveSessions(updatedSessions);
        localStorage.setItem(STORAGE_KEYS.CURRENT_SESSION, newSession.id);
    };

    const createSession = useCallback((name?: string): Session => {
        const newSession: Session = {
            id: `session_${Date.now()}`,
            name: name || `Chat ${sessions.length + 1}`,
            createdAt: Date.now(),
            updatedAt: Date.now(),
            messageIds: [],
        };

        const updatedSessions = [...sessions, newSession];
        setSessions(updatedSessions);
        setCurrentSession(newSession);
        setMessages([]);
        saveSessions(updatedSessions);
        localStorage.setItem(STORAGE_KEYS.CURRENT_SESSION, newSession.id);

        return newSession;
    }, [sessions]);

    const loadSession = useCallback((sessionId: string) => {
        const session = sessions.find(s => s.id === sessionId);
        if (session) {
            setCurrentSession(session);
            loadMessagesForSession(sessionId);
            localStorage.setItem(STORAGE_KEYS.CURRENT_SESSION, sessionId);
        }
    }, [sessions]);

    const deleteSession = useCallback((sessionId: string) => {
        const updatedSessions = sessions.filter(s => s.id !== sessionId);
        setSessions(updatedSessions);
        saveSessions(updatedSessions);

        // Delete associated messages
        try {
            const stored = localStorage.getItem(STORAGE_KEYS.MESSAGES);
            const allMessages: Message[] = stored ? JSON.parse(stored) : [];
            const session = sessions.find(s => s.id === sessionId);

            if (session) {
                const filteredMessages = allMessages.filter(m =>
                    !session.messageIds.includes(m.id)
                );
                localStorage.setItem(STORAGE_KEYS.MESSAGES, JSON.stringify(filteredMessages));
            }
        } catch (error) {
            console.error('Failed to delete messages:', error);
        }

        // Switch to another session if deleting current
        if (currentSession?.id === sessionId) {
            if (updatedSessions.length > 0) {
                loadSession(updatedSessions[0].id);
            } else {
                createDefaultSession();
            }
        }
    }, [sessions, currentSession, loadSession]);

    const renameSession = useCallback((sessionId: string, newName: string) => {
        const updatedSessions = sessions.map(s =>
            s.id === sessionId ? { ...s, name: newName, updatedAt: Date.now() } : s
        );
        setSessions(updatedSessions);
        saveSessions(updatedSessions);

        if (currentSession?.id === sessionId) {
            setCurrentSession({ ...currentSession, name: newName });
        }
    }, [sessions, currentSession]);

    const addMessage = useCallback(async (role: 'user' | 'gemini', content: string, metadata?: any) => {
        if (!currentSession) return;

        const message: Message = {
            id: `msg_${Date.now()}_${Math.random()}`,
            role,
            content,
            timestamp: Date.now(),
            metadata,
        };

        // Save message
        saveMessage(message);

        // Update session
        const updatedSession = {
            ...currentSession,
            messageIds: [...currentSession.messageIds, message.id],
            updatedAt: Date.now(),
        };

        const updatedSessions = sessions.map(s =>
            s.id === currentSession.id ? updatedSession : s
        );

        setSessions(updatedSessions);
        setCurrentSession(updatedSession);
        setMessages([...messages, message]);
        saveSessions(updatedSessions);
    }, [currentSession, sessions, messages]);

    return {
        sessions,
        currentSession,
        messages,
        createSession,
        loadSession,
        deleteSession,
        renameSession,
        addMessage,
    };
}
