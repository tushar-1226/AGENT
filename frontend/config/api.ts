const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

const config = {
    apiUrl: API_BASE_URL,
    apiBaseUrl: API_BASE_URL, // Used by components
    wsUrl: WS_BASE_URL,
    endpoints: {
        command: `${API_BASE_URL}/api/command`,
        fileAnalysis: `${API_BASE_URL}/api/analyze-file`,
        systemStats: `${API_BASE_URL}/api/system/stats`,
        sessions: `${API_BASE_URL}/api/sessions`,
        websocket: `${WS_BASE_URL}/ws`,
    },
};

export default config;
