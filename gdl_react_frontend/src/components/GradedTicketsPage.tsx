import React, { useState, useMemo } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useTheme } from '../sportslotto/contexts/ThemeContext';

export interface GradedTicket {
  id: string;
  createdAt: string;
  atRisk: number;
  result: 'WIN' | 'LOSS' | 'PUSH';
  payout: number;
  picks?: number;
}

export interface GradedTicketsPageProps {
  onBack?: () => void;
}

// Mock data for demonstration
const mockGradedTickets: GradedTicket[] = [
  { id: '7fa89bc1-4e32-4a9b-8f21-d1e5c7b2a890', createdAt: '2026-01-27 18:45:12', picks: 1, atRisk: 20, result: 'WIN', payout: 4941 },
  { id: '2c4e5f67-8a9b-4c1d-9e2f-3a4b5c6d7e8f', createdAt: '2026-01-27 17:30:45', picks: 1, atRisk: 20, result: 'LOSS', payout: 0 },
  { id: '9b8c7d6e-5f4a-3b2c-1d0e-9f8e7d6c5b4a', createdAt: '2026-01-27 16:15:30', picks: 2, atRisk: 40, result: 'WIN', payout: 120 },
  { id: '5a6b7c8d-9e0f-1a2b-3c4d-5e6f7a8b9c0d', createdAt: '2026-01-27 15:00:20', picks: 1, atRisk: 20, result: 'PUSH', payout: 20 },
  { id: '1e2f3a4b-5c6d-7e8f-9a0b-1c2d3e4f5a6b', createdAt: '2026-01-26 22:45:10', picks: 1, atRisk: 20, result: 'WIN', payout: 38 },
  { id: '8d7c6b5a-4f3e-2d1c-0b9a-8f7e6d5c4b3a', createdAt: '2026-01-26 21:30:55', picks: 3, atRisk: 60, result: 'LOSS', payout: 0 },
  { id: 'a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d', createdAt: '2026-01-26 20:15:40', picks: 1, atRisk: 20, result: 'WIN', payout: 40 },
  { id: '7e8f9a0b-1c2d-3e4f-5a6b-7c8d9e0f1a2b', createdAt: '2026-01-26 19:00:25', picks: 2, atRisk: 40, result: 'WIN', payout: 100 },
  { id: 'f1e2d3c4-b5a6-9870-1e2d-3c4b5a697801', createdAt: '2026-01-26 18:30:15', picks: 1, atRisk: 20, result: 'LOSS', payout: 0 },
  { id: 'b2c3d4e5-f6a7-b8c9-0d1e-2f3a4b5c6d7e', createdAt: '2026-01-26 17:15:50', picks: 1, atRisk: 20, result: 'WIN', payout: 42 },
  { id: 'c3d4e5f6-a7b8-c9d0-e1f2-a3b4c5d6e7f8', createdAt: '2026-01-26 16:00:35', picks: 2, atRisk: 40, result: 'WIN', payout: 95 },
  { id: 'd4e5f6a7-b8c9-d0e1-f2a3-b4c5d6e7f8a9', createdAt: '2026-01-26 15:45:20', picks: 1, atRisk: 20, result: 'LOSS', payout: 0 },
];

const ITEMS_PER_PAGE = 10;

