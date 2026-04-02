import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { ticketWebSocket } from '../../services/websocket-service';
import { csrfPost } from '../utils/csrf';
import { logSessionStatus, waitForSession } from '../utils/session-checker';
import { useBootstrap } from '../../contexts/BootstrapContext';

interface User {
  id: string;
  username: string;
  email?: string;
  balance?: number;
  pending?: number;
  bonus?: number;
  available?: number;
  avatar?: string;
  acctnum?: string;
  acctname?: string;  // Full account name from bootstrap
  message_count?: number;  // Unread message count
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  register: (username: string, email: string, password: string) => Promise<void>;
  updateBalances: (balances: { balance?: number; pending?: number; bonus?: number; available?: number }) => void;
  handleSessionExpired: () => void;  // Add session expiration handler
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Helper to construct full avatar URL if Django returns relative path
function getFullAvatarUrl(avatar: string | undefined): string | undefined {
  if (!avatar) return undefined;

  // If avatar is already a full URL (starts with http/https), return as-is
  if (avatar.startsWith('http://') || avatar.startsWith('https://')) {
    return avatar;
  }

  // If it's a relative path, prepend the origin
  if (avatar.startsWith('/')) {
    return window.location.origin + avatar;
  }

  // Otherwise assume it needs /media/ prefix (Django default)
  return window.location.origin + '/media/' + avatar;
}

// Helper to check if a string is a UUID
function isUUID(str: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

// Helper to format account number for display
function formatAccountNumber(acctnum: string | undefined, uuid: string): string {
  // If no acctnum provided, use last 8 chars of UUID
  if (!acctnum) {
    return uuid.slice(-8).toUpperCase();
  }

  // If acctnum is a UUID (same as user ID), format it nicely
  if (isUUID(acctnum)) {
    return uuid.slice(-8).toUpperCase();
  }

  // Otherwise return the acctnum as-is
  return acctnum;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { bootstrap } = useBootstrap();

  // Load user from bootstrap data when it becomes available
  useEffect(() => {
    if (bootstrap && bootstrap.session.authenticated && bootstrap.account) {
      console.log('📦 Loading user from bootstrap data:', bootstrap.account);

      const account = bootstrap.account;

      // Use acctname if available, otherwise fall back to acctnum
      const displayName = account.acctname && account.acctname !== ""
        ? account.acctname
        : account.acctnum;

      const user: User = {
        id: account.uuid,
        username: displayName,
        email: '', // Not provided in bootstrap
        balance: parseFloat(account.balances.latest_balance),
        pending: parseFloat(account.balances.pending),
        bonus: parseFloat(account.balances.latest_bonus),
        available: parseFloat(account.balances.available),
        avatar: getFullAvatarUrl(account.avatar),
        acctnum: account.acctnum,
        acctname: account.acctname,
        message_count: account.message_count || 0,
      };

      console.log('✅ User loaded from bootstrap:', {
        id: user.id,
        username: user.username,
        acctnum: user.acctnum,
        acctname: user.acctname,
        balance: user.balance,
        bonus: user.bonus,
        pending: user.pending,
        available: user.available,
        avatar: user.avatar,  // Include avatar in log
        message_count: user.message_count,
      });

      setUser(user);
      localStorage.setItem('sportslotto_user', JSON.stringify(user));

      // Initialize WebSocket connection for authenticated user
      ticketWebSocket.connect();
      setIsLoading(false);
    } else if (bootstrap && !bootstrap.session.authenticated) {
      // Bootstrap loaded but user is not authenticated
      console.log('📦 Bootstrap loaded: User not authenticated');
      setIsLoading(false);
    }
  }, [bootstrap]);

  // Check for existing session on mount (fallback to localStorage if bootstrap fails)
  useEffect(() => {
    const checkSession = async () => {
      const storedUser = localStorage.getItem('sportslotto_user');
      if (storedUser && !user) { // Only use stored user if bootstrap hasn't loaded user yet
        try {
          const userData = JSON.parse(storedUser);
          setUser(userData);
          // Initialize WebSocket connection for authenticated user
          ticketWebSocket.connect();
        } catch (error) {
          console.error('Failed to parse stored user:', error);
          localStorage.removeItem('sportslotto_user');
        }
      }
      // No auto-guest login - user must authenticate
      if (!bootstrap) {
        setIsLoading(false);
      }
    };

    checkSession();
  }, [bootstrap, user]);

  const login = async (username: string, password: string) => {
    try {
      console.log('🔐 Attempting login for:', username);

      const res = await csrfPost('/api/v1/account/login', {
        username,
        password
      });

      console.log('📥 Login response:', res);

      if (res.res === "err") {
        throw new Error(res.err || 'Login failed. Please check your credentials.');
      }

      // Use acctname if available, otherwise fall back to acctnum
      let displayName = res.data["acctname"] && res.data["acctname"] !== ""
        ? res.data["acctname"]
        : res.data["acctnum"];

      const user: User = {
        id: res.data["uuid"],
        username: displayName,
        email: res.data["email"],
        balance: res.data["balances"]["latest_balance"] * 1,
        pending: res.data["balances"]["pending"] * 1,
        bonus: res.data["balances"]["latest_bonus"] * 1,
        available: res.data["balances"]["available"] * 1,
        avatar: getFullAvatarUrl(res.data["avatar"]),
        acctnum: res.data["acctnum"],  // Direct assignment
        acctname: res.data["acctname"],  // Store full account name
        message_count: res.data["message_count"] || 0,  // Message count for notifications
      };

      console.log('✅ User logged in:', {
        id: user.id,
        username: user.username,
        acctnum: user.acctnum
      });

      // Check if session was set
      const sessionCookie = document.cookie.split(';').find(c => c.trim().startsWith('sessionid='));
      console.log('🍪 Session cookie after login:', sessionCookie ? 'EXISTS' : 'MISSING');

      setUser(user);
      localStorage.setItem('sportslotto_user', JSON.stringify(user));

      // Initialize WebSocket connection AFTER successful login
      // ticketWebSocket.connect();
    } catch (error) {
      console.error('❌ Login failed:', error);
      throw new Error('Login failed. Please check your credentials.');
    }
  };

  const register = async (username: string, email: string, password: string) => {
    try {
      const res = await csrfPost('/api/v1/account/register/', {
        username,
        email,
        password
      });

      if (res.res === "err") {
        throw new Error('Registration failed. Please try again.');
      }

      // Use acctname if available, otherwise fall back to acctnum
      let displayName = res.data["acctname"] && res.data["acctname"] !== ""
        ? res.data["acctname"]
        : res.data["acctnum"];

      const user: User = {
        id: res.data["uuid"],
        username: displayName,
        email: res.data["email"],
        balance: res.data["balances"]["latest_balance"] * 1,
        pending: res.data["balances"]["pending"] * 1,
        bonus: res.data["balances"]["latest_bonus"] * 1,
        available: res.data["balances"]["available"] * 1,
        avatar: getFullAvatarUrl(res.data["avatar"]),
        acctnum: res.data["acctnum"],  // Direct assignment
        acctname: res.data["acctname"],  // Store full account name
        message_count: res.data["message_count"] || 0,  // Message count for notifications
      };

      setUser(user);
      localStorage.setItem('sportslotto_user', JSON.stringify(user));

      // Initialize WebSocket connection AFTER successful registration
      // ticketWebSocket.connect();
    } catch (error) {
      console.error('Registration failed:', error);
      throw new Error('Registration failed. Please try again.');
    }
  };

  const logout = () => {
    // Clear user session completely
    setUser(null);
    localStorage.removeItem('sportslotto_user');

    // Disconnect WebSocket
    ticketWebSocket.disconnect();
  };

  const updateBalances = (balances: { balance?: number; pending?: number; bonus?: number; available?: number }) => {
    if (user) {
      setUser({
        ...user,
        balance: balances.balance !== undefined ? balances.balance : user.balance,
        pending: balances.pending !== undefined ? balances.pending : user.pending,
        bonus: balances.bonus !== undefined ? balances.bonus : user.bonus,
        available: balances.available !== undefined ? balances.available : user.available,
      });
    }
  };

  const handleSessionExpired = () => {
    // Handle session expiration by logging out the user
    logout();
    // Optionally, redirect to login page or show a message
    // window.location.href = '/login';
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        register,
        updateBalances,
        handleSessionExpired,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}