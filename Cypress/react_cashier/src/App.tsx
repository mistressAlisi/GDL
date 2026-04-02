import { useState, useEffect } from "react";
import { Cashier } from "./Cashier";
import type { Transaction } from "./Cashier";
import { loadBootstrap, reloadBootstrap } from "./bootstrap";
import type { BootstrapPayload, Provider } from "./bootstrap";
import { createDeposit, createWithdrawal } from "./api/cashier";
import type { CashierResponse } from "./api/cashier";

// Default empty providers for unauthenticated state
const EMPTY_PROVIDERS = { deposit: [] as Provider[], withdrawal: [] as Provider[] };

export default function App() {
  const [bootstrap, setBootstrap] = useState<BootstrapPayload | null>(null);
  const [balance, setBalance] = useState(0);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load bootstrap data on mount
  useEffect(() => {
    loadBootstrap()
      .then((data) => {
        setBootstrap(data);
        if (data.account) {
          setBalance(data.account.balance);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load bootstrap:", err);
        setError("Failed to load configuration");
        setLoading(false);
      });
  }, []);

  const handleDeposit = async (transaction: Transaction): Promise<void> => {
    // Call the deposit API
    const result: CashierResponse = await createDeposit({
      provider: transaction.paymentMethod, // This will be the module name from provider
      amount: transaction.amount,
    });

    if (result.res === "ok") {
      // Update balance if returned
      if (result.avail_balance !== undefined) {
        setBalance(result.avail_balance);
      }

      // Add transaction to history
      const completedTx: Transaction = {
        ...transaction,
        status: result.status === "pending" ? "pending" : "completed",
      };
      setTransactions((prev) => [completedTx, ...prev]);

      // Handle different response statuses
      if (result.status === "pending") {
        throw new Error(
          result.title || "Transaction pending - check your payment provider"
        );
      } else if (result.status === "external") {
        // Open external payment provider link
        if (result.body_msg) {
          const linkMatch = result.body_msg.match(/href='([^']+)'/);
          if (linkMatch) {
            window.open(linkMatch[1], "_blank");
          }
        }
        throw new Error(result.msg || "Please complete payment with provider");
      } else if (result.further_steps) {
        throw new Error(result.msg || "Additional steps required");
      }

      // Reload bootstrap to get fresh balance
      const freshData = await reloadBootstrap();
      if (freshData.account) {
        setBalance(freshData.account.balance);
      }
    } else {
      // Handle error response
      throw new Error(result.error_body || result.msg || "Deposit failed");
    }
  };

  const handleWithdraw = async (
    transaction: Transaction,
    password?: string
  ): Promise<void> => {
    if (!password) {
      throw new Error("Password is required for withdrawals");
    }

    // Call the withdrawal API
    const result: CashierResponse = await createWithdrawal({
      provider: transaction.paymentMethod, // This will be the module name from provider
      amount: transaction.amount,
      password: password,
    });

    if (result.res === "ok") {
      // Update balance if returned
      if (result.avail_balance !== undefined) {
        setBalance(result.avail_balance);
      }

      // Add transaction to history
      const pendingTx: Transaction = {
        ...transaction,
        status: "pending",
      };
      setTransactions((prev) => [pendingTx, ...prev]);

      // Handle different response statuses
      if (result.status === "external") {
        if (result.body_msg) {
          const linkMatch = result.body_msg.match(/href='([^']+)'/);
          if (linkMatch) {
            window.open(linkMatch[1], "_blank");
          }
        }
      }

      // Reload bootstrap to get fresh balance
      const freshData = await reloadBootstrap();
      if (freshData.account) {
        setBalance(freshData.account.balance);
      }
    } else {
      // Handle error response
      throw new Error(result.error_body || result.msg || "Withdrawal failed");
    }
  };

  const handleError = (errorMsg: string) => {
    console.error("Cashier error:", errorMsg);
    setError(errorMsg);
    // Clear error after 5 seconds
    setTimeout(() => setError(null), 5000);
  };

  const handleSuccess = (message: string) => {
    console.log("Cashier success:", message);
  };

  // Show loading state
  if (loading) {
    return (
      <div className="w-full h-screen bg-gradient-to-br from-purple-900 via-black to-orange-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  // Show login required if not authenticated
  if (!bootstrap?.session.authenticated) {
    return (
      <div className="w-full h-screen bg-gradient-to-br from-purple-900 via-black to-orange-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-white text-xl mb-4">Please log in to access the cashier</div>
          <a href="/login" className="px-6 py-3 bg-yellow-500 text-black font-bold rounded-lg">
            Go to Login
          </a>
        </div>
      </div>
    );
  }

  const providers = bootstrap.providers || EMPTY_PROVIDERS;

  return (
    <>
      {error && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg">
          {error}
        </div>
      )}
      <Cashier
        balance={balance}
        providers={providers}
        onDeposit={handleDeposit}
        onWithdraw={handleWithdraw}
        showBonusOffer={true}
        bonusAmount="$500"
        bonusPercentage={20}
        recentTransactions={transactions}
        onError={handleError}
        onSuccess={handleSuccess}
      />
    </>
  );
}
