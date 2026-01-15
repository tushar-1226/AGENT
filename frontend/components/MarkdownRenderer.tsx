'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import CodeBlock from './CodeBlock';

interface MarkdownRendererProps {
    content: string;
}

export default function MarkdownRenderer({ content }: MarkdownRendererProps) {
    return (
        <div className="markdown-content">
            <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                    // Code blocks
                    code({ node, inline, className, children, ...props }: any) {
                        const match = /language-(\w+)/.exec(className || '');
                        const language = match ? match[1] : '';
                        const codeContent = String(children).replace(/\n$/, '');

                        return !inline && match ? (
                            <CodeBlock code={codeContent} language={language} />
                        ) : (
                            <code
                                className="px-1.5 py-0.5 rounded bg-white/[0.08] text-blue-300 font-mono text-sm"
                                {...props}
                            >
                                {children}
                            </code>
                        );
                    },
                    // Headings
                    h1: ({ children }) => (
                        <h1 className="text-2xl font-bold text-white mt-6 mb-4">{children}</h1>
                    ),
                    h2: ({ children }) => (
                        <h2 className="text-xl font-bold text-white mt-5 mb-3">{children}</h2>
                    ),
                    h3: ({ children }) => (
                        <h3 className="text-lg font-semibold text-white mt-4 mb-2">{children}</h3>
                    ),
                    // Paragraphs
                    p: ({ children }) => (
                        <p className="text-gray-300 leading-relaxed mb-4">{children}</p>
                    ),
                    // Lists
                    ul: ({ children }) => (
                        <ul className="list-disc list-inside text-gray-300 space-y-2 mb-4 ml-4">{children}</ul>
                    ),
                    ol: ({ children }) => (
                        <ol className="list-decimal list-inside text-gray-300 space-y-2 mb-4 ml-4">{children}</ol>
                    ),
                    li: ({ children }) => (
                        <li className="text-gray-300">{children}</li>
                    ),
                    // Links
                    a: ({ href, children }) => (
                        <a
                            href={href}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-400 hover:text-blue-300 underline"
                        >
                            {children}
                        </a>
                    ),
                    // Blockquotes
                    blockquote: ({ children }) => (
                        <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-400 my-4">
                            {children}
                        </blockquote>
                    ),
                    // Tables
                    table: ({ children }) => (
                        <div className="overflow-x-auto mb-4">
                            <table className="min-w-full border border-white/[0.08]">{children}</table>
                        </div>
                    ),
                    thead: ({ children }) => (
                        <thead className="bg-white/[0.04]">{children}</thead>
                    ),
                    th: ({ children }) => (
                        <th className="px-4 py-2 text-left text-white font-semibold border-b border-white/[0.08]">
                            {children}
                        </th>
                    ),
                    td: ({ children }) => (
                        <td className="px-4 py-2 text-gray-300 border-b border-white/[0.05]">
                            {children}
                        </td>
                    ),
                    // Horizontal rule
                    hr: () => (
                        <hr className="border-white/[0.08] my-6" />
                    ),
                    // Strong/Bold
                    strong: ({ children }) => (
                        <strong className="font-bold text-white">{children}</strong>
                    ),
                    // Emphasis/Italic
                    em: ({ children }) => (
                        <em className="italic text-gray-200">{children}</em>
                    ),
                }}
            >
                {content}
            </ReactMarkdown>
        </div>
    );
}
