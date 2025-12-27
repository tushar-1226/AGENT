'use client';

import { useState, useRef, useEffect } from 'react';
import CodeAssistant from './CodeAssistant';
import AnalyticsDashboard from './AnalyticsDashboard';

interface SplitScreenProps {
    isActive: boolean;
    onClose: () => void;
    leftContent: 'chat' | 'code' | 'analytics';
    rightContent: 'chat' | 'code' | 'analytics';
    chatComponent?: React.ReactNode;
}

export default function SplitScreen({
    isActive,
    onClose,
    leftContent,
    rightContent,
    chatComponent
}: SplitScreenProps) {
    const [dividerPosition, setDividerPosition] = useState(50); // percentage
    const [isDragging, setIsDragging] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (!isDragging || !containerRef.current) return;

            const container = containerRef.current;
            const containerRect = container.getBoundingClientRect();
            const newPosition = ((e.clientX - containerRect.left) / containerRect.width) * 100;

            // Limit between 20% and 80%
            setDividerPosition(Math.min(Math.max(newPosition, 20), 80));
        };

        const handleMouseUp = () => {
            setIsDragging(false);
        };

        if (isDragging) {
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
        }

        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isDragging]);

    if (!isActive) return null;

    const renderContent = (content: string) => {
        switch (content) {
            case 'chat':
                return chatComponent || <div className="p-8 text-gray-400">Chat component not provided</div>;
            case 'code':
                return <CodeAssistant />;
            case 'analytics':
                return <AnalyticsDashboard />;
            default:
                return null;
        }
    };

    return (
        <div className="fixed inset-0 z-50 bg-[#0a0a0a]">
            {/* Header */}
            <div className="h-16 border-b border-white/[0.08] flex items-center justify-between px-6">
                <div className="flex items-center gap-4">
                    <h2 className="text-lg font-semibold text-white">Split View</h2>
                    <div className="flex gap-2 text-sm text-gray-400">
                        <span className="px-3 py-1 rounded-lg bg-white/[0.04]">
                            {leftContent.charAt(0).toUpperCase() + leftContent.slice(1)}
                        </span>
                        <span>|</span>
                        <span className="px-3 py-1 rounded-lg bg-white/[0.04]">
                            {rightContent.charAt(0).toUpperCase() + rightContent.slice(1)}
                        </span>
                    </div>
                </div>

                <button
                    onClick={onClose}
                    className="p-2 rounded-lg hover:bg-white/[0.04] transition-colors"
                >
                    <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            {/* Split Content */}
            <div ref={containerRef} className="flex h-[calc(100vh-4rem)] relative">
                {/* Left Pane */}
                <div
                    className="overflow-y-auto scrollbar-dark p-6"
                    style={{ width: `${dividerPosition}%` }}
                >
                    {renderContent(leftContent)}
                </div>

                {/* Divider */}
                <div
                    className="w-1 bg-white/[0.08] hover:bg-blue-500/50 cursor-col-resize relative group transition-colors"
                    onMouseDown={() => setIsDragging(true)}
                >
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-8 h-12 bg-white/[0.1] group-hover:bg-blue-500/30 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                        <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l4-4 4 4m0 6l-4 4-4-4" />
                        </svg>
                    </div>
                </div>

                {/* Right Pane */}
                <div
                    className="overflow-y-auto scrollbar-dark p-6"
                    style={{ width: `${100 - dividerPosition}%` }}
                >
                    {renderContent(rightContent)}
                </div>
            </div>

            {/* Keyboard Shortcuts Hint */}
            <div className="fixed bottom-4 right-4 glass-card px-4 py-2 text-xs text-gray-400">
                <kbd className="px-2 py-1 bg-white/[0.05] rounded">Esc</kbd> to close
            </div>
        </div>
    );
}
