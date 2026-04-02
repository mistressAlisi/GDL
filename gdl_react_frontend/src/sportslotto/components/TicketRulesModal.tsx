import React from 'react';
import { X, Settings, Trophy, Dumbbell, GraduationCap, Clock, Target } from 'lucide-react';
import { useTicketRules, Timeframe } from '../contexts/TicketRulesContext';
import { useTheme } from '../contexts/ThemeContext';

interface TicketRulesModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const TIMEFRAMES: { value: Timeframe; label: string }[] = [
  { value: 48, label: '48 Hours' },
  { value: 42, label: '42 Hours' },
  { value: 36, label: '36 Hours' },
  { value: 30, label: '30 Hours' },
  { value: 24, label: '24 Hours' },
  { value: 18, label: '18 Hours' },
  { value: 12, label: '12 Hours' },
];

const SPORTS_CONFIG = [
  { id: 'tennis' as const, label: 'Tennis', icon: Trophy },
  { id: 'us-sports' as const, label: 'US Sports', icon: Target },
  { id: 'soccer' as const, label: 'Soccer', icon: Dumbbell },
  { id: 'ncaa-basketball' as const, label: 'NCAA Basketball', icon: GraduationCap },
];

export function TicketRulesModal({ isOpen, onClose }: TicketRulesModalProps) {
  const { theme } = useTheme();
  const { rules, toggleSport, updateTimeframe, isAllSportsSelected, toggleAllSports } = useTicketRules();

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div 
        className="rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden backdrop-blur-md"
        onClick={(e) => e.stopPropagation()}
        style={{
          background: theme.cardBg,
          border: `2px solid ${theme.cardBorder}`,
          boxShadow: `0 8px 32px ${theme.cardGlow}`
        }}
      >
        {/* Header */}
        <div className="border-b px-6 py-4 flex items-center justify-between" style={{
          background: 'rgba(0, 0, 0, 0.3)',
          borderColor: theme.cardBorder
        }}>
          <div className="flex items-center gap-3 mb-6">
            <Settings className="w-6 h-6" style={{ color: theme.accentColor }} />
            <h3 className="text-2xl font-bold bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
              Ticket Defaults
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors text-2xl"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
          {/* Sports Selection Section */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Trophy className="w-5 h-5" style={{ color: theme.accentColor }} />
                <h4 className="text-lg font-bold text-white">Select Sports</h4>
              </div>
              <button
                onClick={toggleAllSports}
                className="px-4 py-2 rounded-lg text-sm font-semibold transition-all"
                style={{
                  background: isAllSportsSelected() ? theme.buttonGradient : 'rgba(60, 60, 80, 0.5)',
                  color: 'white',
                  boxShadow: isAllSportsSelected() ? `0 4px 20px ${theme.cardGlow}` : 'none'
                }}
              >
                {isAllSportsSelected() ? 'All Selected' : 'Select All'}
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {SPORTS_CONFIG.map((sport) => {
                const Icon = sport.icon;
                const isSelected = rules.selectedSports.includes(sport.id);
                
                return (
                  <button
                    key={sport.id}
                    onClick={() => toggleSport(sport.id)}
                    className="p-4 rounded-xl transition-all flex items-center gap-3 text-left"
                    style={{
                      background: isSelected ? `${theme.cardBorder}40` : 'rgba(0, 0, 0, 0.3)',
                      border: `2px solid ${isSelected ? theme.cardBorder : 'transparent'}`,
                      boxShadow: isSelected ? `0 4px 20px ${theme.cardGlow}40` : 'none'
                    }}
                  >
                    <div 
                      className="w-10 h-10 rounded-lg flex items-center justify-center"
                      style={{
                        background: isSelected ? theme.buttonGradient : 'rgba(60, 60, 80, 0.5)'
                      }}
                    >
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="font-bold text-white">{sport.label}</div>
                      <div className="text-xs text-gray-400">
                        {isSelected ? 'Included' : 'Excluded'}
                      </div>
                    </div>
                    <div 
                      className="w-6 h-6 rounded-full border-2 flex items-center justify-center"
                      style={{
                        borderColor: isSelected ? theme.accentColor : 'rgba(255, 255, 255, 0.3)',
                        background: isSelected ? theme.accentColor : 'transparent'
                      }}
                    >
                      {isSelected && (
                        <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>

            {rules.selectedSports.length === 0 && (
              <p className="text-yellow-400 text-sm mt-2">
                ⚠️ At least one sport must be selected
              </p>
            )}
          </div>

          {/* Timeframe Selection Section */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Clock className="w-5 h-5" style={{ color: theme.accentColor }} />
              <h4 className="text-lg font-bold text-white">Event Timeframe</h4>
            </div>

            <p className="text-sm text-gray-400 mb-4">
              Select how far in advance you want to bet on events. Only one timeframe can be active.
            </p>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {TIMEFRAMES.map((tf) => {
                const isSelected = rules.timeframe === tf.value;
                
                return (
                  <button
                    key={tf.value}
                    onClick={() => updateTimeframe(tf.value)}
                    className="p-4 rounded-xl transition-all text-center"
                    style={{
                      background: isSelected ? theme.buttonGradient : 'rgba(0, 0, 0, 0.3)',
                      border: `2px solid ${isSelected ? theme.cardBorder : 'transparent'}`,
                      boxShadow: isSelected ? `0 4px 20px ${theme.cardGlow}` : 'none'
                    }}
                  >
                    <div className="text-2xl font-bold text-white mb-1">
                      {tf.value}h
                    </div>
                    <div className="text-xs text-gray-400">
                      {isSelected ? 'Active' : 'Select'}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Info Box */}
          <div 
            className="mt-6 p-4 rounded-lg"
            style={{
              background: 'rgba(59, 130, 246, 0.1)',
              border: '1px solid rgba(59, 130, 246, 0.3)'
            }}
          >
            <p className="text-sm text-blue-300">
              <strong>💡 Note:</strong> These rules apply to both Quick Picks and sport-specific betting. 
              Only events from selected sports within the chosen timeframe will be available.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t px-6 py-4 flex gap-3" style={{
          background: 'rgba(0, 0, 0, 0.3)',
          borderColor: theme.cardBorder
        }}>
          <button
            onClick={onClose}
            className="flex-1 py-3 rounded-lg font-bold text-white transition-all"
            style={{
              background: theme.buttonGradient,
              boxShadow: `0 4px 20px ${theme.cardGlow}`
            }}
          >
            Save & Close
          </button>
        </div>
      </div>
    </div>
  );
}