/**
 * WebSocket Service - Matches Django WSManager pattern
 * 
 * Features:
 * - Request/response pairing via request_id
 * - Queue management with inflight tracking
 * - Auto-reconnection with exponential backoff
 * - Heartbeat/ping support
 */

interface QueuedRequest {
  payload: any;
  resolve: (data: any) => void;
  reject: (error: Error) => void;
}

type MessageHandler = (event: MessageEvent) => void;

export class WebSocketService {
  private ws: WebSocket | null = null;
  private queue: QueuedRequest[] = [];
  private inflight: string | null = null;
  private state: 'idle' | 'waiting' = 'idle';
  private reconnectDelay = 100;
  private maxReconnectDelay = 250;
  private heartbeatInterval: number | null = null;
  private url: string;
  private onMessage: MessageHandler;
  private reconnecting = false;

  constructor(url: string, onMessage: MessageHandler) {
    this.url = url;
    this.onMessage = onMessage;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log(`[WS] Connected: ${this.url}`);
          this.reconnectDelay = 100;
          this.state = 'idle';
          this.inflight = null;
          this.startHeartbeat();
          this.flushQueue();
          resolve();
        };

        this.ws.onmessage = (event) => {
          let msg: any = null;

          try {
            msg = JSON.parse(event.data);
          } catch {
            // Non-JSON message, forward raw
            this.onMessage(event);
            return;
          }

          // Always forward to app
          this.onMessage(event);

          // State management
          const isTerminal = msg?.type === 'complete' || msg?.type === 'error';

          if (isTerminal || (msg?.request_id && msg.request_id === this.inflight)) {
            this.inflight = null;
            this.state = 'idle';
            this.flushQueue();
          }
        };

        this.ws.onclose = () => {
          console.warn(`[WS] Disconnected. Reconnecting in ${this.reconnectDelay}ms...`);
          this.stopHeartbeat();
          
          if (!this.reconnecting) {
            this.reconnecting = true;
            setTimeout(() => {
              this.reconnecting = false;
              this.connect().catch(console.error);
            }, this.reconnectDelay);
            
            this.reconnectDelay = Math.min(
              this.reconnectDelay * 2,
              this.maxReconnectDelay
            );
          }
        };

        this.ws.onerror = (error) => {
          console.error('[WS] Error:', error);
          reject(error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  send(payload: any): void {
    if (!payload.request_id) {
      payload.request_id = this.generateUUID();
    }

    this.queue.push({
      payload,
      resolve: () => {},
      reject: () => {},
    });

    this.flushQueue();
  }

  private flushQueue(): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    if (this.state !== 'idle') return;
    if (this.queue.length === 0) return;

    const item = this.queue.shift();
    if (!item) return;

    const { payload } = item;

    this.inflight = payload.request_id;
    this.state = 'waiting';

    this.ws.send(JSON.stringify(payload));
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    
    this.heartbeatInterval = window.setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({
          action: 'ping',
          request_id: this.generateUUID(),
          data: { time: new Date().toISOString() },
        }));
      }
    }, 15000);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  disconnect(): void {
    this.stopHeartbeat();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.queue = [];
    this.inflight = null;
    this.state = 'idle';
  }

  private generateUUID(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (crypto.getRandomValues(new Uint8Array(1))[0] & 15) >> (c === 'x' ? 0 : 3);
      return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
    });
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

/**
 * WebSocket Manager - Manages multiple named streams
 */
export class WebSocketManager {
  private streams: Map<string, WebSocketService> = new Map();

  initStream(name: string, url: string, onMessage: MessageHandler): void {
    if (this.streams.has(name)) {
      console.warn(`[WSManager] Stream ${name} already exists, reconnecting...`);
      this.streams.get(name)?.disconnect();
    }

    const service = new WebSocketService(url, onMessage);
    this.streams.set(name, service);
    
    service.connect().catch((error) => {
      console.error(`[WSManager] Failed to connect stream ${name}:`, error);
    });
  }

  send(name: string, payload: any): void {
    const stream = this.streams.get(name);
    
    if (!stream) {
      console.error(`[WSManager] Stream ${name} not initialized`);
      return;
    }

    stream.send(payload);
  }

  disconnect(name: string): void {
    const stream = this.streams.get(name);
    
    if (stream) {
      stream.disconnect();
      this.streams.delete(name);
    }
  }

  disconnectAll(): void {
    this.streams.forEach((stream) => stream.disconnect());
    this.streams.clear();
  }

  isConnected(name: string): boolean {
    return this.streams.get(name)?.isConnected() ?? false;
  }
}
