/**
 * Example: How to Use Processing and NoEvents Modals
 * 
 * This demonstrates the proper usage of both modals during ticket generation
 * with the Django backend API integration.
 */

import React, { useState, useEffect } from 'react';
import { ProcessingModal } from '../../sportslotto/components/ProcessingModal';
import { NoEventsModal } from '../../sportslotto/components/NoEventsModal';
import { useTicketGeneration } from '../../services/api-hooks';

export function ModalUsageExample() {
  const { generateTicket, loading, error, response } = useTicketGeneration();
  const [showNoEvents, setShowNoEvents] = useState(false);

  // Example 1: Quick Picks Submission
  const handleQuickPicksSubmit = () => {
    // Show processing modal (via loading state)
    generateTicket({
      wager: 10,
      entries: 5,
      sports: ['tennis', 'soccer', 'us-sports'],
      timeframe: '24h',
      luckyPick: true,
      gameType: 'quick-play',
    });
  };

  // Example 2: Custom Tickets Submission
  const handleCustomTicketsSubmit = () => {
    // Show processing modal (via loading state)
    generateTicket({
      wager: 25,
      entries: 7,
      sports: ['ncaa-basketball', 'us-sports'],
      timeframe: '48h',
      luckyPick: false,
      gameType: 'custom',
    });
  };

  // Watch for API response
  useEffect(() => {
    if (error) {
      // Check if it's a "not enough events" error
      if (error.includes('not enough') || error.includes('events') || error.includes('available')) {
        setShowNoEvents(true);
      }
    }

    if (response?.success && response.ticket) {
      console.log('✅ Ticket generated successfully:', response.ticket);
      // Add ticket to cart, show success, etc.
    }
  }, [error, response]);

  return (
    <div className="space-y-6 p-6">
      <h2 className="text-2xl font-bold bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
        Modal Usage Examples
      </h2>

      {/* Example Buttons */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          onClick={handleQuickPicksSubmit}
          disabled={loading}
          className="py-4 px-6 rounded-xl font-bold text-white transition-all shadow-lg disabled:opacity-50"
          style={{
            background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.8) 0%, rgba(236, 72, 153, 0.8) 50%, rgba(251, 146, 60, 0.8) 100%)'
          }}
        >
          {loading ? 'Processing...' : 'Test Quick Picks'}
        </button>

        <button
          onClick={handleCustomTicketsSubmit}
          disabled={loading}
          className="py-4 px-6 rounded-xl font-bold text-white transition-all shadow-lg disabled:opacity-50"
          style={{
            background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.8) 0%, rgba(236, 72, 153, 0.8) 50%, rgba(251, 146, 60, 0.8) 100%)'
          }}
        >
          {loading ? 'Processing...' : 'Test Custom Tickets'}
        </button>

        <button
          onClick={() => setShowNoEvents(true)}
          className="py-4 px-6 rounded-xl font-bold text-white transition-all shadow-lg"
          style={{
            background: 'rgba(251, 191, 36, 0.3)',
            border: '2px solid rgba(251, 191, 36, 0.5)'
          }}
        >
          Test "No Events" Modal
        </button>
      </div>

      {/* Response Display */}
      {response && (
        <div className="rounded-lg p-4 bg-green-500/20 border border-green-500/50">
          <p className="text-green-300">✅ Success: {JSON.stringify(response, null, 2)}</p>
        </div>
      )}

      {error && !showNoEvents && (
        <div className="rounded-lg p-4 bg-red-500/20 border border-red-500/50">
          <p className="text-red-300">❌ Error: {error}</p>
        </div>
      )}

      {/* Processing Modal - Shows automatically when loading=true */}
      <ProcessingModal
        isOpen={loading}
        message="Processing..."
        subMessage="Ticket Generation in progress"
      />

      {/* No Events Modal - Shows when not enough events available */}
      <NoEventsModal
        isOpen={showNoEvents}
        onClose={() => setShowNoEvents(false)}
        title="Oops! Not Enough Events"
        message="Not enough events available for this combo right now!"
        suggestion="Try adding more events or reducing the payout!"
      />

      {/* Usage Documentation */}
      <div className="rounded-xl p-6 backdrop-blur-md" style={{
        background: 'rgba(20, 20, 40, 0.7)',
        border: '2px solid rgba(251, 146, 60, 0.4)',
      }}>
        <h3 className="text-xl font-bold text-orange-400 mb-4">Integration Guide</h3>
        
        <div className="space-y-4 text-gray-300">
          <div>
            <h4 className="font-bold text-white mb-2">1. Processing Modal Usage:</h4>
            <pre className="bg-black/50 p-3 rounded text-xs overflow-x-auto">
{`const { generateTicket, loading } = useTicketGeneration();

// Show automatically based on loading state
<ProcessingModal isOpen={loading} />`}
            </pre>
          </div>

          <div>
            <h4 className="font-bold text-white mb-2">2. No Events Modal Usage:</h4>
            <pre className="bg-black/50 p-3 rounded text-xs overflow-x-auto">
{`const [showNoEvents, setShowNoEvents] = useState(false);

// Show when API returns "not enough events" error
useEffect(() => {
  if (error?.includes('not enough events')) {
    setShowNoEvents(true);
  }
}, [error]);

<NoEventsModal 
  isOpen={showNoEvents} 
  onClose={() => setShowNoEvents(false)} 
/>`}
            </pre>
          </div>

          <div>
            <h4 className="font-bold text-white mb-2">3. Theme Responsiveness:</h4>
            <p className="text-sm">
              Both modals automatically adapt to the current theme selected in Theme Settings.
              Try changing themes to see the modals update colors in real-time!
            </p>
          </div>

          <div>
            <h4 className="font-bold text-white mb-2">4. Custom Messages:</h4>
            <pre className="bg-black/50 p-3 rounded text-xs overflow-x-auto">
{`// Processing Modal
<ProcessingModal 
  isOpen={true}
  message="Generating Tickets..."
  subMessage="Finding the best matches"
/>

// No Events Modal  
<NoEventsModal 
  isOpen={true}
  onClose={() => {}}
  title="Custom Title"
  message="Custom error message"
  suggestion="Custom suggestion text"
/>`}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
