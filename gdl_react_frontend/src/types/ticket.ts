export interface Team {
  uuid: string;
  name: string;
  card_logo: string | false;
}

export interface TicketLeg {
  match_id: string;
  match_name: string;
  match_time: string;
  sport_id?: string;
  sport_name?: string;
  home_team: Team | null;
  away_team: Team | null;
  outcome: 'home' | 'away' | 'draw';
}

export interface OutcomeMeta {
  [matchId: string]: {
    outcome: 'home' | 'away' | 'draw';
    odds: number;
  };
}

export interface Ticket {
  type: 'ticket';
  uuid?: string; // Set by backend for QuickPicks
  lines: string[];
  muuids: string[];
  outcomes: ('home' | 'away' | 'draw')[];
  total_odds: number;
  total_returns: number;
  total_stake: number;
  status: 'C' | 'P' | 'M' | 'W' | 'L'; // Created, Pending, Mixed, Won, Lost
  depth: number;
  legs: TicketLeg[];
  outcome_meta: OutcomeMeta;
  old_uuid?: string; // For replacements
}

export interface CompleteMessage {
  type: 'complete';
  message?: string;
  trials?: number;
  failed?: number;
  ticket_count?: number; // QuickPicks only
  total_risk?: number; // QuickPicks only
  total_wins?: number; // QuickPicks only
  old_uuid?: string;
}

export interface EmptyMessage {
  type: 'empty';
  error?: string;
  incomplete?: boolean;
}

export interface ErrorMessage {
  type: 'error';
  error: string;
}

export interface PongMessage {
  type: 'pong';
  timestamp: string;
}

export type WebSocketMessage = 
  | Ticket 
  | CompleteMessage 
  | EmptyMessage 
  | ErrorMessage 
  | PongMessage;

export interface GenerateSettings {
  vhost: string;
  account: string;
  vdomain: string;
  stake: number;
  count: number;
  depth: number;
  min_payout: number;
  events_within?: number;
  [key: string]: any; // Allow dynamic sport_/group_ filters
}

export interface CartEntry {
  uuid: string;
  risk: number;
  returns: number;
  events: number;
}

export interface CartResponse {
  data: {
    tickets: CartEntry[];
    count: number;
  };
}
