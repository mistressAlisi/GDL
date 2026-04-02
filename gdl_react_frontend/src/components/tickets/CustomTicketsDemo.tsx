import React, { useState } from 'react';
import { useTicketGenerator } from '../../hooks/useTicketGenerator';
import { useCart } from '../../hooks/useCart';
import type { Ticket } from '../../types/ticket';

export function CustomTicketsDemo() {
  const [stake, setStake] = useState(10);
  const [count, setCount] = useState(5);
  const [depth, setDepth] = useState(3);
  const [minPayout, setMinPayout] = useState(200);
  const [selectedSports, setSelectedSports] = useState<string[]>([]);

  const { tickets, isGenerating, generate, replace, clearTickets } = useTicketGenerator({
    streamName: 'custom_tickets',
    endpoint: '/game/stream_tickets',
    onTicket: (ticket) => {
      console.log('Received ticket:', ticket);
    },
    onComplete: (data) => {
      console.log('Generation complete:', data);
    },
    onError: (error) => {
      alert(`Error: ${error}`);
    },
    onEmpty: (data) => {
      if (data.incomplete) {
        alert('Not enough events available to generate tickets');
      }
    },
  });

  const { acceptTicket, rejectTicket, fetchCart } = useCart();

  const handleGenerate = () => {
    clearTickets();

    const settings: any = {
      stake,
      count,
      depth,
      min_payout: minPayout,
    };

    // Add sport filters if any selected
    selectedSports.forEach((sportUuid, index) => {
      settings[`sport_${index}`] = sportUuid;
    });

    generate(settings);
  };

  const handleAccept = async (ticket: Ticket) => {
    const formData = new FormData();
    formData.append('matches', ticket.muuids.join(','));
    formData.append('type', ticket.outcomes.join(','));
    formData.append('stake', ticket.total_stake.toString());
    formData.append('returns', ticket.total_returns.toString());
    formData.append('lines', ticket.lines.join(','));
    formData.append('outcome_meta', JSON.stringify(ticket.outcome_meta));

    try {
      await acceptTicket(formData);
      alert('Ticket accepted!');
    } catch (error) {
      alert('Failed to accept ticket');
    }
  };

  const handleReject = async (ticket: Ticket, requestReplacement: boolean) => {
    if (requestReplacement) {
      // Generate replacement ticket with same settings
      replace(ticket.lines[0], {
        stake,
        depth,
        min_payout: minPayout,
      });
    }
    
    // Just remove from UI if no UUID (not in cart yet)
    clearTickets();
  };

  return (
    <div className="p-6 space-y-6">
      <div className="glass-card p-6">
        <h2 className="text-2xl font-bold mb-4 gradient-text">Custom Tickets</h2>
        
        {/* Controls */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
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
              min="1"
              max="10"
            />
          </div>
          
          <div>
            <label className="block text-sm mb-2">Min Payout ($)</label>
            <input
              type="number"
              value={minPayout}
              onChange={(e) => setMinPayout(Number(e.target.value))}
              className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg"
              min="0"
            />
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={isGenerating}
          className="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg font-bold disabled:opacity-50"
        >
          {isGenerating ? 'Generating...' : 'Generate Tickets'}
        </button>
      </div>

      {/* Tickets Display */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {tickets.map((ticket, index) => (
          <TicketCard
            key={`${ticket.lines.join('-')}-${index}`}
            ticket={ticket}
            onAccept={() => handleAccept(ticket)}
            onReject={(replace) => handleReject(ticket, replace)}
          />
        ))}
      </div>

      {tickets.length === 0 && !isGenerating && (
        <div className="text-center py-12 text-white/50">
          Click "Generate Tickets" to start
        </div>
      )}

      {isGenerating && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent"></div>
          <p className="mt-4 text-white/70">Generating tickets...</p>
        </div>
      )}
    </div>
  );
}

interface TicketCardProps {
  ticket: Ticket;
  onAccept: () => void;
  onReject: (requestReplacement: boolean) => void;
}

function TicketCard({ ticket, onAccept, onReject }: TicketCardProps) {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div className="glass-card p-4 space-y-3">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <div className="text-3xl font-bold gradient-text">
            ${ticket.total_returns}
          </div>
          <div className="text-sm text-white/50">
            Risking ${ticket.total_stake}
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm text-white/70">{ticket.depth} Legs</div>
          <div className="text-xs text-white/50">
            {ticket.total_odds}x odds
          </div>
        </div>
      </div>

      {/* Legs Summary */}
      <div className="space-y-2">
        {ticket.legs.slice(0, showDetails ? undefined : 3).map((leg, i) => (
          <div key={i} className="text-sm">
            <div className="font-medium">
              {leg.home_team?.name} vs {leg.away_team?.name}
            </div>
            <div className="text-white/50 text-xs">
              Pick: {leg.outcome} • {leg.sport_name}
            </div>
          </div>
        ))}
        
        {ticket.legs.length > 3 && !showDetails && (
          <button
            onClick={() => setShowDetails(true)}
            className="text-xs text-purple-400 hover:text-purple-300"
          >
            Show {ticket.legs.length - 3} more...
          </button>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-2 pt-2 border-t border-white/10">
        <button
          onClick={() => onReject(true)}
          className="flex-1 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-sm"
        >
          Reject
        </button>
        <button
          onClick={onAccept}
          className="flex-1 py-2 bg-green-500/20 hover:bg-green-500/30 rounded-lg text-sm"
        >
          Accept
        </button>
      </div>
    </div>
  );
}
