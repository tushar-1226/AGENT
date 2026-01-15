import config from '@/config/api';

export interface WorkflowData {
    id?: string;
    name: string;
    nodes: any[];
    edges: any[];
}

export const VisualBuilderService = {
    createWorkflow: async (workflow: WorkflowData) => {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/visual-programming/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(workflow),
            });
            return await response.json();
        } catch (error) {
            console.error('Error creating workflow:', error);
            throw error;
        }
    },

    generateCode: async (workflowId: string, language: string) => {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/visual-programming/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ workflow_id: workflowId, language }),
            });
            return await response.json();
        } catch (error) {
            console.error('Error generating code:', error);
            throw error;
        }
    },

    getTemplates: async () => {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/visual-programming/templates`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching templates:', error);
            return { success: false, templates: {} };
        }
    }
};
