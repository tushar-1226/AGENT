'use client';

export default function FilesPage() {
    const files = [
        { name: 'Market Report.pdf', type: 'PDF', size: '2.4 MB' },
        { name: 'Project Plan.docx', type: 'DOC', size: '1.8 MB' },
        { name: 'Budget_2022.xlsx', type: 'XLS', size: '856 KB' }
    ];

    return (
        <div className="min-h-screen bg-[#0a0a0a] p-8">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-4xl font-bold text-white mb-6">Recent Files</h1>
                <div className="glass-card p-6">
                    <div className="space-y-3">
                        {files.map((file, idx) => (
                            <div
                                key={idx}
                                className="flex items-center gap-4 p-4 rounded-lg hover:bg-white/[0.04] transition-all cursor-pointer"
                            >
                                <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center">
                                    <span className="text-sm font-bold text-blue-400">{file.type}</span>
                                </div>
                                <div className="flex-1">
                                    <p className="text-white font-medium">{file.name}</p>
                                    <p className="text-sm text-gray-400">{file.size}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