export default function GradedTicketsPage({ onBack }: GradedTicketsPageProps) {
  const { theme } = useTheme();
  const [selectedTicket, setSelectedTicket] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);

  // Pagination
  const totalPages = Math.ceil(mockGradedTickets.length / ITEMS_PER_PAGE);
  const paginatedTickets = useMemo(() => {
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    return mockGradedTickets.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  }, [currentPage]);

  const handlePrevPage = () => {
    if (currentPage > 1) setCurrentPage(currentPage - 1);
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) setCurrentPage(currentPage + 1);
  };

  const getResultColor = (result: GradedTicket['result']) => {
    switch (result) {
      case 'WIN':
        return 'text-green-400';
      case 'LOSS':
        return 'text-red-400';
      case 'PUSH':
        return 'text-yellow-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="min-h-screen text-white relative overflow-hidden" style={{
      background: 'linear-gradient(180deg, #1a0a2e 0%, #2d1b4e 25%, #4a2c5e 50%, #5c3a3e 75%, #6e3a2e 100%)'
    }}>
      {/* Particle/Star Background */}
      <div className="absolute inset-0 opacity-40 pointer-events-none" style={{
        backgroundImage: `radial-gradient(2px 2px at 20% 30%, white, transparent),
                         radial-gradient(2px 2px at 60% 70%, white, transparent),
                         radial-gradient(1px 1px at 50% 50%, white, transparent),
                         radial-gradient(1px 1px at 80% 10%, white, transparent),
                         radial-gradient(2px 2px at 90% 60%, orange, transparent),
                         radial-gradient(1px 1px at 33% 80%, orange, transparent),
                         radial-gradient(2px 2px at 15% 90%, white, transparent)`,
        backgroundSize: '200% 200%',
        backgroundPosition: '0% 0%, 40% 60%, 70% 20%, 10% 80%, 90% 30%, 30% 90%, 60% 10%'
      }}></div>

      {/* Header */}
      <div className="relative z-10 backdrop-blur-md bg-black/40 border-b py-4 px-4 lg:px-6" style={{
        borderColor: theme.cardBorder
      }}>
        <div className="max-w-7xl mx-auto flex items-center gap-4">
          {onBack && (
            <button
              onClick={onBack}
              className="flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all shadow-lg"
              style={{
                background: theme.buttonGradient,
                boxShadow: `0 4px 20px ${theme.cardGlow}`
              }}
            >
              <ChevronLeft className="w-5 h-5" />
              <span className="hidden sm:inline">Back</span>
            </button>
          )}
          <h1 className="text-2xl lg:text-3xl font-bold bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
            Graded Tickets
          </h1>
        </div>
      </div>

      {/* Tickets Table */}
      <div className="relative z-10 max-w-7xl mx-auto p-4 lg:p-6">
        <div className="rounded-2xl overflow-hidden backdrop-blur-md" style={{
          background: theme.cardBg,
          border: `2px solid ${theme.cardBorder}`,
          boxShadow: `0 8px 32px ${theme.cardGlow}`
        }}>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b" style={{ 
                background: 'rgba(0, 0, 0, 0.3)',
                borderColor: theme.cardBorder
              }}>
                <tr>
                  <th className="px-3 lg:px-6 py-4 text-left text-xs lg:text-sm font-semibold text-gray-400 uppercase tracking-wider">
                    Bet ID
                  </th>
                  <th className="px-3 lg:px-6 py-4 text-left text-xs lg:text-sm font-semibold text-gray-400 uppercase tracking-wider">
                    Created At
                  </th>
                  <th className="px-3 lg:px-6 py-4 text-center text-xs lg:text-sm font-semibold text-gray-400 uppercase tracking-wider">
                    At Risk
                  </th>
                  <th className="px-3 lg:px-6 py-4 text-center text-xs lg:text-sm font-semibold text-gray-400 uppercase tracking-wider">
                    Result
                  </th>
                  <th className="px-3 lg:px-6 py-4 text-center text-xs lg:text-sm font-semibold text-gray-400 uppercase tracking-wider">
                    Payout
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y" style={{ divideColor: `${theme.cardBorder}40` }}>
                {paginatedTickets.map((ticket, index) => (
                  <tr
                    key={ticket.id}
                    onClick={() => setSelectedTicket(selectedTicket === ticket.id ? null : ticket.id)}
                    className="cursor-pointer transition-all hover:brightness-125"
                    style={{
                      background: selectedTicket === ticket.id 
                        ? `${theme.cardBorder}40`
                        : index % 2 === 0 
                          ? 'rgba(255, 255, 255, 0.03)' 
                          : 'rgba(0, 0, 0, 0.2)'
                    }}
                  >
                    <td className="px-3 lg:px-6 py-4 text-xs lg:text-sm font-mono text-gray-300">
                      <span className="hidden lg:inline">{ticket.id}</span>
                      <span className="lg:hidden">{ticket.id.substring(0, 8)}...</span>
                    </td>
                    <td className="px-3 lg:px-6 py-4 text-xs lg:text-sm text-gray-300">
                      {ticket.createdAt}
                    </td>
                    <td className="px-3 lg:px-6 py-4 text-xs lg:text-sm text-center font-semibold text-white">
                      ${ticket.atRisk}
                    </td>
                    <td className={`px-3 lg:px-6 py-4 text-xs lg:text-sm text-center font-bold ${getResultColor(ticket.result)}`}>
                      {ticket.result}
                    </td>
                    <td className="px-3 lg:px-6 py-4 text-xs lg:text-sm text-center font-bold" style={{ color: theme.accentColor }}>
                      {ticket.payout > 0 ? `$${ticket.payout}` : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Empty state if no tickets */}
          {mockGradedTickets.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-400 text-lg">No graded tickets found</p>
            </div>
          )}

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="border-t px-6 py-4 flex flex-col sm:flex-row items-center justify-between gap-4" style={{
              borderColor: theme.cardBorder,
              background: 'rgba(0, 0, 0, 0.3)'
            }}>
              <div className="text-sm text-gray-400">
                Page {currentPage} of {totalPages} ({mockGradedTickets.length} total tickets)
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handlePrevPage}
                  disabled={currentPage === 1}
                  className="px-4 py-2 rounded-lg font-semibold text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{
                    background: currentPage === 1 ? 'rgba(60, 60, 80, 0.5)' : theme.buttonGradient,
                    boxShadow: currentPage === 1 ? 'none' : `0 4px 20px ${theme.cardGlow}`
                  }}
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button
                  onClick={handleNextPage}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 rounded-lg font-semibold text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{
                    background: currentPage === totalPages ? 'rgba(60, 60, 80, 0.5)' : theme.buttonGradient,
                    boxShadow: currentPage === totalPages ? 'none' : `0 4px 20px ${theme.cardGlow}`
                  }}
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Summary Stats */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="rounded-xl p-6 text-center backdrop-blur-md" style={{
            background: theme.cardBg,
            border: `2px solid ${theme.cardBorder}`,
            boxShadow: `0 4px 20px ${theme.cardGlow}`
          }}>
            <p className="text-sm text-gray-400 mb-2">Total Wins</p>
            <p className="text-3xl font-bold text-green-400">
              {mockGradedTickets.filter(t => t.result === 'WIN').length}
            </p>
          </div>
          <div className="rounded-xl p-6 text-center backdrop-blur-md" style={{
            background: theme.cardBg,
            border: `2px solid ${theme.cardBorder}`,
            boxShadow: `0 4px 20px ${theme.cardGlow}`
          }}>
            <p className="text-sm text-gray-400 mb-2">Total Losses</p>
            <p className="text-3xl font-bold text-red-400">
              {mockGradedTickets.filter(t => t.result === 'LOSS').length}
            </p>
          </div>
          <div className="rounded-xl p-6 text-center backdrop-blur-md" style={{
            background: theme.cardBg,
            border: `2px solid ${theme.cardBorder}`,
            boxShadow: `0 4px 20px ${theme.cardGlow}`
          }}>
            <p className="text-sm text-gray-400 mb-2">Total Payout</p>
            <p className="text-3xl font-bold" style={{ color: theme.accentColor }}>
              ${mockGradedTickets.reduce((sum, t) => sum + t.payout, 0).toFixed(2)}
            </p>
          </div>
        </div>

        {/* Ticket Details Panel (if ticket selected) */}
        {selectedTicket && (() => {
          const ticket = mockGradedTickets.find(t => t.id === selectedTicket);
          if (!ticket) return null;
          
          return (
            <div 
              className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
              onClick={() => setSelectedTicket(null)}
            >
              <div 
                className="rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden backdrop-blur-md"
                onClick={(e) => e.stopPropagation()}
                style={{
                  background: theme.cardBg,
                  border: `2px solid ${theme.cardBorder}`,
                  boxShadow: `0 8px 32px ${theme.cardGlow}`
                }}
              >
                {/* Modal Header */}
                <div className="border-b px-6 py-4 flex items-center justify-between" style={{
                  background: 'rgba(0, 0, 0, 0.3)',
                  borderColor: theme.cardBorder
                }}>
                  <h3 className="text-xl font-bold bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
                    Ticket Details
                  </h3>
                  <button
                    onClick={() => setSelectedTicket(null)}
                    className="text-gray-400 hover:text-white transition-colors text-2xl"
                  >
                    ✕
                  </button>
                </div>

                {/* Modal Content */}
                <div className="p-6 overflow-y-auto max-h-[calc(80vh-120px)]">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-400">Ticket ID</p>
                      <p className="text-white font-mono text-sm break-all">{ticket.id}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Result</p>
                      <p className={`font-bold ${getResultColor(ticket.result)}`}>{ticket.result}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Created</p>
                      <p className="text-white text-sm">{ticket.createdAt}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Number of Picks</p>
                      <p className="text-white font-semibold">{ticket.picks || 1}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Amount Risked</p>
                      <p className="text-white font-semibold">${ticket.atRisk.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Payout</p>
                      <p className="font-bold text-lg" style={{ color: theme.accentColor }}>${ticket.payout.toFixed(2)}</p>
                    </div>
                  </div>

                  <div className="mt-4 p-4 rounded-lg" style={{
                    background: 'rgba(0, 0, 0, 0.3)',
                    border: `1px solid ${theme.cardBorder}`
                  }}>
                    <p className="text-sm text-gray-400 text-center">
                      Full ticket details and picks will be displayed here
                    </p>
                  </div>
                </div>

                {/* Modal Footer */}
                <div className="border-t px-6 py-4" style={{
                  background: 'rgba(0, 0, 0, 0.3)',
                  borderColor: theme.cardBorder
                }}>
                  <button
                    onClick={() => setSelectedTicket(null)}
                    className="w-full py-3 rounded-lg font-bold text-white transition-all"
                    style={{
                      background: theme.buttonGradient,
                      boxShadow: `0 4px 20px ${theme.cardGlow}`
                    }}
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          );
        })()}
      </div>
    </div>
  );
}