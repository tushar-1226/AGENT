'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import config from '@/config/api';

type WebSocketStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

interface WebSocketMessage {
    type: string;
    [key: string]: any;
}

export function useWebSocket() {
    const [status, setStatus] = useState<WebSocketStatus>('disconnected');
    const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const reconnectAttemptsRef = useRef(0);

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            return; // Already connected
        }

        try {
            setStatus('connecting');
            const ws = new WebSocket(config.endpoints.websocket);

            ws.onopen = () => {
                console.log('✅ WebSocket connected');
                setStatus('connected');
                reconnectAttemptsRef.current = 0;
            };

            ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    setLastMessage(message);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            ws.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                setStatus('error');
            };

            ws.onclose = () => {
                console.log('🔌 WebSocket disconnected');
                setStatus('disconnected');
                wsRef.current = null;

                // Attempt to reconnect with exponential backoff
                const maxAttempts = 5;
                if (reconnectAttemptsRef.current < maxAttempts) {
                    const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
                    console.log(`🔄 Reconnecting in ${delay}ms... (attempt ${reconnectAttemptsRef.current + 1}/${maxAttempts})`);

                    reconnectTimeoutRef.current = setTimeout(() => {
                        reconnectAttemptsRef.current++;
                        connect();
                    }, delay);
                }
            };

            wsRef.current = ws;
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            setStatus('error');
        }
    }, []);

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        setStatus('disconnected');
    }, []);

    const sendMessage = useCallback((message: WebSocketMessage): boolean => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            try {
                wsRef.current.send(JSON.stringify(message));
                return true;
            } catch (error) {
                console.error('Failed to send WebSocket message:', error);
                return false;
            }
        }
        return false;
    }, []);

    useEffect(() => {
        connect();

        return () => {
            disconnect();
        };
    }, [connect, disconnect]);

    return {
        status,
        lastMessage,
        sendMessage,
        connect,
        disconnect,
    };
}
