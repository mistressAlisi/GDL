import React from 'react';
import { useTheme, themes, ThemeType } from '../contexts/ThemeContext';
import { Palette } from 'lucide-react';

export function ThemeSettings() {
  const { currentTheme, setTheme } = useTheme();

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <Palette className="w-6 h-6 text-orange-400" />
        <h3 className="text-2xl font-bold bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
          Theme Settings
        </h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(themes).map(([key, theme]) => {
          const isActive = currentTheme === key;
          return (
            <button
              key={key}
              onClick={() => setTheme(key as ThemeType)}
              className={`group relative rounded-xl p-6 transition-all duration-300 ${
                isActive ? 'scale-105' : 'hover:scale-105'
              }`}
              style={{
                background: isActive 
                  ? theme.cardBg 
                  : 'rgba(20, 20, 40, 0.5)',
                border: isActive 
                  ? `3px solid ${theme.cardBorder}` 
                  : '2px solid rgba(255, 255, 255, 0.1)',
                boxShadow: isActive 
                  ? `0 0 30px ${theme.cardGlow}` 
                  : 'none'
              }}
            >
              {/* Theme Preview */}
              <div className="space-y-3">
                {/* Name */}
                <h4 className="text-lg font-bold text-white mb-3">{theme.name}</h4>
                
                {/* Color Preview */}
                <div 
                  className="h-20 rounded-lg"
                  style={{
                    background: theme.gradient
                  }}
                />

                {/* Sample Ticket Preview */}
                <div
                  className="rounded-lg p-4 text-center relative overflow-hidden"
                  style={{
                    background: `linear-gradient(135deg, rgba(0, 0, 0, 0.6) 0%, rgba(20, 20, 40, 0.6) 100%)`,
                    border: `2px solid ${theme.cardBorder}`,
                    boxShadow: `
                      0 0 30px ${theme.cardGlow}, 
                      0 0 20px ${theme.accentColor}60,
                      0 4px 16px rgba(0, 0, 0, 0.5),
                      inset 0 0 40px ${theme.accentColor}15
                    `
                  }}
                >
                  {/* Accent glow overlay */}
                  <div 
                    className="absolute inset-0 opacity-20 pointer-events-none"
                    style={{
                      background: `radial-gradient(circle at top right, ${theme.accentColor}60, transparent 70%)`
                    }}
                  />
                  <div className="relative z-10">
                    <p 
                      className="text-xs mb-1"
                      style={{
                        color: theme.accentColor,
                        textShadow: `0 0 10px ${theme.accentColor}80, 0 0 20px ${theme.accentColor}40`
                      }}
                    >
                      TICKET WINS
                    </p>
                    <p 
                      className="text-2xl font-bold"
                      style={{ 
                        color: theme.accentColor,
                        textShadow: `
                          0 0 25px ${theme.accentColor}, 
                          0 0 50px ${theme.accentColor}80,
                          0 0 75px ${theme.accentColor}40,
                          0 2px 6px rgba(0, 0, 0, 0.9)
                        `
                      }}
                    >
                      2489
                    </p>
                  </div>
                </div>

                {/* Active Indicator */}
                {isActive && (
                  <div className="flex items-center justify-center gap-2 mt-3">
                    <div 
                      className="w-2 h-2 rounded-full"
                      style={{ background: theme.accentColor }}
                    />
                    <span 
                      className="text-xs font-bold"
                      style={{ color: theme.accentColor }}
                    >
                      ACTIVE
                    </span>
                  </div>
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* Info */}
      <div 
        className="rounded-xl p-4 backdrop-blur-sm"
        style={{
          background: 'rgba(251, 146, 60, 0.1)',
          border: '1px solid rgba(251, 146, 60, 0.3)'
        }}
      >
        <p className="text-sm text-gray-300">
          💡 <strong className="text-orange-400">Tip:</strong> Your theme preference affects all ticket cards and UI elements throughout the platform.
        </p>
      </div>
    </div>
  );
}