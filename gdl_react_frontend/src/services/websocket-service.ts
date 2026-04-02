import { API_CONFIG, buildWsUrl } from './api-config';

/**
 * Ticket generation request from components
 */
export interface TicketGenerationRequest {
  entries: number;
  wager: number;
  sports: string[];
  timeframe: string;
  drawDate?: string;
}

/**
 * Ticket generation response from backend
 */
export interface TicketGenerationResponse {
  success: boolean;
  ticket?: {
    id: string;
    entries: Array<{
      id: string;
      sport: string;
      sportName: string;
      event: string;
      team1: string;
      team2: string;
      prediction: string;
      odds: number;
      startTime: string;
    }>;
    wager: number;
    potentialPayout: number;
    totalOdds: number;
    drawDate: string;
    generatedAt: string;
  };
  error?: string;
  message?: string;
}

/**
 * WebSocket connection manager for a single endpoint
 */
class WebSocketConnection {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private messageHandlers: Map<string, (data: any) => void> = new Map();
  public activeRequests: Map<string, (data: any) => void> = new Map(); // requestId -> callback (public for QuickPicks)
  private isConnected = false;
  private endpoint: string;
  private globalHandlersRegistered = false;

  constructor(endpoint: string) {
    this.endpoint = endpoint;
  }

  connect() {
    // Only connect if not already connected
    if (this.isConnected || this.ws?.readyState === WebSocket.OPEN) {
      console.log(`⚠️ WebSocket already connected to ${this.endpoint}`);
      return;
    }

    if (API_CONFIG.USE_MOCK_DATA) {
      console.log('📦 Using mock data - WebSocket connection skipped');
      this.isConnected = false;
      return;
    }

    const wsUrl = buildWsUrl(this.endpoint);
    console.log(`🔌 Connecting to WebSocket: ${wsUrl}`);

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log(`✅ WebSocket connected to ${this.endpoint}`);
        this.reconnectAttempts = 0;
        this.isConnected = true;

        // Register global handlers if not already registered
        if (!this.globalHandlersRegistered) {
          this.registerGlobalHandlers();
          this.globalHandlersRegistered = true;
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error(`❌ WebSocket error on ${this.endpoint}:`, error);
      };

      this.ws.onclose = () => {
        console.log(`🔌 WebSocket disconnected from ${this.endpoint}`);
        this.isConnected = false;
        this.attemptReconnect();
      };

    } catch (error) {
      console.error(`Failed to create WebSocket connection to ${this.endpoint}:`, error);
      this.isConnected = false;
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect to ${this.endpoint} (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

      setTimeout(() => {
        this.connect();
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error(`Max reconnection attempts reached for ${this.endpoint}. Please refresh the page.`);
    }
  }

  private handleMessage(data: any) {
    // Handle both camelCase (requestId) and snake_case (request_id) from Django
    const requestId = data.requestId || data.request_id;
    const { type } = data;

    console.log('📨 WebSocket message received:', data);
    console.log('📨 Extracted:', { type, requestId });

    // Try to find handler by requestId first, then by type
    const handler = this.messageHandlers.get(requestId) || this.messageHandlers.get(type);

    if (handler) {
      console.log('✅ Handler found for:', requestId || type);
      // Pass the entire data object to the handler, including type and requestId
      handler({ ...data, requestId });

      // Only remove handler if it's a completion message with a requestId
      if (requestId && (type === 'complete' || type === 'error')) {
        this.messageHandlers.delete(requestId);
      }
    } else {
      console.warn('⚠️ No handler found for message:', { type, requestId });
      console.warn('⚠️ Available handlers:', Array.from(this.messageHandlers.keys()));
    }
  }

  send(data: any): boolean {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log(`📤 [WebSocket ${this.endpoint}] Sending:`, JSON.stringify(data, null, 2));
      this.ws.send(JSON.stringify(data));
      return true;
    }
    console.error(`❌ [WebSocket ${this.endpoint}] Cannot send - not connected`);
    return false;
  }

  registerHandler(id: string, handler: (data: any) => void) {
    console.log(`📝 Registering handler with id: "${id}"`);
    this.messageHandlers.set(id, handler);
    console.log(`📝 Total handlers now:`, Array.from(this.messageHandlers.keys()));
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.isConnected = false;
    }
  }

