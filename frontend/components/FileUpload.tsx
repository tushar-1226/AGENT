'use client';

import { useState, useCallback } from 'react';
import config from '@/config/api';

interface FileUploadProps {
    onFileAnalyzed: (analysis: string, fileInfo: any) => void;
}

export default function FileUpload({ onFileAnalyzed }: FileUploadProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [preview, setPreview] = useState<string | null>(null);
    const [fileName, setFileName] = useState<string | null>(null);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const processFile = useCallback(async (file: File) => {
        setUploading(true);
        setFileName(file.name);

        try {
            // Create preview for images
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => setPreview(e.target?.result as string);
                reader.readAsDataURL(file);
            }

            // Upload file
            const formData = new FormData();
            formData.append('file', file);

            const uploadResponse = await fetch(`${config.apiBaseUrl}/api/upload`, {
                method: 'POST',
                body: formData
            });

            const uploadData = await uploadResponse.json();

            if (uploadData.success) {
                // Analyze file
                const analyzeResponse = await fetch(`${config.apiBaseUrl}/api/analyze`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        file_path: uploadData.file.path,
                        file_type: uploadData.file.type
                    })
                });

                const analyzeData = await analyzeResponse.json();

                if (analyzeData.success) {
                    onFileAnalyzed(analyzeData.analysis, {
                        fileName: file.name,
                        fileType: uploadData.file.type,
                        ...analyzeData.metadata
                    });
                }
            }
        } catch (error) {
            console.error('File upload/analysis failed:', error);
        } finally {
            setUploading(false);
            setPreview(null);
            setFileName(null);
        }
    }, [onFileAnalyzed]);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        const file = e.dataTransfer.files[0];
        if (file) {
            processFile(file);
        }
    }, [processFile]);

    const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            processFile(file);
        }
    }, [processFile]);

    return (
        <div className="relative">
            {/* File Input */}
            <input
                type="file"
                id="file-upload"
                className="hidden"
                accept="image/*,.pdf"
                onChange={handleFileSelect}
                disabled={uploading}
            />

            {/* Upload Button */}
            <label
                htmlFor="file-upload"
                className={`flex items-center justify-center w-12 h-12 rounded-xl cursor-pointer transition-all duration-300 ${isDragging
                        ? 'bg-blue-500/20 border-2 border-blue-500 scale-105'
                        : 'bg-white/[0.04] border border-white/[0.08] hover:bg-white/[0.08] hover:border-blue-500/30'
                    } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                title="Upload file (image or PDF)"
            >
                {uploading ? (
                    <svg className="w-6 h-6 text-blue-400 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        />
                    </svg>
                ) : (
                    <svg
                        className="w-6 h-6 text-gray-400"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                        />
                    </svg>
                )}
            </label>

            {/* Preview Popup */}
            {preview && (
                <div className="absolute top-full mt-2 left-0 z-50 glass-card p-3 border-blue-500/30 min-w-[200px]">
                    <img src={preview} alt="Preview" className="max-w-[200px] max-h-[200px] rounded" />
                    <p className="text-xs text-gray-400 mt-2 truncate">{fileName}</p>
                </div>
            )}
        </div>
    );
}
