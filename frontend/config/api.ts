// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

export const config = {
  apiBaseUrl: API_BASE_URL,
  wsUrl: WS_URL,
  endpoints: {
    status: `${API_BASE_URL}/api/status`,
    command: `${API_BASE_URL}/api/command`,
    voiceStart: `${API_BASE_URL}/api/voice/start`,
    voiceStop: `${API_BASE_URL}/api/voice/stop`,
    appsRunning: `${API_BASE_URL}/api/apps/running`,
    appsAvailable: `${API_BASE_URL}/api/apps/available`,
    launchApp: (appName: string) => `${API_BASE_URL}/api/apps/launch/${appName}`,
    closeApp: (appName: string) => `${API_BASE_URL}/api/apps/close/${appName}`,
  }
};

export default config;
