import React, { useState } from 'react';
import { CustomTicketsDemo } from './tickets/CustomTicketsDemo';
import { QuickPicksDemo } from './tickets/QuickPicksDemo';
import { useBootstrap } from '../contexts/BootstrapContext';

export function TicketGeneratorDemo() {
  const [activeTab, setActiveTab] = useState<'custom' | 'quickpicks'>('custom');
  const { bootstrap } = useBootstrap();

  // Check if we're in mock mode
  const isMockMode = bootstrap?.vhost.uuid === '00000000-0000-0000-0000-000000000001';

  return (
    <div className="min-h-screen w-full bg-black text-white">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 gradient-text">
            Ticket Generator Demo
          </h1>
          <p className="text-white/70">
            WebSocket-powered real-time ticket generation
          </p>
          
          {/* Mock Mode Banner */}
          {isMockMode && (
            <div className="mt-4 glass-card border-2 border-yellow-500/50 bg-yellow-500/10 p-4 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="text-2xl">⚠️</div>
                <div>
                  <div className="font-bold text-yellow-300">Demo Mode</div>
                  <div className="text-sm text-white/70">
                    Django backend not connected. WebSocket functionality requires Django + GPU daemon.
                    <br />
                    UI components are fully functional and ready for backend integration.
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setActiveTab('custom')}
            className={`px-6 py-3 rounded-lg font-bold transition-all ${
              activeTab === 'custom'
                ? 'bg-gradient-to-r from-purple-500 to-pink-500'
                : 'bg-white/5 hover:bg-white/10'
            }`}
          >
            Custom Tickets
          </button>
          <button
            onClick={() => setActiveTab('quickpicks')}
            className={`px-6 py-3 rounded-lg font-bold transition-all ${
              activeTab === 'quickpicks'
                ? 'bg-gradient-to-r from-purple-500 to-pink-500'
                : 'bg-white/5 hover:bg-white/10'
            }`}
          >
            Quick Picks
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'custom' && <CustomTicketsDemo />}
        {activeTab === 'quickpicks' && <QuickPicksDemo />}
      </div>
    </div>
  );
}