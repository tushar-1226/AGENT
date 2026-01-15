'use client';

import { useState, useEffect } from 'react';
import config from '@/config/api';

interface SnippetTemplate {
  name: string;
  description: string;
  code: string;
  category: string;
}

export default function CodeSnippetsPage() {
  const [languages, setLanguages] = useState<string[]>([]);
  const [selectedLanguage, setSelectedLanguage] = useState('python');
  const [templates, setTemplates] = useState<Record<string, SnippetTemplate>>({});
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [templateDetails, setTemplateDetails] = useState<SnippetTemplate | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchLanguages();
  }, []);

  useEffect(() => {
    if (selectedLanguage) {
      fetchTemplates();
    }
  }, [selectedLanguage]);

  const fetchLanguages = async () => {
    try {
      const response = await fetch(`${config.apiBaseUrl}/api/snippets/languages`);
      const data = await response.json();
      if (data.success) {
        setLanguages(data.languages);
      }
    } catch (error) {
      console.error('Failed to fetch languages:', error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${config.apiBaseUrl}/api/snippets/templates?language=${selectedLanguage}`);
      const data = await response.json();
      if (data.success) {
        setTemplates(data.templates);
      }
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    }
  };

  const fetchTemplateDetails = async (templateName: string) => {
    try {
      const response = await fetch(`${config.apiBaseUrl}/api/snippets/template/${selectedLanguage}/${templateName}`);
      const data = await response.json();
      if (data.success) {
        setTemplateDetails(data.template);
        setSelectedTemplate(templateName);
      }
    } catch (error) {
      console.error('Failed to fetch template details:', error);
    }
  };

  const copyToClipboard = () => {
    if (templateDetails) {
      navigator.clipboard.writeText(templateDetails.code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getLanguageColor = (lang: string) => {
    const colors: Record<string, string> = {
      python: 'from-blue-500 to-cyan-500',
      javascript: 'from-yellow-500 to-orange-500',
      typescript: 'from-blue-600 to-indigo-600',
      react: 'from-cyan-400 to-blue-500',
      sql: 'from-purple-500 to-pink-500',
    };
    return colors[lang] || 'from-gray-500 to-gray-600';
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
            Code Snippets Library
          </h1>
          <p className="text-gray-400">Quick access to common code patterns and templates</p>
        </div>

        <div className="grid grid-cols-4 gap-6">
          {/* Language Selector */}
          <div className="col-span-1 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Languages</h2>
            <div className="space-y-2">
              {languages.map((lang) => (
                <button
                  key={lang}
                  onClick={() => {
                    setSelectedLanguage(lang);
                    setSelectedTemplate(null);
                    setTemplateDetails(null);
                  }}
                  className={`w-full px-4 py-3 rounded-lg text-left transition-all ${
                    selectedLanguage === lang
                      ? `bg-gradient-to-r ${getLanguageColor(lang)} text-white shadow-lg`
                      : 'bg-white/5 hover:bg-white/10'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${selectedLanguage === lang ? 'bg-white' : 'bg-gray-500'}`} />
                    <span className="capitalize">{lang}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Templates List */}
          <div className="col-span-1 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Templates</h2>
            {Object.keys(templates).length > 0 ? (
              <div className="space-y-2">
                {Object.entries(templates).map(([name, template]) => (
                  <button
                    key={name}
                    onClick={() => fetchTemplateDetails(name)}
                    className={`w-full px-4 py-3 rounded-lg text-left transition-all ${
                      selectedTemplate === name
                        ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                        : 'bg-white/5 hover:bg-white/10'
                    }`}
                  >
                    <div className="font-medium">{template.name}</div>
                    <div className="text-xs text-gray-400 mt-1">{template.category}</div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="text-gray-500 text-sm">No templates available</div>
            )}
          </div>

          {/* Template Preview */}
          <div className="col-span-2 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg overflow-hidden">
            {templateDetails ? (
              <div className="flex flex-col h-full">
                {/* Template Header */}
                <div className="p-6 border-b border-white/10">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h2 className="text-2xl font-bold">{templateDetails.name}</h2>
                      <p className="text-gray-400 mt-2">{templateDetails.description}</p>
                    </div>
                    <button
                      onClick={copyToClipboard}
                      className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all flex items-center gap-2"
                    >
                      {copied ? (
                        <>
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          Copied!
                        </>
                      ) : (
                        <>
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                          Copy Code
                        </>
                      )}
                    </button>
                  </div>
                  <div className="flex gap-2">
                    <span className={`px-3 py-1 bg-gradient-to-r ${getLanguageColor(selectedLanguage)} rounded-full text-xs font-semibold`}>
                      {selectedLanguage}
                    </span>
                    <span className="px-3 py-1 bg-white/10 rounded-full text-xs">
                      {templateDetails.category}
                    </span>
                  </div>
                </div>

                {/* Code Display */}
                <div className="flex-1 p-6 overflow-auto">
                  <pre className="text-sm font-mono bg-black/50 p-6 rounded-lg overflow-x-auto">
                    <code className="text-gray-300">{templateDetails.code}</code>
                  </pre>
                </div>

                {/* Usage Hints */}
                <div className="p-6 border-t border-white/10 bg-white/5">
                  <h3 className="font-semibold mb-2 flex items-center gap-2">
                    <svg className="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Usage Tips
                  </h3>
                  <ul className="text-sm text-gray-400 space-y-1">
                    <li>• Click "Copy Code" to copy the template to your clipboard</li>
                    <li>• Replace placeholder values with your actual data</li>
                    <li>• Customize the code to fit your specific needs</li>
                  </ul>
                </div>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center p-12">
                <div className="text-center">
                  <svg className="w-24 h-24 mx-auto mb-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                  <h3 className="text-xl font-semibold text-gray-400 mb-2">Select a Template</h3>
                  <p className="text-gray-600">Choose a template from the list to view its code</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="mt-8 grid grid-cols-3 gap-6">
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-lg">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <div className="text-2xl font-bold">{Object.keys(templates).length}</div>
                <div className="text-sm text-gray-400">Templates Available</div>
              </div>
            </div>
          </div>

          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
              </div>
              <div>
                <div className="text-2xl font-bold">{languages.length}</div>
                <div className="text-sm text-gray-400">Languages Supported</div>
              </div>
            </div>
          </div>

          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-gradient-to-r from-yellow-600 to-orange-600 rounded-lg">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <div className="text-2xl font-bold">Instant</div>
                <div className="text-sm text-gray-400">Copy & Paste</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
