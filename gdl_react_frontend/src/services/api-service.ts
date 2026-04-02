/**
 * REST API Service for Django Backend
 * Handles HTTP requests for sports configuration, tables, and data
 */

import { API_CONFIG, buildUrl } from './api-config';

export interface SportConfig {
  id: string;
  name: string;
  icon: string;
  enabled: boolean;
  settings: {
    minOdds: number;
    maxOdds: number;
    defaultTimeframe: string;
    availableTimeframes: string[];
  };
}

export interface SportsConfigResponse {
  sports: SportConfig[];
  customTickets: {
    enabled: boolean;
    availableSports: string[];
    defaultSports: string[];
  };
}

export interface TicketRecord {
  id: string;
  userId?: string;
  userName?: string;
  wager: number;
  potentialPayout: number;
  totalOdds: number;
  entries: number;
  status: 'pending' | 'won' | 'lost' | 'void';
  createdAt: string;
  drawDate: string;
}

export interface LeaderboardEntry {
  rank: number;
  userId: string;
  userName: string;
  totalWins: number;
  totalWager: number;
  totalPayout: number;
  winRate: number;
}

class APIService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = buildUrl(endpoint);
    
    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };
    
    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }
  
  /**
   * Get sports configuration from backend
   * This determines which sports are available and their settings
   */
  async getSportsConfig(): Promise<SportsConfigResponse> {
    if (API_CONFIG.USE_MOCK_DATA) {
      return this.getMockSportsConfig();
    }
    
    return this.request<SportsConfigResponse>(
      API_CONFIG.ENDPOINTS.SPORTS_CONFIG
    );
  }
  
  /**
   * Get specific sport settings
   */
  async getSportSettings(sportId: string): Promise<SportConfig> {
    if (API_CONFIG.USE_MOCK_DATA) {
      const config = await this.getMockSportsConfig();
      const sport = config.sports.find(s => s.id === sportId);
      if (!sport) throw new Error(`Sport ${sportId} not found`);
      return sport;
    }
    
    return this.request<SportConfig>(
      API_CONFIG.ENDPOINTS.SPORT_SETTINGS,
      { params: { sportId } } as any
    );
  }
  
  /**
   * Get recent tickets
   */
  async getRecentTickets(limit: number = 20): Promise<TicketRecord[]> {
    if (API_CONFIG.USE_MOCK_DATA) {
      return this.getMockRecentTickets(limit);
    }
    
    return this.request<TicketRecord[]>(
      `${API_CONFIG.ENDPOINTS.RECENT_TICKETS}?limit=${limit}`
    );
  }
  
  /**
   * Get user's tickets
   */
  async getUserTickets(userId: string): Promise<TicketRecord[]> {
    if (API_CONFIG.USE_MOCK_DATA) {
      return this.getMockRecentTickets(10);
    }
    
    return this.request<TicketRecord[]>(
      `${API_CONFIG.ENDPOINTS.USER_TICKETS}?userId=${userId}`
    );
  }
  
  /**
   * Get leaderboard
   */
  async getLeaderboard(limit: number = 10): Promise<LeaderboardEntry[]> {
    if (API_CONFIG.USE_MOCK_DATA) {
      return this.getMockLeaderboard(limit);
    }
    
    return this.request<LeaderboardEntry[]>(
      `${API_CONFIG.ENDPOINTS.LEADERBOARD}?limit=${limit}`
    );
  }
  
  /**
   * Get statistics
   */
  async getStatistics(): Promise<any> {
    if (API_CONFIG.USE_MOCK_DATA) {
      return this.getMockStatistics();
    }
    
    return this.request<any>(API_CONFIG.ENDPOINTS.STATISTICS);
  }
  
  /**
   * Validate a ticket
   */
  async validateTicket(ticketData: any): Promise<{ valid: boolean; errors?: string[] }> {
    if (API_CONFIG.USE_MOCK_DATA) {
      return { valid: true };
    }
    
    return this.request<{ valid: boolean; errors?: string[] }>(
      API_CONFIG.ENDPOINTS.VALIDATE_TICKET,
      {
        method: 'POST',
        body: JSON.stringify(ticketData),
      }
    );
  }
  
  // ============ MOCK DATA METHODS ============
  
  private getMockSportsConfig(): SportsConfigResponse {
    return {
      sports: [
        {
          id: 'tennis',
          name: 'Tennis',
          icon: '🎾',
          enabled: true,
          settings: {
            minOdds: 1.5,
            maxOdds: 5.0,
            defaultTimeframe: '24h',
            availableTimeframes: ['12h', '18h', '24h', '30h', '36h', '42h', '48h'],
          },
        },
        {
          id: 'us-sports',
          name: 'US Sports',
          icon: '🏈',
          enabled: true,
          settings: {
            minOdds: 1.4,
            maxOdds: 4.5,
            defaultTimeframe: '24h',
            availableTimeframes: ['12h', '18h', '24h', '30h', '36h', '42h', '48h'],
          },
        },
        {
          id: 'soccer',
          name: 'Soccer',
          icon: '⚽',
          enabled: true,
          settings: {
            minOdds: 1.3,
            maxOdds: 6.0,
            defaultTimeframe: '24h',
            availableTimeframes: ['12h', '18h', '24h', '30h', '36h', '42h', '48h'],
          },
        },
        {
          id: 'ncaa-basketball',
          name: 'NCAA Basketball',
          icon: '🏀',
          enabled: true,
          settings: {
            minOdds: 1.5,
            maxOdds: 5.5,
            defaultTimeframe: '24h',
            availableTimeframes: ['12h', '18h', '24h', '30h', '36h', '42h', '48h'],
          },
        },
      ],
      customTickets: {
        enabled: true,
        availableSports: ['tennis', 'us-sports', 'soccer', 'ncaa-basketball'],
        defaultSports: ['tennis', 'us-sports', 'soccer', 'ncaa-basketball'],
      },
    };
  }
  
  private getMockRecentTickets(limit: number): TicketRecord[] {
    return Array.from({ length: limit }, (_, i) => ({
      id: `ticket_${Date.now()}_${i}`,
      userId: `user_${Math.floor(Math.random() * 1000)}`,
      userName: `Player${Math.floor(Math.random() * 1000)}`,
      wager: [5, 10, 20, 50, 100][Math.floor(Math.random() * 5)],
      potentialPayout: Math.round((Math.random() * 500 + 50) * 100) / 100,
      totalOdds: Math.round((Math.random() * 10 + 2) * 100) / 100,
      entries: Math.floor(Math.random() * 8) + 3,
      status: ['pending', 'won', 'lost'][Math.floor(Math.random() * 3)] as any,
      createdAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      drawDate: new Date(Date.now() + Math.random() * 48 * 60 * 60 * 1000).toISOString(),
    }));
  }
  
  private getMockLeaderboard(limit: number): LeaderboardEntry[] {
    return Array.from({ length: limit }, (_, i) => ({
      rank: i + 1,
      userId: `user_${i}`,
      userName: `Champion${i + 1}`,
      totalWins: Math.floor(Math.random() * 50) + 10,
      totalWager: Math.round((Math.random() * 5000 + 1000) * 100) / 100,
      totalPayout: Math.round((Math.random() * 10000 + 2000) * 100) / 100,
      winRate: Math.round((Math.random() * 40 + 20) * 100) / 100,
    }));
  }
  
  private getMockStatistics(): any {
    return {
      totalTickets: 15234,
      totalWagers: 523450.75,
      totalPayouts: 645320.50,
      activeUsers: 3421,
      biggestWin: 15000.00,
      averageOdds: 3.45,
      popularSport: 'Soccer',
    };
  }
}

// Singleton instance
export const apiService = new APIService();
