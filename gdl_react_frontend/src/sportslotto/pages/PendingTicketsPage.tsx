import React from 'react';
import { useNavigate } from 'react-router';
import { ArrowLeft } from 'lucide-react';
import { Sidebar } from '../components/Sidebar';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';

export function PendingTicketsPage() {
  const { theme } = useTheme();
  const { logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div
      className="flex min-h-screen text-white relative overflow-hidden"
      style={{ background: theme.backgroundGradient }}
    >
      {/* Glassmorphism overlay layers */}
      <div className="absolute inset-0 pointer-events-none">
        <div
          className="absolute inset-0 opacity-30"
          style={{ background: theme.glassOverlay }}
        />
        <div
          className="absolute inset-0 backdrop-blur-[100px] opacity-20"
          style={{ background: theme.glassHighlight }}
        />
      </div>

      {/* Animated particles */}
      <div className="absolute inset-0 opacity-20 pointer-events-none" style={{
        backgroundImage: `radial-gradient(2px 2px at 20% 30%, white, transparent),
                         radial-gradient(2px 2px at 60% 70%, ${theme.accentColor}, transparent),
                         radial-gradient(1px 1px at 50% 50%, white, transparent),
                         radial-gradient(1px 1px at 80% 10%, ${theme.accentColor}, transparent),
                         radial-gradient(2px 2px at 90% 60%, white, transparent),
                         radial-gradient(1px 1px at 33% 80%, ${theme.accentColor}, transparent)`,
        backgroundSize: '200% 200%',
        animation: 'particle-float 20s ease-in-out infinite'
      }}></div>

      {/* Sidebar */}
      <Sidebar
        onGetTickets={() => navigate('/')}
        onOpenTickets={() => navigate('/tickets/pending')}
        onGradedTickets={() => navigate('/tickets/graded')}
        onLogout={() => logout()}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col relative z-10 w-full lg:w-auto">
        {/* Top Bar */}
        <div className="backdrop-blur-md bg-black/40 border-b border-white/10 py-3 px-6 lg:px-6 px-16">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 text-golden hover:text-yellow-300 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span className="hidden sm:inline">Back to Sports Lotto</span>
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-4 lg:p-6 overflow-y-auto">
          <div className="max-w-6xl mx-auto">
            <div className="bg-white/5 backdrop-blur-md rounded-xl p-8 border border-white/10">
              <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                Pending Tickets
              </h1>
              <p className="text-lg opacity-80">Your pending tickets will appear here.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
