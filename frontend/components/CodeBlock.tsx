'use client';

import { useEffect, useState } from 'react';
import hljs from 'highlight.js';
import 'highlight.js/styles/tokyo-night-dark.css';

interface CodeBlockProps {
    code: string;
    language?: string;
}

export default function CodeBlock({ code, language = 'plaintext' }: CodeBlockProps) {
    const [copied, setCopied] = useState(false);
    const [highlighted, setHighlighted] = useState('');

    useEffect(() => {
        try {
            const result = language && hljs.getLanguage(language)
                ? hljs.highlight(code, { language }).value
                : hljs.highlightAuto(code).value;
            setHighlighted(result);
        } catch (e) {
            setHighlighted(code);
        }
    }, [code, language]);

    const handleCopy = async () => {
        await navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="relative group my-4">
            {/* Header with language and copy button */}
            <div className="flex items-center justify-between px-4 py-2 bg-[#1a1b26] border border-white/[0.08] rounded-t-lg">
                <span className="text-xs text-gray-400 font-mono uppercase">{language}</span>
                <button
                    onClick={handleCopy}
                    className="flex items-center gap-2 px-3 py-1 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] transition-colors text-xs text-gray-300"
                >
                    {copied ? (
                        <>
                            <svg className="w-4 h-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                            Copied!
                        </>
                    ) : (
                        <>
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                            Copy
                        </>
                    )}
                </button>
            </div>

            {/* Code content */}
            <div className="overflow-x-auto bg-[#1a1b26] border border-t-0 border-white/[0.08] rounded-b-lg">
                <pre className="p-4">
                    <code
                        className={`language-${language}`}
                        dangerouslySetInnerHTML={{ __html: highlighted }}
                    />
                </pre>
            </div>
        </div>
    );
}
