/**
 * React Hooks for API Integration
 */

import { useState, useEffect, useCallback } from 'react';
import { 
  ticketWebSocket, 
  TicketGenerationRequest, 
  TicketGenerationResponse 
} from './websocket-service';
import { 
  apiService, 
  SportsConfigResponse, 
  TicketRecord, 
  LeaderboardEntry 
} from './api-service';

/**
 * Hook for generating tickets via WebSocket
 * @deprecated REMOVED - Use ticket-websocket-adapter.ts functions instead
 */
export function useTicketGeneration() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(
    '❌ useTicketGeneration() is DEPRECATED!\n' +
    'Use generateCustomTickets() from /sportslotto/services/ticket-websocket-adapter.ts instead.\n' +
    'This hook sends the WRONG payload format to Django.'
  );
  const [response, setResponse] = useState<TicketGenerationResponse | null>(null);

  const generateTicket = useCallback((request: TicketGenerationRequest) => {
    throw new Error(
      '❌ useTicketGeneration().generateTicket() has been REMOVED!\n' +
      'Use generateCustomTickets() from /sportslotto/services/ticket-websocket-adapter.ts instead.\n' +
      'The old format is incompatible with Django.'
    );
  }, []);

  return {
    generateTicket,
    loading,
    error,
    response,
  };
}

/**
 * Hook for fetching sports configuration
 */
export function useSportsConfig() {
  const [config, setConfig] = useState<SportsConfigResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    const fetchConfig = async () => {
      try {
        setLoading(true);
        const data = await apiService.getSportsConfig();

        if (mounted) {
          setConfig(data);
          setError(null);
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to fetch sports config');
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    fetchConfig();

    return () => {
      mounted = false;
    };
  }, []);

  return { config, loading, error };
}

/**
 * Hook for fetching recent tickets
 */
export function useRecentTickets(limit: number = 20, autoRefresh: boolean = false) {
  const [tickets, setTickets] = useState<TicketRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTickets = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiService.getRecentTickets(limit);
      setTickets(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tickets');
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    fetchTickets();

    // Auto-refresh every 30 seconds if enabled
    if (autoRefresh) {
      const interval = setInterval(fetchTickets, 30000);
      return () => clearInterval(interval);
    }
  }, [fetchTickets, autoRefresh]);

  return { tickets, loading, error, refresh: fetchTickets };
}

/**
 * Hook for fetching leaderboard
 */
export function useLeaderboard(limit: number = 10) {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLeaderboard = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiService.getLeaderboard(limit);
      setLeaderboard(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch leaderboard');
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    fetchLeaderboard();
  }, [fetchLeaderboard]);

  return { leaderboard, loading, error, refresh: fetchLeaderboard };
}

/**
 * Hook for live results subscription
 */
export function useLiveResults() {
  const [results, setResults] = useState<any[]>([]);

  useEffect(() => {
    const handleUpdate = (data: any) => {
      setResults(prev => [data, ...prev].slice(0, 50)); // Keep last 50 results
    };

    ticketWebSocket.subscribeLiveResults(handleUpdate);

    return () => {
      ticketWebSocket.unsubscribeLiveResults();
    };
  }, []);

  return { results };
}

/**
 * Hook for statistics
 */
export function useStatistics() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    const fetchStats = async () => {
      try {
        setLoading(true);
        const data = await apiService.getStatistics();

        if (mounted) {
          setStats(data);
          setError(null);
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to fetch statistics');
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    fetchStats();

    return () => {
      mounted = false;
    };
  }, []);

  return { stats, loading, error };
}