'use client';

import { useState } from 'react';
import PomodoroTimer from './PomodoroTimer';
import QuickCalculator from './QuickCalculator';
import TaskManager from './TaskManager';
import EnhancedDailyBriefing from './EnhancedDailyBriefing';

interface ProductivityHubProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function ProductivityHub({ isOpen, onClose }: ProductivityHubProps) {
    const [activeTab, setActiveTab] = useState<'pomodoro' | 'calculator' | 'tasks' | 'briefing'>('tasks');

    if (!isOpen) return null;

    return (
        <>
            {/* Overlay */}
            <div
                className="fixed inset-0 bg-black/60 z-50 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
                <div
                    className="glass-card w-full max-w-2xl max-h-[90vh] overflow-y-auto pointer-events-auto scrollbar-dark"
                    onClick={(e) => e.stopPropagation()}
                >
                    {/* Header */}
                    <div className="flex items-center justify-between p-6 border-b border-white/[0.08]">
                        <h2 className="text-2xl font-bold text-white">Productivity Tools</h2>
                        <button
                            onClick={onClose}
                            className="p-2 rounded-lg hover:bg-white/[0.04] transition-colors"
                        >
                            <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    {/* Tabs */}
                    <div className="flex border-b border-white/[0.08]">
                        <button
                            onClick={() => setActiveTab('tasks')}
                            className={`flex-1 px-4 py-3 text-sm font-semibold transition-colors ${activeTab === 'tasks'
                                ? 'text-white border-b-2 border-purple-500'
                                : 'text-gray-400 hover:text-gray-300'
                                }`}
                        >
                            Tasks
                        </button>
                        <button
                            onClick={() => setActiveTab('pomodoro')}
                            className={`flex-1 px-4 py-3 text-sm font-semibold transition-colors ${activeTab === 'pomodoro'
                                ? 'text-white border-b-2 border-red-500'
                                : 'text-gray-400 hover:text-gray-300'
                                }`}
                        >
                            🍅 Pomodoro
                        </button>
                        <button
                            onClick={() => setActiveTab('calculator')}
                            className={`flex-1 px-4 py-3 text-sm font-semibold transition-colors ${activeTab === 'calculator'
                                ? 'text-white border-b-2 border-blue-500'
                                : 'text-gray-400 hover:text-gray-300'
                                }`}
                        >
                            🔢 Calculator
                        </button>
                        <button
                            onClick={() => setActiveTab('briefing')}
                            className={`flex-1 px-4 py-3 text-sm font-semibold transition-colors ${activeTab === 'briefing'
                                ? 'text-white border-b-2 border-green-500'
                                : 'text-gray-400 hover:text-gray-300'
                                }`}
                        >
                            Briefing
                        </button>
                    </div>

                    {/* Content */}
                    <div className="p-6">
                        {activeTab === 'tasks' && <TaskManager />}
                        {activeTab === 'pomodoro' && <PomodoroTimer />}
                        {activeTab === 'calculator' && <QuickCalculator />}
                        {activeTab === 'briefing' && <EnhancedDailyBriefing />}
                    </div>
                </div>
            </div>
        </>
    );
}
