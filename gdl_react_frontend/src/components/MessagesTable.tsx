/**
 * Messages Table Component
 * 
 * Displays user messages (deposits, withdrawals, bonuses, system notifications)
 * in a table format matching the tickets table design.
 */

import React, { useState } from 'react';

// Message type definition
interface Message {
  uuid: string;
  title: string;
  type: 'deposit' | 'withdraw' | 'bonus' | 'system';
  createdAt: string;
  seenAt: string | null;
  content: string;
  status: 'pending' | 'completed' | 'failed';
}

export function MessagesTable() {
  const [selectedMessages, setSelectedMessages] = useState<Set<string>>(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const [viewingMessage, setViewingMessage] = useState<Message | null>(null);
  const itemsPerPage = 15;

  // Mock data - Replace with API call: useMessages() hook
  const mockMessages: Message[] = [
    {
      uuid: '62963392-928f-4464-acc8-899f300fafa4',
      title: 'Withdraw Pending',
      type: 'withdraw',
      createdAt: '2026-01-27 20:34:34',
      seenAt: null,
      content: 'Your withdrawal request of $500.00 is being processed.',
      status: 'pending'
    },
    {
      uuid: '77fa549b-927a-45d5-a4e4-2fcaf0c3459f4',
      title: 'Deposit Pending',
      type: 'deposit',
      createdAt: '2026-01-21 14:26:53',
      seenAt: null,
      content: 'Your deposit of $100.00 is pending confirmation.',
      status: 'pending'
    },
    {
      uuid: '9f3f6ac7-aef3-4c12-ace6-d0de02ba353c',
      title: 'Deposit',
      type: 'deposit',
      createdAt: '2026-01-21 14:26:46',
      seenAt: null,
      content: 'Your deposit of $250.00 has been successfully credited to your account.',
      status: 'completed'
    },
    {
      uuid: '1ea0adb-2b21-4da9-8d27-ad56dc7fa638',
      title: 'Deposit Pending',
      type: 'deposit',
      createdAt: '2026-01-21 14:23:09',
      seenAt: null,
      content: 'Your deposit of $75.00 is pending.',
      status: 'pending'
    },
    {
      uuid: 'a153e38e-88a1-4696-92b2-4792fae87a5',
      title: 'Deposit Pending',
      type: 'deposit',
      createdAt: '2026-01-21 14:22:54',
      seenAt: null,
      content: 'Your deposit of $150.00 is being processed.',
      status: 'pending'
    },
    {
      uuid: '5279be98-5fe4-47c3-b483-c73ea7a008fe',
      title: 'Deposit',
      type: 'deposit',
      createdAt: '2026-01-20 14:49:57',
      seenAt: null,
      content: 'Your deposit of $200.00 has been completed.',
      status: 'completed'
    },
    {
      uuid: '4bd844db-64f2-48c2-a896-0a652c786e36',
      title: 'Deposit Pending',
      type: 'deposit',
      createdAt: '2026-01-20 14:36:47',
      seenAt: null,
      content: 'Deposit pending approval.',
      status: 'pending'
    },
    {
      uuid: 'aa2056cb-3f4f-4cd8-b04e-3658856a6095',
      title: 'Deposit Pending',
      type: 'deposit',
      createdAt: '2026-01-20 14:34:00',
      seenAt: null,
      content: 'Deposit pending.',
      status: 'pending'
    },
    {
      uuid: 'db2f3e6b-d862-419e-be00-42069f1279e9',
      title: 'Bonus',
      type: 'bonus',
      createdAt: '2026-01-20 09:33:57',
      seenAt: '2026-01-20 09:35:11',
      content: 'Welcome bonus of $50.00 has been credited to your account!',
      status: 'completed'
    },
    {
      uuid: '1ce78369-b1f3-4d20-887c-3ab237af61bf',
      title: 'Bonus',
      type: 'bonus',
      createdAt: '2026-01-20 09:33:57',
      seenAt: '2026-01-20 09:35:08',
      content: 'Daily login bonus $10.00 added.',
      status: 'completed'
    },
    {
      uuid: 'bb5c97c-a2fc-45c1-a6d4-42091fa048cb',
      title: 'Bonus',
      type: 'bonus',
      createdAt: '2026-01-20 09:33:57',
      seenAt: '2026-01-20 09:35:04',
      content: 'Referral bonus $25.00 credited.',
      status: 'completed'
    },
    {
      uuid: 'a6fa0029-3829a-0a5f-9dae-7bb5c8baa218',
      title: 'Bonus',
      type: 'bonus',
      createdAt: '2026-01-20 09:33:57',
      seenAt: '2026-01-20 09:34:56',
      content: 'Reload bonus $15.00 applied.',
      status: 'completed'
    },
    {
      uuid: 'e0c4d8c8-a196-4196-8dc4-e08027d087a9',
      title: 'Bonus',
      type: 'bonus',
      createdAt: '2026-01-20 09:33:57',
      seenAt: '2026-01-20 09:34:46',
      content: 'VIP bonus $100.00 awarded!',
      status: 'completed'
    },
    {
      uuid: '932e1ef6-8411-4418-b0fa-85eb86c48ec0',
      title: 'Deposit',
      type: 'deposit',
      createdAt: '2026-01-20 09:33:57',
      seenAt: '2026-01-20 09:34:53',
      content: 'Deposit successful.',
      status: 'completed'
    },
    {
      uuid: 'aef9f934-fde9-48f9-8f9f-ac0000128af6',
      title: 'Deposit Pending',
      type: 'deposit',
      createdAt: '2026-01-20 09:19:34',
      seenAt: null,
      content: 'Awaiting deposit confirmation.',
      status: 'pending'
    },
  ];

  const totalRecords = mockMessages.length;
  const totalPages = Math.ceil(totalRecords / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentMessages = mockMessages.slice(startIndex, endIndex);

  const handleSelectAll = () => {
    if (selectedMessages.size === currentMessages.length) {
      setSelectedMessages(new Set());
    } else {
      setSelectedMessages(new Set(currentMessages.map(m => m.uuid)));
    }
  };

  const handleSelectMessage = (uuid: string) => {
    const newSelected = new Set(selectedMessages);
    if (newSelected.has(uuid)) {
      newSelected.delete(uuid);
    } else {
      newSelected.add(uuid);
    }
    setSelectedMessages(newSelected);
  };

  const handleViewMessage = (message: Message) => {
    setViewingMessage(message);
    // Mark as seen
    // TODO: API call to mark message as seen
  };

  const handleDeleteSelected = () => {
    if (selectedMessages.size === 0) return;
    if (confirm(`Delete ${selectedMessages.size} selected message(s)?`)) {
      // TODO: API call to delete messages
      setSelectedMessages(new Set());
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
          Messages
        </h2>
        <div className="flex items-center gap-2">
          {selectedMessages.size > 0 && (
            <>
              <button
                onClick={handleDeleteSelected}
                className="px-4 py-2 rounded bg-red-500/20 hover:bg-red-500/30 text-red-300 transition-colors text-sm"
              >
                Delete Sel.
              </button>
              <button
                onClick={() => setSelectedMessages(new Set())}
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
                  Title
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  created at
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  Seen At
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  View Message
                </th>
                <th className="px-4 py-3 text-left text-xs font-bold text-orange-300 uppercase tracking-wider">
                  Select
                </th>
              </tr>
            </thead>
            <tbody>
              {currentMessages.map((message, index) => (
                <tr 
                  key={message.uuid}
                  className="border-b border-orange-500/10 hover:bg-orange-500/5 transition-colors"
                  style={{
                    background: index % 2 === 0 ? 'rgba(30, 30, 50, 0.3)' : 'rgba(40, 40, 60, 0.3)'
                  }}
                >
                  <td className="px-4 py-3 text-sm text-gray-400 font-mono">
                    {message.uuid}
                  </td>
                  <td className="px-4 py-3 text-sm text-white font-semibold">
                    {message.title}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-300">
                    {message.createdAt}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-300">
                    {message.seenAt || '-'}
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => handleViewMessage(message)}
                      className="px-3 py-1 rounded text-sm bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 transition-colors"
                    >
                      View
                    </button>
                  </td>
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={selectedMessages.has(message.uuid)}
                      onChange={() => handleSelectMessage(message.uuid)}
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
            disabled={selectedMessages.size === 0}
            className="px-3 py-1 rounded text-sm bg-red-500/20 hover:bg-red-500/30 text-red-300 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Delete Sel.
          </button>
          <button
            onClick={handleSelectAll}
            className="px-3 py-1 rounded text-sm bg-gray-500/20 hover:bg-gray-500/30 text-gray-300 transition-colors"
          >
            (De)Select All
          </button>
        </div>
      </div>

      {/* Message Viewer Modal */}
      {viewingMessage && (
        <div 
          className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          onClick={() => setViewingMessage(null)}
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
                  {viewingMessage.title}
                </h3>
                <p className="text-sm text-gray-400">
                  {viewingMessage.createdAt}
                </p>
              </div>
              <button
                onClick={() => setViewingMessage(null)}
                className="text-gray-400 hover:text-white text-2xl leading-none"
              >
                ×
              </button>
            </div>

            {/* Message Content */}
            <div className="rounded-lg p-4 mb-4" style={{
              background: 'rgba(10, 10, 20, 0.6)',
              border: '1px solid rgba(251, 146, 60, 0.2)'
            }}>
              <p className="text-white leading-relaxed">
                {viewingMessage.content}
              </p>
            </div>

            {/* Message Meta */}
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">UUID:</span>
                <p className="text-gray-300 font-mono text-xs mt-1 break-all">
                  {viewingMessage.uuid}
                </p>
              </div>
              <div>
                <span className="text-gray-400">Type:</span>
                <p className="text-white font-semibold mt-1 capitalize">
                  {viewingMessage.type}
                </p>
              </div>
              <div>
                <span className="text-gray-400">Status:</span>
                <p className="mt-1">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${
                    viewingMessage.status === 'completed' ? 'bg-green-500/20 text-green-300' :
                    viewingMessage.status === 'failed' ? 'bg-red-500/20 text-red-300' :
                    'bg-yellow-500/20 text-yellow-300'
                  }`}>
                    {viewingMessage.status.toUpperCase()}
                  </span>
                </p>
              </div>
              <div>
                <span className="text-gray-400">Seen:</span>
                <p className="text-white mt-1">
                  {viewingMessage.seenAt || 'Not yet'}
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2 mt-6">
              <button
                onClick={() => setViewingMessage(null)}
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
