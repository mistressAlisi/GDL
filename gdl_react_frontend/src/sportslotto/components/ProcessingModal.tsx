/**
 * Processing Modal Component
 * 
 * Displays a loading state while tickets are being generated.
 * Used during Quick Picks and Custom Ticket generation.
 */

import React from 'react';
import { useTheme } from '../contexts/ThemeContext';

interface ProcessingModalProps {
  isOpen: boolean;
  message?: string;
  subMessage?: string;
}

export function ProcessingModal({ 
  isOpen, 
  message = "Processing...", 
  subMessage = "Ticket Generation in progress" 
}: ProcessingModalProps) {
  const { theme } = useTheme();
  
  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4"
    >
      <div 
        className="rounded-3xl p-8 max-w-md w-full backdrop-blur-md text-center"
        style={{
          background: 'rgba(40, 40, 60, 0.95)',
          border: `2px solid ${theme.cardBorder}`,
          boxShadow: `0 8px 32px ${theme.cardGlow}`
        }}
      >
        {/* Spinning Loader */}
        <div className="flex justify-center mb-6">
          <div 
            className="w-24 h-24 rounded-full flex items-center justify-center animate-spin"
            style={{
              background: `${theme.cardBg}`,
              border: `3px solid ${theme.cardBorder}`,
              boxShadow: `0 4px 24px ${theme.cardGlow}, inset 0 0 20px ${theme.cardGlow}`
            }}
          >
            <div 
              className="w-20 h-20 rounded-full flex items-center justify-center"
              style={{
                background: 'rgba(40, 40, 60, 0.9)',
              }}
            >
              <svg 
                className="w-12 h-12" 
                fill="none" 
                viewBox="0 0 24 24"
                style={{
                  animation: 'spin 1s linear infinite reverse',
                  color: theme.accentColor
                }}
              >
                <circle 
                  className="opacity-25" 
                  cx="12" 
                  cy="12" 
                  r="10" 
                  stroke="currentColor" 
                  strokeWidth="4"
                />
                <path 
                  className="opacity-75" 
                  fill="currentColor" 
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            </div>
          </div>
        </div>

        {/* Message */}
        <h2 className="text-3xl font-bold text-white mb-3">
          {message}
        </h2>
        
        {/* Sub Message */}
        <p className="text-lg text-gray-300 mb-8">
          {subMessage}
        </p>

        {/* Three Dots Animation */}
        <div className="flex justify-center gap-2">
          <div 
            className="w-3 h-3 rounded-full"
            style={{
              backgroundColor: theme.accentColor,
              animation: 'bounce 1.4s infinite ease-in-out both',
              animationDelay: '-0.32s'
            }}
          />
          <div 
            className="w-3 h-3 rounded-full"
            style={{
              backgroundColor: theme.accentColor,
              animation: 'bounce 1.4s infinite ease-in-out both',
              animationDelay: '-0.16s'
            }}
          />
          <div 
            className="w-3 h-3 rounded-full"
            style={{
              backgroundColor: theme.accentColor,
              animation: 'bounce 1.4s infinite ease-in-out both'
            }}
          />
        </div>
      </div>

      <style>{`
        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }

        @keyframes bounce {
          0%, 80%, 100% {
            transform: scale(0);
            opacity: 0.5;
          }
          40% {
            transform: scale(1);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
}