/**
 * Example Component: Statistics Dashboard with API Integration
 * 
 * This demonstrates how to integrate the Django backend API
 * for displaying platform statistics.
 */

import React from 'react';
import { useStatistics } from '../../services/api-hooks';

export function StatisticsDashboard() {
  const { stats, loading, error } = useStatistics();

  if (loading) {
    return (
      <div className="rounded-2xl p-8 backdrop-blur-md text-center" style={{
        background: 'rgba(20, 20, 40, 0.7)',
        border: '2px solid rgba(251, 146, 60, 0.4)',
      }}>
        <div className="animate-spin text-4xl mb-4">📊</div>
        <p className="text-gray-300">Loading statistics...</p>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="rounded-2xl p-8 backdrop-blur-md" style={{
        background: 'rgba(20, 20, 40, 0.7)',
        border: '2px solid rgba(239, 68, 68, 0.4)',
      }}>
        <p className="text-red-400">❌ {error || 'Failed to load statistics'}</p>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Tickets',
      value: stats.totalTickets?.toLocaleString() || '0',
      icon: '🎫',
      color: 'from-purple-500 to-pink-500',
    },
    {
      title: 'Total Wagers',
      value: `$${stats.totalWagers?.toFixed(2) || '0'}`,
      icon: '💰',
      color: 'from-orange-500 to-yellow-500',
    },
    {
      title: 'Total Payouts',
      value: `$${stats.totalPayouts?.toFixed(2) || '0'}`,
      icon: '💵',
      color: 'from-green-500 to-emerald-500',
    },
    {
      title: 'Active Users',
      value: stats.activeUsers?.toLocaleString() || '0',
      icon: '👥',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      title: 'Biggest Win',
      value: `$${stats.biggestWin?.toFixed(2) || '0'}`,
      icon: '🏆',
      color: 'from-yellow-500 to-orange-500',
    },
    {
      title: 'Average Odds',
      value: `${stats.averageOdds?.toFixed(2) || '0'}x`,
      icon: '📈',
      color: 'from-pink-500 to-purple-500',
    },
    {
      title: 'Most Popular Sport',
      value: stats.popularSport || 'N/A',
      icon: '⚽',
      color: 'from-indigo-500 to-purple-500',
    },
    {
      title: 'Platform Status',
      value: 'Online',
      icon: '✅',
      color: 'from-green-500 to-teal-500',
    },
  ];

  return (
    <div className="space-y-4">
      {/* Header */}
      <h2 className="text-2xl font-bold bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
        📊 Platform Statistics
      </h2>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, index) => (
          <div
            key={index}
            className="rounded-xl p-6 backdrop-blur-md hover:scale-105 transition-transform"
            style={{
              background: 'rgba(20, 20, 40, 0.7)',
              border: '2px solid rgba(251, 146, 60, 0.4)',
            }}
          >
            {/* Icon */}
            <div className="text-4xl mb-3">{stat.icon}</div>

            {/* Title */}
            <p className="text-xs text-gray-400 uppercase tracking-wider mb-2">
              {stat.title}
            </p>

            {/* Value */}
            <p 
              className={`text-2xl font-bold bg-gradient-to-r ${stat.color} bg-clip-text text-transparent`}
            >
              {stat.value}
            </p>
          </div>
        ))}
      </div>

      {/* Additional Info */}
      <div className="rounded-xl p-6 backdrop-blur-md" style={{
        background: 'rgba(20, 20, 40, 0.7)',
        border: '2px solid rgba(251, 146, 60, 0.4)',
      }}>
        <p className="text-sm text-gray-400 text-center">
          Statistics updated in real-time • Last updated: {new Date().toLocaleString()}
        </p>
      </div>
    </div>
  );
}
