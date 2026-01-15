'use client';

import WorkflowEditor from '@/components/visual-builder/WorkflowEditor';

export default function VisualBuilderPage() {
    return (
        <div className="h-screen flex flex-col">
            <div className="h-16 border-b border-white/10 flex items-center px-6 bg-[#0a0a0a] justify-between z-10">
                <div className="flex items-center gap-4">
                    <div className="w-8 h-8 rounded bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5 text-white">
                            <path d="M13.5 16.875h3.375c.207 0 .375.168.375.375v3.375c0 .207-.168.375-.375.375h-3.375a.375.375 0 01-.375-.375v-3.375c0-.207.168-.375.375-.375zm-6.75 0h3.375c.207 0 .375.168.375.375v3.375c0 .207-.168.375-.375.375H6.75a.375.375 0 01-.375-.375v-3.375c0-.207.168-.375.375-.375zM13.5 3h3.375c.207 0 .375.168.375.375v3.375c0 .207-.168.375-.375.375h-3.375a.375.375 0 01-.375-.375V3.375c0-.207.168-.375.375-.375zm-6.75 0h3.375c.207 0 .375.168.375.375v3.375c0 .207-.168.375-.375.375H6.75a.375.375 0 01-.375-.375V3.375c0-.207.168-.375.375-.375z" />
                        </svg>
                    </div>
                    <div>
                        <h1 className="text-lg font-bold text-white">Visual Agent Builder</h1>
                        <p className="text-xs text-gray-400">Design workflows and APIs visually</p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <span className="text-xs text-green-400 bg-green-400/10 px-2 py-1 rounded-full border border-green-400/20">
                        ● Connected to Backend
                    </span>
                </div>
            </div>

            <WorkflowEditor />
        </div>
    );
}
