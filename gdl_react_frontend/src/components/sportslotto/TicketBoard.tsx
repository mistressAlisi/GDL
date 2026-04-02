import React, { useState, useEffect } from 'react';
import { X, Check } from 'lucide-react';
import { generateCustomTickets, replaceTicket, CustomTicketFormData, DjangoTicketResponse } from '../../sportslotto/services/ticket-websocket-adapter';
import { acceptTicket, rejectTicket, TicketData } from '../../sportslotto/services/api';
import { useCart } from '../../sportslotto/contexts/CartContext';

// Browser-compatible UUID generation function
// Fallback for browsers that don't support crypto.randomUUID()
function generateUUID(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  
  // Fallback using crypto.getRandomValues (broader browser support)
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = (crypto.getRandomValues(new Uint8Array(1))[0] & 15) >> (c === 'x' ? 0 : 3);
    return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
  });
}

interface TicketBoardProps {
  formData: CustomTicketFormData;
  onBack: () => void;
  onAddToCart: (ticket: DjangoTicketResponse) => void;
}

interface TicketSlot {
  ticket: DjangoTicketResponse | null;
  status: 'loading' | 'ready' | 'accepted' | 'rejected';
  flipped: boolean;
}

export function TicketBoard({ formData, onBack, onAddToCart }: TicketBoardProps) {
  // Use a Map to store tickets by UUID (prevents duplicates and ensures idempotency)
  const [ticketsMap, setTicketsMap] = useState<Map<string, TicketSlot>>(new Map());
  const { cartCount, setCartCount } = useCart(); // Use cart context instead of local state
  const [showProcessing, setShowProcessing] = useState(true);
  const [selectedTicket, setSelectedTicket] = useState<DjangoTicketResponse | null>(null);
  const [selectedCardUuid, setSelectedCardUuid] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  // Initialize and generate tickets
  useEffect(() => {
    console.log('🚀 Starting ticket generation');

    // Clear existing tickets
    setTicketsMap(new Map());

    generateCustomTickets(
      formData,
      (ticket) => {
        // Generate a random UUID for this ticket card (ticket.uuid doesn't exist from Django)
        const cardUuid = generateUUID();
        console.log('🎫 onTicket() called! Ticket received, generating card UUID:', cardUuid);

        // Add ticket to map using generated UUID as key (prevents duplicates)
        setTicketsMap(prev => {
          const newMap = new Map(prev);
          newMap.set(cardUuid, {
            ticket,
            status: 'ready',
            flipped: false,
          });
          console.log(`   Total tickets in map: ${newMap.size}`);
          return newMap;
        });

        // Hide processing modal after first ticket
        setShowProcessing(false);
      },
      (error) => {
        console.error('❌ Ticket generation error:', error);
        setShowProcessing(false);
      }
    );
  }, [formData]);

  // Convert map to array for rendering
  const ticketsArray = Array.from(ticketsMap.entries());

  // Handle reject (replace ticket)
  const handleReject = (uuid: string) => {
    const slot = ticketsMap.get(uuid);
    if (!slot?.ticket) return;

    // Mark as rejected and show loading
    setTicketsMap(prev => {
      const newMap = new Map(prev);
      newMap.set(uuid, {
        ...slot,
        status: 'loading',
        flipped: false,
      });
      return newMap;
    });

    // Request replacement
    replaceTicket(
      formData,
      slot.ticket.uuid,
      (newTicket) => {
        // Replace with new ticket (remove old, add new with new UUID)
        setTicketsMap(prev => {
          const newMap = new Map(prev);
          newMap.delete(uuid); // Remove old ticket
          newMap.set(newTicket.uuid, {
            ticket: newTicket,
            status: 'ready',
            flipped: false,
          });
          return newMap;
        });
      },
      (error) => {
        console.error('Replacement error:', error);
        // Restore original ticket on error
        setTicketsMap(prev => {
          const newMap = new Map(prev);
          newMap.set(uuid, {
            ...slot,
            status: 'ready',
          });
          return newMap;
        });
      }
    );
  };

  // Handle accept (add to cart)
  const handleAccept = async (uuid: string) => {
    const slot = ticketsMap.get(uuid);
    if (!slot?.ticket) return;

    const ticket = slot.ticket;
    console.log('✅ Accepting ticket:', ticket);

    // Validate required fields
    if ( !ticket.muuids || !ticket.outcomes || !ticket.lines) {
      console.error('❌ Ticket missing required fields:', ticket);
      alert('Cannot accept ticket: missing required data');
      return;
    }

    // Mark as loading immediately
    setTicketsMap(prev => {
      const newMap = new Map(prev);
      newMap.set(uuid, {
        ...slot,
        status: 'loading',
        flipped: false,
      });
      return newMap;
    });

    try {
      // Convert DjangoTicketResponse to TicketData format for API
      const ticketData: TicketData = {
        uuid: ticket.uuid,
        muuids: ticket.muuids || [],
        outcomes: ticket.outcomes || [],
        lines: ticket.lines || [],
        stake: ticket.total_stake,
        returns: ticket.total_returns,
        outcome_meta: ticket.outcome_meta || {},
        depth: ticket.depth,
      };

      // POST to accept_ticket REST API
      const response = await acceptTicket(ticketData);

      if (response.res === 'ok') {
        console.log('✅ Ticket accepted successfully:', response);

        // Update cart count from server response
        if (response.data?.count !== undefined) {
          setCartCount(response.data.count);
        } else {
          setCartCount(prev => prev + 1);
        }

        // Notify parent component (for updating cart UI)
        onAddToCart(slot.ticket);

        // Request replacement ticket
        replaceTicket(
          formData,
          ticket.uuid,
          (newTicket) => {
            // Generate new card UUID and replace the old ticket
            const newCardUuid = generateUUID();
            setTicketsMap(prev => {
              const newMap = new Map(prev);
              newMap.delete(uuid); // Remove old ticket
              newMap.set(newCardUuid, {
                ticket: newTicket,
                status: 'ready',
                flipped: false,
              });
              return newMap;
            });
          },
          (error) => {
            console.error('Replacement error:', error);
            // Just remove the accepted ticket on replacement error
            setTicketsMap(prev => {
              const newMap = new Map(prev);
              newMap.delete(uuid);
              return newMap;
            });
          }
        );
      } else {
        // API returned error
        console.error('❌ Accept ticket API error:', response.err);
        alert(`Failed to accept ticket: ${response.err || 'Unknown error'}`);

        // Restore original ticket
        setTicketsMap(prev => {
          const newMap = new Map(prev);
          newMap.set(uuid, {
            ...slot,
            status: 'ready',
          });
          return newMap;
        });
      }
    } catch (error) {
      console.error('❌ Accept ticket error:', error);
      alert('Failed to accept ticket. Please try again.');

      // Restore original ticket
      setTicketsMap(prev => {
        const newMap = new Map(prev);
        newMap.set(uuid, {
          ...slot,
          status: 'ready',
        });
        return newMap;
      });
    }
  };

  // Toggle flip
  const handleFlip = (uuid: string) => {
    const slot = ticketsMap.get(uuid);
    if (!slot) return;

    setTicketsMap(prev => {
      const newMap = new Map(prev);
      newMap.set(uuid, {
        ...slot,
        flipped: !slot.flipped,
      });
      return newMap;
    });
  };

  // Show ticket details
  const handleShowDetails = (ticket: DjangoTicketResponse, uuid: string) => {
    setSelectedTicket(ticket);
    setSelectedCardUuid(uuid);
    setShowDetails(true);
  };

  return (
    <div className="ticket-board-container min-h-screen" style={{ background: 'linear-gradient(135deg, #1a0033 0%, #000000 100%)' }}>

      {/* Processing Modal */}
      {showProcessing && (
        <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.8)' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content bg-dark text-white text-center p-5" style={{
              border: '2px solid rgba(138, 43, 226, 0.5)',
              borderRadius: '24px',
            }}>
              <div className="spinner-border text-primary mx-auto mb-4" style={{ width: '4rem', height: '4rem' }}></div>
              <h4 className="mb-2">Processing...</h4>
              <p className="text-muted">Ticket Generation in progress</p>
              <div className="d-flex justify-content-center gap-2 mt-3">
                <div className="spinner-grow spinner-grow-sm text-primary"></div>
                <div className="spinner-grow spinner-grow-sm text-primary" style={{ animationDelay: '0.2s' }}></div>
                <div className="spinner-grow spinner-grow-sm text-primary" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="container-fluid py-3">
        <div className="d-flex justify-content-center align-items-center">
          <button
            onClick={onBack}
            className="btn"
            style={{
              background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.3) 0%, rgba(236, 72, 153, 0.3) 100%)',
              backdropFilter: 'blur(10px)',
              border: '2px solid rgba(168, 85, 247, 0.5)',
              borderRadius: '12px',
              color: '#fff',
              fontWeight: '600',
              padding: '0.5rem 1.5rem',
              fontSize: '0.95rem',
              boxShadow: '0 4px 15px rgba(168, 85, 247, 0.3)',
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 6px 25px rgba(168, 85, 247, 0.5)';
              e.currentTarget.style.borderColor = 'rgba(168, 85, 247, 0.8)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 15px rgba(168, 85, 247, 0.3)';
              e.currentTarget.style.borderColor = 'rgba(168, 85, 247, 0.5)';
            }}
          >
            <i className="fa-solid fa-arrow-left me-2"></i>
            Back to Menu
          </button>
        </div>
      </div>

      {/* Ticket Grid - Horizontal Flex Layout */}
      <div className="px-4 py-3" id="gdl_play_area" style={{ width: '100%' }}>
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'space-around',
            alignItems: 'start',
            gap: '16px',
            padding: '0',
            width: '100%',
          }}
        >
          {ticketsArray.map(([uuid, slot], index) => (
            <TicketCard
              key={uuid}
              slot={slot}
              index={index}
              onReject={() => handleReject(uuid)}
              onAccept={() => handleAccept(uuid)}
              onFlip={() => handleFlip(uuid)}
              onShowDetails={() => slot.ticket && handleShowDetails(slot.ticket, uuid)}
            />
          ))}
        </div>
      </div>

      {/* Ticket Details Modal */}
      {showDetails && selectedTicket && selectedCardUuid && (
        <TicketDetailsModal
          ticket={selectedTicket}
          onClose={() => {
            setShowDetails(false);
            setSelectedTicket(null);
            setSelectedCardUuid(null);
          }}
          onAccept={() => {
            if (selectedCardUuid) {
              handleAccept(selectedCardUuid);
              setShowDetails(false);
              setSelectedTicket(null);
              setSelectedCardUuid(null);
            }
          }}
          onReject={() => {
            if (selectedCardUuid) {
              handleReject(selectedCardUuid);
              setShowDetails(false);
              setSelectedTicket(null);
              setSelectedCardUuid(null);
            }
          }}
        />
      )}
    </div>
  );
}

