import React, { useState, useEffect } from 'react';
import { useTicketGenerator } from '../../hooks/useTicketGenerator';
import { useCart } from '../../hooks/useCart';

export function QuickPicksDemo() {
  const [stake, setStake] = useState(1);
  const [count, setCount] = useState(5);
  const [depth, setDepth] = useState(3);
  const minPayout = stake * 20; // 20:1 odds

  const [completionData, setCompletionData] = useState<any>(null);

  const {
    isGenerating,
    generate,
  } = useTicketGenerator({
    streamName: 'quickpicks',
    endpoint: '/game/stream_quickpicks',
    onTicket: (ticket) => {
      console.log('QuickPick ticket auto-saved:', ticket.uuid);
    },
    onComplete: (data) => {
      console.log('QuickPicks complete:', data);
      setCompletionData(data);
      // Fetch cart to show updated totals
      fetchCart();
    },
    onError: (error) => {
      alert(`Error: ${error}`);
    },
    onEmpty: (data) => {
      if (data.incomplete) {
        alert('Not enough events available to generate QuickPicks');
      }
    },
  });

  const { cartCount, totalRisk, totalWins, fetchCart, emptyCart } = useCart();

  // Fetch cart on mount
  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  const handleGenerate = () => {
    setCompletionData(null);

    generate({
      stake,
      count,
      depth,
      min_payout: minPayout,
    });
  };

  const handlePurchase = async () => {
    if (cartCount === 0) {
      alert('Cart is empty!');
      return;
    }

    // In real app, this would submit purchase
    const confirmed = confirm(
      `Purchase ${cartCount} tickets for $${totalRisk}?\n\nPotential win: $${totalWins}`
    );

    if (confirmed) {
      // TODO: Submit to /api/v1/game/tickets/purchase or similar
      alert('Purchase flow would execute here');
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="glass-card p-6">
        <h2 className="text-2xl font-bold mb-4 gradient-text">Quick Picks</h2>
        <p className="text-sm text-white/70 mb-6">
          Instant tickets automatically added to your cart. 20:1 minimum payout.
        </p>

        {/* Controls */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm mb-2">Stake ($)</label>
            <input
              type="number"
              value={stake}
              onChange={(e) => setStake(Number(e.target.value))}
              className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg"
              min="1"
            />
          </div>

          <div>
            <label className="block text-sm mb-2">Tickets</label>
            <input
              type="number"
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
              className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg"
              min="1"
              max="20"
            />
          </div>

          <div>
            <label className="block text-sm mb-2">Legs</label>
            <input
              type="number"
              value={depth}
              onChange={(e) => setDepth(Number(e.target.value))}
              className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg"
              min="2"
              max="10"
            />
          </div>
        </div>

        {/* Payout Preview */}
        <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30 rounded-lg p-4 mb-6">
          <div className="text-sm text-white/70 mb-1">Minimum Payout (20:1)</div>
          <div className="text-3xl font-bold gradient-text">
            ${minPayout.toFixed(2)}
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={isGenerating}
          className="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg font-bold disabled:opacity-50"
        >
          {isGenerating ? 'Generating...' : 'Generate Quick Picks'}
        </button>
      </div>

      {/* Completion Stats */}
      {completionData && (
        <div className="glass-card p-6">
          <h3 className="text-xl font-bold mb-4">Generation Complete!</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatBox
              label="Tickets Created"
              value={completionData.ticket_count || 0}
            />
            <StatBox
              label="Total Risk"
              value={`$${completionData.total_risk || 0}`}
            />
            <StatBox
              label="Potential Win"
              value={`$${completionData.total_wins || 0}`}
            />
            <StatBox
              label="Trials"
              value={completionData.trials || 0}
            />
          </div>
        </div>
      )}

      {/* Cart Summary */}
      <div className="glass-card p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold">Cart</h3>
          {cartCount > 0 && (
            <button
              onClick={emptyCart}
              className="text-sm text-red-400 hover:text-red-300"
            >
              Empty Cart
            </button>
          )}
        </div>

        {cartCount > 0 ? (
          <>
            <div className="grid grid-cols-3 gap-4 mb-6">
              <StatBox label="Tickets" value={cartCount} />
              <StatBox label="Total Risk" value={`$${totalRisk}`} />
              <StatBox label="Potential Win" value={`$${totalWins}`} />
            </div>

            <button
              onClick={handlePurchase}
              className="w-full py-3 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg font-bold"
            >
              Purchase {cartCount} Ticket{cartCount !== 1 ? 's' : ''}
            </button>
          </>
        ) : (
          <div className="text-center py-8 text-white/50">
            Your cart is empty
          </div>
        )}
      </div>

      {isGenerating && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="glass-card p-8 text-center">
            <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-purple-500 border-t-transparent mb-4"></div>
            <p className="text-xl font-bold">Generating QuickPicks...</p>
            <p className="text-sm text-white/70 mt-2">
              Tickets will be automatically added to your cart
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function StatBox({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-white/5 rounded-lg p-3">
      <div className="text-xs text-white/50 mb-1">{label}</div>
      <div className="text-lg font-bold">{value}</div>
    </div>
  );
}
