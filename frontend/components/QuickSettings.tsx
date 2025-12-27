'use client';

import { useState, useEffect } from 'react';

interface Settings {
    voiceEnabled: boolean;
    autoPlayTTS: boolean;
    wakeWordEnabled: boolean;
    theme: 'dark' | 'light';
    fontSize: 'small' | 'medium' | 'large';
    notificationsEnabled: boolean;
}

export default function QuickSettings() {
    const [settings, setSettings] = useState<Settings>({
        voiceEnabled: true,
        autoPlayTTS: true,
        wakeWordEnabled: false,
        theme: 'dark',
        fontSize: 'medium',
        notificationsEnabled: true
    });

    useEffect(() => {
        // Load from localStorage
        const saved = localStorage.getItem('friday_settings');
        if (saved) {
            try {
                setSettings(JSON.parse(saved));
            } catch (e) {
                console.error('Failed to load settings');
            }
        }
    }, []);

    const updateSetting = (key: keyof Settings, value: any) => {
        const updated = { ...settings, [key]: value };
        setSettings(updated);
        localStorage.setItem('friday_settings', JSON.stringify(updated));
    };

    return (
        <div className="p-4 space-y-4">
            <h3 className="text-sm font-semibold text-white">Quick Settings</h3>

            {/* Voice Settings */}
            <div className="space-y-3">
                <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Voice</div>

                <div className="flex items-center justify-between glass-card p-3">
                    <div>
                        <div className="text-sm text-white">Voice Input</div>
                        <div className="text-xs text-gray-500">Enable voice commands</div>
                    </div>
                    <button
                        onClick={() => updateSetting('voiceEnabled', !settings.voiceEnabled)}
                        className={`w-12 h-6 rounded-full transition-colors ${settings.voiceEnabled ? 'bg-blue-500' : 'bg-white/[0.1]'
                            }`}
                    >
                        <div
                            className={`w-5 h-5 bg-white rounded-full shadow-md transform transition-transform ${settings.voiceEnabled ? 'translate-x-6' : 'translate-x-1'
                                }`}
                        />
                    </button>
                </div>

                <div className="flex items-center justify-between glass-card p-3">
                    <div>
                        <div className="text-sm text-white">Auto-play TTS</div>
                        <div className="text-xs text-gray-500">Speak responses aloud</div>
                    </div>
                    <button
                        onClick={() => updateSetting('autoPlayTTS', !settings.autoPlayTTS)}
                        className={`w-12 h-6 rounded-full transition-colors ${settings.autoPlayTTS ? 'bg-blue-500' : 'bg-white/[0.1]'
                            }`}
                    >
                        <div
                            className={`w-5 h-5 bg-white rounded-full shadow-md transform transition-transform ${settings.autoPlayTTS ? 'translate-x-6' : 'translate-x-1'
                                }`}
                        />
                    </button>
                </div>

                <div className="flex items-center justify-between glass-card p-3">
                    <div>
                        <div className="text-sm text-white">Wake Word ("Hey Friday")</div>
                        <div className="text-xs text-gray-500">Always listening for activation</div>
                    </div>
                    <button
                        onClick={() => updateSetting('wakeWordEnabled', !settings.wakeWordEnabled)}
                        className={`w-12 h-6 rounded-full transition-colors ${settings.wakeWordEnabled ? 'bg-blue-500' : 'bg-white/[0.1]'
                            }`}
                    >
                        <div
                            className={`w-5 h-5 bg-white rounded-full shadow-md transform transition-transform ${settings.wakeWordEnabled ? 'translate-x-6' : 'translate-x-1'
                                }`}
                        />
                    </button>
                </div>
            </div>

            {/* Appearance */}
            <div className="space-y-3">
                <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Appearance</div>

                <div className="glass-card p-3">
                    <div className="text-sm text-white mb-2">Font Size</div>
                    <div className="flex gap-2">
                        {(['small', 'medium', 'large'] as const).map((size) => (
                            <button
                                key={size}
                                onClick={() => updateSetting('fontSize', size)}
                                className={`flex-1 py-2 rounded-lg text-xs font-semibold transition-all ${settings.fontSize === size
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-white/[0.04] text-gray-400 hover:bg-white/[0.08]'
                                    }`}
                            >
                                {size.charAt(0).toUpperCase() + size.slice(1)}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Notifications */}
            <div className="space-y-3">
                <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Notifications</div>

                <div className="flex items-center justify-between glass-card p-3">
                    <div>
                        <div className="text-sm text-white">Browser Notifications</div>
                        <div className="text-xs text-gray-500">Pomodoro & task reminders</div>
                    </div>
                    <button
                        onClick={() => updateSetting('notificationsEnabled', !settings.notificationsEnabled)}
                        className={`w-12 h-6 rounded-full transition-colors ${settings.notificationsEnabled ? 'bg-blue-500' : 'bg-white/[0.1]'
                            }`}
                    >
                        <div
                            className={`w-5 h-5 bg-white rounded-full shadow-md transform transition-transform ${settings.notificationsEnabled ? 'translate-x-6' : 'translate-x-1'
                                }`}
                        />
                    </button>
                </div>
            </div>

            {/* Data Management */}
            <div className="space-y-3">
                <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Data</div>

                <button
                    onClick={() => {
                        if (confirm('Clear all chat history? This cannot be undone.')) {
                            localStorage.removeItem('friday_sessions');
                            window.location.reload();
                        }
                    }}
                    className="w-full glass-card p-3 text-left hover:border-red-500/30 transition-all"
                >
                    <div className="text-sm text-red-400">Clear All Data</div>
                    <div className="text-xs text-gray-500">Remove all sessions and settings</div>
                </button>
            </div>

            {/* Local Mode */}
            <div className="space-y-3">
                <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Privacy</div>

                <div className="glass-card p-3 border-purple-500/20">
                    <div className="flex items-center justify-between mb-2">
                        <div>
                            <div className="text-sm text-white">Local-Only Mode</div>
                            <div className="text-xs text-gray-500">Use Ollama instead of cloud</div>
                        </div>
                        <div className="w-2 h-2 rounded-full bg-gray-500" title="Not configured"></div>
                    </div>
                    <div className="text-xs text-gray-400 mt-2">
                        Requires Ollama installation. See Settings → Advanced
                    </div>
                </div>
            </div>

            {/* Google Integration */}
            <div className="space-y-3">
                <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Integrations</div>

                <div className="glass-card p-3 border-blue-500/20">
                    <div className="flex items-center justify-between mb-2">
                        <div>
                            <div className="text-sm text-white">Google Calendar & Email</div>
                            <div className="text-xs text-gray-500">Connect your Google account</div>
                        </div>
                        <div className="w-2 h-2 rounded-full bg-gray-500" title="Not connected"></div>
                    </div>
                    <div className="text-xs text-gray-400 mt-2">
                        Requires OAuth setup. See documentation
                    </div>
                </div>
            </div>
        </div>
    );
}
