import React, { useCallback, useRef } from 'react';
import ReactFlow, {
    ReactFlowProvider,
    addEdge,
    useNodesState,
    useEdgesState,
    Controls,
    Background,
    MiniMap,
    Connection,
    Edge,
    Node,
    Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import Sidebar from './Sidebar';
import { Button } from '@/components/ui/button';
import { Play, Save, Code } from 'lucide-react';

const initialNodes: Node[] = [
    {
        id: '1',
        type: 'input',
        data: { label: 'Start Flow' },
        position: { x: 250, y: 5 },
    },
];

let id = 0;
const getId = () => `dndnode_${id++}`;

const WorkflowEditor = () => {
    const reactFlowWrapper = useRef<HTMLDivElement>(null);
    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [reactFlowInstance, setReactFlowInstance] = React.useState<any>(null);

    const onConnect = useCallback(
        (params: Connection) => setEdges((eds) => addEdge(params, eds)),
        [setEdges]
    );

    const onDragOver = useCallback((event: React.DragEvent) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }, []);

    const onDrop = useCallback(
        (event: React.DragEvent) => {
            event.preventDefault();

            const type = event.dataTransfer.getData('application/reactflow');

            // check if the dropped element is valid
            if (typeof type === 'undefined' || !type) {
                return;
            }

            if (reactFlowWrapper.current && reactFlowInstance) {
                const position = reactFlowInstance.screenToFlowPosition({
                    x: event.clientX,
                    y: event.clientY,
                });
                const newNode: Node = {
                    id: getId(),
                    type,
                    position,
                    data: { label: `${type} node` },
                };

                setNodes((nds) => nds.concat(newNode));
            }

        },
        [reactFlowInstance, setNodes]
    );

    const handleSave = () => {
        if (reactFlowInstance) {
            const flow = reactFlowInstance.toObject();
            console.log('Flow saved:', flow);
            // todo: call save api
        }
    };

    return (
        <div className="flex h-[calc(100vh-64px)] w-full">
            <Sidebar />
            <div className="flex-1 h-full" ref={reactFlowWrapper}>
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    onInit={setReactFlowInstance}
                    onDrop={onDrop}
                    onDragOver={onDragOver}
                    fitView
                    className="bg-black/90"
                >
                    <Controls className="bg-white/10 border-white/20 text-white" />
                    <MiniMap className="bg-black/50 border-white/10" maskColor="rgba(0,0,0,0.6)" />
                    <Background color="#333" gap={16} />

                    <Panel position="top-right" className="flex gap-2">
                        <Button onClick={handleSave} className="bg-blue-600 hover:bg-blue-700">
                            <Save className="w-4 h-4 mr-2" />
                            Save
                        </Button>
                        <Button className="bg-green-600 hover:bg-green-700">
                            <Play className="w-4 h-4 mr-2" />
                            Run
                        </Button>
                        <Button className="bg-purple-600 hover:bg-purple-700">
                            <Code className="w-4 h-4 mr-2" />
                            Generate Code
                        </Button>
                    </Panel>
                </ReactFlow>
            </div>
        </div>
    );
};

export default () => (
    <ReactFlowProvider>
        <WorkflowEditor />
    </ReactFlowProvider>
);
