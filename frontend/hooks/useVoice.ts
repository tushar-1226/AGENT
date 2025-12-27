import { useState, useEffect, useRef, useCallback } from 'react';

interface VoiceSettings {
    enabled: boolean;
    autoPlay: boolean;
    language: string;
}

interface UseVoiceReturn {
    isListening: boolean;
    isSupported: boolean;
    transcript: string;
    startListening: () => void;
    stopListening: () => void;
    speak: (text: string) => Promise<void>;
    isSpeaking: boolean;
    settings: VoiceSettings;
    updateSettings: (settings: Partial<VoiceSettings>) => void;
    wakeWordActive: boolean;
    toggleWakeWord: () => void;
}

export function useVoice(): UseVoiceReturn {
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [isSupported, setIsSupported] = useState(false);
    const [wakeWordActive, setWakeWordActive] = useState(false);
    const [settings, setSettings] = useState<VoiceSettings>({
        enabled: true,
        autoPlay: true,
        language: 'en-US'
    });

    const recognitionRef = useRef<any>(null);
    const synthRef = useRef<SpeechSynthesis | null>(null);

    // Initialize Web Speech API
    useEffect(() => {
        if (typeof window !== 'undefined') {
            const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

            if (SpeechRecognition) {
                setIsSupported(true);
                recognitionRef.current = new SpeechRecognition();
                recognitionRef.current.continuous = false;
                recognitionRef.current.interimResults = false;
                recognitionRef.current.lang = settings.language;

                recognitionRef.current.onresult = (event: any) => {
                    const transcript = event.results[0][0].transcript;
                    setTranscript(transcript);
                };

                recognitionRef.current.onend = () => {
                    setIsListening(false);
                    // Restart if wake word mode is active
                    if (wakeWordActive && recognitionRef.current) {
                        setTimeout(() => {
                            try {
                                recognitionRef.current.start();
                            } catch (e) {
                                console.log('Wake word restart failed:', e);
                            }
                        }, 100);
                    }
                };

                recognitionRef.current.onerror = (event: any) => {
                    console.error('Speech recognition error:', event.error);
                    setIsListening(false);
                };
            }

            if (window.speechSynthesis) {
                synthRef.current = window.speechSynthesis;
            }
        }

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.stop();
            }
            if (synthRef.current) {
                synthRef.current.cancel();
            }
        };
    }, [settings.language, wakeWordActive]);

    const startListening = useCallback(() => {
        if (recognitionRef.current && !isListening) {
            setTranscript('');
            recognitionRef.current.start();
            setIsListening(true);
        }
    }, [isListening]);

    const stopListening = useCallback(() => {
        if (recognitionRef.current && isListening) {
            recognitionRef.current.stop();
            setIsListening(false);
        }
    }, [isListening]);

    const speak = useCallback(async (text: string) => {
        if (!synthRef.current || !settings.autoPlay) return;

        return new Promise<void>((resolve) => {
            // Cancel any ongoing speech
            synthRef.current!.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = settings.language;
            utterance.rate = 1.0;
            utterance.pitch = 1.0;

            utterance.onstart = () => setIsSpeaking(true);
            utterance.onend = () => {
                setIsSpeaking(false);
                resolve();
            };
            utterance.onerror = () => {
                setIsSpeaking(false);
                resolve();
            };

            synthRef.current!.speak(utterance);
        });
    }, [settings.autoPlay, settings.language]);

    const updateSettings = useCallback((newSettings: Partial<VoiceSettings>) => {
        setSettings(prev => ({ ...prev, ...newSettings }));
    }, []);

    const toggleWakeWord = useCallback(() => {
        setWakeWordActive(prev => !prev);
        if (!wakeWordActive && recognitionRef.current) {
            // Start listening for wake word
            startListening();
        } else if (recognitionRef.current) {
            // Stop wake word listening
            stopListening();
        }
    }, [wakeWordActive, startListening, stopListening]);

    return {
        isListening,
        isSupported,
        transcript,
        startListening,
        stopListening,
        speak,
        isSpeaking,
        settings,
        updateSettings,
        wakeWordActive,
        toggleWakeWord
    };
}
