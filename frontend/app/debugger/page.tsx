'use client';

import { useState } from 'react';
import config from '@/config/api';

interface Breakpoint {
  line: number;
  enabled: boolean;
  condition?: string;
  hit_count: number;
}

interface DebugSession {
  session_id: string;
  file_path: string;
  breakpoints: Breakpoint[];
  current_line: number | null;
  variables: Record<string, any>;
  call_stack: any[];
  is_running: boolean;
  is_paused: boolean;
}

export default function DebuggerPage() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [session, setSession] = useState<DebugSession | null>(null);
  const [filePath, setFilePath] = useState('');
  const [code, setCode] = useState('');
  const [expression, setExpression] = useState('');
  const [evalResult, setEvalResult] = useState<any>(null);

  const createSession = async () => {
    if (!filePath) {
      alert('Please enter a file path');
      return;
    }

    try {
      const response = await fetch(`${config.apiBaseUrl}/api/debugger/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_path: filePath }),
      });

      const data = await response.json();
      if (data.success) {
        setSessionId(data.session.session_id);
        setSession(data.session);
      }
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const addBreakpoint = async (lineNumber: number) => {
    if (!sessionId) return;

    try {
      const response = await fetch(`${config.apiBaseUrl}/api/debugger/${sessionId}/breakpoint`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ line_number: lineNumber }),
      });

      const data = await response.json();
      if (data.success) {
        // Refresh session
        await refreshSession();
      }
    } catch (error) {
      console.error('Failed to add breakpoint:', error);
    }
  };

  const startDebugging = async () => {
    if (!sessionId) return;

    try {
      const response = await fetch(`${config.apiBaseUrl}/api/debugger/${sessionId}/start`, {
        method: 'POST',
      });

      const data = await response.json();
      if (data.success) {
        setSession(data.session);
      }
    } catch (error) {
      console.error('Failed to start debugging:', error);
    }
  };

  const stepOver = async () => {
    if (!sessionId) return;

    try {
      const response = await fetch(`${config.apiBaseUrl}/api/debugger/${sessionId}/step-over`, {
        method: 'POST',
      });

      const data = await response.json();
      if (data.success) {
        setSession(data.session);
      }
    } catch (error) {
      console.error('Failed to step over:', error);
    }
  };

  const stepInto = async () => {
    if (!sessionId) return;

    try {
      const response = await fetch(`${config.apiBaseUrl}/api/debugger/${sessionId}/step-into`, {
        method: 'POST',
      });

      const data = await response.json();
      if (data.success) {
        setSession(data.session);
      }
    } catch (error) {
      console.error('Failed to step into:', error);
    }
  };

  const continueExecution = async () => {
    if (!sessionId) return;

    try {
      const response = await fetch(`${config.apiBaseUrl}/api/debugger/${sessionId}/continue`, {
        method: 'POST',
      });

      const data = await response.json();
      if (data.success) {
        setSession(data.session);
      }
    } catch (error) {
      console.error('Failed to continue:', error);
    }
  };

  const evaluateExpression = async () => {
    if (!sessionId || !expression) return;

    try {
      const response = await fetch(`${config.apiBaseUrl}/api/debugger/${sessionId}/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expression }),
      });

      const data = await response.json();
      setEvalResult(data);
    } catch (error) {
      console.error('Failed to evaluate:', error);
    }
  };

  const refreshSession = async () => {
    if (!sessionId) return;

    try {
      const response = await fetch(`${config.apiBaseUrl}/api/debugger/sessions`);
      const data = await response.json();
      if (data.success) {
        const currentSession = data.sessions.find((s: any) => s.session_id === sessionId);
        if (currentSession) {
          setSession(currentSession);
        }
      }
    } catch (error) {
      console.error('Failed to refresh session:', error);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-red-400 to-orange-600 bg-clip-text text-transparent">
            Integrated Debugger
          </h1>
          <p className="text-gray-400">Debug Python code with breakpoints and variable inspection</p>
        </div>

        {!sessionId ? (
          /* Session Creation */
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-8">
            <h2 className="text-xl font-semibold mb-6">Create Debug Session</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Python File Path</label>
                <input
                  type="text"
                  value={filePath}
                  onChange={(e) => setFilePath(e.target.value)}
                  placeholder="/path/to/your/script.py"
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <button
                onClick={createSession}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all"
              >
                Start Debug Session
              </button>
            </div>
          </div>
        ) : (
          /* Debugging Interface */
          <div className="grid grid-cols-3 gap-6">
            {/* Main Debugging Panel */}
            <div className="col-span-2 space-y-6">
              {/* Controls */}
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
                <div className="flex gap-3 mb-4">
                  <button
                    onClick={startDebugging}
                    disabled={session?.is_running}
                    className="px-4 py-2 bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Start
                  </button>
                  
                  <button
                    onClick={stepOver}
                    disabled={!session?.is_paused}
                    className="px-4 py-2 bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Step Over
                  </button>
                  
                  <button
                    onClick={stepInto}
                    disabled={!session?.is_paused}
                    className="px-4 py-2 bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Step Into
                  </button>
                  
                  <button
                    onClick={continueExecution}
                    disabled={!session?.is_paused}
                    className="px-4 py-2 bg-yellow-600 rounded-lg hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Continue
                  </button>
                </div>

                <div className="text-sm text-gray-400">
                  Status: {session?.is_running ? (
                    <span className="text-green-400">Running</span>
                  ) : session?.is_paused ? (
                    <span className="text-yellow-400">Paused</span>
                  ) : (
                    <span className="text-gray-500">Stopped</span>
                  )}
                  {session?.current_line && (
                    <span className="ml-4">Current Line: <span className="text-white">{session.current_line}</span></span>
                  )}
                </div>
              </div>

              {/* Breakpoints */}
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
                <h3 className="font-semibold mb-4">Breakpoints</h3>
                {session?.breakpoints && session.breakpoints.length > 0 ? (
                  <div className="space-y-2">
                    {session.breakpoints.map((bp, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-white/5 rounded">
                        <div className="flex items-center gap-3">
                          <div className={`w-3 h-3 rounded-full ${bp.enabled ? 'bg-red-500' : 'bg-gray-500'}`} />
                          <span>Line {bp.line}</span>
                          <span className="text-xs text-gray-500">Hit count: {bp.hit_count}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-gray-500 text-sm">No breakpoints set</div>
                )}
                
                <div className="mt-4">
                  <input
                    type="number"
                    placeholder="Line number"
                    className="px-3 py-2 bg-white/5 border border-white/10 rounded mr-2"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        const lineNum = parseInt((e.target as HTMLInputElement).value);
                        if (!isNaN(lineNum)) {
                          addBreakpoint(lineNum);
                          (e.target as HTMLInputElement).value = '';
                        }
                      }
                    }}
                  />
                  <span className="text-xs text-gray-500">Press Enter to add</span>
                </div>
              </div>

              {/* Expression Evaluator */}
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
                <h3 className="font-semibold mb-4">Evaluate Expression</h3>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={expression}
                    onChange={(e) => setExpression(e.target.value)}
                    placeholder="Enter expression (e.g., x + y)"
                    className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    onKeyPress={(e) => e.key === 'Enter' && evaluateExpression()}
                  />
                  <button
                    onClick={evaluateExpression}
                    className="px-6 py-2 bg-blue-600 rounded-lg hover:bg-blue-700"
                  >
                    Evaluate
                  </button>
                </div>
                {evalResult && (
                  <div className="mt-4 p-4 bg-white/5 rounded-lg">
                    {evalResult.success ? (
                      <div>
                        <div className="text-sm text-gray-400">Result:</div>
                        <div className="text-white font-mono">{evalResult.result}</div>
                        <div className="text-xs text-gray-500 mt-1">Type: {evalResult.type}</div>
                      </div>
                    ) : (
                      <div className="text-red-400">{evalResult.error}</div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Side Panel */}
            <div className="space-y-6">
              {/* Variables */}
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
                <h3 className="font-semibold mb-4">Variables</h3>
                {session?.variables && Object.keys(session.variables).length > 0 ? (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {Object.entries(session.variables).map(([name, value]: [string, any]) => (
                      <div key={name} className="p-2 bg-white/5 rounded text-sm">
                        <div className="font-mono text-blue-400">{name}</div>
                        <div className="text-gray-400 text-xs mt-1">{value.type}</div>
                        <div className="text-white text-xs mt-1 truncate">{value.value}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-gray-500 text-sm">No variables</div>
                )}
              </div>

              {/* Call Stack */}
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
                <h3 className="font-semibold mb-4">Call Stack</h3>
                {session?.call_stack && session.call_stack.length > 0 ? (
                  <div className="space-y-2">
                    {session.call_stack.map((frame, index) => (
                      <div key={index} className="p-2 bg-white/5 rounded text-sm">
                        <div className="font-mono text-purple-400">{frame.function}</div>
                        <div className="text-gray-500 text-xs">{frame.file}:{frame.line}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-gray-500 text-sm">No call stack</div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
