import React from 'react';
import { Ticket } from '../App';
import { useTheme } from '../contexts/ThemeContext';

interface TicketDetailsPanelProps {
  ticket: Ticket;
  onClose: () => void;
  onAccept: () => void;
  onReject: () => void;
}

export function TicketDetailsPanel({ ticket, onClose, onAccept, onReject }: TicketDetailsPanelProps) {
  const { theme } = useTheme();

  return (
    <div 
      className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
      style={{
        animation: 'fadeIn 0.3s ease-out'
      }}
    >
      <div 
        className="rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden backdrop-blur-xl"
        onClick={(e) => e.stopPropagation()}
        style={{
          background: `linear-gradient(135deg, rgba(0, 0, 0, 0.8) 0%, rgba(10, 20, 30, 0.9) 100%)`,
          border: `3px solid ${theme.cardBorder}`,
          boxShadow: `
            0 0 80px ${theme.cardGlow}, 
            0 0 60px ${theme.accentColor}70,
            0 20px 80px rgba(0, 0, 0, 0.9),
            inset 0 0 60px rgba(255, 255, 255, 0.05)
          `,
          animation: 'modalSlideIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)'
        }}
      >
        {/* Header */}
        <div className="backdrop-blur-md px-6 py-4 border-b flex items-center justify-between relative overflow-hidden" style={{
          background: 'rgba(10, 10, 20, 0.7)',
          borderColor: theme.cardBorder
        }}>
          {/* Animated glow overlay */}
          <div 
            className="absolute inset-0 opacity-30 pointer-events-none"
            style={{
              background: `radial-gradient(circle at left, ${theme.accentColor}60, transparent 70%)`,
              animation: 'glow-sweep 3s ease-in-out infinite'
            }}
          />
          
          <h3 
            className="text-2xl font-bold relative z-10"
            style={{
              background: `linear-gradient(to right, ${theme.accentColor}, ${theme.cardBorder})`,
              WebkitBackgroundClip: 'text',
              backgroundClip: 'text',
              color: 'transparent',
              filter: `drop-shadow(0 0 20px ${theme.accentColor}60)`
            }}
          >
            Ticket Details
          </h3>
          <button
            onClick={onClose}
            className="relative z-10 text-gray-400 hover:text-white transition-all text-2xl hover:scale-110 active:scale-95"
            style={{
              textShadow: '0 0 15px rgba(255, 255, 255, 0.5)'
            }}
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {/* Ticket Summary */}
          <div className="backdrop-blur-sm rounded-xl p-6 mb-6 relative overflow-hidden" style={{
            background: `linear-gradient(135deg, ${theme.cardBorder}20 0%, ${theme.accentColor}10 100%)`,
            border: `2px solid ${theme.cardBorder}`,
            boxShadow: `0 0 30px ${theme.cardGlow}40, inset 0 0 40px ${theme.accentColor}10`
          }}>
            {/* Animated glow */}
            <div 
              className="absolute inset-0 opacity-20 pointer-events-none"
              style={{
                background: `radial-gradient(circle at top, ${theme.accentColor}60, transparent 70%)`,
                animation: 'glow-pulse 2s ease-in-out infinite'
              }}
            />
            
            <div className="text-center mb-4 relative z-10">
              <p 
                className="text-sm font-bold mb-2" 
                style={{ 
                  color: theme.accentColor,
                  textShadow: `0 0 15px ${theme.accentColor}80, 0 2px 4px rgba(0, 0, 0, 0.8)`
                }}
              >
                {ticket.type === 'pending' && 'PENDING TICKET'}
                {ticket.type === 'win' && 'WINNING TICKET'}
                {ticket.type === 'loss' && 'LOST TICKET'}
              </p>
              <p 
                className="text-5xl font-bold mb-1" 
                style={{ 
                  color: theme.accentColor,
                  textShadow: `
                    0 0 30px ${theme.accentColor}, 
                    0 0 60px ${theme.accentColor}80,
                    0 0 90px ${theme.accentColor}40,
                    0 4px 12px rgba(0, 0, 0, 1)
                  `,
                  animation: 'potential-pulse 2s ease-in-out infinite'
                }}
              >
                ${ticket.potential.toFixed(2)}
              </p>
              <p className="text-sm text-gray-400">Potential Win</p>
            </div>

            <div className="grid grid-cols-2 gap-4 mt-4 relative z-10">
              <div className="text-center">
                <p className="text-sm text-gray-400">Bet Amount</p>
                <p className="text-xl font-bold text-white">${ticket.amount.toFixed(2)}</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-400">Events</p>
                <p className="text-xl font-bold text-white">{ticket.events.length || 7}</p>
              </div>
            </div>
          </div>

          {/* Events List */}
          <div className="space-y-4">
            {ticket.events.map((event) => (
              <div 
                key={event.id}
                className="backdrop-blur-sm rounded-lg p-4 transition-colors"
                style={{
                  background: 'rgba(10, 10, 20, 0.6)',
                  border: `1px solid ${theme.cardBorder}`
                }}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <p className="font-bold text-white text-lg mb-1">
                      {event.homeTeam} <span style={{ color: theme.accentColor }}>vs</span> {event.awayTeam}
                    </p>
                    <p className="text-sm text-gray-400">{event.league}</p>
                  </div>
                  <div className="text-right">
                    <span className="inline-block px-3 py-1 rounded-full text-xs font-bold" style={{
                      background: `${theme.cardBorder}50`,
                      color: theme.accentColor
                    }}>
                      #{ticket.events.indexOf(event) + 1}
                    </span>
                  </div>
                </div>
                <p className="text-xs text-gray-500">{event.date}</p>
              </div>
            ))}

            {/* Sample events if none exist */}
            {ticket.events.length === 0 && (
              <>
                <div className="backdrop-blur-sm rounded-lg p-4" style={{
                  background: 'rgba(10, 10, 20, 0.6)',
                  border: '1px solid rgba(251, 146, 60, 0.2)'
                }}>
                  <p className="font-bold text-white text-lg mb-1">
                    Dinamo Zagreb <span className="text-orange-400">vs</span> FC Midtjylland
                  </p>
                  <p className="text-sm text-gray-400">UEFA Europa League</p>
                  <p className="text-xs text-gray-500 mt-2">01/30/2025 01:00 PM</p>
                </div>
                
                <div className="backdrop-blur-sm rounded-lg p-4" style={{
                  background: 'rgba(10, 10, 20, 0.6)',
                  border: '1px solid rgba(251, 146, 60, 0.2)'
                }}>
                  <p className="font-bold text-white text-lg mb-1">
                    Metaloglobus <span className="text-orange-400">vs</span> CFR Cluj
                  </p>
                  <p className="text-sm text-gray-400">Romania Liga 1</p>
                  <p className="text-xs text-gray-500 mt-2">01/30/2025 02:30 PM</p>
                </div>

                <div className="backdrop-blur-sm rounded-lg p-4" style={{
                  background: 'rgba(10, 10, 20, 0.6)',
                  border: '1px solid rgba(251, 146, 60, 0.2)'
                }}>
                  <p className="font-bold text-white text-lg mb-1">
                    Boston Bruins <span className="text-orange-400">vs</span> Philadelphia Flyers
                  </p>
                  <p className="text-sm text-gray-400">National Hockey League</p>
                  <p className="text-xs text-gray-500 mt-2">01/30/2025 03:07 PM</p>
                </div>

                <div className="backdrop-blur-sm rounded-lg p-4" style={{
                  background: 'rgba(10, 10, 20, 0.6)',
                  border: '1px solid rgba(251, 146, 60, 0.2)'
                }}>
                  <p className="font-bold text-white text-lg mb-1">
                    Brann <span className="text-orange-400">vs</span> SK Sturm Graz
                  </p>
                  <p className="text-sm text-gray-400">UEFA Europa League</p>
                  <p className="text-xs text-gray-500 mt-2">01/30/2025 04:45 PM</p>
                </div>

                <div className="backdrop-blur-sm rounded-lg p-4" style={{
                  background: 'rgba(10, 10, 20, 0.6)',
                  border: '1px solid rgba(251, 146, 60, 0.2)'
                }}>
                  <p className="font-bold text-white text-lg mb-1">
                    Melbourne City <span className="text-orange-400">vs</span> Wellington Phoenix
                  </p>
                  <p className="text-sm text-gray-400">Australia A-League</p>
                  <p className="text-xs text-gray-500 mt-2">01/30/2025 06:30 PM</p>
                </div>

                <div className="backdrop-blur-sm rounded-lg p-4" style={{
                  background: 'rgba(10, 10, 20, 0.6)',
                  border: '1px solid rgba(251, 146, 60, 0.2)'
                }}>
                  <p className="font-bold text-white text-lg mb-1">
                    Utah Mammoth <span className="text-orange-400">vs</span> Carolina Hurricanes
                  </p>
                  <p className="text-sm text-gray-400">National Hockey League</p>
                  <p className="text-xs text-gray-500 mt-2">01/30/2025 08:07 PM</p>
                </div>

                <div className="backdrop-blur-sm rounded-lg p-4" style={{
                  background: 'rgba(10, 10, 20, 0.6)',
                  border: '1px solid rgba(251, 146, 60, 0.2)'
                }}>
                  <p className="font-bold text-white text-lg mb-1">
                    Jacob Fearnley <span className="text-orange-400">vs</span> Lukas Pokorny
                  </p>
                  <p className="text-sm text-gray-400">Association of Tennis Professionals - Challengers</p>
                  <p className="text-xs text-gray-500 mt-2">01/30/2025 10:00 AM</p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="backdrop-blur-md px-6 py-4 border-t flex gap-4 relative overflow-hidden" style={{
          background: 'rgba(10, 10, 20, 0.7)',
          borderColor: theme.cardBorder
        }}>
          {/* Animated glow */}
          <div 
            className="absolute inset-0 opacity-15 pointer-events-none"
            style={{
              background: `radial-gradient(circle at center, ${theme.accentColor}60, transparent 70%)`,
              animation: 'glow-pulse 2s ease-in-out infinite'
            }}
          />
          
          <button
            onClick={onReject}
            className="relative z-10 flex-1 py-3 rounded-xl font-bold bg-red-600 hover:bg-red-700 text-white transition-all hover:scale-105 active:scale-95"
            style={{
              boxShadow: '0 0 25px rgba(220, 38, 38, 0.7), 0 4px 20px rgba(220, 38, 38, 0.5)',
              textShadow: '0 0 10px rgba(255, 255, 255, 0.6)',
              border: '2px solid rgba(220, 38, 38, 0.5)'
            }}
          >
            ✕ Reject
          </button>
          <button
            onClick={onClose}
            className="relative z-10 flex-1 py-3 rounded-xl font-bold text-white transition-all backdrop-blur-sm hover:scale-105 active:scale-95"
            style={{
              background: 'rgba(60, 60, 80, 0.5)',
              border: '2px solid rgba(255, 255, 255, 0.2)',
              textShadow: '0 2px 4px rgba(0, 0, 0, 0.8)'
            }}
          >
            Close
          </button>
          <button
            onClick={onAccept}
            className="relative z-10 flex-1 py-3 rounded-xl font-bold bg-green-600 hover:bg-green-700 text-white transition-all hover:scale-105 active:scale-95"
            style={{
              boxShadow: '0 0 30px rgba(22, 163, 74, 0.8), 0 4px 25px rgba(22, 163, 74, 0.6)',
              textShadow: '0 0 10px rgba(255, 255, 255, 0.6)',
              border: '2px solid rgba(22, 163, 74, 0.5)',
              animation: 'modal-accept-pulse 2s ease-in-out infinite'
            }}
          >
            ✓ Accept!
          </button>
        </div>
      </div>

      {/* Animations */}
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes modalSlideIn {
          0% {
            opacity: 0;
            transform: scale(0.85) translateY(30px);
          }
          100% {
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }

        @keyframes glow-sweep {
          0%, 100% {
            transform: translateX(-50%);
            opacity: 0.2;
          }
          50% {
            transform: translateX(50%);
            opacity: 0.4;
          }
        }

        @keyframes glow-pulse {
          0%, 100% {
            opacity: 0.15;
          }
          50% {
            opacity: 0.3;
          }
        }

        @keyframes potential-pulse {
          0%, 100% {
            filter: brightness(1) drop-shadow(0 0 20px ${theme.accentColor}80);
            transform: scale(1);
          }
          50% {
            filter: brightness(1.3) drop-shadow(0 0 40px ${theme.accentColor});
            transform: scale(1.03);
          }
        }

        @keyframes modal-accept-pulse {
          0%, 100% {
            box-shadow: 0 0 30px rgba(22, 163, 74, 0.8), 0 4px 25px rgba(22, 163, 74, 0.6);
          }
          50% {
            box-shadow: 0 0 45px rgba(22, 163, 74, 1), 0 4px 35px rgba(22, 163, 74, 0.8);
          }
        }
      `}</style>
    </div>
  );
}