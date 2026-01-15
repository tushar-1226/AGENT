import React from 'react';

const Sidebar = () => {
    const onDragStart = (event: React.DragEvent, nodeType: string) => {
        event.dataTransfer.setData('application/reactflow', nodeType);
        event.dataTransfer.effectAllowed = 'move';
    };

    const draggables = [
        { type: 'input', label: 'Input Node', color: 'border-blue-500' },
        { type: 'default', label: 'Processing Node', color: 'border-green-500' },
        { type: 'output', label: 'Output Node', color: 'border-red-500' },
        { type: 'condition', label: 'Condition', color: 'border-yellow-500' },
        { type: 'api_call', label: 'API Call', color: 'border-purple-500' },
        { type: 'database', label: 'Database', color: 'border-orange-500' },
    ];

    return (
        <aside className="w-64 bg-[#0a0a0a] border-r border-white/10 p-4 overflow-y-auto">
            <div className="mb-6">
                <h2 className="text-xl font-bold mb-2 text-white">Nodes</h2>
                <p className="text-sm text-gray-400">Drag items to the canvas</p>
            </div>

            <div className="space-y-3">
                {draggables.map((item) => (
                    <div
                        key={item.type}
                        className={`p-3 bg-white/5 border-l-4 ${item.color} rounded cursor-grab hover:bg-white/10 transition-colors text-white text-sm font-medium`}
                        onDragStart={(event) => onDragStart(event, item.type)}
                        draggable
                    >
                        {item.label}
                    </div>
                ))}
            </div>

            <div className="mt-8 border-t border-white/10 pt-4">
                <h3 className="text-sm font-semibold text-gray-400 mb-3">Templates</h3>
                <button className="w-full text-left p-2 text-sm text-gray-300 hover:bg-white/5 rounded mb-1">
                    Build REST API
                </button>
                <button className="w-full text-left p-2 text-sm text-gray-300 hover:bg-white/5 rounded mb-1">
                    Data Pipeline
                </button>
                <button className="w-full text-left p-2 text-sm text-gray-300 hover:bg-white/5 rounded">
                    Webhook Listener
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
