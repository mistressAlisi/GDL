/**
 * Open Tickets Table Component
 * 
 * Displays open/pending betting tickets using the same format as MessagesTable.
 */

import React, { useState } from 'react';

// Open Ticket type definition
interface OpenTicket {
  uuid: string;
  createdAt: string;
  atRisk: number;
  toWin: number;
  picks: number;
  status: 'pending' | 'active';
}

export function OpenTicketsTable() {
  const [selectedTickets, setSelectedTickets] = useState<Set<string>>(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const [viewingTicket, setViewingTicket] = useState<OpenTicket | null>(null);
  const itemsPerPage = 15;

  // Mock data - Replace with API call: useOpenTickets() hook
  const mockTickets: OpenTicket[] = [
    { uuid: '3ca04ab8-ab07-49e8-9fc2-cd42f1ffd885', createdAt: '2026-01-28 20:18:27', atRisk: 20, picks: 1, toWin: 4941, status: 'pending' },
    { uuid: '14e6f460-2a4c-4974-bda1-95a4c7c49929', createdAt: '2026-01-28 20:18:27', atRisk: 20, picks: 1, toWin: 4934, status: 'pending' },
    { uuid: '51f8bf862-f604-4b88-9c3e-5c8ff06c21f2', createdAt: '2026-01-28 20:16:39', atRisk: 20, picks: 1, toWin: 5062, status: 'pending' },
    { uuid: '505c67b8-6e4d-4c48-978b-e8048c6648d8', createdAt: '2026-01-28 20:16:39', atRisk: 20, picks: 1, toWin: 4906, status: 'pending' },
    { uuid: '576fe44b-5d7a-48fa-839b-d7b3e3d8844e', createdAt: '2026-01-28 20:16:07', atRisk: 1, picks: 1, toWin: 21, status: 'active' },
    { uuid: '4f976b0a-f020-4dc9-99a2-75a57884b03a', createdAt: '2026-01-28 20:16:07', atRisk: 1, picks: 1, toWin: 20, status: 'active' },
    { uuid: '9d33257a-1397-4403-878b-1f8e65ae2a72', createdAt: '2026-01-28 20:16:07', atRisk: 1, picks: 1, toWin: 20, status: 'active' },
    { uuid: '652b848a-ae92-47d1-9385-1ce7778ff809', createdAt: '2026-01-28 20:16:06', atRisk: 1, picks: 1, toWin: 21, status: 'active' },
    { uuid: '480b885f-ddf4-4beb-b0a0-d6b04b8ea402', createdAt: '2026-01-28 20:16:06', atRisk: 1, picks: 1, toWin: 20, status: 'active' },
    { uuid: 'a8c47d4b-7947-472b-b7c5-e2d6f9c49afb', createdAt: '2026-01-28 20:15:11', atRisk: 1, picks: 1, toWin: 21, status: 'pending' },
    { uuid: '995deda1-839a-42dc-ae8b-47bdbc0392e2', createdAt: '2026-01-28 20:15:11', atRisk: 1, picks: 1, toWin: 20, status: 'pending' },
    { uuid: '2eeebf04-f315-4406-afd4-aeb7a872c1f9', createdAt: '2026-01-28 20:15:11', atRisk: 1, picks: 1, toWin: 20, status: 'pending' },
    { uuid: 'ff3b6afe-81e2-4665-a936-c8ca2f4fd166', createdAt: '2026-01-28 20:15:11', atRisk: 1, picks: 1, toWin: 20, status: 'pending' },
    { uuid: 'be07343f-5367-402e-8765-903380f3ddd9', createdAt: '2026-01-28 20:15:11', atRisk: 1, picks: 1, toWin: 20, status: 'active' },
    { uuid: 'a8965427-d0bd-4986-86c7-a9f8c61526f0', createdAt: '2026-01-28 20:15:11', atRisk: 1, picks: 1, toWin: 20, status: 'active' },
    { uuid: '1565cc6f-8120-427f-aba2-404d9af5d68a', createdAt: '2026-01-28 20:15:11', atRisk: 1, picks: 1, toWin: 20, status: 'active' },
    { uuid: 'df41d848-0073-403c-aed7-47259f5638ae', createdAt: '2026-01-28 20:15:11', atRisk: 1, picks: 1, toWin: 20, status: 'pending' },
    { uuid: 'a0c3f8c9-3a4-4f54-834e-e34a61da0e77', createdAt: '2026-01-28 20:15:11', atRisk: 1, picks: 1, toWin: 20, status: 'pending' },
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

  const handleViewTicket = (ticket: OpenTicket) => {
    setViewingTicket(ticket);
  };

  const handleDeleteSelected = () => {
    if (selectedTickets.size === 0) return;
    if (confirm(`Cancel ${selectedTickets.size} selected ticket(s)?`)) {
      // TODO: API call to cancel tickets
      setSelectedTickets(new Set());
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
          Open Tickets
        </h2>
        <div className="flex items-center gap-2">
          {selectedTickets.size > 0 && (
            <>
              <button
                onClick={handleDeleteSelected}
                className="px-4 py-2 rounded bg-red-500/20 hover:bg-red-500/30 text-red-300 transition-colors text-sm"
              >
                Cancel Sel.
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
                  at risk
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  to win
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  picks
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
                  <td className="px-4 py-3 text-sm text-orange-400 font-bold">
                    ${ticket.atRisk.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-sm text-green-400 font-bold">
                    ${ticket.toWin.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-sm text-white font-semibold">
                    {ticket.picks}
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
            Cancel Sel.
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
                <p className="text-sm text-gray-400">
                  {viewingTicket.createdAt}
                </p>
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
                <p className="text-sm text-gray-400 mb-1">To Win</p>
                <p className="text-2xl font-bold text-green-400">
                  ${viewingTicket.toWin.toFixed(2)}
                </p>
              </div>
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
                <span className="text-gray-400">Status:</span>
                <p className="mt-1">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${
                    viewingTicket.status === 'active' ? 'bg-green-500/20 text-green-300' :
                    'bg-yellow-500/20 text-yellow-300'
                  }`}>
                    {viewingTicket.status.toUpperCase()}
                  </span>
                </p>
              </div>
              <div>
                <span className="text-gray-400">Created:</span>
                <p className="text-white mt-1">
                  {viewingTicket.createdAt}
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
              <button
                onClick={() => {
                  if (confirm('Cancel this ticket?')) {
                    // TODO: API call to cancel ticket
                    setViewingTicket(null);
                  }
                }}
                className="flex-1 py-2 rounded bg-red-500/20 hover:bg-red-500/30 text-red-300 font-semibold transition-all border border-red-500/30"
              >
                Cancel Ticket
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
