'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import config from '@/config/api';
import './dashboard.css';

interface ModelDocs {
    model: {
        name: string;
        provider: string;
        version: string;
        type: string;
        description: string;
    };
    capabilities: Array<{
        name: string;
        description: string;
        examples?: string[];
        intents?: string[];
        actions?: string[];
        features?: string[];
    }>;
    api_endpoints: Array<{
        method: string;
        path: string;
        description: string;
        parameters?: any;
        response?: any;
    }>;
    usage_examples: Array<{
        title: string;
        code: string;
        language: string;
    }>;
    features: {
        context_awareness: boolean;
        multi_language: boolean;
        voice_support: boolean;
        websocket_support: boolean;
        real_time_processing: boolean;
    };
}

export default function Dashboard() {
    const [modelDocs, setModelDocs] = useState<ModelDocs | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchModelDocs();
    }, []);

    const fetchModelDocs = async () => {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/docs/model`);
            const data = await response.json();
            setModelDocs(data);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch model docs:', error);
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="doc-container">
                <div className="doc-loading">Loading documentation...</div>
            </div>
        );
    }

    if (!modelDocs) {
        return (
            <div className="doc-container">
                <div className="doc-error">Failed to load documentation</div>
            </div>
        );
    }

    return (
        <div className="doc-container">
            {/* Header */}
            <header className="doc-header">
                <div className="doc-header-content">
                    <Link href="/" className="doc-back-link">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                            <path d="M12 4L6 10L12 16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                        Back to Home
                    </Link>
                    <h1 className="doc-title">F.R.I.D.A.Y. Agent Documentation</h1>
                </div>
            </header>

            {/* Main Content */}
            <main className="doc-main">
                <div className="doc-content">
                    {/* Model Overview */}
                    <section className="doc-section">
                        <h2 className="doc-section-title">Model Overview</h2>
                        <div className="doc-card">
                            <div className="doc-model-header">
                                <h3 className="doc-model-name">{modelDocs.model.name}</h3>
                                <span className="doc-badge">{modelDocs.model.version}</span>
                            </div>
                            <p className="doc-model-provider">Provider: {modelDocs.model.provider}</p>
                            <p className="doc-model-type">Type: {modelDocs.model.type}</p>
                            <p className="doc-description">{modelDocs.model.description}</p>
                        </div>
                    </section>

                    {/* Capabilities */}
                    <section className="doc-section">
                        <h2 className="doc-section-title">Capabilities</h2>
                        <div className="doc-grid">
                            {modelDocs.capabilities.map((capability, index) => (
                                <div key={index} className="doc-card">
                                    <h3 className="doc-capability-name">{capability.name}</h3>
                                    <p className="doc-capability-description">{capability.description}</p>

                                    {capability.examples && (
                                        <div className="doc-list-section">
                                            <p className="doc-list-label">Examples:</p>
                                            <ul className="doc-list">
                                                {capability.examples.map((example, i) => (
                                                    <li key={i} className="doc-list-item">
                                                        <code>{example}</code>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}

                                    {capability.intents && (
                                        <div className="doc-list-section">
                                            <p className="doc-list-label">Intents:</p>
                                            <div className="doc-tag-list">
                                                {capability.intents.map((intent, i) => (
                                                    <span key={i} className="doc-tag">{intent}</span>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {capability.actions && (
                                        <div className="doc-list-section">
                                            <p className="doc-list-label">Actions:</p>
                                            <div className="doc-tag-list">
                                                {capability.actions.map((action, i) => (
                                                    <span key={i} className="doc-tag">{action}</span>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {capability.features && (
                                        <div className="doc-list-section">
                                            <p className="doc-list-label">Features:</p>
                                            <ul className="doc-list">
                                                {capability.features.map((feature, i) => (
                                                    <li key={i} className="doc-list-item">{feature}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </section>

                    {/* API Reference */}
                    <section className="doc-section">
                        <h2 className="doc-section-title">API Reference</h2>
                        <div className="doc-api-list">
                            {modelDocs.api_endpoints.map((endpoint, index) => (
                                <div key={index} className="doc-card doc-api-card">
                                    <div className="doc-api-header">
                                        <span className={`doc-method doc-method-${endpoint.method.toLowerCase()}`}>
                                            {endpoint.method}
                                        </span>
                                        <code className="doc-api-path">{endpoint.path}</code>
                                    </div>
                                    <p className="doc-api-description">{endpoint.description}</p>

                                    {endpoint.parameters && (
                                        <div className="doc-api-section">
                                            <p className="doc-api-section-title">Parameters:</p>
                                            <div className="doc-code-block">
                                                <pre>{JSON.stringify(endpoint.parameters, null, 2)}</pre>
                                            </div>
                                        </div>
                                    )}

                                    {endpoint.response && (
                                        <div className="doc-api-section">
                                            <p className="doc-api-section-title">Response:</p>
                                            <div className="doc-code-block">
                                                <pre>{JSON.stringify(endpoint.response, null, 2)}</pre>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </section>

                    {/* Usage Examples */}
                    <section className="doc-section">
                        <h2 className="doc-section-title">Usage Examples</h2>
                        <div className="doc-examples">
                            {modelDocs.usage_examples.map((example, index) => (
                                <div key={index} className="doc-card">
                                    <h3 className="doc-example-title">{example.title}</h3>
                                    <div className="doc-code-block">
                                        <pre><code>{example.code}</code></pre>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>

                    {/* Features */}
                    <section className="doc-section">
                        <h2 className="doc-section-title">System Features</h2>
                        <div className="doc-card">
                            <div className="doc-features-grid">
                                {Object.entries(modelDocs.features).map(([key, value]) => (
                                    <div key={key} className="doc-feature-item">
                                        <div className="doc-feature-icon">
                                            {value ? (
                                                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                                    <path d="M4 10L8 14L16 6" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                                </svg>
                                            ) : (
                                                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                                    <path d="M6 6L14 14M6 14L14 6" stroke="#6b7280" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                                </svg>
                                            )}
                                        </div>
                                        <span className="doc-feature-label">
                                            {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </section>
                </div>
            </main>

            {/* Footer */}
            <footer className="doc-footer">
                <p>F.R.I.D.A.Y. Agent v1.0.0 • Powered by Gemini 2.5 Flash</p>
            </footer>
        </div>
    );
}
