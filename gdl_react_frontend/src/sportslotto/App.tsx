import React, { useState, useEffect } from "react";
import { MainMenu } from "./components/MainMenu";
import { CustomTicketsForm } from "../components/sportslotto/CustomTicketsForm";
import { TicketBoard } from "../components/sportslotto/TicketBoard";
import { QuickPicksFormPage } from "../components/sportslotto/QuickPicksFormPage";
import { TicketsGrid } from "./components/TicketsGrid";
import { TicketDetailsPanel } from "./components/TicketDetailsPanel";
import { Sidebar } from "./components/Sidebar";
import { CartSidebar } from "./components/CartSidebar";
import { ThemeSettings } from "./components/ThemeSettings";
import { TicketRulesModal } from "./components/TicketRulesModal";
import { MessagesTable } from "../components/MessagesTable";
import { ProcessingModal } from "./components/ProcessingModal";
import { NoEventsModal } from "./components/NoEventsModal";
import { OpenTicketsTable } from "../components/OpenTicketsTable";
import { GradedTicketsTable } from "../components/GradedTicketsTable";
import { useTheme } from "./contexts/ThemeContext";
import { useAuth } from "./contexts/AuthContext";
import { CustomTicketFormData, DjangoTicketResponse } from "./services/ticket-websocket-adapter";
import { ticketWebSocket } from "../services/websocket-service";

export type Page = 'menu' | 'custom' | 'ticket-board' | 'quickpicks' | 'tickets' | 'theme-settings' | 'messages' | 'open-tickets' | 'graded-tickets';
export type Sport = 'tennis' | 'us-sports' | 'soccer' | 'ncaa-basketball';

export interface Ticket {
  id: string;
  type: 'pending' | 'win' | 'loss';
  amount: number;
  potential: number;
  events: Event[];
  sport: Sport;
  timestamp: Date;
  flipped: boolean;
}

export interface Event {
  id: string;
  homeTeam: string;
  awayTeam: string;
  league: string;
  date: string;
  pick?: string;
}

export interface SportsLottoAppProps {
  onBalanceClick?: () => void;
  onCashierClick?: () => void;
  onProfileClick?: () => void;
  onOpenTicketsClick?: () => void;
  onGradedTicketsClick?: () => void;
}

