
'use client';
import { useState } from 'react';
import NavigationSidebar from '../components/NavigationSidebar';

export default function SidebarLayout({ children }: { children: React.ReactNode }) {
  // Sidebar is now always visible and doesn't need toggle state
  // Keeping these for compatibility but they're not used anymore
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Always-visible rail sidebar */}
      <NavigationSidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />

      {/* Main content with left padding to account for sidebar */}
      <div className="flex-1 overflow-auto relative ml-20">
        {children}
      </div>
    </div>
  );
}
