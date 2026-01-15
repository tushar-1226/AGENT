'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

export function useVoice() {
    const [isListening, setIsListening] = useState(false);
    const [isSupported, setIsSupported] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [timeRemaining, setTimeRemaining] = useState<number | null>(null);

    const recognitionRef = useRef<any>(null);
    const synthRef = useRef<SpeechSynthesis | null>(null);
    const timeoutRef = useRef<NodeJS.Timeout | null>(null);
    const intervalRef = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        // Check if browser supports Web Speech API
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        const speechSynthesis = window.speechSynthesis;

        if (SpeechRecognition && speechSynthesis) {
            setIsSupported(true);

            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onresult = (event: any) => {
                const result = event.results[0][0].transcript;
                setTranscript(result);
                setIsListening(false);
            };

            recognition.onerror = (event: any) => {
                console.error('Speech recognition error:', event.error);
                setIsListening(false);
                if (timeoutRef.current) {
                    clearTimeout(timeoutRef.current);
                }
                if (intervalRef.current) {
                    clearInterval(intervalRef.current);
                }
            };

            recognition.onend = () => {
                setIsListening(false);
                setTimeRemaining(null);
                if (timeoutRef.current) {
                    clearTimeout(timeoutRef.current);
                }
                if (intervalRef.current) {
                    clearInterval(intervalRef.current);
                }
            };

            recognitionRef.current = recognition;
            synthRef.current = speechSynthesis;
        }

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.stop();
            }
            if (synthRef.current) {
                synthRef.current.cancel();
            }
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
        };
    }, []);

    const startListening = useCallback(() => {
        if (!isSupported || !recognitionRef.current) return;

        try {
            setTranscript('');
            setIsListening(true);
            recognitionRef.current.start();

            // Auto-stop after 10 seconds
            const duration = 10000;
            const startTime = Date.now();
            setTimeRemaining(duration);

            timeoutRef.current = setTimeout(() => {
                if (recognitionRef.current) {
                    recognitionRef.current.stop();
                }
            }, duration);

            // Update time remaining every 100ms
            intervalRef.current = setInterval(() => {
                const elapsed = Date.now() - startTime;
                const remaining = Math.max(0, duration - elapsed);
                setTimeRemaining(remaining);
                if (remaining === 0 && intervalRef.current) {
                    clearInterval(intervalRef.current);
                }
            }, 100);
        } catch (error) {
            console.error('Failed to start speech recognition:', error);
            setIsListening(false);
        }
    }, [isSupported]);

    const stopListening = useCallback(() => {
        if (recognitionRef.current) {
            recognitionRef.current.stop();
        }
        setIsListening(false);
        setTimeRemaining(null);
        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
        }
        if (intervalRef.current) {
            clearInterval(intervalRef.current);
        }
    }, []);

    const speak = useCallback((text: string) => {
        if (!isSupported || !synthRef.current) return;

        // Cancel any ongoing speech
        synthRef.current.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        utterance.onstart = () => {
            setIsSpeaking(true);
        };

        utterance.onend = () => {
            setIsSpeaking(false);
        };

        utterance.onerror = () => {
            setIsSpeaking(false);
        };

        synthRef.current.speak(utterance);
    }, [isSupported]);

    const stopSpeaking = useCallback(() => {
        if (synthRef.current) {
            synthRef.current.cancel();
            setIsSpeaking(false);
        }
    }, []);

    return {
        isListening,
        isSupported,
        transcript,
        isSpeaking,
        timeRemaining,
        startListening,
        stopListening,
        speak,
        stopSpeaking,
    };
}
