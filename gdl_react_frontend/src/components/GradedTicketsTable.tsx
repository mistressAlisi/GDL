/**
 * Graded Tickets Table Component
 * 
 * Displays graded/completed betting tickets using the same format as MessagesTable.
 */

import React, { useState } from 'react';

// Graded Ticket type definition
interface GradedTicket {
  uuid: string;
  createdAt: string;
  gradedAt: string;
  atRisk: number;
  payout: number;
  picks: number;
  status: 'won' | 'lost' | 'void' | 'cashout';
}

export function GradedTicketsTable() {
  const [selectedTickets, setSelectedTickets] = useState<Set<string>>(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const [viewingTicket, setViewingTicket] = useState<GradedTicket | null>(null);
  const itemsPerPage = 15;

  // Mock data - Replace with API call: useGradedTickets() hook
  const mockTickets: GradedTicket[] = [
    { uuid: '8f3d6ac7-aef3-4c12-ace6-d0de02ba353c', createdAt: '2026-01-27 18:22:15', gradedAt: '2026-01-28 10:45:30', atRisk: 50, payout: 1250, picks: 5, status: 'won' },
    { uuid: '7c2e8db-2b21-4da9-8d27-ad56dc7fa638', createdAt: '2026-01-27 16:15:00', gradedAt: '2026-01-28 09:30:22', atRisk: 25, payout: 0, picks: 4, status: 'lost' },
    { uuid: 'b5c97c-a2fc-45c1-a6d4-42091fa048cb', createdAt: '2026-01-27 14:30:45', gradedAt: '2026-01-28 08:15:10', atRisk: 100, payout: 2500, picks: 7, status: 'won' },
    { uuid: 'a6fa0029-3829a-0a5f-9dae-7bb5c8baa218', createdAt: '2026-01-27 12:45:30', gradedAt: '2026-01-27 22:00:00', atRisk: 10, payout: 0, picks: 3, status: 'lost' },
    { uuid: 'e0c4d8c8-a196-4196-8dc4-e08027d087a9', createdAt: '2026-01-27 10:20:00', gradedAt: '2026-01-27 20:30:15', atRisk: 75, payout: 1875, picks: 6, status: 'won' },
    { uuid: '932e1ef6-8411-4418-b0fa-85eb86c48ec0', createdAt: '2026-01-27 08:15:22', gradedAt: '2026-01-27 18:45:00', atRisk: 20, payout: 0, picks: 2, status: 'lost' },
    { uuid: 'aef9f934-fde9-48f9-8f9f-ac0000128af6', createdAt: '2026-01-26 22:30:10', gradedAt: '2026-01-27 16:20:30', atRisk: 30, payout: 750, picks: 4, status: 'won' },
    { uuid: '5279be98-5fe4-47c3-b483-c73ea7a008fe', createdAt: '2026-01-26 20:15:45', gradedAt: '2026-01-27 14:10:00', atRisk: 15, payout: 0, picks: 3, status: 'lost' },
    { uuid: '4bd844db-64f2-48c2-a896-0a652c786e36', createdAt: '2026-01-26 18:00:00', gradedAt: '2026-01-27 12:00:00', atRisk: 40, payout: 40, picks: 5, status: 'void' },
    { uuid: 'aa2056cb-3f4f-4cd8-b04e-3658856a6095', createdAt: '2026-01-26 16:45:30', gradedAt: '2026-01-27 10:30:15', atRisk: 60, payout: 1500, picks: 6, status: 'won' },
    { uuid: 'db2f3e6b-d862-419e-be00-42069f1279e9', createdAt: '2026-01-26 14:20:15', gradedAt: '2026-01-27 08:15:30', atRisk: 25, payout: 0, picks: 4, status: 'lost' },
    { uuid: '1ce78369-b1f3-4d20-887c-3ab237af61bf', createdAt: '2026-01-26 12:00:00', gradedAt: '2026-01-27 06:00:00', atRisk: 35, payout: 875, picks: 5, status: 'won' },
    { uuid: 'f2a1d3e8-9c7b-4a5e-8f6d-1b2c3d4e5f6a', createdAt: '2026-01-26 10:30:45', gradedAt: '2026-01-26 22:45:10', atRisk: 50, payout: 0, picks: 7, status: 'lost' },
    { uuid: 'c8b9a0f1-2d3e-4f5a-9b8c-7d6e5f4a3b2c', createdAt: '2026-01-26 08:15:30', gradedAt: '2026-01-26 20:30:00', atRisk: 45, payout: 1125, picks: 6, status: 'won' },
    { uuid: 'e1f2a3b4-c5d6-7e8f-9a0b-1c2d3e4f5a6b', createdAt: '2026-01-26 06:00:00', gradedAt: '2026-01-26 18:15:45', atRisk: 20, payout: 400, picks: 4, status: 'cashout' },
    { uuid: 'a9b8c7d6-e5f4-3a2b-1c0d-9e8f7a6b5c4d', createdAt: '2026-01-25 22:45:15', gradedAt: '2026-01-26 16:00:30', atRisk: 55, payout: 0, picks: 5, status: 'lost' },
    { uuid: 'f6e5d4c3-b2a1-9f8e-7d6c-5b4a3e2d1c0b', createdAt: '2026-01-25 20:30:00', gradedAt: '2026-01-26 14:45:00', atRisk: 70, payout: 1750, picks: 7, status: 'won' },
    { uuid: 'd3c2b1a0-9f8e-7d6c-5b4a-3e2d1c0b9a8f', createdAt: '2026-01-25 18:15:45', gradedAt: '2026-01-26 12:30:15', atRisk: 12, payout: 0, picks: 2, status: 'lost' },
  ];

  const totalRecords = mockTickets.length;
  const totalPages = Math.ceil(totalRecords / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentTickets = mockTickets.slice(startIndex, endIndex);

  const handleSelectAll = () => {
    if (selectedTickets.size === currentTickets.length) {
      setSelectedTickets(new Set());
    } else {
      setSelectedTickets(new Set(currentTickets.map(t => t.uuid)));
    }
  };

  const handleSelectTicket = (uuid: string) => {
    const newSelected = new Set(selectedTickets);
    if (newSelected.has(uuid)) {
      newSelected.delete(uuid);
    } else {
      newSelected.add(uuid);
    }
    setSelectedTickets(newSelected);
  };

  const handleViewTicket = (ticket: GradedTicket) => {
    setViewingTicket(ticket);
  };

  const handleDeleteSelected = () => {
    if (selectedTickets.size === 0) return;
    if (confirm(`Archive ${selectedTickets.size} selected ticket(s)?`)) {
      // TODO: API call to archive tickets
      setSelectedTickets(new Set());
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
          Graded Tickets
        </h2>
        <div className="flex items-center gap-2">
          {selectedTickets.size > 0 && (
            <>
              <button
                onClick={handleDeleteSelected}
                className="px-4 py-2 rounded bg-red-500/20 hover:bg-red-500/30 text-red-300 transition-colors text-sm"
              >
                Archive Sel.
              </button>
              <button
                onClick={() => setSelectedTickets(new Set())}
                className="px-4 py-2 rounded bg-gray-500/20 hover:bg-gray-500/30 text-gray-300 transition-colors text-sm"
              >
                (De)Select All
              </button>
            </>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="rounded-2xl overflow-hidden backdrop-blur-md" style={{
        background: 'rgba(20, 20, 40, 0.7)',
        border: '2px solid rgba(251, 146, 60, 0.4)',
      }}>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-orange-500/30" style={{ background: 'rgba(40, 40, 60, 0.5)' }}>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  uuid
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  created at
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  graded at
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  at risk
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  payout
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  status
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  view ticket
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  select
                </th>
              </tr>
            </thead>
            <tbody>
              {currentTickets.map((ticket, index) => (
                <tr 
                  key={ticket.uuid}
                  className="border-b border-orange-500/10 hover:bg-orange-500/5 transition-colors"
                  style={{
                    background: index % 2 === 0 ? 'rgba(30, 30, 50, 0.3)' : 'rgba(40, 40, 60, 0.3)'
                  }}
                >
                  <td className="px-4 py-3 text-sm text-gray-400 font-mono">
                    {ticket.uuid}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-300">
                    {ticket.createdAt}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-300">
                    {ticket.gradedAt}
                  </td>
                  <td className="px-4 py-3 text-sm text-orange-400 font-bold">
                    ${ticket.atRisk.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-sm font-bold" style={{
                    color: ticket.payout > 0 ? '#4ade80' : '#6b7280'
                  }}>
                    ${ticket.payout.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      ticket.status === 'won' ? 'bg-green-500/20 text-green-300' :
                      ticket.status === 'lost' ? 'bg-red-500/20 text-red-300' :
                      ticket.status === 'void' ? 'bg-gray-500/20 text-gray-300' :
                      'bg-blue-500/20 text-blue-300'
                    }`}>
                      {ticket.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => handleViewTicket(ticket)}
                      className="px-3 py-1 rounded text-sm bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 transition-colors"
                    >
                      View
                    </button>
                  </td>
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={selectedTickets.has(ticket.uuid)}
                      onChange={() => handleSelectTicket(ticket.uuid)}
                      className="w-4 h-4 rounded border-orange-500/30 bg-black/30 text-orange-500 focus:ring-orange-500 focus:ring-offset-0 cursor-pointer"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between px-4 py-3 rounded-xl backdrop-blur-md" style={{
        background: 'rgba(20, 20, 40, 0.7)',
        border: '2px solid rgba(251, 146, 60, 0.4)',
      }}>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            className="px-3 py-1 rounded text-sm bg-orange-500/20 hover:bg-orange-500/30 text-orange-300 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          
          {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
            <button
              key={page}
              onClick={() => setCurrentPage(page)}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                currentPage === page
                  ? 'bg-orange-500/40 text-white font-bold'
                  : 'bg-orange-500/20 hover:bg-orange-500/30 text-orange-300'
              }`}
            >
              {page}
            </button>
          ))}
          
          <button
            onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
            disabled={currentPage === totalPages}
            className="px-3 py-1 rounded text-sm bg-orange-500/20 hover:bg-orange-500/30 text-orange-300 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>

        <div className="text-sm text-gray-400">
          Viewing {startIndex + 1}-{Math.min(endIndex, totalRecords)} of {totalRecords} records
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 text-xs text-green-400">
            <span>✓</span>
            <span>Ready!</span>
          </div>
          <button
            onClick={handleDeleteSelected}
            disabled={selectedTickets.size === 0}
            className="px-3 py-1 rounded text-sm bg-red-500/20 hover:bg-red-500/30 text-red-300 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Archive Sel.
          </button>
          <button
            onClick={handleSelectAll}
            className="px-3 py-1 rounded text-sm bg-gray-500/20 hover:bg-gray-500/30 text-gray-300 transition-colors"
          >
            (De)Select All
          </button>
        </div>
      </div>

      {/* Ticket Viewer Modal */}
      {viewingTicket && (
        <div 
          className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          onClick={() => setViewingTicket(null)}
        >
          <div 
            className="rounded-2xl p-6 max-w-2xl w-full backdrop-blur-md"
            style={{
              background: 'rgba(20, 20, 40, 0.95)',
              border: '2px solid rgba(251, 146, 60, 0.6)',
              boxShadow: '0 8px 32px rgba(251, 146, 60, 0.5)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-2xl font-bold text-white mb-1">
                  Ticket Details
                </h3>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${
                    viewingTicket.status === 'won' ? 'bg-green-500/20 text-green-300' :
                    viewingTicket.status === 'lost' ? 'bg-red-500/20 text-red-300' :
                    viewingTicket.status === 'void' ? 'bg-gray-500/20 text-gray-300' :
                    'bg-blue-500/20 text-blue-300'
                  }`}>
                    {viewingTicket.status.toUpperCase()}
                  </span>
                  <span className="text-sm text-gray-400">{viewingTicket.gradedAt}</span>
                </div>
              </div>
              <button
                onClick={() => setViewingTicket(null)}
                className="text-gray-400 hover:text-white text-2xl leading-none"
              >
                ×
              </button>
            </div>

            {/* Ticket Stats */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="rounded-lg p-4" style={{
                background: 'rgba(10, 10, 20, 0.6)',
                border: '1px solid rgba(251, 146, 60, 0.2)'
              }}>
                <p className="text-sm text-gray-400 mb-1">At Risk</p>
                <p className="text-2xl font-bold text-orange-400">
                  ${viewingTicket.atRisk.toFixed(2)}
                </p>
              </div>
              <div className="rounded-lg p-4" style={{
                background: 'rgba(10, 10, 20, 0.6)',
                border: '1px solid rgba(251, 146, 60, 0.2)'
              }}>
                <p className="text-sm text-gray-400 mb-1">Payout</p>
                <p className={`text-2xl font-bold ${
                  viewingTicket.payout > 0 ? 'text-green-400' : 'text-gray-500'
                }`}>
                  ${viewingTicket.payout.toFixed(2)}
                </p>
              </div>
            </div>

            {/* Net Profit/Loss */}
            <div className="rounded-lg p-4 mb-4" style={{
              background: viewingTicket.payout > viewingTicket.atRisk 
                ? 'rgba(16, 185, 129, 0.1)' 
                : viewingTicket.status === 'void'
                ? 'rgba(107, 114, 128, 0.1)'
                : 'rgba(239, 68, 68, 0.1)',
              border: `1px solid ${
                viewingTicket.payout > viewingTicket.atRisk 
                  ? 'rgba(16, 185, 129, 0.3)' 
                  : viewingTicket.status === 'void'
                  ? 'rgba(107, 114, 128, 0.3)'
                  : 'rgba(239, 68, 68, 0.3)'
              }`
            }}>
              <p className="text-sm text-gray-400 mb-1">Net Profit/Loss</p>
              <p className={`text-3xl font-bold ${
                viewingTicket.payout > viewingTicket.atRisk ? 'text-green-400' :
                viewingTicket.status === 'void' ? 'text-gray-400' :
                'text-red-400'
              }`}>
                {viewingTicket.payout > viewingTicket.atRisk ? '+' : ''}
                ${(viewingTicket.payout - viewingTicket.atRisk).toFixed(2)}
              </p>
            </div>

            {/* Ticket Meta */}
            <div className="grid grid-cols-2 gap-4 text-sm mb-4">
              <div>
                <span className="text-gray-400">UUID:</span>
                <p className="text-gray-300 font-mono text-xs mt-1 break-all">
                  {viewingTicket.uuid}
                </p>
              </div>
              <div>
                <span className="text-gray-400">Number of Picks:</span>
                <p className="text-white font-semibold mt-1">
                  {viewingTicket.picks}
                </p>
              </div>
              <div>
                <span className="text-gray-400">Created:</span>
                <p className="text-white mt-1">
                  {viewingTicket.createdAt}
                </p>
              </div>
              <div>
                <span className="text-gray-400">Graded:</span>
                <p className="text-white mt-1">
                  {viewingTicket.gradedAt}
                </p>
              </div>
            </div>

            {/* Picks Details Placeholder */}
            <div className="rounded-lg p-4 mb-4" style={{
              background: 'rgba(10, 10, 20, 0.6)',
              border: '1px solid rgba(251, 146, 60, 0.2)'
            }}>
              <p className="text-sm text-gray-400 text-center">
                Ticket picks and event details will be loaded from backend API
              </p>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <button
                onClick={() => setViewingTicket(null)}
                className="flex-1 py-2 rounded bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold transition-all"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
