'use client';

import { useEffect, useState } from 'react';
import { X } from 'lucide-react';

interface DocumentSummaryModalProps {
    documentId: string;
    documentName: string;
    isOpen: boolean;
    onClose: () => void;
}

export default function DocumentSummaryModal({ documentId, documentName, isOpen, onClose }: DocumentSummaryModalProps) {
    const [loading, setLoading] = useState(false);
    const [summary, setSummary] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (isOpen && documentId) {
            fetchSummary();
        }
    }, [isOpen, documentId]);

    const fetchSummary = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`http://localhost:8000/api/documents/${documentId}/summarize`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                setSummary(data);
            } else {
                setError(data.error || 'Failed to generate summary');
            }
        } catch (err: any) {
            setError(err.message || 'Network error');
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <div className="glass-card max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-white/[0.08]">
                    <div>
                        <h2 className="text-2xl font-bold text-white">Document Summary</h2>
                        <p className="text-sm text-gray-400 mt-1">{documentName}</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-lg hover:bg-white/[0.08] transition-colors"
                    >
                        <X className="w-6 h-6 text-gray-400" />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">
                    {loading ? (
                        <div className="flex flex-col items-center justify-center py-12">
                            <div className="w-12 h-12 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mb-4"></div>
                            <p className="text-gray-400">Generating AI summary...</p>
                        </div>
                    ) : error ? (
                        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                            <p className="text-red-400">{error}</p>
                            <button
                                onClick={fetchSummary}
                                className="mt-3 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-sm text-red-300 transition-colors"
                            >
                                Try Again
                            </button>
                        </div>
                    ) : summary ? (
                        <div className="space-y-6">
                            {/* Metadata */}
                            {summary.metadata && (
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div className="bg-white/[0.04] rounded-lg p-3">
                                        <div className="text-xs text-gray-400">Words</div>
                                        <div className="text-lg font-semibold text-white">{summary.metadata.word_count?.toLocaleString()}</div>
                                    </div>
                                    <div className="bg-white/[0.04] rounded-lg p-3">
                                        <div className="text-xs text-gray-400">Characters</div>
                                        <div className="text-lg font-semibold text-white">{summary.metadata.char_count?.toLocaleString()}</div>
                                    </div>
                                    <div className="bg-white/[0.04] rounded-lg p-3">
                                        <div className="text-xs text-gray-400">Chunks</div>
                                        <div className="text-lg font-semibold text-white">{summary.metadata.total_chunks}</div>
                                    </div>
                                    <div className="bg-white/[0.04] rounded-lg p-3">
                                        <div className="text-xs text-gray-400">Type</div>
                                        <div className="text-lg font-semibold text-white uppercase">{summary.metadata.extension?.replace('.', '')}</div>
                                    </div>
                                </div>
                            )}

                            {/* Summary */}
                            {summary.summary && (
                                <div>
                                    <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                                        <span className="w-1 h-6 bg-blue-500 rounded"></span>
                                        Summary
                                    </h3>
                                    <div className="bg-white/[0.04] rounded-lg p-4 border border-white/[0.08]">
                                        <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">{summary.summary}</p>
                                    </div>
                                </div>
                            )}

                            {/* Key Points */}
                            {summary.key_points && summary.key_points.length > 0 && (
                                <div>
                                    <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                                        <span className="w-1 h-6 bg-green-500 rounded"></span>
                                        Key Points
                                    </h3>
                                    <div className="space-y-2">
                                        {summary.key_points.map((point: string, idx: number) => (
                                            <div key={idx} className="flex items-start gap-3 bg-white/[0.04] rounded-lg p-3 border border-white/[0.05]">
                                                <div className="w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                                                    <span className="text-xs font-bold text-green-400">{idx + 1}</span>
                                                </div>
                                                <p className="text-gray-300 flex-1">{point}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Topics */}
                            {summary.topics && summary.topics.length > 0 && (
                                <div>
                                    <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                                        <span className="w-1 h-6 bg-purple-500 rounded"></span>
                                        Topics Covered
                                    </h3>
                                    <div className="flex flex-wrap gap-2">
                                        {summary.topics.map((topic: string, idx: number) => (
                                            <span
                                                key={idx}
                                                className="px-3 py-1.5 bg-purple-500/20 border border-purple-500/30 rounded-lg text-sm text-purple-300"
                                            >
                                                {topic}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : null}
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-white/[0.08] flex justify-end gap-3">
                    <button
                        onClick={onClose}
                        className="px-6 py-2 rounded-lg bg-white/[0.08] hover:bg-white/[0.12] text-white font-medium transition-colors"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
}
