'use client';

import { useState, useEffect, useRef } from 'react';
import config from '@/config/api';

interface Suggestion {
  type: string;
  label: string;
  insert_text: string;
  detail: string;
  documentation?: string;
  score: number;
  source?: string;
}

interface Signature {
  function: string;
  signature: string;
  active_parameter: number;
}

interface CodeIssue {
  type: string;
  line: number;
  message: string;
  severity: string;
}

interface Improvement {
  type: string;
  line: number;
  suggestion: string;
  priority: string;
}

export default function AICopilotPage() {
  const [code, setCode] = useState('# Start typing Python code...\n');
  const [language, setLanguage] = useState('python');
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [signature, setSignature] = useState<Signature | null>(null);
  const [cursorPosition, setCursorPosition] = useState(0);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [errors, setErrors] = useState<CodeIssue[]>([]);
  const [improvements, setImprovements] = useState<Improvement[]>([]);
  const [explanation, setExplanation] = useState('');
  const [activeTab, setActiveTab] = useState<'code' | 'errors' | 'improvements' | 'explain'>('code');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);

  const languages = [
    { value: 'python', label: 'Python', icon: '🐍' },
    { value: 'javascript', label: 'JavaScript', icon: '📜' },
    { value: 'typescript', label: 'TypeScript', icon: '💙' },
  ];

  const getCompletions = async (text: string, position: number) => {
    try {
      const response = await fetch(`${config.apiBaseUrl}/api/copilot/completions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: text,
          cursor_position: position,
          language,
        }),
      });

      const data = await response.json();
      if (data.success && data.suggestions) {
        setSuggestions(data.suggestions);
        setShowSuggestions(data.suggestions.length > 0);
      }
    } catch (error) {
      console.error('Failed to get completions:', error);
    }
  };

  const getSignatureHelp = async (text: string, position: number) => {
    try {
      const response = await fetch(`${config.apiBaseUrl}/api/copilot/signature`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: text,
          cursor_position: position,
          language,
        }),
      });

      const data = await response.json();
      if (data.success && data.signature) {
        setSignature(data.signature);
      } else {
        setSignature(null);
      }
    } catch (error) {
      console.error('Failed to get signature help:', error);
    }
  };

  const handleCodeChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newCode = e.target.value;
    const newPosition = e.target.selectionStart;

    setCode(newCode);
    setCursorPosition(newPosition);

    // Debounce suggestions
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    debounceTimer.current = setTimeout(() => {
      getCompletions(newCode, newPosition);
      getSignatureHelp(newCode, newPosition);
    }, 300);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Ctrl+Space to trigger completions
    if (e.ctrlKey && e.code === 'Space') {
      e.preventDefault();
      getCompletions(code, cursorPosition);
    }

    // Escape to close suggestions
    if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  const insertSuggestion = (suggestion: Suggestion) => {
    if (textareaRef.current) {
      const start = code.substring(0, cursorPosition);
      const end = code.substring(cursorPosition);
      const newCode = start + suggestion.insert_text + end;
      
      setCode(newCode);
      setShowSuggestions(false);
      
      // Focus back on textarea
      textareaRef.current.focus();
    }
  };

  const detectErrors = async () => {
    setIsAnalyzing(true);
    try {
      const response = await fetch(`${config.apiBaseUrl}/api/copilot/detect-errors`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language }),
      });

      const data = await response.json();
      if (data.success) {
        setErrors(data.issues || []);
        setActiveTab('errors');
      }
    } catch (error) {
      console.error('Error detection failed:', error);
    }
    setIsAnalyzing(false);
  };

  const getImprovements = async () => {
    setIsAnalyzing(true);
    try {
      const response = await fetch(`${config.apiBaseUrl}/api/copilot/improvements`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language }),
      });

      const data = await response.json();
      if (data.success) {
        setImprovements(data.improvements || []);
        setActiveTab('improvements');
      }
    } catch (error) {
      console.error('Improvements fetch failed:', error);
    }
    setIsAnalyzing(false);
  };

  const explainCode = async () => {
    setIsAnalyzing(true);
    try {
      const response = await fetch(`${config.apiBaseUrl}/api/copilot/explain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language }),
      });

      const data = await response.json();
      if (data.success) {
        setExplanation(data.explanation);
        setActiveTab('explain');
      }
    } catch (error) {
      console.error('Code explanation failed:', error);
    }
    setIsAnalyzing(false);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'text-red-400 bg-red-500/10';
      case 'medium': return 'text-yellow-400 bg-yellow-500/10';
      case 'low': return 'text-blue-400 bg-blue-500/10';
      default: return 'text-gray-400 bg-gray-500/10';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
            AI Code Copilot
          </h1>
          <p className="text-gray-400">Real-time code suggestions and intelligent completions</p>
        </div>

        {/* Controls */}
        <div className="mb-6 flex gap-4 items-center">
          <label className="text-sm text-gray-400">Language:</label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {languages.map((lang) => (
              <option key={lang.value} value={lang.value} className="bg-[#1a1a1a]">
                {lang.icon} {lang.label}
              </option>
            ))}
          </select>

          {/* AI Action Buttons */}
          <div className="ml-auto flex gap-2">
            <button
              onClick={detectErrors}
              disabled={isAnalyzing}
              className="px-4 py-2 bg-red-600/20 border border-red-600/30 text-red-400 rounded-lg hover:bg-red-600/30 transition-all disabled:opacity-50 text-sm flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              Detect Errors
            </button>
            <button
              onClick={getImprovements}
              disabled={isAnalyzing}
              className="px-4 py-2 bg-yellow-600/20 border border-yellow-600/30 text-yellow-400 rounded-lg hover:bg-yellow-600/30 transition-all disabled:opacity-50 text-sm flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Improve
            </button>
            <button
              onClick={explainCode}
              disabled={isAnalyzing}
              className="px-4 py-2 bg-blue-600/20 border border-blue-600/30 text-blue-400 rounded-lg hover:bg-blue-600/30 transition-all disabled:opacity-50 text-sm flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              Explain
            </button>
          </div>

          <div className="text-sm text-gray-500">
            <kbd className="px-2 py-1 bg-white/5 rounded">Ctrl+Space</kbd> completions
          </div>
        </div>

        <div className="grid grid-cols-3 gap-6">
          {/* Code Editor */}
          <div className="col-span-2 relative">
            <div className="bg-[#1a1a1a] rounded-lg border border-white/10 overflow-hidden">
              <div className="bg-white/5 px-4 py-2 border-b border-white/10 flex items-center justify-between">
                <span className="text-sm font-semibold text-gray-400">Code Editor</span>
                <div className="flex gap-2">
                  <span className="text-xs text-gray-500">Ln {code.substring(0, cursorPosition).split('\n').length}</span>
                  <span className="text-xs text-gray-500">Col {cursorPosition - code.lastIndexOf('\n', cursorPosition - 1)}</span>
                </div>
              </div>
              
              <div className="relative">
                <textarea
                  ref={textareaRef}
                  value={code}
                  onChange={handleCodeChange}
                  onKeyDown={handleKeyDown}
                  className="w-full h-[600px] p-4 bg-transparent text-gray-100 font-mono text-sm resize-none focus:outline-none"
                  spellCheck={false}
                />

                {/* Signature Help Popup */}
                {signature && (
                  <div className="absolute top-0 left-0 mt-2 ml-2 bg-gray-900 border border-blue-500 rounded-lg px-4 py-2 shadow-xl z-10">
                    <div className="text-sm">
                      <span className="text-blue-400 font-semibold">{signature.function}</span>
                      <span className="text-gray-400">{signature.signature}</span>
                    </div>
                  </div>
                )}

                {/* Suggestions Popup */}
                {showSuggestions && suggestions.length > 0 && (
                  <div className="absolute top-12 left-4 bg-[#1a1a1a] border border-white/20 rounded-lg shadow-2xl overflow-hidden z-20 max-w-md">
                    <div className="px-3 py-2 bg-white/5 border-b border-white/10 flex items-center justify-between">
                      <span className="text-xs text-gray-400">Suggestions</span>
                      <span className="text-xs text-gray-600">{suggestions.length} items</span>
                    </div>
                    <div className="max-h-64 overflow-y-auto">
                      {suggestions.slice(0, 10).map((suggestion, index) => (
                        <button
                          key={index}
                          onClick={() => insertSuggestion(suggestion)}
                          className="w-full px-4 py-3 text-left hover:bg-white/10 transition-colors border-b border-white/5 last:border-0"
                        >
                          <div className="flex items-start gap-3">
                            <div className={`mt-1 w-6 h-6 rounded flex items-center justify-center text-xs font-bold ${
                              suggestion.source === 'ai' ? 'bg-gradient-to-br from-purple-600 to-pink-600' :
                              suggestion.type === 'keyword' ? 'bg-purple-600' :
                              suggestion.type === 'function' ? 'bg-blue-600' :
                              suggestion.type === 'method' ? 'bg-green-600' :
                              suggestion.type === 'import' ? 'bg-yellow-600' :
                              'bg-gray-600'
                            }`}>
                              {suggestion.source === 'ai' ? '🤖' : suggestion.type[0].toUpperCase()}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className="font-mono text-sm text-white truncate">
                                  {suggestion.label}
                                </span>
                                {suggestion.source === 'ai' && (
                                  <span className="text-xs px-1.5 py-0.5 bg-gradient-to-r from-purple-600 to-pink-600 rounded text-white font-semibold">
                                    AI
                                  </span>
                                )}
                              </div>
                              <div className="text-xs text-gray-500 truncate">
                                {suggestion.detail}
                              </div>
                              {suggestion.documentation && (
                                <div className="text-xs text-gray-600 mt-1 truncate">
                                  {suggestion.documentation}
                                </div>
                              )}
                            </div>
                            <div className="text-xs text-gray-600">
                              {Math.round(suggestion.score * 100)}%
                            </div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* AI Analysis Panel */}
          <div className="space-y-6">
            {/* Tabs */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg overflow-hidden">
              <div className="flex border-b border-white/10">
                <button
                  onClick={() => setActiveTab('code')}
                  className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                    activeTab === 'code' ? 'bg-blue-600/20 text-blue-400 border-b-2 border-blue-400' : 'text-gray-400 hover:text-white'
                  }`}
                >
                  Features
                </button>
                <button
                  onClick={() => setActiveTab('errors')}
                  className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                    activeTab === 'errors' ? 'bg-red-600/20 text-red-400 border-b-2 border-red-400' : 'text-gray-400 hover:text-white'
                  }`}
                >
                  Errors {errors.length > 0 && `(${errors.length})`}
                </button>
                <button
                  onClick={() => setActiveTab('improvements')}
                  className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                    activeTab === 'improvements' ? 'bg-yellow-600/20 text-yellow-400 border-b-2 border-yellow-400' : 'text-gray-400 hover:text-white'
                  }`}
                >
                  Tips {improvements.length > 0 && `(${improvements.length})`}
                </button>
                <button
                  onClick={() => setActiveTab('explain')}
                  className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                    activeTab === 'explain' ? 'bg-purple-600/20 text-purple-400 border-b-2 border-purple-400' : 'text-gray-400 hover:text-white'
                  }`}
                >
                  Explain
                </button>
              </div>

              <div className="p-6 max-h-[600px] overflow-y-auto">
                {isAnalyzing && (
                  <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                  </div>
                )}

                {!isAnalyzing && activeTab === 'code' && (
                  <div>
                    <h3 className="font-semibold mb-4 text-blue-400">Copilot Features</h3>
                    <ul className="space-y-3 text-sm">
                      <li className="flex items-start gap-2">
                        <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="text-gray-300">🤖 AI-Powered Suggestions</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="text-gray-300">Real-time code completion</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="text-gray-300">Function signatures</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="text-gray-300">Context-aware suggestions</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="text-gray-300">Smart import detection</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="text-gray-300">Type inference & methods</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="text-gray-300">Code quality checks</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="text-gray-300">Error detection</span>
                      </li>
                    </ul>
                  </div>
                )}

                {!isAnalyzing && activeTab === 'errors' && (
                  <div>
                    <h3 className="font-semibold mb-4 text-red-400">Code Issues</h3>
                    {errors.length === 0 ? (
                      <div className="text-center py-8">
                        <svg className="w-16 h-16 mx-auto mb-3 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <p className="text-gray-400">No issues detected!</p>
                        <p className="text-sm text-gray-500 mt-2">Click "Detect Errors" to analyze your code</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {errors.map((error, idx) => (
                          <div key={idx} className={`p-3 rounded-lg border ${getSeverityColor(error.severity)}`}>
                            <div className="flex items-start justify-between mb-1">
                              <span className="text-xs font-semibold uppercase">{error.type}</span>
                              <span className="text-xs">Line {error.line}</span>
                            </div>
                            <p className="text-sm">{error.message}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {!isAnalyzing && activeTab === 'improvements' && (
                  <div>
                    <h3 className="font-semibold mb-4 text-yellow-400">Improvement Suggestions</h3>
                    {improvements.length === 0 ? (
                      <div className="text-center py-8">
                        <svg className="w-16 h-16 mx-auto mb-3 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        <p className="text-gray-400">No suggestions yet</p>
                        <p className="text-sm text-gray-500 mt-2">Click "Improve" to get AI suggestions</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {improvements.map((improvement, idx) => (
                          <div key={idx} className="p-3 bg-white/5 rounded-lg border border-white/10">
                            <div className="flex items-start justify-between mb-2">
                              <span className={`text-xs font-semibold uppercase ${getPriorityColor(improvement.priority)}`}>
                                {improvement.type}
                              </span>
                              <span className="text-xs text-gray-500">Line {improvement.line}</span>
                            </div>
                            <p className="text-sm text-gray-300">{improvement.suggestion}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {!isAnalyzing && activeTab === 'explain' && (
                  <div>
                    <h3 className="font-semibold mb-4 text-purple-400">Code Explanation</h3>
                    {!explanation ? (
                      <div className="text-center py-8">
                        <svg className="w-16 h-16 mx-auto mb-3 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                        <p className="text-gray-400">No explanation yet</p>
                        <p className="text-sm text-gray-500 mt-2">Click "Explain" to understand your code</p>
                      </div>
                    ) : (
                      <div className="prose prose-invert prose-sm max-w-none">
                        <div className="text-gray-300 whitespace-pre-wrap">{explanation}</div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Features */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
              <h3 className="font-semibold mb-4 text-blue-400">Features</h3>
              <ul className="space-y-3 text-sm">
                <li className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-gray-300">Real-time code completion</span>
                </li>
                <li className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-gray-300">Function signatures</span>
                </li>
                <li className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-gray-300">Context-aware suggestions</span>
                </li>
                <li className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-gray-300">Import suggestions</span>
                </li>
                <li className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-gray-300">Pattern suggestions</span>
                </li>
              </ul>
            </div>

            {/* Suggestions Stats */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
              <h3 className="font-semibold mb-4 text-purple-400">Current Suggestions</h3>
              <div className="space-y-3">
                <div>
                  <div className="text-2xl font-bold text-white">{suggestions.length}</div>
                  <div className="text-xs text-gray-500">Available suggestions</div>
                </div>
                {suggestions.length > 0 && (
                  <div className="pt-3 border-t border-white/10">
                    <div className="text-xs text-gray-500 mb-2">Type Distribution:</div>
                    <div className="flex flex-wrap gap-2">
                      {Array.from(new Set(suggestions.map(s => s.type))).map(type => (
                        <span key={type} className="px-2 py-1 bg-white/10 rounded text-xs">
                          {type}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Keyboard Shortcuts */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
              <h3 className="font-semibold mb-4 text-green-400">Shortcuts</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Completions</span>
                  <kbd className="px-2 py-1 bg-white/10 rounded text-xs">Ctrl+Space</kbd>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Close</span>
                  <kbd className="px-2 py-1 bg-white/10 rounded text-xs">Esc</kbd>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
