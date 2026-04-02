import React from 'react';
import { Sport } from '../App';

interface MainMenuProps {
  onSportSelect: (sport: Sport) => void;
  onQuickPicksSelect?: () => void;
  onCustomTicketsSelect?: () => void;
}

export function MainMenu({ onSportSelect, onQuickPicksSelect, onCustomTicketsSelect }: MainMenuProps) {
  const sports: { id: Sport; name: string; icon: string }[] = [
    { id: 'tennis', name: 'Tennis', icon: '🎾' },
    { id: 'us-sports', name: 'US Sports', icon: '🏈' },
    { id: 'soccer', name: 'Soccer', icon: '⚽' },
    { id: 'ncaa-basketball', name: 'NCAA Basketball', icon: '🏀' },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-yellow-400 via-orange-500 to-orange-600 bg-clip-text text-transparent">SPORTSLOTTO</h1>
        <p className="text-lg md:text-xl text-gray-300">Choose Your Game Mode</p>
      </div>

      {/* Main Action Buttons */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 max-w-4xl mx-auto">
        <button
          onClick={() => onCustomTicketsSelect && onCustomTicketsSelect()}
          className="group relative overflow-hidden rounded-2xl p-6 md:p-8 transition-all duration-300 hover:scale-105 backdrop-blur-md"
          style={{
            background: 'rgba(20, 20, 40, 0.6)',
            border: '3px solid rgba(168, 85, 247, 0.6)',
            boxShadow: '0 8px 32px rgba(168, 85, 247, 0.4), inset 0 0 20px rgba(168, 85, 247, 0.1)'
          }}
        >
          <div className="relative z-10">
            <div className="text-4xl md:text-6xl mb-4">🎫</div>
            <h2 className="text-2xl md:text-3xl font-bold text-white mb-2">Custom Tickets</h2>
            <p className="text-sm md:text-base text-gray-300">Build your own sports lottery ticket</p>
          </div>
          <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </button>

        <button
          onClick={() => onQuickPicksSelect && onQuickPicksSelect()}
          className="group relative overflow-hidden rounded-2xl p-6 md:p-8 transition-all duration-300 hover:scale-105 backdrop-blur-md"
          style={{
            background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.8) 0%, rgba(236, 72, 153, 0.8) 50%, rgba(251, 146, 60, 0.8) 100%)',
            border: '2px solid rgba(251, 146, 60, 0.8)',
            boxShadow: '0 8px 32px rgba(251, 146, 60, 0.5)'
          }}
        >
          <div className="relative z-10">
            <div className="text-4xl md:text-6xl mb-4">⚡</div>
            <h2 className="text-2xl md:text-3xl font-bold text-white mb-2">Quick Play</h2>
            <p className="text-sm md:text-base text-white/90">Fast & Easy - All Your Favorites In One Place</p>
          </div>
          <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-white/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </button>
      </div>

      {/* Sport Categories */}
      <div className="mt-12">
        <h3 className="text-xl md:text-2xl font-bold text-center mb-6 bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">Choose a Sport</h3>
        <div className="grid grid-cols-2 gap-3 md:gap-4 max-w-2xl mx-auto">
          {sports.map((sport) => (
            <button
              key={sport.id}
              onClick={() => onSportSelect(sport.id)}
              className="group relative overflow-hidden rounded-xl p-4 md:p-6 transition-all duration-300 hover:scale-105 backdrop-blur-sm"
              style={{
                background: 'rgba(20, 20, 40, 0.7)',
                border: '2px solid rgba(251, 146, 60, 0.5)',
                boxShadow: '0 4px 16px rgba(251, 146, 60, 0.3)'
              }}
            >
              <div className="text-3xl md:text-5xl mb-3">{sport.icon}</div>
              <h4 className="text-base md:text-lg font-bold text-white">{sport.name}</h4>
              <div className="absolute inset-0 bg-gradient-to-br from-orange-500/10 to-yellow-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}