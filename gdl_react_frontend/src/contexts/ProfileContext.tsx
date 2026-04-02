import React, { createContext, useContext, useState, ReactNode } from 'react';

// Types for the profile system
export type PaymentMethod = 'credit-card' | 'cryptocurrency' | 'e-wallet';
export type TicketStatus = 'open' | 'graded';
export type BetOutcome = 'win' | 'loss' | 'pending';

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  pronouns?: string;
  phone?: string;
  email2?: string;
  profilePicture?: string;
  balance: number;
  activeBetsCount: number;
  totalWins: number;
  timezone: string;
  region: string;
  language: 'en' | 'es';
}

export interface Ticket {
  id: string;
  ticketNumber: string;
  lottery: string;
  state: string;
  pickType: number; // 2, 3, 4, or 5
  numbers: (number | string)[];
  betType: 'straight' | 'boxed';
  betAmount: number;
  bonusBets?: { betId: string; amount: number }[]; // Added bonus bets
  drawDate: Date;
  status: TicketStatus;
  outcome?: BetOutcome;
  winAmount?: number;
  createdAt: Date;
}

export interface Transaction {
  id: string;
  type: 'deposit' | 'withdrawal' | 'bet' | 'win';
  amount: number;
  paymentMethod?: PaymentMethod;
  status: 'completed' | 'pending' | 'failed';
  timestamp: Date;
  description: string;
}

export interface LossLimits {
  daily: number;
  weekly: number;
  monthly: number;
  isActive: boolean;
}

export interface SecuritySettings {
  lastPasswordChange: Date;
  loginNotifications: boolean;
}

interface ProfileContextType {
  // User data
  userProfile: UserProfile;
  updateUserProfile: (updates: Partial<UserProfile>) => void;
  
  // Tickets
  tickets: Ticket[];
  addTicket: (ticket: Ticket) => void;
  updateTicket: (id: string, updates: Partial<Ticket>) => void;
  getOpenTickets: () => Ticket[];
  getGradedTickets: () => Ticket[];
  
  // Transactions
  transactions: Transaction[];
  addTransaction: (transaction: Transaction) => void;
  
  // Settings
  lossLimits: LossLimits;
  updateLossLimits: (limits: Partial<LossLimits>) => void;
  securitySettings: SecuritySettings;
  updateSecuritySettings: (settings: Partial<SecuritySettings>) => void;
  
  // Account actions
  lockAccount: (duration: number) => void; // duration in days
  changePassword: (oldPassword: string, newPassword: string) => Promise<boolean>;
  
  // UI state
  profileDrawerOpen: boolean;
  setProfileDrawerOpen: (open: boolean) => void;
  currentProfilePage: string | null;
  setCurrentProfilePage: (page: string | null) => void;
}

const ProfileContext = createContext<ProfileContextType | undefined>(undefined);

export const useProfile = () => {
  const context = useContext(ProfileContext);
  if (!context) {
    throw new Error('useProfile must be used within ProfileProvider');
  }
  return context;
};

interface ProfileProviderProps {
  children: ReactNode;
}

