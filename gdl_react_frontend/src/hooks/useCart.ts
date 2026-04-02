import { useState, useCallback } from 'react';
import type { CartEntry, CartResponse } from '../types/ticket';

export function useCart() {
  const [cartEntries, setCartEntries] = useState<CartEntry[]>([]);
  const [cartCount, setCartCount] = useState(0);
  const [totalRisk, setTotalRisk] = useState(0);
  const [totalWins, setTotalWins] = useState(0);
  const [loading, setLoading] = useState(false);

  // Fetch cart from server
  const fetchCart = useCallback(async () => {
    setLoading(true);
    
    try {
      const response = await fetch('/api/v1/game/tickets/cart/', {
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch cart: ${response.status}`);
      }

      const data: CartResponse = await response.json();
      
      setCartEntries(data.data.tickets);
      setCartCount(data.data.count);
      
      // Calculate totals
      const risk = data.data.tickets.reduce((sum, t) => sum + t.risk, 0);
      const wins = data.data.tickets.reduce((sum, t) => sum + t.returns, 0);
      
      setTotalRisk(risk);
      setTotalWins(wins);
    } catch (error) {
      console.error('[Cart] Failed to fetch:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Accept ticket (add to cart)
  const acceptTicket = useCallback(async (formData: FormData) => {
    try {
      const response = await fetch('/api/v1/game/tickets/accept/', {
        method: 'POST',
        credentials: 'include',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Failed to accept ticket: ${response.status}`);
      }

      const data = await response.json();
      
      // Refresh cart
      await fetchCart();
      
      return data;
    } catch (error) {
      console.error('[Cart] Failed to accept ticket:', error);
      throw error;
    }
  }, [fetchCart]);

  // Reject ticket (remove from cart)
  const rejectTicket = useCallback(async (uuid: string) => {
    try {
      const response = await fetch(`/api/v1/game/tickets/reject/${uuid}?ng=1`, {
        method: 'POST',
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error(`Failed to reject ticket: ${response.status}`);
      }

      // Refresh cart
      await fetchCart();
    } catch (error) {
      console.error('[Cart] Failed to reject ticket:', error);
      throw error;
    }
  }, [fetchCart]);

  // Empty cart
  const emptyCart = useCallback(async () => {
    if (!confirm('Empty cart?')) return;

    try {
      const response = await fetch('/api/v1/game/tickets/cart/empty', {
        method: 'DELETE',
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error(`Failed to empty cart: ${response.status}`);
      }

      setCartEntries([]);
      setCartCount(0);
      setTotalRisk(0);
      setTotalWins(0);
    } catch (error) {
      console.error('[Cart] Failed to empty:', error);
      throw error;
    }
  }, []);

  return {
    cartEntries,
    cartCount,
    totalRisk,
    totalWins,
    loading,
    fetchCart,
    acceptTicket,
    rejectTicket,
    emptyCart,
  };
}
