import React, { useState, useMemo } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useTheme } from '../sportslotto/contexts/ThemeContext';

export interface OpenTicket {
  id: string;
  createdAt: string;
  atRisk: number;
  toWin: number;
  picks?: number;
}

export interface OpenTicketsPageProps {
  onBack?: () => void;
}

// Mock data for demonstration
const mockOpenTickets: OpenTicket[] = [
  { id: '3ca04ab8-ab07-49e8-9fc2-cd42f1ffd885', createdAt: '2026-01-28 20:18:27', atRisk: 20, picks: 1, toWin: 4941 },
  { id: '14e6f460-2a4c-4974-bda1-95a4c7c49929f', createdAt: '2026-01-28 20:18:27', atRisk: 20, picks: 1, toWin: 4934 },
  { id: '51f8bf862-f604-4b88-9c3e-5c8ff06c21f2', createdAt: '2026-01-28 20:16:39', atRisk: 20, picks: 1, toWin: 5062 },
  { id: '505c67b8-6e4d-4c48-978b-e8048c6648d8', createdAt: '2026-01-28 20:16:39', atRisk: 20, picks: 1, toWin: 4906 },
  { id: '576fe44b-5d7a-48fa-839b-d7b3e3d8844e', createdAt: '2026-01-28 20:16:07', atRisk: 1, picks: 1, toWin: 21 },
  { id: '4f976b0a-f020-4dc9-99a2-75a57884b03a', createdAt: '2026-01-28 20:16:07', atRisk: 1, picks: 1, toWin: 20 },
  { id: '9d33257a-1397-4403-878b-1f8e65ae2a72', createdAt: '2026-01-28 20:16:07', atRisk: 1, picks: 1, toWin: 20 },
  { id: '652b848a-ae92-47d1-9385-1ce7778ff809', createdAt: '2026-01-28 20:16:06', atRisk: 1, picks: 1, toWin: 21 },
  { id: '480b885f-ddf4-4beb-b0a0-d6b04b8ea402', createdAt: '2026-01-28 20:16:06', atRisk: 1, picks: 1, toWin: 20 },
  { id: 'a8c47d4b-7947-472b-b7c5-e2d6f9c49afb', createdAt: '2026-01-28 20:15:11', atRisk: 1, picks: 1, toWin: 21 },
  { id: '995deda1-839a-42dc-ae8b-47bdbc0392e2', createdAt: '2026-01-28 20:15:11', atRisk: 1, picks: 1, toWin: 20 },
  { id: '2eeebf04-f315-4406-afd4-aeb7a872c1f9', createdAt: '2026-01-28 20:15:11', atRisk: 1, picks: 1, toWin: 20 },
  { id: 'ff3b6afe-81e2-4665-a936-c8ca2f4fd166', createdAt: '2026-01-28 20:15:11', atRisk: 1, picks: 1, toWin: 20 },
  { id: 'be07343f-5367-402e-8765-903380f3ddd9', createdAt: '2026-01-28 20:15:11', atRisk: 1, picks: 1, toWin: 20 },
  { id: 'a8965427-d0bd-4986-86c7-a9f8c61526f0', createdAt: '2026-01-28 20:15:11', atRisk: 1, picks: 1, toWin: 20 },
  { id: '1565cc6f-8120-427f-aba2-404d9af5d68a', createdAt: '2026-01-28 20:15:11', atRisk: 1, picks: 1, toWin: 20 },
  { id: 'df41d848-0073-403c-aed7-47259f5638ae', createdAt: '2026-01-28 20:15:11', atRisk: 1, picks: 1, toWin: 20 },
  { id: 'a0c3f8c9-3a4-4f54-834e-e34a61da0e77', createdAt: '2026-01-28 20:15:11', atRisk: 1, picks: 1, toWin: 20 },
];

const ITEMS_PER_PAGE = 10;

export default function OpenTicketsPage({ onBack }: OpenTicketsPageProps) {
  const { theme } = useTheme();
  const [selectedTicket, setSelectedTicket] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);

  // Pagination
  const totalPages = Math.ceil(mockOpenTickets.length / ITEMS_PER_PAGE);
  const paginatedTickets = useMemo(() => {
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    return mockOpenTickets.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  }, [currentPage]);

  const handlePrevPage = () => {
    if (currentPage > 1) setCurrentPage(currentPage - 1);
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) setCurrentPage(currentPage + 1);
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
            Open Tickets
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
                    To Win
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
                    <td className="px-3 lg:px-6 py-4 text-xs lg:text-sm text-center font-bold" style={{ color: theme.accentColor }}>
                      {ticket.toWin}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Empty state if no tickets */}
          {mockOpenTickets.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-400 text-lg">No open tickets found</p>
            </div>
          )}

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="border-t px-6 py-4 flex items-center justify-between" style={{
              borderColor: theme.cardBorder,
              background: 'rgba(0, 0, 0, 0.3)'
            }}>
              <div className="text-sm text-gray-400">
                Page {currentPage} of {totalPages} ({mockOpenTickets.length} total tickets)
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

        {/* Ticket Details Panel (if ticket selected) */}
        {selectedTicket && (
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
                    <p className="text-white font-mono text-sm break-all">{selectedTicket}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Status</p>
                    <p className="text-yellow-400 font-semibold">PENDING</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Created</p>
                    <p className="text-white text-sm">
                      {mockOpenTickets.find(t => t.id === selectedTicket)?.createdAt}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">At Risk</p>
                    <p className="text-white font-semibold">
                      ${mockOpenTickets.find(t => t.id === selectedTicket)?.atRisk}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Potential Win</p>
                    <p className="font-bold text-lg" style={{ color: theme.accentColor }}>
                      {mockOpenTickets.find(t => t.id === selectedTicket)?.toWin}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Number of Picks</p>
                    <p className="text-white font-semibold">
                      {mockOpenTickets.find(t => t.id === selectedTicket)?.picks || 1}
                    </p>
                  </div>
                </div>

                <div className="mt-4 p-4 rounded-lg" style={{
                  background: 'rgba(0, 0, 0, 0.3)',
                  border: `1px solid ${theme.cardBorder}`
                }}>
                  <p className="text-sm text-gray-400 text-center">
                    Full ticket picks and event details will be displayed here
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
        )}
      </div>
    </div>
  );
}