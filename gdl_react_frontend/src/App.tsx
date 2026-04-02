import React, { useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { Balance, BalanceData } from "./components/Balance";
import SportsLottoApp from "./sportslotto/App";
import OpenTicketsPage from "./components/OpenTicketsPage";
import GradedTicketsPage from "./components/GradedTicketsPage";
import ProfileSettingsPage from "./components/ProfileSettingsPage";
import { ThemeProvider } from "./sportslotto/contexts/ThemeContext";
import { AuthProvider, useAuth } from "./sportslotto/contexts/AuthContext";
import { CartProvider } from "./sportslotto/contexts/CartContext";
import { TicketRulesProvider } from "./sportslotto/contexts/TicketRulesContext";
import { BootstrapProvider } from "./contexts/BootstrapContext";
import { Cashier, Transaction } from "./components/Cashier";
import { OpenTicketsTable } from "./components/OpenTicketsTable";
import { GradedTicketsTable } from "./components/GradedTicketsTable";
import { LoginPage } from "./components/auth/LoginPage";
import { RegisterPage } from "./components/auth/RegisterPage";
import { RecoveryPage } from "./components/auth/RecoveryPage";

type Page = 'balance' | 'cashier' | 'sportslotto' | 'openTickets' | 'gradedTickets' | 'profile';
type AuthPage = 'login' | 'register' | 'recovery';

function AppContent() {
  const { isAuthenticated, isLoading } = useAuth();
  const [currentPage, setCurrentPage] = useState<Page>('sportslotto');
  const [authPage, setAuthPage] = useState<AuthPage>('login');
  const [balance, setBalance] = useState(142.75);
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  // Balance data for the balance page
  const balanceData: BalanceData = {
    availableBalance: 22.00,
    freePlay: 25.00,
    currentBalance: 41.00,
    pendingBalance: 19.00,
    pendingRollover: 121.00
  };

  const handleDeposit = (transaction: Transaction) => {
    // Update balance
    setBalance(prev => prev + transaction.amount);

    // Add transaction to history
    setTransactions(prev => [transaction, ...prev]);

    console.log('Deposit processed:', transaction);
  };

  const handleWithdraw = (transaction: Transaction) => {
    // Update balance (subtract for withdrawals)
    setBalance(prev => prev - transaction.amount);

    // Add transaction to history
    setTransactions(prev => [transaction, ...prev]);

    console.log('Withdrawal processed:', transaction);
  };

  // Page handlers
  const handleAddFunds = () => {
    setCurrentPage('cashier');
  };

  const handleWithdrawClick = () => {
    setCurrentPage('cashier');
  };

  const handleOpenTickets = () => {
    setCurrentPage('openTickets');
  };

  const handleGradedTickets = () => {
    setCurrentPage('gradedTickets');
  };

  const handleCloseCashier = () => {
    setCurrentPage('sportslotto');
  };

  const handleBalanceClick = () => {
    setCurrentPage('balance');
  };

  const handleSportsLottoClick = () => {
    setCurrentPage('sportslotto');
  };

  const handleSportsLottoBalance = () => {
    setCurrentPage('balance');
  };

  const handleSportsLottoCashier = () => {
    setCurrentPage('cashier');
  };

  const handleSportsLottoProfile = () => {
    setCurrentPage('profile');
  };

  const handleSportsLottoOpenTickets = () => {
    setCurrentPage('openTickets');
  };

  const handleSportsLottoGradedTickets = () => {
    setCurrentPage('gradedTickets');
  };

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-black">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  // Show auth pages if not authenticated
  if (!isAuthenticated) {
    if (authPage === 'login') {
      return (
        <LoginPage
          onNavigateToRegister={() => setAuthPage('register')}
          onNavigateToRecovery={() => setAuthPage('recovery')}
        />
      );
    }

    if (authPage === 'register') {
      return (
        <RegisterPage
          onNavigateToLogin={() => setAuthPage('login')}
        />
      );
    }

    if (authPage === 'recovery') {
      return (
        <RecoveryPage
          onNavigateToLogin={() => setAuthPage('login')}
        />
      );
    }
  }

  // Show main app if authenticated
  return (
    <TicketRulesProvider>
      {currentPage === 'balance' && (
        <Balance
          balanceData={balanceData}
          onAddFunds={handleAddFunds}
          onWithdraw={handleWithdrawClick}
          onOpenTickets={handleOpenTickets}
          onGradedTickets={handleGradedTickets}
          onBackToMenu={handleSportsLottoClick}
        />
      )}

      {currentPage === 'cashier' && (
        <Cashier
          balance={balance}
          onDeposit={handleDeposit}
          onWithdraw={handleWithdraw}
          onBalanceClick={handleBalanceClick}
          onBackToMenu={handleSportsLottoClick}
          recentTransactions={transactions}
        />
      )}

      {currentPage === 'sportslotto' && (
        <SportsLottoApp
          onBalanceClick={handleSportsLottoBalance}
          onCashierClick={handleSportsLottoCashier}
          onProfileClick={handleSportsLottoProfile}
          onOpenTicketsClick={handleSportsLottoOpenTickets}
          onGradedTicketsClick={handleSportsLottoGradedTickets}
        />
      )}

      {currentPage === 'openTickets' && (
        <OpenTicketsPage
          onBack={handleSportsLottoClick}
        />
      )}

      {currentPage === 'gradedTickets' && (
        <GradedTicketsPage
          onBack={handleSportsLottoClick}
        />
      )}

      {currentPage === 'profile' && (
        <ProfileSettingsPage
          onBack={handleSportsLottoClick}
        />
      )}
    </TicketRulesProvider>
  );
}

export default function App() {
  return (
    <BootstrapProvider>
      <AuthProvider>
        <ThemeProvider>
          <CartProvider>
            <AppContent />
          </CartProvider>
        </ThemeProvider>
      </AuthProvider>
    </BootstrapProvider>
  );
}