  isReady(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  private registerGlobalHandlers() {
    // Register handlers for common message types
    // Since Django doesn't echo our requestId, we route to the LATEST active request
    this.registerHandler('ticket', (data) => {
      console.log('📥 Received ticket type message:', data);

      // Get the most recent callback (since we typically only have one active request)
      const callbacks = Array.from(this.activeRequests.values());
      if (callbacks.length > 0) {
        const callback = callbacks[callbacks.length - 1]; // Use most recent
        callback(data);
      } else {
        console.warn('⚠️ No active request callbacks found for ticket message');
      }
    });

    this.registerHandler('complete', (data) => {
      console.log('📥 Received complete type message:', data);

      // Get the most recent callback
      const callbacks = Array.from(this.activeRequests.values());
      if (callbacks.length > 0) {
        const callback = callbacks[callbacks.length - 1];
        callback(data);

        // Clear all active requests after completion
        this.activeRequests.clear();
      }
    });

    this.registerHandler('error', (data) => {
      console.log('📥 Received error type message:', data);

      // Get the most recent callback
      const callbacks = Array.from(this.activeRequests.values());
      if (callbacks.length > 0) {
        const callback = callbacks[callbacks.length - 1];
        callback(data);

        // Clear all active requests after error
        this.activeRequests.clear();
      }
    });
  }
}

/**
 * Main WebSocket Service
 * Manages connections to both ticket generation endpoints
 */
export class TicketWebSocketService {
  private ticketsConnection: WebSocketConnection;
  private quickPicksConnection: WebSocketConnection;

  constructor() {
    this.ticketsConnection = new WebSocketConnection(API_CONFIG.WS_ENDPOINTS.STREAM_TICKETS);
    this.quickPicksConnection = new WebSocketConnection(API_CONFIG.WS_ENDPOINTS.STREAM_QUICKPICKS);
  }

  /**
   * Connect to WebSocket endpoints
   * Call this after user login
   */
  connect() {
    this.ticketsConnection.connect();
    this.quickPicksConnection.connect();
  }

  /**
   * Generate a ticket via WebSocket (normal custom form)
   * @deprecated REMOVED - Use sendRawTicketPayload() for Django integration
   */
  generateTicket(
    request: TicketGenerationRequest,
    onResponse: (response: TicketGenerationResponse) => void
  ): string {
    throw new Error(
      '❌ generateTicket() has been REMOVED!\n' +
      'This method sends the WRONG payload format to Django.\n' +
      'Use sendRawTicketPayload() instead with proper Django payload structure.\n' +
      'See: /sportslotto/services/ticket-websocket-adapter.ts for examples.'
    );
  }

