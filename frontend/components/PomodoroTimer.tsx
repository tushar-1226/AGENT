'use client';

import { useState, useEffect, useRef } from 'react';

interface PomodoroTimerProps {
    onComplete?: () => void;
}

export default function PomodoroTimer({ onComplete }: PomodoroTimerProps) {
    const [minutes, setMinutes] = useState(25);
    const [seconds, setSeconds] = useState(0);
    const [isActive, setIsActive] = useState(false);
    const [isBreak, setIsBreak] = useState(false);
    const [sessions, setSessions] = useState(0);
    const audioRef = useRef<HTMLAudioElement | null>(null);

    useEffect(() => {
        let interval: NodeJS.Timeout | null = null;

        if (isActive) {
            interval = setInterval(() => {
                if (seconds === 0) {
                    if (minutes === 0) {
                        // Timer completed
                        setIsActive(false);
                        playNotification();

                        if (isBreak) {
                            // Break finished, start work session
                            setMinutes(25);
                            setIsBreak(false);
                            setSessions(prev => prev + 1);
                        } else {
                            // Work finished, start break
                            setMinutes(sessions % 4 === 3 ? 15 : 5); // Long break every 4 sessions
                            setIsBreak(true);
                        }

                        if (onComplete) onComplete();
                    } else {
                        setMinutes(minutes - 1);
                        setSeconds(59);
                    }
                } else {
                    setSeconds(seconds - 1);
                }
            }, 1000);
        }

        return () => {
            if (interval) clearInterval(interval);
        };
    }, [isActive, minutes, seconds, isBreak, sessions, onComplete]);

    const playNotification = () => {
        // Browser notification
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('🍅 Pomodoro Timer', {
                body: isBreak ? 'Break time is over! Back to work.' : 'Great work! Time for a break.',
                icon: '/favicon.ico'
            });
        }

        // Audio beep
        if (audioRef.current) {
            audioRef.current.play().catch(e => console.log('Audio play failed:', e));
        }

        // Text-to-speech
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(
                isBreak ? 'Break time is over. Back to work!' : 'Great work! Time for a break.'
            );
            window.speechSynthesis.speak(utterance);
        }
    };

    const requestNotificationPermission = async () => {
        if ('Notification' in window && Notification.permission === 'default') {
            await Notification.requestPermission();
        }
    };

    const toggleTimer = () => {
        if (!isActive) {
            requestNotificationPermission();
        }
        setIsActive(!isActive);
    };

    const resetTimer = () => {
        setIsActive(false);
        setMinutes(25);
        setSeconds(0);
        setIsBreak(false);
    };

    const progress = isBreak
        ? ((5 * 60 - (minutes * 60 + seconds)) / (5 * 60)) * 100
        : ((25 * 60 - (minutes * 60 + seconds)) / (25 * 60)) * 100;

    return (
        <div className="glass-card p-6 border-red-500/20">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">🍅 Pomodoro Timer</h3>
                <div className="text-xs text-gray-400">
                    Session {sessions + 1} {isBreak ? '(Break)' : '(Focus)'}
                </div>
            </div>

            {/* Timer Display */}
            <div className="relative mb-6">
                {/* Circular Progress */}
                <svg className="w-48 h-48 mx-auto transform -rotate-90">
                    <circle
                        cx="96"
                        cy="96"
                        r="88"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        className="text-white/5"
                    />
                    <circle
                        cx="96"
                        cy="96"
                        r="88"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        strokeDasharray={`${2 * Math.PI * 88}`}
                        strokeDashoffset={`${2 * Math.PI * 88 * (1 - progress / 100)}`}
                        className={`transition-all ${isBreak ? 'text-green-500' : 'text-red-500'}`}
                        strokeLinecap="round"
                    />
                </svg>

                {/* Time Display */}
                <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                        <div className="text-5xl font-bold text-white tabular-nums">
                            {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
                        </div>
                        <div className={`text-sm mt-2 ${isBreak ? 'text-green-400' : 'text-red-400'}`}>
                            {isBreak ? 'Break Time' : 'Focus Time'}
                        </div>
                    </div>
                </div>
            </div>

            {/* Controls */}
            <div className="flex gap-3">
                <button
                    onClick={toggleTimer}
                    className={`flex-1 py-3 rounded-xl font-semibold transition-all ${isActive
                            ? 'bg-yellow-500 hover:bg-yellow-600 text-black'
                            : isBreak
                                ? 'bg-green-500 hover:bg-green-600 text-white'
                                : 'bg-red-500 hover:bg-red-600 text-white'
                        }`}
                >
                    {isActive ? 'Pause' : 'Start'}
                </button>
                <button
                    onClick={resetTimer}
                    className="px-6 py-3 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] text-white font-semibold transition-all"
                >
                    Reset
                </button>
            </div>

            {/* Stats */}
            <div className="mt-4 pt-4 border-t border-white/[0.08]">
                <div className="flex justify-around text-center">
                    <div>
                        <div className="text-2xl font-bold text-white">{sessions}</div>
                        <div className="text-xs text-gray-400">Completed</div>
                    </div>
                    <div>
                        <div className="text-2xl font-bold text-white">{sessions * 25}</div>
                        <div className="text-xs text-gray-400">Minutes Focused</div>
                    </div>
                </div>
            </div>

            {/* Hidden audio element */}
            <audio ref={audioRef} preload="auto">
                <source src="data:audio/wav;base64,UklGRhIAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQA=" />
            </audio>
        </div>
    );
}