// Individual Ticket Card
interface TicketCardProps {
  slot: TicketSlot;
  index: number;
  onReject: () => void;
  onAccept: () => void;
  onFlip: () => void;
  onShowDetails: () => void;
}

function TicketCard({ slot, index, onReject, onAccept, onFlip, onShowDetails }: TicketCardProps) {
  const { ticket, status, flipped } = slot;

  // Loading state - Don't show anything until ticket is ready
  if (status === 'loading' || !ticket) {
    return null;
  }

  // Get random glowing border color
  const borderColors = [
    'rgba(236, 72, 153, 0.8)', // pink
    'rgba(34, 197, 94, 0.8)',  // green
    'rgba(59, 130, 246, 0.8)', // blue
    'rgba(168, 85, 247, 0.8)', // purple
  ];
  const borderColor = borderColors[index % borderColors.length];

  return (
    <div
      className={`flip-card gdl-ticket-card ${flipped ? 'flipped active' : ''}`}
      style={{
        animation: `slideFadeIn 0.4s ease-out forwards`,
        animationDelay: `${(index % 20) * 30}ms`, // Stagger animation
        flexShrink: 0,
      }}
    >
      <div className="flip-card-inner" style={{ cursor: 'pointer', position: 'relative' }}>

        {/* Action Buttons - Positioned on Left and Right - ONLY VISIBLE WHEN NOT FLIPPED */}
        {!flipped && (
          <>
            <button
              className="btn btn-sm p-0"
              style={{
                position: 'absolute',
                left: '4px',
                top: '50%',
                transform: 'translateY(-50%)',
                zIndex: 10,
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                background: 'rgba(239, 68, 68, 0.95)',
                border: 'none',
                color: '#fff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s ease',
                boxShadow: '0 4px 12px rgba(239, 68, 68, 0.4)',
              }}
              onClick={(e) => { e.stopPropagation(); onReject(); }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-50%) scale(1.15)';
                e.currentTarget.style.boxShadow = '0 6px 20px rgba(239, 68, 68, 0.6)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(-50%) scale(1)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(239, 68, 68, 0.4)';
              }}
              title="Reject & Replace"
            >
              <X size={20} />
            </button>

            <button
              className="btn btn-sm p-0"
              style={{
                position: 'absolute',
                right: '4px',
                top: '50%',
                transform: 'translateY(-50%)',
                zIndex: 10,
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                background: 'rgba(34, 197, 94, 0.95)',
                border: 'none',
                color: '#fff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s ease',
                boxShadow: '0 4px 12px rgba(34, 197, 94, 0.4)',
              }}
              onClick={(e) => { e.stopPropagation(); onAccept(); }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-50%) scale(1.15)';
                e.currentTarget.style.boxShadow = '0 6px 20px rgba(34, 197, 94, 0.6)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(-50%) scale(1)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(34, 197, 94, 0.4)';
              }}
              title="Accept & Add to Cart"
            >
              <Check size={20} />
            </button>
          </>
        )}

        {/* Front - Compact Card matching image 3 */}
        <div className="flip-card-front" onClick={onFlip} style={{
          background: 'rgba(20, 20, 30, 0.9)',
          border: `3px solid ${borderColor}`,
          borderRadius: '16px',
          padding: '1.25rem',
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: `0 0 20px ${borderColor}, 0 0 40px ${borderColor.replace('0.8', '0.4')}`,
        }}>
          {/* Title */}
          <div className="text-uppercase mb-2" style={{
            fontSize: '0.65rem',
            color: '#fff',
            letterSpacing: '1px',
            fontWeight: '700',
          }}>
            TICKET WINS
          </div>

          {/* Payout - Large Number */}
          <div className="fw-bold mb-2" style={{
            fontSize: '2.5rem',
            color: '#fff',
            lineHeight: '1',
            textShadow: '0 0 10px rgba(255, 255, 255, 0.5)',
          }}>
            {ticket.total_returns.toFixed(0)}
          </div>

          {/* CTA Text */}
          <div className="text-uppercase" style={{
            fontSize: '0.55rem',
            color: 'rgba(255, 255, 255, 0.7)',
            letterSpacing: '0.5px',
            fontWeight: '600',
          }}>
            CLICK TO REVEAL DETAILS!
          </div>
        </div>

        {/* Back - Premium Glassmorphism */}
        <div className="flip-card-back" onClick={onFlip} style={{
          // Solid opaque background to hide the front card completely
          background: 'linear-gradient(135deg, rgba(20, 20, 35, 0.98) 0%, rgba(30, 15, 45, 0.98) 100%)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '2px solid rgba(236, 72, 153, 0.6)',
          borderRadius: '16px',
          padding: '1.25rem',
          width: '200px',
          minHeight: '140px',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 8px 32px rgba(236, 72, 153, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2)',
          overflow: 'hidden',
        }}>
          {/* Header */}
          <div className="text-center mb-2" style={{
            padding: '0.5rem',
            background: 'rgba(236, 72, 153, 0.15)',
            borderRadius: '8px',
            border: '1px solid rgba(236, 72, 153, 0.3)',
          }}>
            <div className="d-flex justify-content-between align-items-center mb-1">
              <span style={{ fontSize: '0.65rem', color: 'rgba(255, 255, 255, 0.6)' }}>WAGER</span>
              <span className="fw-bold" style={{ color: '#fff', fontSize: '0.75rem' }}>${ticket.total_stake.toFixed(2)}</span>
            </div>
            <div className="d-flex justify-content-between align-items-center">
              <span style={{ fontSize: '0.65rem', color: 'rgba(255, 255, 255, 0.6)' }}>RETURNS</span>
              <span className="fw-bold" style={{
                background: 'linear-gradient(135deg, #FFD700, #FFA500)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontSize: '0.75rem',
              }}>
                ${ticket.total_returns.toFixed(2)}
              </span>
            </div>
          </div>

          {/* Stats */}
          <div className="text-center mb-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
                e.preventDefault();
                onShowDetails();
              }}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.25rem',
                padding: '0.25rem 0.75rem',
                background: 'rgba(255, 255, 255, 0.05)',
                borderRadius: '8px',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                color: 'rgba(255, 255, 255, 0.8)',
                fontSize: '0.75rem',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                position: 'relative',
                zIndex: 100,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(138, 43, 226, 0.2)';
                e.currentTarget.style.borderColor = 'rgba(138, 43, 226, 0.4)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
              }}
            >
              {ticket.depth} Events
            </button>
          </div>

          {/* Preview */}
          <div className="flex-grow-1 mb-2" style={{
            background: 'rgba(0, 0, 0, 0.2)',
            borderRadius: '8px',
            padding: '0.5rem',
            position: 'relative',
          }}>
            <button
              onClick={(e) => {
                e.stopPropagation();
                e.preventDefault();
                onShowDetails();
              }}
              className="btn btn-sm w-100"
              style={{
                background: 'rgba(138, 43, 226, 0.2)',
                border: '1px solid rgba(138, 43, 226, 0.4)',
                color: '#fff',
                fontSize: '0.7rem',
                padding: '0.25rem',
                position: 'relative',
                zIndex: 100,
                cursor: 'pointer',
              }}
            >
              {ticket.depth} Events
            </button>
          </div>

          {/* Actions */}
          <div className="d-flex gap-2">
            <button
              className="btn btn-sm flex-fill"
              style={{
                background: 'rgba(239, 68, 68, 0.2)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(239, 68, 68, 0.5)',
                color: '#ef4444',
                fontSize: '0.7rem',
                fontWeight: '600',
                padding: '0.35rem',
              }}
              onClick={(e) => { e.stopPropagation(); onReject(); }}
            >
              <X size={14} className="me-1" /> Reject
            </button>
            <button
              className="btn btn-sm flex-fill"
              style={{
                background: 'rgba(34, 197, 94, 0.2)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(34, 197, 94, 0.5)',
                color: '#22c55e',
                fontSize: '0.7rem',
                fontWeight: '600',
                padding: '0.35rem',
              }}
              onClick={(e) => { e.stopPropagation(); onAccept(); }}
            >
              <Check size={14} className="me-1" /> Accept
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}

