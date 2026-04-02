export class WSManager {
    constructor(owner) {
        this.owner = owner;
        this.streams = {};
        this.heartbeatInterval = 15000;
    }

    initStream(name, url, onMessage, options = {}) {
        const stream = {
            url,
            ws: null,
            queue: [],
            inflight: null,            // 👈 request_id currently in flight
            state: "idle",             // "idle" | "waiting"
            reconnectDelay: options.reconnectDelay || 100,
            maxReconnectDelay: options.maxReconnectDelay || 250,
            onMessage,
            heartbeatInterval: null
        };

        this.streams[name] = stream;
        this._connect(name);
    }
    _randUUID() {
          return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
            const r =
              (crypto.getRandomValues(new Uint8Array(1))[0] & 15) >>
              (c === 'x' ? 0 : 3);
            return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
          });
    }
    _connect(name) {
        const stream = this.streams[name];
        if (!stream) return;

        const ws = new WebSocket(stream.url);
        stream.ws = ws;
        this.owner[name] = ws;

        ws.onopen = () => {
            console.log(`[WSManager] Connected: ${name}`);
            stream.reconnectDelay = 100;
            stream.state = "idle";
            stream.inflight = null;

            this._flushQueue(name);

            if (stream.heartbeatTimer) clearInterval(stream.heartbeatTimer);
            stream.heartbeatTimer = setInterval(() => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        action: "ping",
                        request_id: this._randUUID(),
                        data: { time: new Date().toISOString() }
                    }));
                }
            }, this.heartbeatInterval);
        };

        ws.onmessage = (event) => {
            let msg = null;

            try {
                msg = JSON.parse(event.data);
            } catch {
                // non-JSON: still forward
                stream.onMessage?.(event);
                return;
            }

            // 🔁 ALWAYS forward to app
            stream.onMessage?.(event);

            // 🔑 state handling (side effects only)
            const isTerminal =
                msg?.type === "complete" ||
                msg?.type === "error";

            if (
                isTerminal ||
                (msg?.request_id && msg.request_id === stream.inflight)
            ) {
                stream.inflight = null;
                stream.state = "idle";
                this._flushQueue(name);
            }
        };

        ws.onclose = () => {
            console.warn(
                `[WSManager] Disconnected: ${name}. Reconnecting in ${stream.reconnectDelay}ms...`
            );
            setTimeout(() => this._connect(name), stream.reconnectDelay);
            stream.reconnectDelay = Math.min(
                stream.reconnectDelay * 2,
                stream.maxReconnectDelay
            );
        };

        ws.onerror = (err) => {
            console.error(`[WSManager] WebSocket error (${name}):`, err);
            ws.close();
        };
    }

    send(name, payload) {
        const stream = this.streams[name];
        if (!stream) {
            console.error(`[WSManager] Stream ${name} not initialized`);
            return;
        }

        // preserve caller API: payload in, stringify internally
        stream.queue.push(payload);
        this._flushQueue(name);
    }

    _flushQueue(name) {
        const stream = this.streams[name];
        if (!stream || !stream.ws) return;
        if (stream.ws.readyState !== WebSocket.OPEN) return;
        if (stream.state !== "idle") return;
        if (!stream.queue.length) return;

        const payload = stream.queue.shift();

        // ensure request_id exists
        const request_id = payload.request_id || this._randUUID()
        payload.request_id = request_id;

        stream.inflight = request_id;
        stream.state = "waiting";

        stream.ws.send(JSON.stringify(payload));
    }
}

export default WSManager;
