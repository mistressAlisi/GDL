import React from 'react';
import { Ticket } from '../App';
import { ThemedTicketCard } from './ThemedTicketCard';

interface TicketsGridProps {
  tickets: Ticket[];
  onFlip: (ticketId: string) => void;
  onSelect: (ticketId: string, action: 'accept' | 'reject') => void;
  onShowDetails: (ticket: Ticket) => void;
}

export function TicketsGrid({ tickets, onFlip, onSelect, onShowDetails }: TicketsGridProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">Your Tickets</h2>
        <div className="text-gray-300">
          Total Tickets: <span className="text-orange-400 font-bold">{tickets.length}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
        {tickets.map((ticket) => (
          <ThemedTicketCard
            key={ticket.id}
            ticket={ticket}
            onShowDetails={() => onShowDetails(ticket)}
            onAccept={(id) => onSelect(id, 'accept')}
            onReject={(id) => onSelect(id, 'reject')}
          />
        ))}
      </div>
    </div>
  );
}