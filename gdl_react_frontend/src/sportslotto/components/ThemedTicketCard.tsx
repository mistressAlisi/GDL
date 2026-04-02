import React from 'react';
import { Ticket } from '../App';
import { useTheme } from '../contexts/ThemeContext';

interface ThemedTicketCardProps {
  ticket: Ticket;
  onShowDetails: (ticket: Ticket) => void;
  onAccept: (id: string) => void;
  onReject: (id: string) => void;
}

export function ThemedTicketCard({ ticket, onShowDetails, onAccept, onReject }: ThemedTicketCardProps) {
  const { theme } = useTheme();

  return (
    <div
      className="rounded-2xl p-6 backdrop-blur-md transition-all duration-300 hover:scale-105 flex flex-col relative overflow-hidden animate-border-glow"
      style={{
        background: `linear-gradient(135deg, rgba(0, 0, 0, 0.6) 0%, rgba(20, 20, 40, 0.6) 100%)`,
        border: `3px solid ${theme.cardBorder}`,
        boxShadow: `
          0 0 50px ${theme.cardGlow}, 
          0 0 30px ${theme.accentColor}60,
          0 8px 32px rgba(0, 0, 0, 0.6), 
          inset 0 0 30px rgba(255, 255, 255, 0.08),
          inset 0 0 60px ${theme.accentColor}20
        `,
        animation: 'border-glow 3s ease-in-out infinite'
      }}
    >
      {/* Accent glow overlay */}
      <div 
        className="absolute inset-0 opacity-30 pointer-events-none"
        style={{
          background: `radial-gradient(circle at top right, ${theme.accentColor}60, transparent 60%)`
        }}
      />
      
      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <div className="text-center mb-3">
          <p 
            className="text-xs font-bold tracking-wider mb-2"
            style={{
              color: theme.accentColor,
              textShadow: `0 0 10px ${theme.accentColor}80, 0 0 20px ${theme.accentColor}40, 0 2px 4px rgba(0, 0, 0, 0.8)`
            }}
          >
            TICKET WINS
          </p>
          <div 
            className="inline-block px-6 py-3 rounded-xl border-2"
            style={{
              borderColor: theme.cardBorder,
              background: `linear-gradient(135deg, rgba(0, 0, 0, 0.5) 0%, rgba(10, 10, 20, 0.7) 100%)`,
              boxShadow: `
                0 0 25px ${theme.cardGlow}60, 
                inset 0 0 20px rgba(255, 255, 255, 0.05),
                inset 0 0 40px ${theme.accentColor}15
              `
            }}
          >
            <p 
              className="text-4xl font-bold"
              style={{ 
                color: theme.accentColor,
                textShadow: `
                  0 0 30px ${theme.accentColor}, 
                  0 0 60px ${theme.accentColor}80,
                  0 0 90px ${theme.accentColor}40,
                  0 2px 8px rgba(0, 0, 0, 0.9)
                `,
                animation: 'text-glow 2s ease-in-out infinite'
              }}
            >
              {ticket.potential.toFixed(0)}
            </p>
          </div>
        </div>

        {/* Details prompt */}
        <div className="text-center mb-4">
          <button
            onClick={() => onShowDetails(ticket)}
            className="text-xs font-bold transition-colors tracking-wide"
            style={{
              color: '#fff',
              textShadow: `
                0 0 15px ${theme.accentColor}80, 
                0 0 30px ${theme.accentColor}40,
                0 2px 6px rgba(0, 0, 0, 0.9)
              `
            }}
          >
            CLICK TO REVEAL DETAILS!
          </button>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between gap-3 mt-auto">
          <button
            onClick={() => onReject(ticket.id)}
            className="w-10 h-10 rounded-lg bg-red-600 hover:bg-red-700 transition-all flex items-center justify-center shadow-lg hover:shadow-red-500/50"
            style={{
              boxShadow: '0 0 20px rgba(220, 38, 38, 0.6), 0 4px 15px rgba(220, 38, 38, 0.4)'
            }}
          >
            <span className="text-white text-xl" style={{
              textShadow: '0 0 10px rgba(255, 255, 255, 0.8), 0 2px 4px rgba(0, 0, 0, 0.8)'
            }}>✕</span>
          </button>
          <button
            onClick={() => onAccept(ticket.id)}
            className="w-10 h-10 rounded-lg bg-green-600 hover:bg-green-700 transition-all flex items-center justify-center shadow-lg hover:shadow-green-500/50"
            style={{
              boxShadow: '0 0 20px rgba(22, 163, 74, 0.6), 0 4px 15px rgba(22, 163, 74, 0.4)'
            }}
          >
            <span className="text-white text-xl" style={{
              textShadow: '0 0 10px rgba(255, 255, 255, 0.8), 0 2px 4px rgba(0, 0, 0, 0.8)'
            }}>✓</span>
          </button>
        </div>
      </div>

      {/* CSS Animations */}
      <style>{`
        @keyframes border-glow {
          0%, 100% {
            box-shadow: 
              0 0 50px ${theme.cardGlow}, 
              0 0 30px ${theme.accentColor}60,
              0 8px 32px rgba(0, 0, 0, 0.6), 
              inset 0 0 30px rgba(255, 255, 255, 0.08),
              inset 0 0 60px ${theme.accentColor}20;
          }
          50% {
            box-shadow: 
              0 0 70px ${theme.cardGlow}, 
              0 0 50px ${theme.accentColor}80,
              0 8px 32px rgba(0, 0, 0, 0.6), 
              inset 0 0 40px rgba(255, 255, 255, 0.12),
              inset 0 0 80px ${theme.accentColor}30;
          }
        }

        @keyframes text-glow {
          0%, 100% {
            filter: brightness(1) drop-shadow(0 0 20px ${theme.accentColor}80);
          }
          50% {
            filter: brightness(1.2) drop-shadow(0 0 35px ${theme.accentColor});
          }
        }
      `}</style>
    </div>
  );
}