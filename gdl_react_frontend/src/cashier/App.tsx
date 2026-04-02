import React, { useState } from "react";
import { Cashier, Transaction } from "./Cashier";
import { Balance, BalanceData } from "./Balance";
import SportsLottoApp from "../sportslotto/App";

type Page = 'balance' | 'cashier' | 'sportslotto';

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('balance');
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

  const handleError = (error: string) => {
    console.error('Cashier error:', error);
    // You could show a toast notification here instead of alert
  };

  const handleSuccess = (message: string) => {
    console.log('Cashier success:', message);
    // You could show a toast notification here instead of alert
  };

  // Page handlers
  const handleAddFunds = () => {
    setCurrentPage('cashier');
  };

  const handleWithdrawClick = () => {
    setCurrentPage('cashier');
  };

  const handleOpenTickets = () => {
    console.log('Open tickets clicked');
    // Navigate to tickets page when implemented
  };

  const handleGradedTickets = () => {
    console.log('Graded tickets clicked');
    // Navigate to graded tickets page when implemented
  };

  const handleCloseCashier = () => {
    setCurrentPage('balance');
  };

  const handleBalanceClick = () => {
    setCurrentPage('balance');
  };

  const handleSportsLottoClick = () => {
    setCurrentPage('sportslotto');
  };

  return (
    <>
      {currentPage === 'balance' && (
        <Balance
          balanceData={balanceData}
          onAddFunds={handleAddFunds}
          onWithdraw={handleWithdrawClick}
          onOpenTickets={handleOpenTickets}
          onGradedTickets={handleGradedTickets}
          onSportsLottoClick={handleSportsLottoClick}
        />
      )}
      
      {currentPage === 'cashier' && (
        <Cashier
          balance={balance}
          onDeposit={handleDeposit}
          onWithdraw={handleWithdraw}
          minWithdrawal={25}
          maxWithdrawal={10000}
          minDeposit={10}
          maxDeposit={10000}
          showBonusOffer={true}
          bonusAmount="$500"
          bonusPercentage={20}
          recentTransactions={transactions}
          onError={handleError}
          onSuccess={handleSuccess}
          onClose={handleCloseCashier}
          onBalanceClick={handleBalanceClick}
        />
      )}
      
      {currentPage === 'sportslotto' && (
        <SportsLottoApp />
      )}
    </>
  );
}