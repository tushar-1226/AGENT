'use client';

import { useState, useEffect } from 'react';
import { Users, Share2, MessageSquare, Code, Star, Search } from 'lucide-react';

interface CollaborativeSession {
  session_id: string;
  name: string;
  owner_id: string;
  participants: Record<string, string>;
  active_file: string | null;
  is_active: boolean;
}

interface TeamSnippet {
  snippet_id: string;
  title: string;
  description: string;
  code: string;
  language: string;
  tags: string[];
  author_id: string;
  usage_count: number;
  ratings: Record<string, number>;
}

export default function CollaborativeFeatures() {
  const [sessions, setSessions] = useState<CollaborativeSession[]>([]);
  const [snippets, setSnippets] = useState<TeamSnippet[]>([]);
  const [activeTab, setActiveTab] = useState<'sessions' | 'reviews' | 'snippets'>('sessions');
  const [loading, setLoading] = useState(false);

  // Create new collaborative session
  const createSession = async (name: string, description: string) => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/collab/session/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          description,
          owner_id: 'user_123', // Replace with actual user ID
        }),
      });
      const data = await response.json();
      if (data.success) {
        // Refresh sessions list
        loadActiveSessions();
      }
    } catch (error) {
      console.error('Error creating session:', error);
    } finally {
      setLoading(false);
    }
  };

  // Load active sessions
  const loadActiveSessions = async () => {
    try {
      // This would call the appropriate API endpoint
      // Placeholder for now
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  // Create team snippet
  const createSnippet = async (snippet: Partial<TeamSnippet>) => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/collab/snippet/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...snippet,
          author_id: 'user_123', // Replace with actual user ID
        }),
      });
      const data = await response.json();
      if (data.success) {
        loadSnippets();
      }
    } catch (error) {
      console.error('Error creating snippet:', error);
    } finally {
      setLoading(false);
    }
  };

  // Search team snippets
  const searchSnippets = async (query: string, tags?: string[], language?: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/collab/snippet/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, tags, language }),
      });
      const data = await response.json();
      if (data.success) {
        setSnippets(data.results);
      }
    } catch (error) {
      console.error('Error searching snippets:', error);
    }
  };

  const loadSnippets = async () => {
    await searchSnippets(''); // Load all snippets
  };

  useEffect(() => {
    loadActiveSessions();
    loadSnippets();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Collaborative Workspace
          </h1>
          <p className="text-gray-400">
            Real-time collaboration, code reviews, and team knowledge sharing
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-6">
          {['sessions', 'reviews', 'snippets'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`px-6 py-3 rounded-lg font-medium transition-all ${
                activeTab === tab
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/50'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {tab === 'sessions' && <Users className="inline-block w-5 h-5 mr-2" />}
              {tab === 'reviews' && <MessageSquare className="inline-block w-5 h-5 mr-2" />}
              {tab === 'snippets' && <Code className="inline-block w-5 h-5 mr-2" />}
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
          {activeTab === 'sessions' && (
            <SessionsTab sessions={sessions} onCreateSession={createSession} loading={loading} />
          )}
          {activeTab === 'reviews' && <ReviewsTab />}
          {activeTab === 'snippets' && (
            <SnippetsTab
              snippets={snippets}
              onCreateSnippet={createSnippet}
              onSearch={searchSnippets}
              loading={loading}
            />
          )}
        </div>
      </div>
    </div>
  );
}

// Sessions Tab Component
function SessionsTab({
  sessions,
  onCreateSession,
  loading,
}: {
  sessions: CollaborativeSession[];
  onCreateSession: (name: string, description: string) => void;
  loading: boolean;
}) {
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  const handleCreate = () => {
    if (name.trim()) {
      onCreateSession(name, description);
      setName('');
      setDescription('');
      setShowCreate(false);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Active Sessions</h2>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition"
        >
          + New Session
        </button>
      </div>

      {showCreate && (
        <div className="mb-6 p-4 bg-gray-700 rounded-lg">
          <input
            type="text"
            placeholder="Session name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full mb-3 px-4 py-2 bg-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <textarea
            placeholder="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full mb-3 px-4 py-2 bg-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
          />
          <div className="flex gap-2">
            <button
              onClick={handleCreate}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition disabled:opacity-50"
            >
              Create
            </button>
            <button
              onClick={() => setShowCreate(false)}
              className="px-4 py-2 bg-gray-600 hover:bg-gray-500 rounded-lg transition"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="grid gap-4">
        {sessions.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <Users className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p>No active sessions. Create one to get started!</p>
          </div>
        ) : (
          sessions.map((session) => (
            <div key={session.session_id} className="p-4 bg-gray-700 rounded-lg hover:bg-gray-650 transition">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-semibold">{session.name}</h3>
                  <p className="text-gray-400 text-sm">
                    {Object.keys(session.participants).length} participant(s)
                  </p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs ${session.is_active ? 'bg-green-600' : 'bg-gray-600'}`}>
                  {session.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <button className="mt-3 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm transition">
                <Share2 className="w-4 h-4 inline-block mr-2" />
                Join Session
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

// Reviews Tab Component
function ReviewsTab() {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Code Reviews</h2>
      <div className="text-center py-12 text-gray-400">
        <MessageSquare className="w-16 h-16 mx-auto mb-4 opacity-50" />
        <p>Code review feature coming soon!</p>
      </div>
    </div>
  );
}

// Snippets Tab Component
function SnippetsTab({
  snippets,
  onCreateSnippet,
  onSearch,
  loading,
}: {
  snippets: TeamSnippet[];
  onCreateSnippet: (snippet: Partial<TeamSnippet>) => void;
  onSearch: (query: string, tags?: string[], language?: string) => void;
  loading: boolean;
}) {
  const [showCreate, setShowCreate] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [newSnippet, setNewSnippet] = useState({
    title: '',
    description: '',
    code: '',
    language: 'python',
    tags: [] as string[],
  });

  const handleCreate = () => {
    if (newSnippet.title.trim() && newSnippet.code.trim()) {
      onCreateSnippet(newSnippet);
      setNewSnippet({ title: '', description: '', code: '', language: 'python', tags: [] });
      setShowCreate(false);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Team Knowledge Base</h2>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition"
        >
          + New Snippet
        </button>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search snippets..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              onSearch(e.target.value);
            }}
            className="w-full pl-12 pr-4 py-3 bg-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {showCreate && (
        <div className="mb-6 p-4 bg-gray-700 rounded-lg">
          <input
            type="text"
            placeholder="Snippet title"
            value={newSnippet.title}
            onChange={(e) => setNewSnippet({ ...newSnippet, title: e.target.value })}
            className="w-full mb-3 px-4 py-2 bg-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <textarea
            placeholder="Description"
            value={newSnippet.description}
            onChange={(e) => setNewSnippet({ ...newSnippet, description: e.target.value })}
            className="w-full mb-3 px-4 py-2 bg-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={2}
          />
          <textarea
            placeholder="Code"
            value={newSnippet.code}
            onChange={(e) => setNewSnippet({ ...newSnippet, code: e.target.value })}
            className="w-full mb-3 px-4 py-2 bg-gray-600 rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={8}
          />
          <select
            value={newSnippet.language}
            onChange={(e) => setNewSnippet({ ...newSnippet, language: e.target.value })}
            className="w-full mb-3 px-4 py-2 bg-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="java">Java</option>
            <option value="go">Go</option>
          </select>
          <div className="flex gap-2">
            <button
              onClick={handleCreate}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition disabled:opacity-50"
            >
              Save Snippet
            </button>
            <button
              onClick={() => setShowCreate(false)}
              className="px-4 py-2 bg-gray-600 hover:bg-gray-500 rounded-lg transition"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="grid gap-4">
        {snippets.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <Code className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p>No snippets found. Create one to start building your team's knowledge base!</p>
          </div>
        ) : (
          snippets.map((snippet) => (
            <div key={snippet.snippet_id} className="p-4 bg-gray-700 rounded-lg">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-semibold">{snippet.title}</h3>
                <span className="px-3 py-1 bg-gray-600 rounded-full text-xs">{snippet.language}</span>
              </div>
              <p className="text-gray-400 text-sm mb-3">{snippet.description}</p>
              <pre className="bg-gray-900 p-3 rounded-lg text-sm overflow-x-auto mb-3">
                <code>{snippet.code}</code>
              </pre>
              <div className="flex justify-between items-center">
                <div className="flex gap-2">
                  {snippet.tags.map((tag) => (
                    <span key={tag} className="px-2 py-1 bg-blue-600 rounded text-xs">
                      {tag}
                    </span>
                  ))}
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-400">
                  <span>
                    <Star className="w-4 h-4 inline-block mr-1" />
                    {Object.keys(snippet.ratings).length} ratings
                  </span>
                  <span>{snippet.usage_count} uses</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
