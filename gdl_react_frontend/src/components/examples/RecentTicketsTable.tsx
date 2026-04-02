/**
 * Example Component: Recent Tickets Table with API Integration
 * 
 * This demonstrates how to integrate the Django backend API
 * for displaying recent tickets data in a table.
 */

import React from 'react';
import { useRecentTickets } from '../../services/api-hooks';

export function RecentTicketsTable() {
  // Fetch recent tickets from backend
  // Set autoRefresh to true to refresh every 30 seconds
  const { tickets, loading, error, refresh } = useRecentTickets(20, true);

  if (loading && tickets.length === 0) {
    return (
      <div className="rounded-2xl p-8 backdrop-blur-md text-center" style={{
        background: 'rgba(20, 20, 40, 0.7)',
        border: '2px solid rgba(251, 146, 60, 0.4)',
      }}>
        <div className="animate-spin text-4xl mb-4">⚡</div>
        <p className="text-gray-300">Loading recent tickets...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-2xl p-8 backdrop-blur-md" style={{
        background: 'rgba(20, 20, 40, 0.7)',
        border: '2px solid rgba(239, 68, 68, 0.4)',
      }}>
        <p className="text-red-400">❌ {error}</p>
        <button 
          onClick={refresh}
          className="mt-4 px-4 py-2 rounded bg-orange-500 hover:bg-orange-600 text-white"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
          Recent Tickets
        </h2>
        <button
          onClick={refresh}
          disabled={loading}
          className="px-4 py-2 rounded bg-orange-500/20 hover:bg-orange-500/30 text-orange-300 transition-colors disabled:opacity-50"
        >
          {loading ? '↻ Refreshing...' : '↻ Refresh'}
        </button>
      </div>

      {/* Table */}
      <div className="rounded-2xl overflow-hidden backdrop-blur-md" style={{
        background: 'rgba(20, 20, 40, 0.7)',
        border: '2px solid rgba(251, 146, 60, 0.4)',
      }}>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-orange-500/30">
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  Ticket ID
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  Player
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  Entries
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  Wager
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  Total Odds
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  Potential
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  Date
                </th>
              </tr>
            </thead>
            <tbody>
              {tickets.map((ticket, index) => (
                <tr 
                  key={ticket.id}
                  className="border-b border-orange-500/10 hover:bg-orange-500/5 transition-colors"
                >
                  <td className="px-4 py-3 text-sm text-gray-300">
                    {ticket.id.substring(0, 12)}...
                  </td>
                  <td className="px-4 py-3 text-sm text-white font-semibold">
                    {ticket.userName || 'Guest'}
                  </td>
                  <td className="px-4 py-3 text-sm text-white">
                    {ticket.entries}
                  </td>
                  <td className="px-4 py-3 text-sm text-orange-400 font-bold">
                    ${ticket.wager.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-sm text-purple-400 font-bold">
                    {ticket.totalOdds.toFixed(2)}x
                  </td>
                  <td className="px-4 py-3 text-sm text-green-400 font-bold">
                    ${ticket.potentialPayout.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      ticket.status === 'won' ? 'bg-green-500/20 text-green-300' :
                      ticket.status === 'lost' ? 'bg-red-500/20 text-red-300' :
                      ticket.status === 'void' ? 'bg-gray-500/20 text-gray-300' :
                      'bg-yellow-500/20 text-yellow-300'
                    }`}>
                      {ticket.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-400">
                    {new Date(ticket.createdAt).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Empty State */}
        {tickets.length === 0 && !loading && (
          <div className="p-8 text-center text-gray-400">
            No recent tickets found
          </div>
        )}
      </div>
    </div>
  );
}