  /**
   * Generate quick pick tickets via WebSocket
   */
  generateQuickPick(
    request: TicketGenerationRequest,
    onResponse: (response: TicketGenerationResponse) => void
  ): string {
    const requestId = `quickpick_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // Register response handler
    this.quickPicksConnection.registerHandler(requestId, (data) => {
      onResponse(data as TicketGenerationResponse);
    });

    if (API_CONFIG.USE_MOCK_DATA) {
      // Use mock data in development
      setTimeout(() => {
        onResponse(this.generateMockTicket(request));
      }, 800); // Slightly faster for quick picks
    } else if (this.quickPicksConnection.isReady()) {
      // Send request to backend
      this.quickPicksConnection.send({
        type: 'generate_quickpick',
        requestId,
        ...request,
      });
    } else {
      // WebSocket not ready
      onResponse({
        success: false,
        error: 'Quick pick service not available. Please try again.',
      });
    }

    return requestId;
  }

  /**
   * Send raw Django-formatted payload directly
   * Used by the adapter to send Django's exact format
   */
  sendRawTicketPayload(
    payload: any,
    onResponse: (response: any) => void
  ): string {
    const requestId = payload.requestId || `ticket_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    console.log('🚀 sendRawTicketPayload called with:', {
      requestId,
      action: payload.action,
      settings: payload.settings,
      USE_MOCK_DATA: API_CONFIG.USE_MOCK_DATA,
      isReady: this.ticketsConnection.isReady(),
    });

    // REMOVED: No longer registering handlers here - they're registered globally on connection
    // Instead, we just store the callback for this request
    console.log('📝 Storing callback for request:', requestId);
    this.ticketsConnection['activeRequests'].set(requestId, onResponse);

    if (API_CONFIG.USE_MOCK_DATA) {
      // Use mock data in development
      console.log('📦 Generating mock responses...');
      const count = payload.settings?.count || 1;
      console.log(`📦 Will generate ${count} mock tickets`);

      // Generate multiple tickets with delays to simulate streaming
      for (let i = 0; i < count; i++) {
        setTimeout(() => {
          const mockResponse = {
            type: 'ticket',
            uuid: `ticket_${Date.now()}_${i}`,
            depth: payload.settings?.depth || 7,
            total_stake: payload.settings?.stake || 1,
            total_returns: payload.settings?.min_payout || 100,
            legs: [],
            muuids: [],
            outcomes: [],
            lines: [],
            outcome_meta: {},
            status: 'C',
            requestId, // Include requestId for proper routing
          };
          console.log(`📦 Sending mock ticket ${i + 1}/${count}:`, mockResponse.uuid);
          onResponse(mockResponse);

          // Send completion message after last ticket
          if (i === count - 1) {
            setTimeout(() => {
              console.log('✅ Mock ticket generation complete');
              onResponse({ type: 'complete', requestId });
            }, 100);
          }
        }, 300 * i); // 300ms delay between tickets
      }
    } else if (this.ticketsConnection.isReady()) {
      // Send raw payload to Django INCLUDING our requestId for response matching
      const payloadWithRequestId = {
        ...payload,
        requestId, // Django should echo this back in responses
      };
      console.log('📤 Sending to WebSocket:', payloadWithRequestId);
      this.ticketsConnection.send(payloadWithRequestId);
    } else {
      // WebSocket not ready
      console.error('❌ WebSocket not ready!');
      onResponse({
        type: 'error',
        error: 'WebSocket connection not established. Please try again.',
      });
    }

    return requestId;
  }

