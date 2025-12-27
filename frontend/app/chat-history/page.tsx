'use client';

import { useState, useEffect } from 'react';

interface ChatMessage {
  id: number;
  message: string;
  response: string;
  project_id: number | null;
  user_id: number;
  created_at: string;
  project_name?: string;
}

export default function ChatHistoryPage() {
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<ChatMessage[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'recent'>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchChatHistory();
  }, []);

  const fetchChatHistory = async () => {
    try {
      const userData = localStorage.getItem('user');
      if (!userData) return;

      const user = JSON.parse(userData);
      const response = await fetch(`http://localhost:8000/api/chat/history?user_id=${user.id}&limit=100`);
      const data = await response.json();

      if (data.history) {
        setChatHistory(data.history);
      }
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
    } finally {
      setLoading(false);
    }
  };

  const searchChat = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }

    try {
      setIsSearching(true);
      const userData = localStorage.getItem('user');
      if (!userData) return;

      const user = JSON.parse(userData);
      const response = await fetch(
        `http://localhost:8000/api/chat/search?q=${encodeURIComponent(searchQuery)}&user_id=${user.id}&limit=50`
      );
      const data = await response.json();

      if (data.results) {
        setSearchResults(data.results);
      }
    } catch (error) {
      console.error('Failed to search chat history:', error);
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchQuery(value);

    if (!value.trim()) {
      setSearchResults([]);
      setIsSearching(false);
    }
  };

  const handleSearchKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      searchChat();
    }
  };

  const displayMessages = isSearching && searchQuery.trim() ? searchResults : chatHistory;

  const filteredMessages = selectedFilter === 'recent'
    ? displayMessages.slice(0, 20)
    : displayMessages;

  const highlightText = (text: string, query: string) => {
    if (!query.trim() || !isSearching) return text;

    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, index) =>
      part.toLowerCase() === query.toLowerCase()
        ? <span key={index} className="bg-yellow-500/30 text-yellow-300">{part}</span>
        : part
    );
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Chat History</h1>
          <p className="text-gray-400">Search and browse your conversation history</p>
        </div>

        {/* Search Bar */}
        <div className="mb-6 flex gap-4">
          <div className="flex-1 relative">
            <input
              type="text"
              placeholder="Search messages..."
              value={searchQuery}
              onChange={handleSearchChange}
              onKeyPress={handleSearchKeyPress}
              className="w-full px-4 py-3 pl-12 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
            />
            <svg
              className="w-5 h-5 absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <button
            onClick={searchChat}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200"
          >
            Search
          </button>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setSelectedFilter('all')}
            className={`px-4 py-2 rounded-lg transition-all ${
              selectedFilter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-white/5 text-gray-400 hover:bg-white/10'
            }`}
          >
            All Messages
          </button>
          <button
            onClick={() => setSelectedFilter('recent')}
            className={`px-4 py-2 rounded-lg transition-all ${
              selectedFilter === 'recent'
                ? 'bg-blue-600 text-white'
                : 'bg-white/5 text-gray-400 hover:bg-white/10'
            }`}
          >
            Recent (20)
          </button>
        </div>

        {/* Results Info */}
        {isSearching && searchQuery.trim() && (
          <div className="mb-4 text-gray-400">
            Found {searchResults.length} result{searchResults.length !== 1 ? 's' : ''} for "{searchQuery}"
          </div>
        )}

        {/* Chat Messages */}
        <div className="space-y-4">
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-gray-400 mt-4">Loading chat history...</p>
            </div>
          ) : filteredMessages.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-400 text-lg">
                {isSearching && searchQuery.trim()
                  ? 'No messages found matching your search'
                  : 'No chat history yet'}
              </p>
            </div>
          ) : (
            filteredMessages.map((chat) => (
              <div
                key={chat.id}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-all duration-200"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <span className="font-medium">You</span>
                  </div>
                  <span className="text-sm text-gray-500">
                    {new Date(chat.created_at).toLocaleString()}
                  </span>
                </div>

                <div className="mb-4">
                  <p className="text-gray-300">
                    {highlightText(chat.message, searchQuery)}
                  </p>
                </div>

                {chat.response && (
                  <div className="border-l-2 border-purple-600 pl-4">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-6 h-6 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                      </div>
                      <span className="font-medium text-sm text-purple-400">AI Assistant</span>
                    </div>
                    <p className="text-gray-400 text-sm">
                      {highlightText(chat.response, searchQuery)}
                    </p>
                  </div>
                )}

                {chat.project_name && (
                  <div className="mt-4 pt-4 border-t border-white/10">
                    <span className="text-xs text-gray-500">
                      Project: <span className="text-blue-400">{chat.project_name}</span>
                    </span>
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Export Button */}
        {filteredMessages.length > 0 && (
          <div className="mt-8 text-center">
            <button
              onClick={() => {
                const dataStr = JSON.stringify(filteredMessages, null, 2);
                const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
                const exportFileDefaultName = `chat-history-${new Date().toISOString()}.json`;

                const linkElement = document.createElement('a');
                linkElement.setAttribute('href', dataUri);
                linkElement.setAttribute('download', exportFileDefaultName);
                linkElement.click();

                const event = new CustomEvent('showToast', {
                  detail: { message: 'Chat history exported successfully', type: 'success' }
                });
                window.dispatchEvent(event);
              }}
              className="px-6 py-3 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-all inline-flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Export History
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
