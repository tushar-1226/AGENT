'use client';

export default function TipBanner() {
    return (
        <div className="px-8 pb-16">
            <div className="glass-card p-5 border-blue-500/[0.15] bg-gradient-to-r from-blue-500/[0.05] to-transparent">
                <div className="flex items-center gap-5">
                    <div className="flex-shrink-0 w-11 h-11 rounded-xl bg-gradient-to-br from-blue-500/20 to-blue-600/10 flex items-center justify-center border border-blue-500/20 shadow-lg shadow-blue-500/10">
                        <svg className="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                    </div>
                    <div className="flex-1">
                        <p className="text-[0.9375rem] text-gray-400 leading-relaxed">
                            <span className="font-semibold text-blue-400">Tip:</span> Try{' '}
                            <span className="italic text-gray-300 font-medium">
                                "Summarize the latest report for me."
                            </span>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
