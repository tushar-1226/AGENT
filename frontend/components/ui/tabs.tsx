'use client';
import React, { createContext, useContext } from 'react';

const TabsContext = createContext<{ value: string; onValueChange: (value: string) => void } | null>(null);

export const Tabs: React.FC<{ 
  children: React.ReactNode;
  value: string;
  onValueChange: (value: string) => void;
  className?: string;
}> = ({ children, value, onValueChange, className = '' }) => (
  <TabsContext.Provider value={{ value, onValueChange }}>
    <div className={className}>{children}</div>
  </TabsContext.Provider>
);

export const TabsList: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`flex gap-2 bg-white/5 p-1 rounded-lg ${className}`}>{children}</div>
);

export const TabsTrigger: React.FC<{ children: React.ReactNode; value: string }> = ({ children, value }) => {
  const ctx = useContext(TabsContext);
  const isActive = ctx?.value === value;
  
  return (
    <button
      onClick={() => ctx?.onValueChange(value)}
      className={`flex items-center justify-center px-4 py-2 rounded-md transition-colors ${
        isActive ? 'bg-white/10 text-white' : 'text-gray-400 hover:bg-white/5'
      }`}
    >
      {children}
    </button>
  );
};

export const TabsContent: React.FC<{ children: React.ReactNode; value: string; className?: string }> = ({ children, value, className = '' }) => {
  const ctx = useContext(TabsContext);
  if (ctx?.value !== value) return null;
  return <div className={className}>{children}</div>;
};
