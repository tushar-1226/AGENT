'use client';

import { useState, useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import {
  Play,
  Save,
  FileText,
  Plus,
  X,
  Terminal as TerminalIcon,
  Settings,
  Download,
  Upload,
  FolderOpen,
  Code2,
  Maximize2,
  Minimize2
} from 'lucide-react';

interface Tab {
  id: string;
  name: string;
  language: string;
  content: string;
}

const LANGUAGE_OPTIONS = [
  { value: 'javascript', label: 'JavaScript', extension: '.js' },
  { value: 'typescript', label: 'TypeScript', extension: '.ts' },
  { value: 'python', label: 'Python', extension: '.py' },
  { value: 'java', label: 'Java', extension: '.java' },
  { value: 'cpp', label: 'C++', extension: '.cpp' },
  { value: 'c', label: 'C', extension: '.c' },
  { value: 'csharp', label: 'C#', extension: '.cs' },
  { value: 'go', label: 'Go', extension: '.go' },
  { value: 'rust', label: 'Rust', extension: '.rs' },
  { value: 'html', label: 'HTML', extension: '.html' },
  { value: 'css', label: 'CSS', extension: '.css' },
  { value: 'json', label: 'JSON', extension: '.json' },
  { value: 'markdown', label: 'Markdown', extension: '.md' },
  { value: 'sql', label: 'SQL', extension: '.sql' },
  { value: 'php', label: 'PHP', extension: '.php' },
  { value: 'ruby', label: 'Ruby', extension: '.rb' },
  { value: 'swift', label: 'Swift', extension: '.swift' },
  { value: 'kotlin', label: 'Kotlin', extension: '.kt' },
  { value: 'yaml', label: 'YAML', extension: '.yaml' },
  { value: 'xml', label: 'XML', extension: '.xml' },
];

const THEMES = [
  { value: 'vs-dark', label: 'Dark' },
  { value: 'light', label: 'Light' },
  { value: 'hc-black', label: 'High Contrast' },
];

export default function CodeIDE() {
  const [tabs, setTabs] = useState<Tab[]>([
    {
      id: '1',
      name: 'main.js',
      language: 'javascript',
      content: '// Welcome to Friday Code IDE\n// Start coding here!\n\nconsole.log("Hello, World!");'
    }
  ]);
  const [activeTab, setActiveTab] = useState('1');
  const [theme, setTheme] = useState('vs-dark');
  const [fontSize, setFontSize] = useState(14);
  const [terminalOutput, setTerminalOutput] = useState<string[]>(['Terminal ready. Type commands here...']);
  const [terminalInput, setTerminalInput] = useState('');
  const [showTerminal, setShowTerminal] = useState(true);
  const [terminalHeight, setTerminalHeight] = useState(250);
  const [isResizing, setIsResizing] = useState(false);
  const terminalRef = useRef<HTMLDivElement>(null);
  const editorRef = useRef<any>(null);

  const currentTab = tabs.find(tab => tab.id === activeTab);

  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor;
  };

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      setTabs(tabs.map(tab =>
        tab.id === activeTab ? { ...tab, content: value } : tab
      ));
    }
  };

  const createNewTab = () => {
    const newId = Date.now().toString();
    const newTab: Tab = {
      id: newId,
      name: `untitled-${tabs.length + 1}.js`,
      language: 'javascript',
      content: ''
    };
    setTabs([...tabs, newTab]);
    setActiveTab(newId);
  };

  const closeTab = (id: string) => {
    if (tabs.length === 1) return; // Don't close the last tab
    const newTabs = tabs.filter(tab => tab.id !== id);
    setTabs(newTabs);
    if (activeTab === id) {
      setActiveTab(newTabs[0].id);
    }
  };

  const changeLanguage = (tabId: string, language: string) => {
    const langOption = LANGUAGE_OPTIONS.find(l => l.value === language);
    setTabs(tabs.map(tab => {
      if (tab.id === tabId) {
        const baseName = tab.name.replace(/\.[^/.]+$/, '');
        return {
          ...tab,
          language,
          name: baseName + (langOption?.extension || '.txt')
        };
      }
      return tab;
    }));
  };

  const runCode = async () => {
    if (!currentTab) return;

    setTerminalOutput(prev => [...prev, `\n> Running ${currentTab.name}...`]);

    try {
      const response = await fetch('http://localhost:8000/api/execute-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: currentTab.content,
          language: currentTab.language
        })
      });

      const data = await response.json();
      setTerminalOutput(prev => [...prev, data.output || data.error || 'Code executed']);
    } catch (error) {
      setTerminalOutput(prev => [...prev, `Error: ${error}`]);
    }
  };

  const saveFile = () => {
    if (!currentTab) return;
    const blob = new Blob([currentTab.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = currentTab.name;
    a.click();
    URL.revokeObjectURL(url);
    setTerminalOutput(prev => [...prev, `✓ Saved ${currentTab.name}`]);
  };

  const loadFile = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      const extension = file.name.split('.').pop() || '';
      const language = LANGUAGE_OPTIONS.find(l => l.extension === `.${extension}`)?.value || 'javascript';

      const newId = Date.now().toString();
      const newTab: Tab = {
        id: newId,
        name: file.name,
        language,
        content
      };
      setTabs([...tabs, newTab]);
      setActiveTab(newId);
      setTerminalOutput(prev => [...prev, `✓ Loaded ${file.name}`]);
    };
    reader.readAsText(file);
  };

  const handleTerminalCommand = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!terminalInput.trim()) return;

    setTerminalOutput(prev => [...prev, `$ ${terminalInput}`]);

    if (terminalInput === 'clear') {
      setTerminalOutput([]);
      setTerminalInput('');
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/terminal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: terminalInput })
      });

      const data = await response.json();
      setTerminalOutput(prev => [...prev, data.output || data.error || '']);
    } catch (error) {
      setTerminalOutput(prev => [...prev, `Command not supported in web terminal: ${terminalInput}`]);
    }

    setTerminalInput('');
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsResizing(true);
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;
      const newHeight = window.innerHeight - e.clientY;
      if (newHeight > 100 && newHeight < 600) {
        setTerminalHeight(newHeight);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [terminalOutput]);

  return (
    <div className="h-screen flex flex-col bg-[#1e1e1e] text-white">
      {/* Top Toolbar */}
      <div className="flex items-center justify-between bg-[#2d2d30] border-b border-[#3e3e42] px-4 py-2">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Code2 className="w-5 h-5 text-blue-400" />
            <h1 className="text-lg font-semibold">Friday Code IDE</h1>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={createNewTab}
              className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded transition"
              title="New File"
            >
              <Plus className="w-4 h-4" />
              <span className="text-sm">New</span>
            </button>

            <label className="flex items-center gap-1 px-3 py-1.5 bg-green-600 hover:bg-green-700 rounded transition cursor-pointer">
              <Upload className="w-4 h-4" />
              <span className="text-sm">Open</span>
              <input
                type="file"
                onChange={loadFile}
                className="hidden"
                accept=".js,.ts,.py,.java,.cpp,.c,.cs,.go,.rs,.html,.css,.json,.md,.sql,.php,.rb,.swift,.kt,.yaml,.xml,.txt"
              />
            </label>

            <button
              onClick={saveFile}
              className="flex items-center gap-1 px-3 py-1.5 bg-purple-600 hover:bg-purple-700 rounded transition"
              title="Save File"
            >
              <Save className="w-4 h-4" />
              <span className="text-sm">Save</span>
            </button>

            <button
              onClick={runCode}
              className="flex items-center gap-1 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 rounded transition"
              title="Run Code"
            >
              <Play className="w-4 h-4" />
              <span className="text-sm">Run</span>
            </button>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-400">Theme:</label>
            <select
              value={theme}
              onChange={(e) => setTheme(e.target.value)}
              className="bg-[#3c3c3c] border border-[#555] rounded px-2 py-1 text-sm"
            >
              {THEMES.map(t => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-400">Font Size:</label>
            <input
              type="number"
              value={fontSize}
              onChange={(e) => setFontSize(Number(e.target.value))}
              min="10"
              max="24"
              className="w-16 bg-[#3c3c3c] border border-[#555] rounded px-2 py-1 text-sm"
            />
          </div>

          <button
            onClick={() => setShowTerminal(!showTerminal)}
            className={`flex items-center gap-1 px-3 py-1.5 rounded transition ${
              showTerminal ? 'bg-blue-600 hover:bg-blue-700' : 'bg-[#3c3c3c] hover:bg-[#4c4c4c]'
            }`}
            title="Toggle Terminal"
          >
            <TerminalIcon className="w-4 h-4" />
            <span className="text-sm">Terminal</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center bg-[#2d2d30] border-b border-[#3e3e42] overflow-x-auto">
        {tabs.map(tab => (
          <div
            key={tab.id}
            className={`flex items-center gap-2 px-4 py-2 border-r border-[#3e3e42] cursor-pointer transition ${
              activeTab === tab.id
                ? 'bg-[#1e1e1e] text-white'
                : 'bg-[#2d2d30] text-gray-400 hover:bg-[#3e3e42]'
            }`}
            onClick={() => setActiveTab(tab.id)}
          >
            <FileText className="w-4 h-4" />
            <span className="text-sm whitespace-nowrap">{tab.name}</span>
            <select
              value={tab.language}
              onChange={(e) => {
                e.stopPropagation();
                changeLanguage(tab.id, e.target.value);
              }}
              className="text-xs bg-[#3c3c3c] border border-[#555] rounded px-1 py-0.5"
              onClick={(e) => e.stopPropagation()}
            >
              {LANGUAGE_OPTIONS.map(lang => (
                <option key={lang.value} value={lang.value}>{lang.label}</option>
              ))}
            </select>
            {tabs.length > 1 && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  closeTab(tab.id);
                }}
                className="hover:bg-red-600 rounded p-0.5 transition"
              >
                <X className="w-3 h-3" />
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Editor */}
      <div className="flex-1 overflow-hidden">
        <Editor
          height="100%"
          language={currentTab?.language}
          value={currentTab?.content}
          theme={theme}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
          options={{
            fontSize,
            minimap: { enabled: true },
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            wordWrap: 'on',
            lineNumbers: 'on',
            renderWhitespace: 'selection',
            bracketPairColorization: { enabled: true },
            guides: {
              bracketPairs: true,
              indentation: true
            },
            suggestOnTriggerCharacters: true,
            quickSuggestions: true,
            formatOnPaste: true,
            formatOnType: true,
          }}
        />
      </div>

      {/* Terminal */}
      {showTerminal && (
        <div className="border-t border-[#3e3e42]" style={{ height: `${terminalHeight}px` }}>
          {/* Resize Handle */}
          <div
            className="h-1 bg-[#3e3e42] hover:bg-blue-500 cursor-ns-resize transition"
            onMouseDown={handleMouseDown}
          />

          <div className="h-full flex flex-col bg-[#1e1e1e]">
            {/* Terminal Header */}
            <div className="flex items-center justify-between bg-[#2d2d30] px-4 py-2 border-b border-[#3e3e42]">
              <div className="flex items-center gap-2">
                <TerminalIcon className="w-4 h-4 text-green-400" />
                <span className="text-sm font-semibold">Terminal</span>
              </div>
              <button
                onClick={() => setTerminalOutput([])}
                className="text-xs px-2 py-1 bg-[#3c3c3c] hover:bg-[#4c4c4c] rounded transition"
              >
                Clear
              </button>
            </div>

            {/* Terminal Output */}
            <div
              ref={terminalRef}
              className="flex-1 overflow-y-auto px-4 py-2 font-mono text-sm"
            >
              {terminalOutput.map((line, i) => (
                <div key={i} className={line.startsWith('$') ? 'text-green-400' : 'text-gray-300'}>
                  {line}
                </div>
              ))}
            </div>

            {/* Terminal Input */}
            <form onSubmit={handleTerminalCommand} className="border-t border-[#3e3e42] px-4 py-2">
              <div className="flex items-center gap-2">
                <span className="text-green-400 font-mono">$</span>
                <input
                  type="text"
                  value={terminalInput}
                  onChange={(e) => setTerminalInput(e.target.value)}
                  className="flex-1 bg-transparent outline-none font-mono text-sm"
                  placeholder="Type command here..."
                  autoComplete="off"
                />
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
