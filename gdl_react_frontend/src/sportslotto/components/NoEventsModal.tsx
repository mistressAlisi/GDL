/**
 * No Events Modal Component
 * 
 * Displays when there are not enough events available to generate tickets.
 * Shows warning and suggestions to the user.
 */

import React from 'react';
import { useTheme } from '../contexts/ThemeContext';

interface NoEventsModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  message?: string;
  suggestion?: string;
}

export function NoEventsModal({ 
  isOpen, 
  onClose,
  title = "Oops! Not Enough Events",
  message = "Not enough events available for this combo right now!",
  suggestion = "Try adding more events or reducing the payout!"
}: NoEventsModalProps) {
  const { theme } = useTheme();
  
  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div 
        className="rounded-3xl p-8 max-w-md w-full backdrop-blur-md relative"
        style={{
          background: 'rgba(40, 40, 60, 0.95)',
          border: '2px solid rgba(251, 191, 36, 0.4)',
          boxShadow: '0 8px 32px rgba(251, 191, 36, 0.3)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors text-2xl leading-none w-8 h-8 flex items-center justify-center"
        >
          ×
        </button>

        {/* Warning Icon */}
        <div className="flex justify-center mb-6">
          <div 
            className="w-24 h-24 rounded-full flex items-center justify-center"
            style={{
              background: 'linear-gradient(135deg, rgba(251, 191, 36, 0.3) 0%, rgba(217, 119, 6, 0.3) 100%)',
              border: '3px solid rgba(251, 191, 36, 0.5)',
              boxShadow: '0 4px 24px rgba(251, 191, 36, 0.4), inset 0 0 20px rgba(251, 191, 36, 0.2)'
            }}
          >
            <svg 
              className="w-12 h-12 text-yellow-400" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
              strokeWidth="3"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" 
              />
            </svg>
          </div>
        </div>

        {/* Title */}
        <h2 className="text-3xl font-bold text-white mb-4 text-center">
          {title}
        </h2>
        
        {/* Message */}
        <p className="text-lg text-gray-200 mb-3 text-center">
          {message}
        </p>

        {/* Suggestion */}
        <p className="text-base text-gray-300 mb-8 text-center">
          {suggestion}
        </p>

        {/* Got It Button */}
        <button
          onClick={onClose}
          className="w-full py-4 rounded-xl font-bold text-white text-lg transition-all shadow-lg hover:scale-105"
          style={{
            background: theme.buttonGradient,
            boxShadow: `0 4px 24px ${theme.cardGlow}`
          }}
        >
          Got It!
        </button>
      </div>
    </div>
  );
}