/**
 * Example Component: Dynamic Sports Selector using Backend Configuration
 * 
 * This demonstrates how to load sports configuration from Django backend
 * and use it to dynamically render sport selection UI.
 */

import React from 'react';
import { useSportsConfig } from '../../services/api-hooks';

interface DynamicSportsSelectorProps {
  onSportSelect: (sportId: string) => void;
  selectedSports: string[];
}

export function DynamicSportsSelector({ onSportSelect, selectedSports }: DynamicSportsSelectorProps) {
  const { config, loading, error } = useSportsConfig();

  if (loading) {
    return (
      <div className="rounded-2xl p-8 backdrop-blur-md text-center" style={{
        background: 'rgba(20, 20, 40, 0.7)',
        border: '2px solid rgba(251, 146, 60, 0.4)',
      }}>
        <div className="animate-spin text-4xl mb-4">⚽</div>
        <p className="text-gray-300">Loading sports configuration...</p>
      </div>
    );
  }

  if (error || !config) {
    return (
      <div className="rounded-2xl p-8 backdrop-blur-md" style={{
        background: 'rgba(20, 20, 40, 0.7)',
        border: '2px solid rgba(239, 68, 68, 0.4)',
      }}>
        <p className="text-red-400">❌ {error || 'Failed to load sports configuration'}</p>
        <p className="text-gray-400 text-sm mt-2">
          Using fallback configuration. Please check your backend connection.
        </p>
      </div>
    );
  }

  // Filter only enabled sports
  const enabledSports = config.sports.filter(sport => sport.enabled);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div>
        <h3 className="text-xl font-bold bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent mb-2">
          Select Sports
        </h3>
        <p className="text-sm text-gray-400">
          Choose which sports to include in your ticket
        </p>
      </div>

      {/* Sports Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {enabledSports.map((sport) => {
          const isSelected = selectedSports.includes(sport.id);
          
          return (
            <button
              key={sport.id}
              onClick={() => onSportSelect(sport.id)}
              className={`rounded-xl p-6 backdrop-blur-md transition-all hover:scale-105 ${
                isSelected ? 'ring-2 ring-orange-500' : ''
              }`}
              style={{
                background: isSelected
                  ? 'linear-gradient(135deg, rgba(168, 85, 247, 0.3) 0%, rgba(236, 72, 153, 0.3) 50%, rgba(251, 146, 60, 0.3) 100%)'
                  : 'rgba(20, 20, 40, 0.7)',
                border: isSelected
                  ? '2px solid rgba(251, 146, 60, 0.8)'
                  : '2px solid rgba(251, 146, 60, 0.3)',
              }}
            >
              {/* Icon */}
              <div className="text-4xl mb-3">{sport.icon}</div>
              
              {/* Name */}
              <p className="font-bold text-white mb-1">{sport.name}</p>
              
              {/* Odds Range */}
              <p className="text-xs text-gray-400">
                Odds: {sport.settings.minOdds}x - {sport.settings.maxOdds}x
              </p>
              
              {/* Selected Indicator */}
              {isSelected && (
                <div className="mt-3 text-green-400 text-sm font-bold">
                  ✓ Selected
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Info Box */}
      <div className="rounded-lg p-4 backdrop-blur-sm" style={{
        background: 'rgba(168, 85, 247, 0.1)',
        border: '1px solid rgba(168, 85, 247, 0.3)',
      }}>
        <p className="text-sm text-purple-300">
          💡 <strong>Tip:</strong> Selecting multiple sports increases your chances of getting diverse picks!
        </p>
      </div>

      {/* Configuration Details (for debugging) */}
      {config.customTickets && (
        <div className="text-xs text-gray-500">
          <p>Backend Configuration:</p>
          <ul className="list-disc list-inside">
            <li>Custom Tickets: {config.customTickets.enabled ? 'Enabled' : 'Disabled'}</li>
            <li>Available Sports: {config.customTickets.availableSports.join(', ')}</li>
            <li>Default Sports: {config.customTickets.defaultSports.join(', ')}</li>
          </ul>
        </div>
      )}
    </div>
  );
}

/**
 * Example usage:
 * 
 * function MyComponent() {
 *   const [selectedSports, setSelectedSports] = useState<string[]>(['tennis', 'soccer']);
 *   
 *   const handleSportToggle = (sportId: string) => {
 *     setSelectedSports(prev => 
 *       prev.includes(sportId)
 *         ? prev.filter(id => id !== sportId)
 *         : [...prev, sportId]
 *     );
 *   };
 *   
 *   return (
 *     <DynamicSportsSelector 
 *       onSportSelect={handleSportToggle}
 *       selectedSports={selectedSports}
 *     />
 *   );
 * }
 */
