import React, { useState } from 'react';
import { DataTable } from '../common/DataTable';

// Get API prefix from URL path
function getApiPrefix(): string {
  const pathParts = window.location.pathname.split('/').filter(p => p);
  if (pathParts.length > 0) {
    return `/api/v1/${pathParts[0]}/`;
  }
  return '/api/v1/';
}

export function PendingTicketsTable() {
  const [selectedTicket, setSelectedTicket] = useState<any>(null);
  const [ticketDetails, setTicketDetails] = useState<any>(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [selectedTickets, setSelectedTickets] = useState<Set<string>>(new Set());

  console.log('🎫 PendingTicketsTable component rendered');

  const API_PREFIX = getApiPrefix();

  // Fetch full ticket details
  const fetchTicketDetails = async (uuid: string) => {
    setLoadingDetails(true);
    try {
      const url = `${API_PREFIX}game/ticket/details/viewer/${uuid}`;
      console.log('📊 Fetching ticket details:', url);

      const response = await fetch(url, {
        method: 'GET',
        credentials: 'include',
      });

      if (!response.ok) {
        if (response.status === 401) {
          alert('Session Expired\n\nYour session has expired. Please log in again.');
          localStorage.removeItem('sportslotto_user');
          window.location.href = '/';
          throw new Error('Session expired');
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('✅ Ticket details:', result);

      if (result.res === 'ok' && result.data) {
        setTicketDetails(result.data);
      } else {
        throw new Error(result.err || 'Failed to load ticket details');
      }
    } catch (err) {
      console.error('❌ Ticket details error:', err);
      alert('Failed to load ticket details: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setLoadingDetails(false);
    }
  };

  const handleRowClick = (row: any) => {
    console.log('Ticket clicked:', row);
    setSelectedTicket(row);
    fetchTicketDetails(row.uuid);
  };

  // Toggle individual ticket selection
  const toggleTicketSelection = (uuid: string) => {
    setSelectedTickets((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(uuid)) {
        newSet.delete(uuid);
      } else {
        newSet.add(uuid);
      }
      return newSet;
    });
  };

  // Select/Deselect all (would need to track all visible tickets)
  const handleSelectAll = () => {
    // This would toggle all visible tickets - implementation depends on DataTable exposing current rows
    console.log('Select/Deselect all clicked');
  };

  const additionalColumns = [
    {
      key: 'picks',
      name: 'PICKS',
      render: (row: any) => (
        <div className="text-center text-white">
          {row.picks || 1}
        </div>
      ),
    },
    {
      key: 'view_ticket',
      name: 'VIEW TICKET',
      render: (row: any) => (
        <button
          className="btn btn-sm"
          style={{
            background: 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)',
            border: 'none',
            color: '#fff',
            fontWeight: '600',
            padding: '0.4rem 1rem',
            borderRadius: '6px',
            fontSize: '0.875rem',
            transition: 'all 0.2s ease',
          }}
          onClick={(e) => {
            e.stopPropagation();
            setSelectedTicket(row);
            fetchTicketDetails(row.uuid);
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'scale(1.05)';
            e.currentTarget.style.boxShadow = '0 4px 12px rgba(139, 92, 246, 0.6)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'scale(1)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          View
        </button>
      ),
    },
    {
      key: 'select',
      name: 'SELECT',
      render: (row: any) => (
        <div className="text-center">
          <input
            type="checkbox"
            className="form-check-input"
            checked={selectedTickets.has(row.uuid)}
            onChange={(e) => {
              e.stopPropagation();
              toggleTicketSelection(row.uuid);
            }}
            style={{
              width: '18px',
              height: '18px',
              cursor: 'pointer',
              borderColor: 'rgba(168, 85, 247, 0.5)',
            }}
          />
        </div>
      ),
    },
  ];

  const handleCloseModal = () => {
    setSelectedTicket(null);
    setTicketDetails(null);
  };

  // Custom render for risk and win columns with color
  const customColumnRender = (value: any, columnKey: string) => {
    if (columnKey === 'risk') {
      return (
        <span style={{ color: '#fb923c', fontWeight: '600' }}>
          ${typeof value === 'number' ? value.toFixed(2) : value}
        </span>
      );
    }
    if (columnKey === 'win') {
      return (
        <span style={{ color: '#4ade80', fontWeight: '600' }}>
          ${typeof value === 'number' ? value.toFixed(2) : value}
        </span>
      );
    }
    return value;
  };

  return (
    <div className="pending-tickets-container p-4">
      <div className="mb-4">
        <h2
          className="text-white mb-2"
          style={{
            fontFamily: 'Orbitron, sans-serif',
            fontSize: '1.5rem',
            fontWeight: '700',
            color: '#a855f7',
          }}
        >
          Open Tickets
        </h2>
      </div>

      <DataTable
        endpoint="tickets/previous/table/"
        pageSize={15}
        onRowClick={handleRowClick}
        additionalColumns={additionalColumns}
        emptyMessage="No open tickets found"
        enableSearch={false}
        enableSort={true}
        enablePagination={true}
        customColumnRender={customColumnRender}
      />

      {/* Select All / Deselect All Button */}
      {selectedTickets.size > 0 && (
        <div className="mt-3 text-end">
          <button
            className="btn btn-outline-light btn-sm"
            onClick={handleSelectAll}
          >
            (De)Select All
          </button>
        </div>
      )}

      {/* Ticket Details Modal */}
      {selectedTicket && (
        <div
          className="modal show d-block"
          style={{
            backgroundColor: 'rgba(0, 0, 0, 0.85)',
            backdropFilter: 'blur(12px)',
            WebkitBackdropFilter: 'blur(12px)',
            zIndex: 9999,
          }}
          onClick={handleCloseModal}
        >
          <div
            className="modal-dialog modal-dialog-centered modal-xl modal-dialog-scrollable"
            onClick={(e) => e.stopPropagation()}
          >
            <div
              className="modal-content"
              style={{
                background: 'linear-gradient(135deg, rgba(30, 20, 50, 0.98) 0%, rgba(15, 10, 30, 0.98) 100%)',
                backdropFilter: 'blur(40px)',
                WebkitBackdropFilter: 'blur(40px)',
                border: '2px solid rgba(168, 85, 247, 0.6)',
                borderRadius: '24px',
                boxShadow: '0 20px 60px rgba(168, 85, 247, 0.5)',
              }}
            >
              <div className="modal-header border-0" style={{
                borderBottom: '1px solid rgba(168, 85, 247, 0.3)',
                background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.15) 0%, rgba(236, 72, 153, 0.15) 100%)',
              }}>
                <h5 className="modal-title text-white fw-bold">
                  <i className="fas fa-ticket-alt me-2"></i>
                  Ticket Details - {selectedTicket.uuid.slice(0, 8)}...
                </h5>
                <button
                  type="button"
                  className="btn-close btn-close-white"
                  onClick={handleCloseModal}
                ></button>
              </div>
              <div className="modal-body text-white" style={{ minHeight: '300px' }}>
                {loadingDetails ? (
                  <div className="text-center py-5">
                    <div className="spinner-border text-primary mb-3" role="status" style={{ width: '3rem', height: '3rem' }}>
                      <span className="visually-hidden">Loading...</span>
                    </div>
                    <p className="text-white-50">Loading ticket details...</p>
                  </div>
                ) : ticketDetails ? (
                  <div className="row g-3">
                    {/* Basic Info */}
                    <div className="col-12">
                      <div
                        className="p-4"
                        style={{
                          background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.15) 0%, rgba(236, 72, 153, 0.15) 100%)',
                          borderRadius: '12px',
                          border: '1px solid rgba(168, 85, 247, 0.3)',
                        }}
                      >
                        <h6 className="text-white mb-3 fw-bold">
                          <i className="fas fa-info-circle me-2"></i>
                          Ticket Information
                        </h6>
                        <div className="row g-3">
                          <div className="col-md-6">
                            <div className="d-flex justify-content-between align-items-center">
                              <span className="text-white-50">Ticket ID:</span>
                              <span className="text-white fw-semibold">{selectedTicket.uuid}</span>
                            </div>
                          </div>
                          <div className="col-md-6">
                            <div className="d-flex justify-content-between align-items-center">
                              <span className="text-white-50">Created:</span>
                              <span className="text-white fw-semibold">{selectedTicket.created}</span>
                            </div>
                          </div>
                          <div className="col-md-6">
                            <div className="d-flex justify-content-between align-items-center">
                              <span className="text-white-50">Risk:</span>
                              <span style={{ color: '#fb923c', fontWeight: '700', fontSize: '1.1rem' }}>
                                ${selectedTicket.risk.toFixed(2)}
                              </span>
                            </div>
                          </div>
                          <div className="col-md-6">
                            <div className="d-flex justify-content-between align-items-center">
                              <span className="text-white-50">To Win:</span>
                              <span style={{ color: '#4ade80', fontWeight: '700', fontSize: '1.1rem' }}>
                                ${selectedTicket.win.toFixed(2)}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Full Details */}
                    <div className="col-12">
                      <div
                        className="p-4"
                        style={{
                          background: 'rgba(0, 0, 0, 0.3)',
                          borderRadius: '12px',
                          border: '1px solid rgba(168, 85, 247, 0.2)',
                        }}
                      >
                        <h6 className="text-white mb-3 fw-bold">
                          <i className="fas fa-list me-2"></i>
                          Complete Details
                        </h6>
                        <pre style={{
                          color: '#fff',
                          background: 'rgba(0, 0, 0, 0.5)',
                          padding: '1.5rem',
                          borderRadius: '8px',
                          fontSize: '0.875rem',
                          maxHeight: '400px',
                          overflowY: 'auto',
                          border: '1px solid rgba(168, 85, 247, 0.2)',
                        }}>
                          {JSON.stringify(ticketDetails, null, 2)}
                        </pre>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-5">
                    <i className="fas fa-exclamation-circle text-warning fa-3x mb-3"></i>
                    <p className="text-white-50">No details available</p>
                  </div>
                )}
              </div>
              <div className="modal-footer border-0" style={{
                borderTop: '1px solid rgba(168, 85, 247, 0.3)',
              }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleCloseModal}
                  style={{
                    background: 'linear-gradient(135deg, rgba(100, 100, 100, 0.5) 0%, rgba(80, 80, 80, 0.5) 100%)',
                    border: 'none',
                    fontWeight: '600',
                  }}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}