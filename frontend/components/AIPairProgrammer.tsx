'use client';

import { useState, useEffect, useRef } from 'react';
import { Lightbulb, Code2, Zap, CheckCircle, XCircle, TrendingUp } from 'lucide-react';
import Editor from '@monaco-editor/react';

interface CodeSuggestion {
  id: string;
  type: string;
  code: string;
  explanation: string;
  confidence: number;
  line_start: number;
  line_end: number;
  priority: string;
}

interface NextStep {
  step: string;
  priority: string;
  reason: string;
}

export default function AIPairProgrammer() {
  const [code, setCode] = useState('# Start coding...\n');
  const [suggestions, setSuggestions] = useState<CodeSuggestion[]>([]);
  const [nextSteps, setNextSteps] = useState<NextStep[]>([]);
  const [loading, setLoading] = useState(false);
  const [completionPercentage, setCompletionPercentage] = useState(0);
  const [selectedLanguage, setSelectedLanguage] = useState('python');
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);

  // Get live suggestions as user types
  const getSuggestions = async (currentCode: string, triggerType = 'typing') => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/pair-programmer/suggestions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code_context: {
            code: currentCode,
            file_path: 'current_file.' + (selectedLanguage === 'javascript' ? 'js' : selectedLanguage),
            language: selectedLanguage,
            cursor_position: { line: currentCode.split('\n').length, column: 0 },
          },
          trigger_type: triggerType,
        }),
      });
      const data = await response.json();
      if (data.success) {
        setSuggestions(data.suggestions || []);
      }
    } catch (error) {
      console.error('Error getting suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  // Get next steps recommendation
  const getNextSteps = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/pair-programmer/next-steps', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          context: {
            code,
            file_path: 'current_file.' + (selectedLanguage === 'javascript' ? 'js' : selectedLanguage),
            language: selectedLanguage,
            cursor_position: { line: code.split('\n').length, column: 0 },
          },
        }),
      });
      const data = await response.json();
      if (data.success) {
        setNextSteps(data.next_steps || []);
        setCompletionPercentage(data.completion_percentage || 0);
      }
    } catch (error) {
      console.error('Error getting next steps:', error);
    }
  };

  // Debounced code change handler
  const handleCodeChange = (value: string | undefined) => {
    if (value !== undefined) {
      setCode(value);
      
      // Clear existing timer
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }

      // Set new timer for suggestions
      debounceTimer.current = setTimeout(() => {
        getSuggestions(value);
      }, 1500); // Wait 1.5 seconds after user stops typing
    }
  };

  // Apply suggestion
  const applySuggestion = async (suggestion: CodeSuggestion, accepted: boolean) => {
    if (accepted) {
      // In a real implementation, this would insert the suggestion at the correct line
      setCode(code + '\n\n# Suggestion applied:\n' + suggestion.code);
    }

    // Send feedback
    try {
      await fetch('http://localhost:8000/api/pair-programmer/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          suggestion_id: suggestion.id,
          accepted,
          user_id: 'user_123',
        }),
      });
    } catch (error) {
      console.error('Error sending feedback:', error);
    }

    // Remove suggestion from list
    setSuggestions(suggestions.filter((s) => s.id !== suggestion.id));
  };

  useEffect(() => {
    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
            AI Pair Programmer
          </h1>
          <p className="text-gray-400">
            Real-time code suggestions, error detection, and best practices as you type
          </p>
        </div>

        <div className="grid grid-cols-3 gap-6">
          {/* Main Code Editor */}
          <div className="col-span-2 bg-gray-800 rounded-xl p-6 shadow-2xl">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Code Editor</h2>
              <div className="flex items-center gap-4">
                <select
                  value={selectedLanguage}
                  onChange={(e) => setSelectedLanguage(e.target.value)}
                  className="px-4 py-2 bg-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript</option>
                  <option value="typescript">TypeScript</option>
                  <option value="java">Java</option>
                </select>
                <button
                  onClick={() => getSuggestions(code, 'manual')}
                  disabled={loading}
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition disabled:opacity-50"
                >
                  {loading ? 'Analyzing...' : 'Get Suggestions'}
                </button>
                <button
                  onClick={getNextSteps}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition"
                >
                  Next Steps
                </button>
              </div>
            </div>

            {/* Monaco Editor */}
            <div className="rounded-lg overflow-hidden border border-gray-700">
              <Editor
                height="600px"
                defaultLanguage={selectedLanguage}
                language={selectedLanguage}
                value={code}
                onChange={handleCodeChange}
                theme="vs-dark"
                options={{
                  minimap: { enabled: true },
                  fontSize: 14,
                  lineNumbers: 'on',
                  roundedSelection: false,
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                }}
              />
            </div>

            {/* Completion Progress */}
            <div className="mt-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-400">Code Completion</span>
                <span className="text-sm font-bold">{completionPercentage}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${completionPercentage}%` }}
                />
              </div>
            </div>
          </div>

          {/* Suggestions Panel */}
          <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
            <h2 className="text-xl font-bold mb-4 flex items-center">
              <Lightbulb className="w-6 h-6 mr-2 text-yellow-400" />
              Suggestions
            </h2>

            {loading && (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
                <p className="text-gray-400 mt-4">Analyzing code...</p>
              </div>
            )}

            <div className="space-y-4 max-h-[600px] overflow-y-auto">
              {suggestions.length === 0 && !loading && (
                <div className="text-center py-12 text-gray-400">
                  <Code2 className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>Start typing to get AI-powered suggestions!</p>
                </div>
              )}

              {suggestions.map((suggestion) => (
                <SuggestionCard
                  key={suggestion.id}
                  suggestion={suggestion}
                  onApply={(accepted) => applySuggestion(suggestion, accepted)}
                />
              ))}
            </div>

            {/* Next Steps */}
            {nextSteps.length > 0 && (
              <div className="mt-6 pt-6 border-t border-gray-700">
                <h3 className="text-lg font-bold mb-3 flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-blue-400" />
                  Recommended Next Steps
                </h3>
                <div className="space-y-2">
                  {nextSteps.map((step, index) => (
                    <div key={index} className="p-3 bg-gray-700 rounded-lg">
                      <div className="flex justify-between items-start mb-1">
                        <span className="font-medium text-sm">{step.step}</span>
                        <span
                          className={`px-2 py-1 rounded text-xs ${
                            step.priority === 'high'
                              ? 'bg-red-600'
                              : step.priority === 'medium'
                              ? 'bg-yellow-600'
                              : 'bg-green-600'
                          }`}
                        >
                          {step.priority}
                        </span>
                      </div>
                      <p className="text-xs text-gray-400">{step.reason}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Suggestion Card Component
function SuggestionCard({
  suggestion,
  onApply,
}: {
  suggestion: CodeSuggestion;
  onApply: (accepted: boolean) => void;
}) {
  const typeColors = {
    completion: 'bg-blue-600',
    refactor: 'bg-purple-600',
    fix: 'bg-red-600',
    optimization: 'bg-green-600',
    documentation: 'bg-yellow-600',
  };

  const priorityIcons = {
    critical: '🔴',
    high: '🟠',
    medium: '🟡',
    low: '🟢',
  };

  return (
    <div className="p-4 bg-gray-700 rounded-lg border border-gray-600 hover:border-purple-500 transition">
      <div className="flex justify-between items-start mb-2">
        <span className={`px-2 py-1 rounded text-xs ${typeColors[suggestion.type as keyof typeof typeColors] || 'bg-gray-600'}`}>
          {suggestion.type}
        </span>
        <div className="flex items-center gap-2">
          <span className="text-xs">
            {priorityIcons[suggestion.priority as keyof typeof priorityIcons]} {suggestion.priority}
          </span>
          <span className="text-xs text-gray-400">
            {Math.round(suggestion.confidence * 100)}% confident
          </span>
        </div>
      </div>

      <p className="text-sm mb-3 text-gray-300">{suggestion.explanation}</p>

      {suggestion.code && (
        <pre className="bg-gray-900 p-3 rounded text-xs overflow-x-auto mb-3">
          <code>{suggestion.code}</code>
        </pre>
      )}

      <div className="flex gap-2">
        <button
          onClick={() => onApply(true)}
          className="flex-1 px-3 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm transition flex items-center justify-center gap-2"
        >
          <CheckCircle className="w-4 h-4" />
          Apply
        </button>
        <button
          onClick={() => onApply(false)}
          className="flex-1 px-3 py-2 bg-gray-600 hover:bg-gray-500 rounded-lg text-sm transition flex items-center justify-center gap-2"
        >
          <XCircle className="w-4 h-4" />
          Dismiss
        </button>
      </div>
    </div>
  );
}