  /**
   * Send raw Django-formatted payload to /stream_quickpicks
   * Used by the quick picks adapter to send Django's exact format
   */
  sendRawQuickPickPayload(
    payload: any,
    onResponse: (response: any) => void
  ): string {
    const requestId = payload.requestId || `quickpick_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // Register response handler in activeRequests (not messageHandlers)
    // This is where the global 'ticket' and 'complete' handlers look for callbacks
    this.quickPicksConnection.activeRequests.set(requestId, onResponse);

    console.log('🎰 Registered QuickPick callback for request:', requestId);
    console.log('🎰 Active requests:', Array.from(this.quickPicksConnection.activeRequests.keys()));

    if (API_CONFIG.USE_MOCK_DATA) {
      // Use mock data in development
      setTimeout(() => {
        const mockResponse = {
          type: 'ticket',
          uuid: `qp_${Date.now()}`,
          depth: 7,
          total_stake: payload.settings?.stake || 1,
          total_returns: (payload.settings?.stake || 1) * 20,
          legs: [],
          status: 'C',
        };
        onResponse(mockResponse);
      }, 500);
    } else if (this.quickPicksConnection.isReady()) {
      // Send raw payload to Django
      this.quickPicksConnection.send(payload);
    } else {
      // WebSocket not ready
      onResponse({
        type: 'error',
        error: 'Quick pick service not available. Please try again.',
      });
    }

    return requestId;
  }

  /**
   * Close all WebSocket connections
   */
  disconnect() {
    this.ticketsConnection.disconnect();
    this.quickPicksConnection.disconnect();
  }

  /**
   * Generate mock ticket for development
   */
  private generateMockTicket(request: TicketGenerationRequest): TicketGenerationResponse {
    const sports = [
      { id: 'tennis', name: 'Tennis', icon: '🎾' },
      { id: 'us-sports', name: 'US Sports', icon: '🏈' },
      { id: 'soccer', name: 'Soccer', icon: '⚽' },
      { id: 'ncaa-basketball', name: 'NCAA Basketball', icon: '🏀' },
    ];

    // Filter sports based on request
    const availableSports = sports.filter(s => request.sports.includes(s.id));

    // Generate entries
    const entries = Array.from({ length: request.entries }, (_, i) => {
      const sport = availableSports[Math.floor(Math.random() * availableSports.length)];
      const odds = 1.5 + Math.random() * 2; // Random odds between 1.5 and 3.5

      return {
        id: `entry_${Date.now()}_${i}`,
        sport: sport.id,
        sportName: sport.name,
        event: this.getMockEvent(sport.id),
        team1: this.getMockTeam(sport.id),
        team2: this.getMockTeam(sport.id),
        prediction: ['Win', 'Over', 'Under'][Math.floor(Math.random() * 3)],
        odds: Math.round(odds * 100) / 100,
        startTime: this.getRandomStartTime(request.timeframe),
      };
    });

    // Calculate total odds
    const totalOdds = entries.reduce((acc, entry) => acc * entry.odds, 1);
    const potentialPayout = request.wager * totalOdds;

    return {
      success: true,
      ticket: {
        id: `ticket_${Date.now()}`,
        entries,
        wager: request.wager,
        potentialPayout: Math.round(potentialPayout * 100) / 100,
        totalOdds: Math.round(totalOdds * 100) / 100,
        drawDate: request.drawDate || new Date().toISOString(),
        generatedAt: new Date().toISOString(),
      },
    };
  }

  private getMockEvent(sport: string): string {
    const events: Record<string, string[]> = {
      'tennis': ['ATP Finals', 'Grand Slam', 'Masters 1000'],
      'us-sports': ['NFL Sunday', 'NBA Game', 'MLB Series'],
      'soccer': ['Premier League', 'Champions League', 'La Liga'],
      'ncaa-basketball': ['March Madness', 'Conference Finals', 'Tournament'],
    };
    const sportEvents = events[sport] || ['Match'];
    return sportEvents[Math.floor(Math.random() * sportEvents.length)];
  }

  private getMockTeam(sport: string): string {
    const teams: Record<string, string[]> = {
      'tennis': ['Nadal', 'Federer', 'Djokovic', 'Alcaraz', 'Medvedev'],
      'us-sports': ['Lakers', 'Patriots', 'Yankees', 'Cowboys', 'Warriors'],
      'soccer': ['Barcelona', 'Real Madrid', 'Man United', 'Liverpool', 'Bayern'],
      'ncaa-basketball': ['Duke', 'UNC', 'Kansas', 'Kentucky', 'UCLA'],
    };
    const sportTeams = teams[sport] || ['Team A', 'Team B'];
    return sportTeams[Math.floor(Math.random() * sportTeams.length)];
  }

  private getRandomStartTime(timeframe: string): string {
    const hours = parseInt(timeframe) || 24;
    const now = Date.now();
    const randomMs = Math.random() * hours * 60 * 60 * 1000;
    return new Date(now + randomMs).toISOString();
  }
}

// Singleton instance
export const ticketWebSocket = new TicketWebSocketService();