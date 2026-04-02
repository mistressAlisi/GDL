/**
 * Example Component: Leaderboard with API Integration
 * 
 * This demonstrates how to integrate the Django backend API
 * for displaying leaderboard data.
 */

import React from 'react';
import { useLeaderboard } from '../../services/api-hooks';

export function LeaderboardDisplay() {
  const { leaderboard, loading, error, refresh } = useLeaderboard(10);

  if (loading) {
    return (
      <div className="rounded-2xl p-8 backdrop-blur-md text-center" style={{
        background: 'rgba(20, 20, 40, 0.7)',
        border: '2px solid rgba(251, 146, 60, 0.4)',
      }}>
        <div className="animate-spin text-4xl mb-4">🏆</div>
        <p className="text-gray-300">Loading leaderboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-2xl p-8 backdrop-blur-md" style={{
        background: 'rgba(20, 20, 40, 0.7)',
        border: '2px solid rgba(239, 68, 68, 0.4)',
      }}>
        <p className="text-red-400">❌ {error}</p>
        <button 
          onClick={refresh}
          className="mt-4 px-4 py-2 rounded bg-orange-500 hover:bg-orange-600 text-white"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
          🏆 Top Players
        </h2>
        <button
          onClick={refresh}
          className="px-4 py-2 rounded bg-orange-500/20 hover:bg-orange-500/30 text-orange-300 transition-colors"
        >
          ↻ Refresh
        </button>
      </div>

      {/* Leaderboard Cards */}
      <div className="space-y-3">
        {leaderboard.map((player, index) => (
          <div 
            key={player.userId}
            className="rounded-xl p-4 backdrop-blur-md flex items-center justify-between hover:scale-[1.02] transition-transform"
            style={{
              background: index < 3 
                ? 'linear-gradient(135deg, rgba(168, 85, 247, 0.3) 0%, rgba(236, 72, 153, 0.3) 50%, rgba(251, 146, 60, 0.3) 100%)'
                : 'rgba(20, 20, 40, 0.7)',
              border: index < 3 
                ? '2px solid rgba(251, 146, 60, 0.6)'
                : '1px solid rgba(251, 146, 60, 0.3)',
            }}
          >
            {/* Rank */}
            <div className="flex items-center gap-4 flex-1">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg ${
                index === 0 ? 'bg-yellow-500 text-black' :
                index === 1 ? 'bg-gray-400 text-black' :
                index === 2 ? 'bg-orange-600 text-white' :
                'bg-gray-700 text-gray-300'
              }`}>
                {index < 3 ? ['🥇', '🥈', '🥉'][index] : player.rank}
              </div>

              {/* Player Info */}
              <div className="flex-1">
                <p className="font-bold text-white text-lg">{player.userName}</p>
                <p className="text-xs text-gray-400">
                  {player.totalWins} wins • {player.winRate.toFixed(1)}% win rate
                </p>
              </div>

              {/* Stats */}
              <div className="text-right space-y-1">
                <p className="text-sm text-gray-400">Total Wagered</p>
                <p className="text-lg font-bold text-orange-400">
                  ${player.totalWager.toFixed(2)}
                </p>
              </div>

              <div className="text-right space-y-1">
                <p className="text-sm text-gray-400">Total Payout</p>
                <p className="text-lg font-bold text-green-400">
                  ${player.totalPayout.toFixed(2)}
                </p>
              </div>

              {/* Profit */}
              <div className="text-right space-y-1">
                <p className="text-sm text-gray-400">Profit</p>
                <p className={`text-lg font-bold ${
                  player.totalPayout - player.totalWager > 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  ${(player.totalPayout - player.totalWager).toFixed(2)}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
