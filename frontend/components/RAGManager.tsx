'use client';

import { useState } from 'react';
import config from '@/config/api';

export default function RAGManager() {
    const [directory, setDirectory] = useState('');
    const [loading, setLoading] = useState(false);
    const [documents, setDocuments] = useState<any[]>([]);
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<any[]>([]);
    const [stats, setStats] = useState<any>(null);

    const uploadDirectory = async () => {
        if (!directory) return;

        setLoading(true);
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/rag/upload-directory`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ directory, extensions: ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp'] })
            });
            const data = await response.json();
            if (data.success) {
                alert(`Uploaded: ${data.stats.success} files`);
                loadDocuments();
            }
        } catch (error) {
            console.error('Upload error:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadDocuments = async () => {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/rag/documents`);
            const data = await response.json();
            if (data.success) {
                setDocuments(data.documents);
            }
        } catch (error) {
            console.error('Load error:', error);
        }
    };

    const searchCode = async () => {
        if (!query) return;

        setLoading(true);
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/rag/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, n_results: 5 })
            });
            const data = await response.json();
            if (data.success) {
                setResults(data.results);
            }
        } catch (error) {
            console.error('Search error:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadStats = async () => {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/rag/stats`);
            const data = await response.json();
            setStats(data);
        } catch (error) {
            console.error('Stats error:', error);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white">RAG Document Intelligence</h2>
                <button onClick={loadStats} className="px-4 py-2 rounded-lg bg-blue-500 hover:bg-blue-600 text-white text-sm">
                    Refresh Stats
                </button>
            </div>

            {/* Stats */}
            {stats && stats.available && (
                <div className="grid grid-cols-3 gap-4">
                    <div className="glass-card p-4">
                        <div className="text-sm text-gray-400">Total Files</div>
                        <div className="text-2xl font-bold text-white">{stats.total_files}</div>
                    </div>
                    <div className="glass-card p-4">
                        <div className="text-sm text-gray-400">Total Chunks</div>
                        <div className="text-2xl font-bold text-white">{stats.total_chunks}</div>
                    </div>
                    <div className="glass-card p-4">
                        <div className="text-sm text-gray-400">Status</div>
                        <div className="text-lg font-semibold text-green-400">Ready</div>
                    </div>
                </div>
            )}

            {/* Upload */}
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Upload Codebase</h3>
                <div className="flex gap-3">
                    <input
                        type="text"
                        value={directory}
                        onChange={(e) => setDirectory(e.target.value)}
                        placeholder="/path/to/your/project"
                        className="flex-1 px-4 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white focus:outline-none focus:border-blue-500/30"
                    />
                    <button
                        onClick={uploadDirectory}
                        disabled={loading}
                        className="px-6 py-2 rounded-lg bg-blue-500 hover:bg-blue-600 text-white font-semibold disabled:opacity-50"
                    >
                        {loading ? 'Uploading...' : 'Upload'}
                    </button>
                </div>
                <p className="text-xs text-gray-500 mt-2">Supports: .py, .js, .jsx, .ts, .tsx, .java, .cpp</p>
            </div>

            {/* Search */}
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Search Codebase</h3>
                <div className="flex gap-3">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="How does authentication work?"
                        className="flex-1 px-4 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white focus:outline-none focus:border-blue-500/30"
                        onKeyPress={(e) => e.key === 'Enter' && searchCode()}
                    />
                    <button
                        onClick={searchCode}
                        disabled={loading}
                        className="px-6 py-2 rounded-lg bg-green-500 hover:bg-green-600 text-white font-semibold disabled:opacity-50"
                    >
                        Search
                    </button>
                </div>
            </div>

            {/* Results */}
            {results.length > 0 && (
                <div className="space-y-3">
                    <h3 className="text-lg font-semibold text-white">Search Results</h3>
                    {results.map((result, idx) => (
                        <div key={idx} className="glass-card p-4 border-green-500/20">
                            <div className="text-sm text-blue-400 mb-2">{result.metadata.path}</div>
                            <pre className="text-sm text-gray-300 whitespace-pre-wrap bg-white/[0.02] p-3 rounded border border-white/[0.05] overflow-x-auto">
                                {result.content}
                            </pre>
                        </div>
                    ))}
                </div>
            )}

            {/* Documents */}
            <div className="glass-card p-6">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-white">Indexed Documents</h3>
                    <button onClick={loadDocuments} className="text-sm text-blue-400 hover:text-blue-300">
                        Refresh
                    </button>
                </div>
                {documents.length > 0 ? (
                    <div className="space-y-2">
                        {documents.map((doc, idx) => (
                            <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-white/[0.02] border border-white/[0.05]">
                                <div className="flex-1">
                                    <div className="text-sm text-white">{doc.path}</div>
                                    <div className="text-xs text-gray-500">{doc.chunks} chunks • {doc.extension}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center text-gray-500 py-8">No documents indexed yet</div>
                )}
            </div>
        </div>
    );
}
