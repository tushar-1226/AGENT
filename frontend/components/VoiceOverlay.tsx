'use client';

import { useEffect, useState } from 'react';

interface VoiceOverlayProps {
    isOpen: boolean;
    transcript: string;
    onClose: () => void;
}

export default function VoiceOverlay({ isOpen, transcript, onClose }: VoiceOverlayProps) {
    const [statusText, setStatusText] = useState("I'm listening, How can I help you today?");
    const [phase, setPhase] = useState<'listening' | 'processing' | 'replying'>('listening');

    useEffect(() => {
        if (isOpen) {
            setPhase('listening');
            setStatusText("I'm listening, How can I help you today?");
        }
    }, [isOpen]);

    useEffect(() => {
        if (transcript) {
            setPhase('processing');
        } else {
            setPhase('listening');
            setStatusText("I'm listening, How can I help you today?");
        }
    }, [transcript]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-black/90 backdrop-blur-xl animate-in fade-in duration-300">
            {/* Close Button */}
            <button
                onClick={onClose}
                className="absolute top-8 right-8 p-3 rounded-full bg-white/10 hover:bg-white/20 text-white transition-colors"
            >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>

            {/* Globe Container */}
            <div className="relative w-64 h-64 mb-12">
                {/* Core Globe */}
                <div className={`absolute inset-0 rounded-full border-2 border-blue-500/50 shadow-[0_0_50px_rgba(59,130,246,0.5)] ${phase === 'listening' ? 'animate-pulse' : 'animate-spin-slow'}`}></div>

                {/* Inner Rings */}
                <div className="absolute inset-4 rounded-full border border-cyan-400/30 animate-spin-reverse-slow"></div>
                <div className="absolute inset-8 rounded-full border border-blue-300/20 animate-spin-slow"></div>

                {/* Holographic scanning effect */}
                <div className="absolute inset-0 rounded-full bg-gradient-to-t from-blue-500/0 via-blue-500/10 to-blue-500/0 animate-scan"></div>

                {/* Center Core */}
                <div className="absolute inset-0 m-auto w-32 h-32 rounded-full bg-blue-500/20 blur-xl animate-pulse"></div>

                {/* Particles/Grid Effect (CSS simulated) */}
                <div className="absolute inset-0 rounded-full opacity-50 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-500/20 to-transparent"></div>
            </div>

            {/* Status TextContainer */}
            <div className="max-w-2xl px-6 text-center space-y-6">
                <h2 className="text-3xl md:text-5xl font-light text-white tracking-tight animate-in slide-in-from-bottom-4 fade-in duration-500">
                    {transcript ? (
                        <>
                            <span className="text-blue-400">User said:</span> "{transcript}"
                        </>
                    ) : (
                        statusText
                    )}
                </h2>

                {phase === 'processing' && (
                    <p className="text-xl text-blue-200/80 animate-pulse">
                        Okay, I'm on it...
                    </p>
                )}
            </div>

            {/* Sound Wave Visualization (Fake) */}
            <div className="absolute bottom-20 left-0 right-0 flex justify-center items-end gap-1 h-16">
                {[...Array(20)].map((_, i) => (
                    <div
                        key={i}
                        className={`w-1 bg-blue-500/50 rounded-full transition-all duration-75 ${phase === 'listening' ? 'animate-wave' : 'h-1'}`}
                        style={{
                            animationDelay: `${i * 0.05}s`,
                            height: phase === 'listening' ? `${Math.random() * 100}%` : '4px'
                        }}
                    ></div>
                ))}
            </div>
        </div>
    );
}
