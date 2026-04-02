/**
 * Tickets Page Wrapper
 * 
 * Wraps ticket tables with the full UI (sidebar, top bar, etc.)
 * Similar to how messages are shown in the sportslotto app.
 */

import React from 'react';

interface TicketsPageWrapperProps {
  children: React.ReactNode;
  onBalanceClick?: () => void;
  onCashierClick?: () => void;
  onOpenTicketsClick?: () => void;
  onGradedTicketsClick?: () => void;
  onProfileClick?: () => void;
  onGetTicketsClick?: () => void;
}

export function TicketsPageWrapper({
  children,
  onBalanceClick,
  onCashierClick,
  onOpenTicketsClick,
  onGradedTicketsClick,
  onProfileClick,
  onGetTicketsClick,
}: TicketsPageWrapperProps) {
  return (
    <div className="flex min-h-screen text-white relative overflow-hidden" style={{
      background: 'linear-gradient(180deg, #1a0a2e 0%, #2d1b4e 25%, #4a2c5e 50%, #5c3a3e 75%, #6e3a2e 100%)'
    }}>
      {/* Particle/Star Background */}
      <div className="absolute inset-0 opacity-40 pointer-events-none" style={{
        backgroundImage: `radial-gradient(2px 2px at 20% 30%, white, transparent),
                         radial-gradient(2px 2px at 60% 70%, white, transparent),
                         radial-gradient(1px 1px at 50% 50%, white, transparent),
                         radial-gradient(1px 1px at 80% 10%, white, transparent),
                         radial-gradient(2px 2px at 90% 60%, orange, transparent),
                         radial-gradient(1px 1px at 33% 80%, orange, transparent),
                         radial-gradient(2px 2px at 15% 90%, white, transparent)`,
        backgroundSize: '200% 200%',
        backgroundPosition: '0% 0%, 40% 60%, 70% 20%, 10% 80%, 90% 30%, 30% 90%, 60% 10%'
      }}></div>

      {/* Import and use Sidebar from sportslotto */}
      {/* This will be rendered by parent */}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col relative z-10 w-full lg:w-auto">
        {/* Top Bar */}
        <div className="backdrop-blur-md bg-black/40 border-b border-white/10 py-3 px-6 lg:px-6 px-16">
          <div className="flex justify-end items-center gap-4">
            {onCashierClick && (
              <button
                onClick={onCashierClick}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 rounded-lg font-semibold transition-all shadow-lg shadow-green-500/30 text-sm lg:text-base"
              >
                💰 <span className="hidden sm:inline">Cashier</span>
              </button>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-4 lg:p-6 overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  );
}
