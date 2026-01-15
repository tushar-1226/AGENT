import React from 'react';

export const Badge: React.FC<{ 
  children: React.ReactNode; 
  className?: string;
  variant?: 'default' | 'secondary' | 'outline' | 'destructive';
}> = ({ children, className = '', variant = 'default' }) => {
  const variantStyles = {
    default: 'bg-blue-600 text-white',
    secondary: 'bg-gray-600 text-white',
    outline: 'border border-white/20 bg-transparent',
    destructive: 'bg-red-600 text-white'
  };
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variantStyles[variant]} ${className}`}>
      {children}
    </span>
  );
};
