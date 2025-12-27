'use client';

export default function DocumentationPage() {
    return (
        <div className="min-h-screen bg-[#0a0a0a] p-8">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-4xl font-bold text-white mb-6">Documentation</h1>
                <div className="glass-card p-8">
                    <p className="text-gray-300 leading-relaxed">
                        View comprehensive model documentation, API references, and usage examples.
                    </p>
                    <div className="mt-6 space-y-4">
                        <div className="p-4 rounded-lg bg-white/[0.02] border border-white/[0.05]">
                            <h3 className="text-lg font-semibold text-white mb-2">Getting Started</h3>
                            <p className="text-sm text-gray-400">Learn the basics of F.R.I.D.A.Y. Agent</p>
                        </div>
                        <div className="p-4 rounded-lg bg-white/[0.02] border border-white/[0.05]">
                            <h3 className="text-lg font-semibold text-white mb-2">API Reference</h3>
                            <p className="text-sm text-gray-400">Complete API documentation</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
