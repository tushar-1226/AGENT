'use client';

import { useState, useEffect, useCallback } from 'react';
import { Upload, FileText, Trash2, Download, Sparkles, File } from 'lucide-react';
import DocumentSummaryModal from '@/components/DocumentSummaryModal';
import toast from 'react-hot-toast';

export default function FilesPage() {
    const [documents, setDocuments] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [isDragging, setIsDragging] = useState(false);
    const [selectedDoc, setSelectedDoc] = useState<{ id: string, name: string } | null>(null);

    useEffect(() => {
        loadDocuments();
    }, []);

    const loadDocuments = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/api/documents/list');
            const data = await response.json();

            if (data.success) {
                setDocuments(data.documents);
            }
        } catch (error) {
            console.error('Error loading documents:', error);
            toast.error('Failed to load documents');
        } finally {
            setLoading(false);
        }
    };

    const handleFileUpload = async (file: File) => {
        setUploading(true);

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('http://localhost:8000/api/documents/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                toast.success(`Uploaded ${file.name}`);
                loadDocuments();
            } else {
                toast.error(data.error || 'Upload failed');
            }
        } catch (error: any) {
            console.error('Upload error:', error);
            toast.error(error.message || 'Upload failed');
        } finally {
            setUploading(false);
        }
    };

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        const file = e.dataTransfer.files[0];
        if (file) {
            handleFileUpload(file);
        }
    }, []);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            handleFileUpload(file);
        }
    };

    const handleDelete = async (docId: string, filename: string) => {
        if (!confirm(`Delete "${filename}"?`)) return;

        try {
            const response = await fetch(`http://localhost:8000/api/documents/${docId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                toast.success('Document deleted');
                loadDocuments();
            } else {
                toast.error(data.error || 'Delete failed');
            }
        } catch (error) {
            console.error('Delete error:', error);
            toast.error('Delete failed');
        }
    };

    const handleDownload = (docId: string, filename: string) => {
        window.open(`http://localhost:8000/api/documents/${docId}/download`, '_blank');
    };

    const formatFileSize = (bytes: number) => {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    };

    const formatDate = (isoDate: string) => {
        const date = new Date(isoDate);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getFileIcon = (fileType: string) => {
        const color = {
            '.pdf': 'text-red-400 bg-red-500/20',
            '.docx': 'text-blue-400 bg-blue-500/20',
            '.txt': 'text-gray-400 bg-gray-500/20',
            '.md': 'text-purple-400 bg-purple-500/20',
        }[fileType] || 'text-gray-400 bg-gray-500/20';

        return (
            <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${color}`}>
                <FileText className="w-6 h-6" />
            </div>
        );
    };

    return (
        <div className="min-h-screen bg-[#0a0a0a] p-8">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-white mb-2">Documents</h1>
                    <p className="text-gray-400">Upload and analyze your documents with AI</p>
                </div>

                {/* Upload Area */}
                <div
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    className={`glass-card p-8 mb-8 transition-all duration-300 ${isDragging
                        ? 'border-2 border-blue-500 bg-blue-500/10'
                        : 'border-2 border-dashed border-white/[0.08]'
                        }`}
                >
                    <input
                        type="file"
                        id="file-upload"
                        className="hidden"
                        accept=".pdf,.txt,.md,.docx"
                        onChange={handleFileSelect}
                        disabled={uploading}
                    />

                    <label
                        htmlFor="file-upload"
                        className="flex flex-col items-center cursor-pointer"
                    >
                        <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 transition-all ${uploading
                            ? 'bg-blue-500/20 animate-pulse'
                            : 'bg-blue-500/20 group-hover:bg-blue-500/30'
                            }`}>
                            {uploading ? (
                                <div className="w-8 h-8 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
                            ) : (
                                <Upload className="w-8 h-8 text-blue-400" />
                            )}
                        </div>
                        <h3 className="text-lg font-semibold text-white mb-2">
                            {uploading ? 'Uploading...' : 'Upload Document'}
                        </h3>
                        <p className="text-sm text-gray-400 mb-4">
                            Drag and drop or click to browse
                        </p>
                        <div className="flex flex-wrap justify-center gap-2">
                            {['.PDF', '.DOCX', '.TXT', '.MD'].map((ext) => (
                                <span
                                    key={ext}
                                    className="px-2 py-1 bg-white/[0.04] border border-white/[0.08] rounded text-xs text-gray-400"
                                >
                                    {ext}
                                </span>
                            ))}
                        </div>
                    </label>
                </div>

                {/* Documents List */}
                <div className="glass-card p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-2xl font-bold text-white">Your Documents</h2>
                        <button
                            onClick={loadDocuments}
                            disabled={loading}
                            className="px-4 py-2 rounded-lg bg-white/[0.08] hover:bg-white/[0.12] text-white text-sm transition-colors disabled:opacity-50"
                        >
                            {loading ? 'Loading...' : 'Refresh'}
                        </button>
                    </div>

                    {loading && documents.length === 0 ? (
                        <div className="flex items-center justify-center py-12">
                            <div className="w-8 h-8 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
                        </div>
                    ) : documents.length === 0 ? (
                        <div className="text-center py-12">
                            <File className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                            <p className="text-gray-400">No documents uploaded yet</p>
                            <p className="text-sm text-gray-500 mt-2">Upload your first document to get started</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {documents.map((doc) => (
                                <div
                                    key={doc.id}
                                    className="flex items-center gap-4 p-4 rounded-lg bg-white/[0.04] border border-white/[0.08] hover:bg-white/[0.06] hover:border-white/[0.12] transition-all group"
                                >
                                    {getFileIcon(doc.file_type)}

                                    <div className="flex-1 min-w-0">
                                        <p className="text-white font-medium truncate">{doc.filename}</p>
                                        <p className="text-sm text-gray-400">
                                            {formatFileSize(doc.size)} • {formatDate(doc.uploaded_at)}
                                        </p>
                                    </div>

                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={() => setSelectedDoc({ id: doc.id, name: doc.filename })}
                                            className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white text-sm font-medium flex items-center gap-2 transition-all"
                                        >
                                            <Sparkles className="w-4 h-4" />
                                            Summarize
                                        </button>
                                        <button
                                            onClick={() => handleDownload(doc.id, doc.filename)}
                                            className="p-2 rounded-lg bg-white/[0.08] hover:bg-white/[0.12] text-gray-400 hover:text-white transition-colors"
                                            title="Download"
                                        >
                                            <Download className="w-4 h-4" />
                                        </button>
                                        <button
                                            onClick={() => handleDelete(doc.id, doc.filename)}
                                            className="p-2 rounded-lg bg-white/[0.08] hover:bg-red-500/20 text-gray-400 hover:text-red-400 transition-colors"
                                            title="Delete"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Summary Modal */}
            {selectedDoc && (
                <DocumentSummaryModal
                    documentId={selectedDoc.id}
                    documentName={selectedDoc.name}
                    isOpen={!!selectedDoc}
                    onClose={() => setSelectedDoc(null)}
                />
            )}
        </div>
    );
}
