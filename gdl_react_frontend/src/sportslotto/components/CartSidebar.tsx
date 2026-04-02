import React, { useEffect, useState } from 'react';
import { X, ShoppingCart, Trash2 } from 'lucide-react';
import { Ticket } from '../App';
import { useTheme } from '../contexts/ThemeContext';
import { useCart } from '../contexts/CartContext';
import { getCart, rejectTicket, emptyCart, submitTicketPurchase, CartTicket } from '../services/api';
import { PurchaseModal } from './PurchaseModal';
import { useAuth } from '../contexts/AuthContext';

interface CartSidebarProps {
  tickets: Ticket[];
  onRemoveTicket: (id: string) => void;
  onShowDetails: (ticket: Ticket) => void;
  onCheckout: () => void;
  isOpen: boolean;
  onToggle: () => void;
}

export function CartSidebar({ tickets, onRemoveTicket, onShowDetails, onCheckout, isOpen, onToggle }: CartSidebarProps) {
  const { theme } = useTheme();
  const { cartCount, setCartCount } = useCart();
  const { isAuthenticated, user } = useAuth();
  const [cartTickets, setCartTickets] = useState<CartTicket[]>([]);
  const [loading, setLoading] = useState(false);
  const [subtotal, setSubtotal] = useState(0);
  const [isPurchaseModalOpen, setIsPurchaseModalOpen] = useState(false);

  // Fetch cart data when cart is opened
  useEffect(() => {
    if (isOpen) {
      fetchCartData();
    }
  }, [isOpen]);

  // Fetch initial cart count on mount
  useEffect(() => {
    fetchCartCount();
  }, []);

  const fetchCartCount = async () => {
    try {
      console.log('🔢 Fetching initial cart count...');
      const response = await getCart();

      if (response.res === 'ok' && response.data) {
        const count = response.data.count || 0;
        console.log('✅ Initial cart count:', count);
        setCartCount(count);
      }
    } catch (error) {
      console.error('❌ Error fetching cart count:', error);
    }
  };

  const fetchCartData = async () => {
    setLoading(true);
    try {
      console.log('🛒 Fetching cart data...');
      const response = await getCart();
      console.log("Cart Response", response);

      if (response.res === 'ok' && response.data) {
        const cartData = response.data;
        console.log('✅ Cart data received:', cartData);
        setCartTickets(cartData.tickets || []);

        // Calculate total_risk by summing all ticket risk values
        const calculatedSubtotal = (cartData.tickets || []).reduce((sum, ticket) => sum + ticket.risk, 0);
        setSubtotal(calculatedSubtotal);

        setCartCount(cartData.count || 0);
      } else {
        console.error('❌ Failed to fetch cart:', response.err);
        setCartTickets([]);
        setSubtotal(0);
      }
    } catch (error) {
      console.error('❌ Error fetching cart:', error);
      setCartTickets([]);
      setSubtotal(0);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveTicket = async (uuid: string) => {
    try {
      console.log('🗑️ Removing ticket:', uuid);
      const response = await rejectTicket(uuid);

      if (response.res === 'ok') {
        console.log('✅ Ticket removed successfully');
        // Refresh cart data
        fetchCartData();
      } else {
        console.error('❌ Failed to remove ticket:', response.err);
        alert(`Failed to remove ticket: ${response.err || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('❌ Error removing ticket:', error);
      alert('Failed to remove ticket. Please try again.');
    }
  };

  const handleEmptyCart = async () => {
    if (!confirm('Are you sure you want to empty your cart?')) {
      return;
    }

    try {
      // Remove all tickets
      await emptyCart();
      // Refresh cart
      fetchCartData();
    } catch (error) {
      console.error('❌ Error emptying cart:', error);
      alert('Failed to empty cart. Please try again.');
    }
  };

  const handlePurchaseConfirm = async (useBonus: boolean) => {
    try {
      console.log('💳 Submitting purchase...', { useBonus });

      // Build FormData for purchase
      const formData = new FormData();
      formData.append('use_bonus', useBonus ? '1' : '0');

      const response = await submitTicketPurchase(formData);

      if (response.res === 'ok') {
        console.log('✅ Purchase successful!', response);

        // Don't refresh cart or close modal here - let the modal handle it
        // The modal will close itself after showing the success animation

        // Return the full response for the modal to display
        return response;
      } else {
        console.error('❌ Purchase failed:', response.err);
        throw new Error(response.err || 'Purchase failed');
      }
    } catch (error) {
      console.error('❌ Error during purchase:', error);
      throw error;
    }
  };

  // Use cart count from context
  const displayCount = cartCount;

  return (
    <>
      {/* Toggle Button (shown when cart is closed) */}
      {!isOpen && (
        <div style={{ position: 'fixed', right: 0, top: '50%', transform: 'translateY(-50%)', zIndex: 40 }}>
          <button
            onClick={onToggle}
            className="px-3 py-6 backdrop-blur-md rounded-l-xl shadow-lg transition-all hover:px-4"
            style={{
              background: 'rgba(20, 20, 40, 0.9)',
              border: `2px solid ${theme.cardBorder}`,
              borderRight: 'none',
              boxShadow: `0 0 20px ${theme.cardGlow}`,
            }}
          >
            <ShoppingCart className="w-5 h-5 lg:w-6 lg:h-6 text-white" />
          </button>
          {displayCount > 0 && (
            <div
              className="rounded-full flex items-center justify-center text-xs font-bold text-white"
              style={{
                position: 'absolute',
                top: '-8px',
                left: '-8px',
                width: '28px',
                height: '28px',
                background: 'linear-gradient(135deg, rgba(236, 72, 153, 0.95) 0%, rgba(220, 38, 38, 0.95) 100%)',
                border: '2px solid rgba(255, 255, 255, 0.3)',
                boxShadow: '0 0 20px rgba(236, 72, 153, 0.8), 0 0 40px rgba(236, 72, 153, 0.4)',
                animation: 'pulse 2s infinite',
                zIndex: 10,
              }}
            >
              {displayCount}
            </div>
          )}
        </div>
      )}

      {/* Cart Sidebar */}
      <div
        className={`fixed right-0 top-0 h-full w-full sm:w-96 lg:w-80 backdrop-blur-md shadow-2xl transition-transform duration-300 z-50 flex flex-col ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
        style={{
          background: 'rgba(10, 10, 20, 0.95)',
          borderLeft: `2px solid ${theme.cardBorder}`,
          boxShadow: `0 0 40px ${theme.cardGlow}`
        }}
      >
        {/* Header */}
        <div
          className="p-4 border-b flex items-center justify-between"
          style={{ borderColor: theme.cardBorder }}
        >
          <div className="flex items-center gap-2">
            <ShoppingCart className="w-5 h-5" style={{ color: theme.accentColor }} />
            <h3 className="font-bold text-lg text-white">
              {displayCount} Ticket{displayCount !== 1 ? 's' : ''} in Cart
            </h3>
          </div>
          <button
            onClick={onToggle}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Subtotal */}
        <div
          className="p-4 border-b"
          style={{ borderColor: theme.cardBorder }}
        >
          <div className="flex justify-between items-center">
            <span className="text-gray-400">Subtotal:</span>
            <span className="text-2xl font-bold" style={{ color: theme.accentColor }}>
              ${subtotal.toFixed(2)}
            </span>
          </div>
        </div>

        {/* Empty Cart Button */}
        {cartTickets.length > 0 && (
          <div className="px-4 py-2">
            <button
              onClick={handleEmptyCart}
              className="w-full py-2 rounded-lg font-semibold text-white transition-colors text-sm flex items-center justify-center gap-2"
              style={{
                background: 'linear-gradient(135deg, rgba(220, 38, 38, 0.8) 0%, rgba(185, 28, 28, 0.8) 100%)',
                border: '1px solid rgba(220, 38, 38, 0.6)',
                boxShadow: '0 4px 12px rgba(220, 38, 38, 0.3)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.style.boxShadow = '0 6px 20px rgba(220, 38, 38, 0.5)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(220, 38, 38, 0.3)';
              }}
            >
              <Trash2 className="w-4 h-4" />
              Empty Cart
            </button>
          </div>
        )}

        {/* Tickets List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {loading ? (
            <div className="text-center py-12">
              <div className="spinner-border text-white mb-3" role="status">
                <span className="sr-only">Loading...</span>
              </div>
              <p className="text-gray-400">Loading cart...</p>
            </div>
          ) : cartTickets.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <ShoppingCart className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Your cart is empty</p>
            </div>
          ) : (
            cartTickets.map((ticket, index) => (
              <div
                key={ticket.uuid}
                className="rounded-lg p-3 backdrop-blur-sm border-2 transition-all hover:scale-105 relative overflow-hidden"
                style={{
                  background: `linear-gradient(135deg, rgba(0, 0, 0, 0.6) 0%, rgba(20, 20, 40, 0.6) 100%)`,
                  borderColor: theme.cardBorder,
                  boxShadow: `
                    0 0 30px ${theme.cardGlow}, 
                    0 0 20px ${theme.accentColor}60,
                    0 4px 16px rgba(0, 0, 0, 0.5),
                    inset 0 0 40px ${theme.accentColor}15
                  `
                }}
              >
                {/* Accent glow */}
                <div
                  className="absolute inset-0 opacity-20 pointer-events-none"
                  style={{
                    background: `radial-gradient(circle at top right, ${theme.accentColor}60, transparent 70%)`
                  }}
                />

                <div className="relative z-10">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span
                          className="font-bold"
                          style={{
                            color: '#fff',
                            textShadow: `
                              0 0 15px ${theme.accentColor}80, 
                              0 0 25px ${theme.accentColor}40,
                              0 2px 6px rgba(0, 0, 0, 0.9)
                            `
                          }}
                        >
                          {index + 1}. Ticket Wins {ticket.returns.toFixed(0)} for {ticket.risk.toFixed(0)}
                        </span>
                      </div>
                      <div
                        className="text-xs"
                        style={{
                          color: theme.accentColor,
                          textShadow: `0 0 10px ${theme.accentColor}60, 0 2px 4px rgba(0, 0, 0, 0.8)`
                        }}
                      >
                        {ticket.events || ticket.depth || 0} events
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 mt-3">
                    <button
                      onClick={() => {
                        // TODO: Show ticket details modal
                        console.log('Show details for ticket:', ticket.uuid);
                      }}
                      className="flex-1 px-3 py-1 rounded text-xs font-semibold text-white transition-colors flex items-center justify-center gap-1"
                      style={{
                        background: `${theme.cardBorder}40`,
                        boxShadow: `0 0 15px ${theme.cardGlow}50, 0 0 25px ${theme.accentColor}30`,
                        textShadow: `0 0 10px ${theme.accentColor}60, 0 2px 4px rgba(0, 0, 0, 0.8)`
                      }}
                    >
                      🔍 Details
                    </button>
                    <button
                      onClick={() => handleRemoveTicket(ticket.uuid)}
                      className="px-3 py-1 rounded text-xs font-semibold text-white bg-red-600 hover:bg-red-700 transition-colors"
                      style={{
                        boxShadow: '0 0 15px rgba(220, 38, 38, 0.6), 0 2px 10px rgba(220, 38, 38, 0.4)',
                        textShadow: '0 0 8px rgba(255, 255, 255, 0.6), 0 2px 4px rgba(0, 0, 0, 0.8)'
                      }}
                    >
                      ✕ Remove
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        {cartTickets.length > 0 && (
          <div
            className="p-4 border-t space-y-3"
            style={{
              borderColor: theme.cardBorder,
              background: 'rgba(0, 0, 0, 0.3)'
            }}
          >
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Total Tickets:</span>
              <span className="text-white font-bold">{cartTickets.length}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Subtotal:</span>
              <span className="text-white font-bold">${subtotal.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Potential Win:</span>
              <span className="text-xl font-bold text-green-400">
                ${cartTickets.reduce((sum, t) => sum + t.returns, 0).toFixed(2)}
              </span>
            </div>

            <button
              onClick={() => {
                if (isAuthenticated) {
                  setIsPurchaseModalOpen(true);
                } else {
                  alert('Please log in to purchase tickets.');
                }
              }}
              className="w-full py-3 rounded-lg font-bold text-white transition-all shadow-lg"
              style={{
                background: theme.buttonGradient,
                boxShadow: `0 4px 20px ${theme.cardGlow}`
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = `0 8px 30px ${theme.cardGlow}`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = `0 4px 20px ${theme.cardGlow}`;
              }}
            >
              Purchase Tickets!
            </button>
          </div>
        )}
      </div>

      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
          onClick={onToggle}
        />
      )}

      {/* Purchase Modal */}
      {isPurchaseModalOpen && (
        <PurchaseModal
          isOpen={isPurchaseModalOpen}
          onClose={() => setIsPurchaseModalOpen(false)}
          ticketCount={cartTickets.length}
          totalRisk={subtotal}
          totalReturns={cartTickets.reduce((sum, t) => sum + t.returns, 0)}
          bonusBalance={user?.bonus || 0}
          onConfirm={handlePurchaseConfirm}
          onSuccess={() => {
            // Close the cart sidebar
            onToggle();
            // Refresh cart data
            fetchCartData();
            // Call parent onCheckout callback
            onCheckout();
            // Close the modal
            setIsPurchaseModalOpen(false);
          }}
        />
      )}
    </>
  );
}