// Ticket Details Modal
function TicketDetailsModal({ ticket, onClose, onAccept, onReject }: { ticket: DjangoTicketResponse; onClose: () => void; onAccept: () => void; onReject: () => void }) {
  return (
    <div
      className="modal show d-block"
      style={{
        backgroundColor: 'rgba(0, 0, 0, 0.85)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        zIndex: 9999,
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
      onClick={onClose}
    >
      <div
        className="modal-dialog modal-dialog-scrollable"
        style={{
          maxWidth: '800px',
          width: '90%',
          margin: 0,
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div
          className="modal-content text-white"
          style={{
            background: 'linear-gradient(135deg, rgba(30, 20, 50, 0.98) 0%, rgba(15, 10, 30, 0.98) 100%)',
            backdropFilter: 'blur(40px)',
            WebkitBackdropFilter: 'blur(40px)',
            border: '2px solid rgba(168, 85, 247, 0.6)',
            borderRadius: '24px',
            boxShadow: '0 20px 60px rgba(168, 85, 247, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
            overflow: 'hidden',
            maxHeight: '90vh',
          }}
        >
          {/* Header with Glassmorphic Border */}
          <div
            className="modal-header border-0 pb-0"
            style={{
              background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.15) 0%, rgba(236, 72, 153, 0.15) 100%)',
              borderBottom: '1px solid rgba(168, 85, 247, 0.3)',
              padding: '1.5rem',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              position: 'relative',
            }}
          >
            <h5 className="modal-title fw-bold" style={{
              fontSize: '1.25rem',
              letterSpacing: '0.5px',
              margin: 0,
            }}>
              Ticket Details
            </h5>
            <button
              type="button"
              className="btn-close btn-close-white"
              onClick={onClose}
              style={{
                opacity: 0.8,
                transition: 'opacity 0.2s',
                position: 'absolute',
                right: '1.5rem',
              }}
              onMouseEnter={(e) => e.currentTarget.style.opacity = '1'}
              onMouseLeave={(e) => e.currentTarget.style.opacity = '0.8'}
            ></button>
          </div>

          {/* Body */}
          <div className="modal-body" style={{ padding: '2rem' }}>
            {/* Header Section */}
            <div className="text-center mb-4 pb-3" style={{
              borderBottom: '1px solid rgba(168, 85, 247, 0.2)',
            }}>
              <h4 className="mb-2" style={{
                fontSize: '1.1rem',
                color: 'rgba(255, 255, 255, 0.9)',
              }}>
                Risking <span style={{
                  color: '#fff',
                  fontWeight: '700',
                }}>${ticket.total_stake.toFixed(2)}</span> returns{' '}
                <span style={{
                  background: 'linear-gradient(135deg, #FFD700, #FFA500)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  fontWeight: '700',
                  fontSize: '1.3rem',
                }}>${ticket.total_returns.toFixed(2)}</span>
              </h4>
              <p className="mb-0" style={{
                fontSize: '0.9rem',
                color: 'rgba(255, 255, 255, 0.6)',
              }}>
                (Across {ticket.depth} events)
              </p>
            </div>

            {/* Events List */}
            <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
              {ticket.legs && ticket.legs.map((leg: any, idx: number) => {
                // Parse match_name to extract teams (format: "Team1 vs Team2")
                const teams = leg.match_name?.split(' vs ') || ['', ''];
                const homeTeam = teams[0] || '';
                const awayTeam = teams[1] || '';

                return (
                  <div
                    key={idx}
                    className="mb-3 p-3 text-center"
                    style={{
                      background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(168, 85, 247, 0.2)',
                      borderRadius: '12px',
                      transition: 'all 0.2s ease',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = 'linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%)';
                      e.currentTarget.style.borderColor = 'rgba(168, 85, 247, 0.4)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%)';
                      e.currentTarget.style.borderColor = 'rgba(168, 85, 247, 0.2)';
                    }}
                  >
                    {/* Match Info */}
                    <h6 className="mb-2" style={{
                      fontSize: '1rem',
                      color: '#fff',
                      fontWeight: '600',
                      textAlign: 'center',
                    }}>
                      {leg.outcome === 'home' ? (
                        <>
                          <span style={{
                            textDecoration: 'underline',
                            textDecorationColor: 'rgba(34, 197, 94, 0.6)',
                            textDecorationThickness: '2px',
                            textUnderlineOffset: '3px',
                            fontWeight: '700',
                          }}>
                            {homeTeam}
                          </span>
                          {' vs '}
                          {awayTeam}
                        </>
                      ) : leg.outcome === 'away' ? (
                        <>
                          <span style={{
                            textDecoration: 'underline',
                            textDecorationColor: 'rgba(34, 197, 94, 0.6)',
                            textDecorationThickness: '2px',
                            textUnderlineOffset: '3px',
                            fontWeight: '700',
                          }}>
                            {awayTeam}
                          </span>
                          {' vs '}
                          {homeTeam}
                        </>
                      ) : (
                        <>{leg.match_name}</>
                      )}
                    </h6>

                    {/* League - Optional if it exists */}
                    {leg.sport_name && (
                      <p className="mb-2" style={{
                        fontSize: '0.85rem',
                        color: 'rgba(255, 255, 255, 0.7)',
                        margin: 0,
                      }}>
                        {leg.sport_name}
                      </p>
                    )}

                    {/* Time */}
                    <p className="mb-0" style={{
                      fontSize: '0.8rem',
                      color: 'rgba(255, 255, 255, 0.5)',
                    }}>
                      {leg.match_time}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Footer with Action Buttons */}
          <div
            className="modal-footer border-0 pt-0"
            style={{
              background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.05) 0%, rgba(236, 72, 153, 0.05) 100%)',
              borderTop: '1px solid rgba(168, 85, 247, 0.2)',
              padding: '1.5rem',
              display: 'flex',
              justifyContent: 'center',
              gap: '1rem',
            }}
          >
            {/* Reject Button */}
            <button
              type="button"
              className="btn px-4 py-2"
              style={{
                background: 'linear-gradient(135deg, rgba(220, 38, 38, 0.8) 0%, rgba(185, 28, 28, 0.8) 100%)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(220, 38, 38, 0.6)',
                borderRadius: '12px',
                color: '#fff',
                fontWeight: '600',
                fontSize: '0.95rem',
                transition: 'all 0.2s ease',
                boxShadow: '0 4px 12px rgba(220, 38, 38, 0.3)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 6px 20px rgba(220, 38, 38, 0.5)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(220, 38, 38, 0.3)';
              }}
              onClick={onReject}
            >
              Reject!
            </button>

            {/* Close Button */}
            <button
              type="button"
              className="btn px-4 py-2"
              onClick={onClose}
              style={{
                background: 'linear-gradient(135deg, rgba(100, 100, 120, 0.6) 0%, rgba(70, 70, 90, 0.6) 100%)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(150, 150, 170, 0.4)',
                borderRadius: '12px',
                color: '#fff',
                fontWeight: '600',
                fontSize: '0.95rem',
                transition: 'all 0.2s ease',
                boxShadow: '0 4px 12px rgba(100, 100, 120, 0.2)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 6px 20px rgba(100, 100, 120, 0.4)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(100, 100, 120, 0.2)';
              }}
            >
              Close
            </button>

            {/* Accept Button */}
            <button
              type="button"
              className="btn px-4 py-2"
              style={{
                background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.8) 0%, rgba(22, 163, 74, 0.8) 100%)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(34, 197, 94, 0.6)',
                borderRadius: '12px',
                color: '#fff',
                fontWeight: '600',
                fontSize: '0.95rem',
                transition: 'all 0.2s ease',
                boxShadow: '0 4px 12px rgba(34, 197, 94, 0.3)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 6px 20px rgba(34, 197, 94, 0.5)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(34, 197, 94, 0.3)';
              }}
              onClick={onAccept}
            >
              Accept!
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
@keyframes slideFadeIn {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}

.flip-card {
  width: 200px;
  height: 140px;
  perspective: 1000px;
  display: inline-block;
  padding: 8px;
}

.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.flip-card.flipped .flip-card-inner {
  transform: rotateY(180deg);
}

.flip-card-front,
.flip-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}

.flip-card-back {
  transform: rotateY(180deg);
}
`;
if (!document.head.querySelector('style[data-ticket-board]')) {
  style.setAttribute('data-ticket-board', 'true');
  document.head.appendChild(style);
}