'use client';

import { useState } from 'react';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    theme: 'dark',
    notifications: true,
    autoSave: true,
    language: 'en',
    fontSize: 'medium',
    apiKey: '',
    showTips: true,
  });

  const handleChange = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = () => {
    // Save settings to localStorage or backend
    localStorage.setItem('appSettings', JSON.stringify(settings));
    alert('Settings saved successfully!');
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-gray-400 mb-8">Manage your application preferences</p>

        <div className="space-y-6">
          {/* Appearance Section */}
          <div className="bg-[#1a1a1a] rounded-lg p-6 border border-gray-800">
            <h2 className="text-xl font-semibold mb-4">Appearance</h2>

            <div className="space-y-4">
              {/* Theme */}
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium">Theme</label>
                  <p className="text-xs text-gray-400">Choose your preferred theme</p>
                </div>
                <select
                  value={settings.theme}
                  onChange={(e) => handleChange('theme', e.target.value)}
                  className="bg-[#0a0a0a] border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
                >
                  <option value="dark">Dark</option>
                  <option value="light">Light</option>
                  <option value="auto">Auto</option>
                </select>
              </div>

              {/* Font Size */}
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium">Font Size</label>
                  <p className="text-xs text-gray-400">Adjust text size</p>
                </div>
                <select
                  value={settings.fontSize}
                  onChange={(e) => handleChange('fontSize', e.target.value)}
                  className="bg-[#0a0a0a] border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
                >
                  <option value="small">Small</option>
                  <option value="medium">Medium</option>
                  <option value="large">Large</option>
                </select>
              </div>
            </div>
          </div>

          {/* General Section */}
          <div className="bg-[#1a1a1a] rounded-lg p-6 border border-gray-800">
            <h2 className="text-xl font-semibold mb-4">General</h2>

            <div className="space-y-4">
              {/* Language */}
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium">Language</label>
                  <p className="text-xs text-gray-400">Select your language</p>
                </div>
                <select
                  value={settings.language}
                  onChange={(e) => handleChange('language', e.target.value)}
                  className="bg-[#0a0a0a] border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </select>
              </div>

              {/* Auto Save */}
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium">Auto Save</label>
                  <p className="text-xs text-gray-400">Automatically save your work</p>
                </div>
                <button
                  onClick={() => handleChange('autoSave', !settings.autoSave)}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    settings.autoSave ? 'bg-blue-500' : 'bg-gray-700'
                  }`}
                >
                  <span
                    className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
                      settings.autoSave ? 'translate-x-6' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>

              {/* Show Tips */}
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium">Show Tips</label>
                  <p className="text-xs text-gray-400">Display helpful tips and hints</p>
                </div>
                <button
                  onClick={() => handleChange('showTips', !settings.showTips)}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    settings.showTips ? 'bg-blue-500' : 'bg-gray-700'
                  }`}
                >
                  <span
                    className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
                      settings.showTips ? 'translate-x-6' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>
            </div>
          </div>

          {/* Notifications Section */}
          <div className="bg-[#1a1a1a] rounded-lg p-6 border border-gray-800">
            <h2 className="text-xl font-semibold mb-4">Notifications</h2>

            <div className="space-y-4">
              {/* Enable Notifications */}
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium">Enable Notifications</label>
                  <p className="text-xs text-gray-400">Receive system notifications</p>
                </div>
                <button
                  onClick={() => handleChange('notifications', !settings.notifications)}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    settings.notifications ? 'bg-blue-500' : 'bg-gray-700'
                  }`}
                >
                  <span
                    className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
                      settings.notifications ? 'translate-x-6' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>
            </div>
          </div>

          {/* API Configuration */}
          <div className="bg-[#1a1a1a] rounded-lg p-6 border border-gray-800">
            <h2 className="text-xl font-semibold mb-4">API Configuration</h2>

            <div className="space-y-4">
              {/* API Key */}
              <div>
                <label className="text-sm font-medium block mb-2">API Key</label>
                <input
                  type="password"
                  value={settings.apiKey}
                  onChange={(e) => handleChange('apiKey', e.target.value)}
                  placeholder="Enter your API key"
                  className="w-full bg-[#0a0a0a] border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
                />
                <p className="text-xs text-gray-400 mt-1">Your API key for external services</p>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end gap-4">
            <button
              onClick={() => window.history.back()}
              className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-6 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg transition-colors"
            >
              Save Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