export default function App({ onBalanceClick, onCashierClick, onProfileClick, onOpenTicketsClick, onGradedTicketsClick }: SportsLottoAppProps = {}) {
  const { theme } = useTheme();
  const { logout, user } = useAuth();
  const [currentPage, setCurrentPage] = useState<Page>('menu');
  const [selectedSport, setSelectedSport] = useState<Sport | null>(null);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [djangoTickets, setDjangoTickets] = useState<DjangoTicketResponse[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [cartOpen, setCartOpen] = useState(false);
  const [showTicketRules, setShowTicketRules] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showNoEvents, setShowNoEvents] = useState(false);
  const [customTicketFormData, setCustomTicketFormData] = useState<CustomTicketFormData | null>(null);

  // Initialize WebSocket connection
  useEffect(() => {
    console.log('🔌 Initializing WebSocket connection...');
    ticketWebSocket.connect();
    return () => {
      console.log('🔌 Disconnecting WebSocket...');
      ticketWebSocket.disconnect();
    };
  }, []);

  // Django configuration (in production, get this from API)
  const djangoConfig = {
    vhost: '11fc00c3-53d1-4b08-ae4e-cf62e2985d0e',
    vdomain: '066d9fcb-4423-4697-808e-5b8ee09eab32',
    account: user?.id || '00000000-0000-0000-0000-000000000000', // Use logged-in user or fallback
    ruleset: {
      "1": {"losses": [0], "payouts": [100], "min_bet": 1.0, "max_bet": 500.0, "juice": 5},
      "2": {"losses": [0], "payouts": [100], "min_bet": 1.0, "max_bet": 500.0, "juice": 5},
      "3": {"losses": [0], "payouts": [100], "min_bet": 1.0, "max_bet": 500.0, "juice": 5},
      "4": {"losses": [0], "payouts": [100], "min_bet": 1.0, "max_bet": 500.0, "juice": 4},
      "5": {"losses": [0], "payouts": [100], "min_bet": 1.0, "max_bet": 500.0, "juice": 4},
      "6": {"losses": [1,0], "payouts": [90,100], "min_bet": 1.0, "max_bet": 500.0, "juice": 4},
      "7": {"losses": [1,0], "payouts": [90,100], "min_bet": 1.0, "max_bet": 500.0, "juice": 4},
    }
  };

  const handleSportSelect = (sport: Sport) => {
    setSelectedSport(sport);
    setCurrentPage('custom');
  };

  const handleCustomTicketsSelect = () => {
    setSelectedSport(null);
    setCurrentPage('custom');
  };

  const handleQuickPicksSelect = () => {
    setCurrentPage('quickpicks');
  };

  // NEW: Handle custom tickets form submission
  const handleCustomSubmit = (formData: CustomTicketFormData) => {
    console.log('📝 Custom form submitted:', formData);
    setCustomTicketFormData(formData);
    setCurrentPage('ticket-board');
  };

  // NEW: Handle adding Django ticket to cart
  const handleAddToCart = (ticket: DjangoTicketResponse) => {
    console.log('🛒 Adding ticket to cart:', ticket.uuid);
    setDjangoTickets(prev => [...prev, ticket]);
    // Don't auto-open cart - just increment the counter
  };

  // NEW: Handle back from ticket board to form
  const handleBackToCustomForm = () => {
    setCurrentPage('custom');
  };

  const handleTicketFlip = (ticketId: string) => {
    setTickets(prev => prev.map(ticket =>
      ticket.id === ticketId ? { ...ticket, flipped: !ticket.flipped } : ticket
    ));
  };

  const handleTicketSelect = (ticketId: string, action: 'accept' | 'reject') => {
    console.log(`Ticket ${ticketId} ${action}ed`);

    // Close the modal if it's open
    if (showDetails) {
      setShowDetails(false);
      setSelectedTicket(null);
    }

    // TODO: Add API call to accept/reject ticket
    // This is where you would call the Django API to update ticket status
  };

  const handleShowDetails = (ticket: Ticket) => {
    setSelectedTicket(ticket);
    setShowDetails(true);
  };

  const handleCloseDetails = () => {
    setShowDetails(false);
    setSelectedTicket(null);
  };

  const handleBackToMenu = () => {
    setCurrentPage('menu');
    setSelectedSport(null);
  };

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
        onGetTickets={handleBackToMenu}
        onOpenTickets={() => window.location.href = '/tickets/pending'}
        onGradedTickets={() => window.location.href = '/tickets/graded'}
        onBalance={onBalanceClick}
        onCashier={onCashierClick}
        onSettings={onProfileClick}
        onThemeSettings={() => setCurrentPage('theme-settings')}
        onTicketRules={() => setShowTicketRules(true)}
        onMessages={() => setCurrentPage('messages')}
        onLogout={() => logout()}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col relative z-10 w-full lg:w-auto">
        {/* Top Bar */}
        <div className="backdrop-blur-md bg-black/40 border-b border-white/10 py-3 px-6 lg:px-6 px-16">
          <div className="flex justify-end items-center gap-4">
            {onCashierClick && (
              <button
                onClick={onCashierClick}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 rounded-lg font-semibold transition-all shadow-lg shadow-green-500/30 text-sm lg:text-base"
              >
                💰 <span className="hidden sm:inline">Cashier</span>
              </button>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-4 lg:p-6 overflow-y-auto">
          {currentPage === 'menu' && (
            <MainMenu
              onSportSelect={handleSportSelect}
              onQuickPicksSelect={handleQuickPicksSelect}
              onCustomTicketsSelect={handleCustomTicketsSelect}
            />
          )}

          {currentPage === 'custom' && (
            <CustomTicketsForm
              vhost={djangoConfig.vhost}
              vdomain={djangoConfig.vdomain}
              account={djangoConfig.account}
              ruleset={djangoConfig.ruleset}
              onBack={handleBackToMenu}
              onSubmit={handleCustomSubmit}
            />
          )}

          {currentPage === 'ticket-board' && customTicketFormData && (
            <TicketBoard
              formData={customTicketFormData}
              onBack={handleBackToCustomForm}
              onAddToCart={handleAddToCart}
            />
          )}

          {currentPage === 'quickpicks' && (
            <QuickPicksFormPage
              vhost={djangoConfig.vhost}
              vdomain={djangoConfig.vdomain}
              ruleset={djangoConfig.ruleset}
              onBack={handleBackToMenu}
              onCartUpdated={(entries) => {
                console.log('🎫 QuickPick cart updated:', entries.length, 'entries');
                setCartOpen(true);
              }}
              onComplete={(summary) => {
                console.log('✅ QuickPick batch complete:', summary);
                setCurrentPage('menu');
              }}
              onError={(error) => {
                console.error('❌ QuickPick error:', error);
                setShowNoEvents(true);
              }}
            />
          )}

          {currentPage === 'tickets' && (
            <div className="space-y-6">
              <button
                onClick={handleBackToMenu}
                className="text-golden hover:text-yellow-300 transition-colors"
              >
                ← Back to Menu
              </button>
              <TicketsGrid
                tickets={tickets}
                onFlip={handleTicketFlip}
                onSelect={handleTicketSelect}
                onShowDetails={handleShowDetails}
              />
            </div>
          )}

          {currentPage === 'theme-settings' && (
            <ThemeSettings />
          )}

          {currentPage === 'messages' && (
            <MessagesTable />
          )}

          {currentPage === 'open-tickets' && (
            <OpenTicketsTable />
          )}

          {currentPage === 'graded-tickets' && (
            <GradedTicketsTable />
          )}
        </div>
      </div>

      {/* Ticket Details Panel */}
      {showDetails && selectedTicket && (
        <TicketDetailsPanel
          ticket={selectedTicket}
          onClose={handleCloseDetails}
          onAccept={() => handleTicketSelect(selectedTicket.id, 'accept')}
          onReject={() => handleTicketSelect(selectedTicket.id, 'reject')}
        />
      )}

      {/* Cart Sidebar */}
      <CartSidebar
        tickets={tickets}
        onRemoveTicket={(id) => setTickets(prev => prev.filter(t => t.id !== id))}
        onShowDetails={handleShowDetails}
        onCheckout={() => {
          console.log('💳 Checkout complete!');
          // Alert removed - handled by PurchaseModal success animation
        }}
        isOpen={cartOpen}
        onToggle={() => setCartOpen(!cartOpen)}
      />

      {/* Ticket Rules Modal */}
      <TicketRulesModal
        isOpen={showTicketRules}
        onClose={() => setShowTicketRules(false)}
      />

      {/* Processing Modal */}
      <ProcessingModal
        isOpen={isProcessing}
      />

      {/* No Events Modal */}
      <NoEventsModal
        isOpen={showNoEvents}
        onClose={() => setShowNoEvents(false)}
      />
    </div>
  );
}