import React from 'react';

export const Button: React.FC<{ 
  children: React.ReactNode; 
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
}> = ({ children, className = '', onClick, disabled = false }) => (
  <button 
    onClick={onClick}
    disabled={disabled}
    className={`px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold disabled:opacity-50 transition-colors ${className}`}
  >
    {children}
  </button>
);
