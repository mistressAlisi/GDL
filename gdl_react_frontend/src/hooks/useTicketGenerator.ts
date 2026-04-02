import { useState, useCallback, useRef, useEffect } from 'react';
import { WebSocketManager } from '../services/WebSocketService';
import { useBootstrap } from '../contexts/BootstrapContext';
import type { Ticket, WebSocketMessage, GenerateSettings } from '../types/ticket';

interface UseTicketGeneratorOptions {
  streamName: string;
  endpoint: string;
  onTicket?: (ticket: Ticket) => void;
  onComplete?: (data: any) => void;
  onError?: (error: string) => void;
  onEmpty?: (data: any) => void;
}

export function useTicketGenerator(options: UseTicketGeneratorOptions) {
  const { streamName, endpoint, onTicket, onComplete, onError, onEmpty } = options;
  const { bootstrap } = useBootstrap();
  const [isGenerating, setIsGenerating] = useState(false);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const wsManagerRef = useRef<WebSocketManager | null>(null);

  // Get WebSocket URL
  const getWsUrl = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    return `${protocol}//${host}${endpoint}`;
  }, [endpoint]);

  // Handle incoming WebSocket messages
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const msg: WebSocketMessage = JSON.parse(event.data);

      switch (msg.type) {
        case 'ticket':
          setTickets((prev) => [...prev, msg as Ticket]);
          onTicket?.(msg as Ticket);
          break;

        case 'complete':
          setIsGenerating(false);
          onComplete?.(msg);
          break;

        case 'empty':
          setIsGenerating(false);
          onEmpty?.(msg);
          break;

        case 'error':
          setIsGenerating(false);
          onError?.(msg.error);
          break;

        case 'pong':
          // Heartbeat response, ignore
          break;

        default:
          console.warn('[TicketGenerator] Unknown message type:', msg);
      }
    } catch (error) {
      console.error('[TicketGenerator] Failed to parse message:', error);
    }
  }, [onTicket, onComplete, onError, onEmpty]);

  // Initialize WebSocket
  useEffect(() => {
    if (!bootstrap?.session.authenticated) return;

    // Skip WebSocket in development if Django not available
    if (import.meta.env.DEV && bootstrap.vhost.uuid === '00000000-0000-0000-0000-000000000001') {
      console.info('[TicketGenerator] Mock mode - WebSocket disabled (Django backend not connected)');
      return;
    }

    const wsManager = new WebSocketManager();
    wsManagerRef.current = wsManager;

    const url = getWsUrl();
    wsManager.initStream(streamName, url, handleMessage);

    return () => {
      wsManager.disconnectAll();
      wsManagerRef.current = null;
    };
  }, [bootstrap, streamName, getWsUrl, handleMessage]);

  // Generate tickets
  const generate = useCallback((settings: Partial<GenerateSettings>) => {
    if (!bootstrap?.session.authenticated || !bootstrap.account) {
      onError?.('Not authenticated');
      return;
    }

    if (!wsManagerRef.current?.isConnected(streamName)) {
      onError?.('WebSocket not connected');
      return;
    }

    // Clear previous tickets
    setTickets([]);
    setIsGenerating(true);

    // Build payload with bootstrap context
    const payload = {
      action: 'generate',
      settings: {
        vhost: bootstrap.vhost.uuid,
        account: bootstrap.account.uuid,
        vdomain: bootstrap.domain.uuid,
        events_within: 129600, // 36 hours default
        ...settings,
      },
    };

    wsManagerRef.current.send(streamName, payload);
  }, [bootstrap, streamName, onError]);

  // Send replacement request
  const replace = useCallback((oldUuid: string, settings: Partial<GenerateSettings>) => {
    if (!bootstrap?.session.authenticated || !bootstrap.account) {
      onError?.('Not authenticated');
      return;
    }

    if (!wsManagerRef.current?.isConnected(streamName)) {
      onError?.('WebSocket not connected');
      return;
    }

    const payload = {
      action: 'generate',
      old_uuid: oldUuid,
      settings: {
        vhost: bootstrap.vhost.uuid,
        account: bootstrap.account.uuid,
        vdomain: bootstrap.domain.uuid,
        count: 1,
        ...settings,
      },
    };

    wsManagerRef.current.send(streamName, payload);
  }, [bootstrap, streamName, onError]);

  return {
    tickets,
    isGenerating,
    generate,
    replace,
    clearTickets: () => setTickets([]),
  };
}