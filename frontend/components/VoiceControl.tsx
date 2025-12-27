'use client';

import { useEffect } from 'react';

interface VoiceControlProps {
    isListening: boolean;
    isSupported: boolean;
    isSpeaking: boolean;
    onToggleListening: () => void;
}

export default function VoiceControl({
    isListening,
    isSupported,
    isSpeaking,
    onToggleListening
}: VoiceControlProps) {

    if (!isSupported) {
        return null; // Hide if browser doesn't support Web Speech API
    }

    return (
        <button
            onClick={onToggleListening}
            className={`relative flex items-center justify-center w-12 h-12 rounded-xl transition-all duration-300 ${isListening
                    ? 'bg-gradient-to-br from-red-500 to-red-600 shadow-lg shadow-red-500/50'
                    : isSpeaking
                        ? 'bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg shadow-blue-500/50'
                        : 'bg-white/[0.04] border border-white/[0.08] hover:bg-white/[0.08] hover:border-blue-500/30'
                }`}
            title={isListening ? 'Stop listening' : 'Start voice input'}
        >
            {/* Microphone Icon */}
            <svg
                className={`w-6 h-6 transition-all ${isListening || isSpeaking ? 'text-white' : 'text-gray-400'
                    }`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
            >
                <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                />
            </svg>

            {/* Listening Animation */}
            {isListening && (
                <div className="absolute inset-0 rounded-xl">
                    <div className="absolute inset-0 rounded-xl bg-red-500 animate-ping opacity-20" />
                </div>
            )}

            {/* Speaking Animation */}
            {isSpeaking && (
                <div className="absolute -right-1 -top-1">
                    <div className="flex gap-0.5">
                        <div className="w-1 h-3 bg-white rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-1 h-3 bg-white rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-1 h-3 bg-white rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                </div>
            )}
        </button>
    );
}
