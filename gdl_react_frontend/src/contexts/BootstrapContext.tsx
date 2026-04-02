import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface VHost {
  uuid: string;
  name: string;
}

interface Domain {
  uuid: string;
  fqdn: string;
  name: string;
  icon: string | null;
}

interface Account {
  uuid: string;
  acctname: string;
  acctnum: string;
  pronouns: string;
  balances: {
    latest_balance: string;
    latest_bonus: string;
    pending: string;
    available: string;
  };
  locale: string;
  timezone: string;
  message_count: number;
  avatar: string;
}

interface Manager {
  uuid: string;
  role: string;
}

interface BootstrapData {
  vhost: VHost;
  domain: Domain;
  features: Record<string, any>;
  appearance: {
    theme: string | null;
  };
  session: {
    authenticated: boolean;
    is_manager: boolean;
  };
  account?: Account;
  manager?: Manager;
}

interface BootstrapContextType {
  bootstrap: BootstrapData | null;
  loading: boolean;
  error: string | null;
  reload: () => Promise<void>;
}

const BootstrapContext = createContext<BootstrapContextType | undefined>(undefined);

// Mock bootstrap data for development when Django isn't available
const MOCK_BOOTSTRAP: BootstrapData = {
  vhost: {
    uuid: '00000000-0000-0000-0000-000000000001',
    name: 'Development VHost',
  },
  domain: {
    uuid: '00000000-0000-0000-0000-000000000002',
    fqdn: 'localhost',
    name: 'BETANY LOTTO',
    icon: null,
  },
  features: {},
  appearance: {
    theme: null,
  },
  session: {
    authenticated: true,
    is_manager: false,
  },
  account: {
    uuid: '00000000-0000-0000-0000-000000000003',
    acctname: 'demo_user',
    acctnum: '123456789',
    pronouns: 'they/them',
    balances: {
      latest_balance: '1000',
      latest_bonus: '0',
      pending: '0',
      available: '1000',
    },
    locale: 'en',
    timezone: 'America/New_York',
    message_count: 0,
    avatar: 'https://example.com/avatar.png',
  },
};

export function BootstrapProvider({ children }: { children: ReactNode }) {
  const [bootstrap, setBootstrap] = useState<BootstrapData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadBootstrap = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/v1/bootstrap', {
        credentials: 'include', // Send session cookies
        headers: {
          'Accept': 'application/json',
        },
      });

      // Check content type first (before reading body)
      const contentType = response.headers.get('content-type');
      const isJson = contentType && contentType.includes('application/json');

      // If not JSON or error, use mock data in development
      if (!response.ok || !isJson) {
        if (import.meta.env.DEV) {
          console.info('[Bootstrap] Using mock data (Django backend not connected)');
          setBootstrap(MOCK_BOOTSTRAP);
          return;
        }
        
        const text = await response.text();
        console.error('[Bootstrap] HTTP error:', response.status);
        console.error('[Bootstrap] Response:', text.substring(0, 200));
        throw new Error(`Bootstrap failed: ${response.status}`);
      }

      const data = await response.json();
      console.log('[Bootstrap] Loaded from Django:', data);
      setBootstrap(data);
    } catch (err) {
      // Network errors, parse errors, etc.
      if (import.meta.env.DEV) {
        console.info('[Bootstrap] Using mock data (Django backend not connected)');
        setBootstrap(MOCK_BOOTSTRAP);
      } else {
        const message = err instanceof Error ? err.message : 'Failed to load bootstrap';
        setError(message);
        console.error('[Bootstrap]', err);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBootstrap();
  }, []);

  return (
    <BootstrapContext.Provider
      value={{
        bootstrap,
        loading,
        error,
        reload: loadBootstrap,
      }}
    >
      {children}
    </BootstrapContext.Provider>
  );
}

export function useBootstrap() {
  const context = useContext(BootstrapContext);
  if (!context) {
    throw new Error('useBootstrap must be used within BootstrapProvider');
  }
  return context;
}