export const ProfileProvider: React.FC<ProfileProviderProps> = ({ children }) => {
  // Initial mock data - replace with API calls in production
  const [userProfile, setUserProfile] = useState<UserProfile>({
    id: 'user_12345',
    username: 'Alex Johnson',
    email: 'alex.johnson@example.com',
    balance: 1250.75,
    activeBetsCount: 0,
    totalWins: 4285.50,
    timezone: 'America/New_York',
    region: 'NY',
    language: 'en',
  });

  const [tickets, setTickets] = useState<Ticket[]>([]);

  const [transactions, setTransactions] = useState<Transaction[]>([
    {
      id: 'txn_001',
      type: 'deposit',
      amount: 500,
      paymentMethod: 'credit-card',
      status: 'completed',
      timestamp: new Date(Date.now() - 86400000),
      description: 'Deposit via Credit Card',
    },
    {
      id: 'txn_002',
      type: 'win',
      amount: 125,
      status: 'completed',
      timestamp: new Date(Date.now() - 43200000),
      description: 'Pick 4 Win - TKT-2024-002',
    },
  ]);

  const [lossLimits, setLossLimits] = useState<LossLimits>({
    daily: 100,
    weekly: 500,
    monthly: 2000,
    isActive: true,
  });

  const [securitySettings, setSecuritySettings] = useState<SecuritySettings>({
    lastPasswordChange: new Date(Date.now() - 7776000000), // 90 days ago
    loginNotifications: true,
  });

  const [profileDrawerOpen, setProfileDrawerOpen] = useState(false);
  const [currentProfilePage, setCurrentProfilePage] = useState<string | null>(null);

  const updateUserProfile = (updates: Partial<UserProfile>) => {
    setUserProfile(prev => ({ ...prev, ...updates }));
    // TODO: API call to update user profile
  };

  const addTicket = (ticket: Ticket) => {
    setTickets(prev => [...prev, ticket]);
    // Update active bets count if ticket is open
    if (ticket.status === 'open') {
      setUserProfile(prev => ({ 
        ...prev, 
        activeBetsCount: prev.activeBetsCount + 1,
        balance: prev.balance - ticket.betAmount
      }));
    }
    // TODO: API call to add ticket
  };

  const updateTicket = (id: string, updates: Partial<Ticket>) => {
    setTickets(prev => prev.map(ticket => 
      ticket.id === id ? { ...ticket, ...updates } : ticket
    ));
    
    // Update stats if ticket is being graded
    if (updates.status === 'graded' && updates.outcome === 'win' && updates.winAmount) {
      setUserProfile(prev => ({
        ...prev,
        activeBetsCount: prev.activeBetsCount - 1,
        totalWins: prev.totalWins + updates.winAmount!,
        balance: prev.balance + updates.winAmount!,
      }));
    } else if (updates.status === 'graded') {
      setUserProfile(prev => ({
        ...prev,
        activeBetsCount: prev.activeBetsCount - 1,
      }));
    }
    // TODO: API call to update ticket
  };

  const getOpenTickets = () => {
    return tickets.filter(ticket => ticket.status === 'open');
  };

  const getGradedTickets = () => {
    return tickets.filter(ticket => ticket.status === 'graded');
  };

  const addTransaction = (transaction: Transaction) => {
    setTransactions(prev => [transaction, ...prev]);
    
    // Update balance based on transaction type
    if (transaction.type === 'deposit' && transaction.status === 'completed') {
      setUserProfile(prev => ({
        ...prev,
        balance: prev.balance + transaction.amount,
      }));
    } else if (transaction.type === 'withdrawal' && transaction.status === 'completed') {
      setUserProfile(prev => ({
        ...prev,
        balance: prev.balance - transaction.amount,
      }));
    }
    // TODO: API call to add transaction
  };

  const updateLossLimits = (limits: Partial<LossLimits>) => {
    setLossLimits(prev => ({ ...prev, ...limits }));
    // TODO: API call to update loss limits
  };

  const updateSecuritySettings = (settings: Partial<SecuritySettings>) => {
    setSecuritySettings(prev => ({ ...prev, ...settings }));
    // TODO: API call to update security settings
  };

  const lockAccount = (duration: number) => {
    console.log(`Account locked for ${duration} days`);
    // TODO: API call to lock account
    alert(`Account will be locked for ${duration} days. You will be logged out.`);
  };

  const changePassword = async (oldPassword: string, newPassword: string): Promise<boolean> => {
    // TODO: API call to change password
    console.log('Password change requested');
    setSecuritySettings(prev => ({
      ...prev,
      lastPasswordChange: new Date(),
    }));
    return true;
  };

  const value: ProfileContextType = {
    userProfile,
    updateUserProfile,
    tickets,
    addTicket,
    updateTicket,
    getOpenTickets,
    getGradedTickets,
    transactions,
    addTransaction,
    lossLimits,
    updateLossLimits,
    securitySettings,
    updateSecuritySettings,
    lockAccount,
    changePassword,
    profileDrawerOpen,
    setProfileDrawerOpen,
    currentProfilePage,
    setCurrentProfilePage,
  };

  return (
    <ProfileContext.Provider value={value}>
      {children}
    </ProfileContext.Provider>
  );
};