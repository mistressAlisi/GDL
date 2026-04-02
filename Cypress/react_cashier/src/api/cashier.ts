// Cashier API functions for deposits and withdrawals

import { apiPost, apiGet } from "./client";

// Request parameters
export interface DepositParams {
  provider: string; // e.g. "cashier.providers.ionBlock"
  amount: number;
  symbol?: string; // crypto symbol
  address?: string; // for some providers
  [key: string]: string | number | undefined; // additional provider-specific params
}

export interface WithdrawParams {
  provider: string;
  amount: number;
  password: string; // Required for withdrawals
  address?: string; // crypto address
  network?: string; // default "ETH"
  symbol?: string; // crypto symbol
}

// Response types
export interface CashierResponse {
  res: "ok" | "error";
  status?: "pending" | "external";
  avail_balance?: number;
  msg?: string;
  hdr?: string;
  title?: string;
  body_msg?: string;
  further_steps?: Array<{ type: string; data: unknown }>;
  // Error fields
  error_title?: string;
  error_body?: string;
}

export interface IonBlockStatusResponse {
  res?: "ok";
  error?: string;
  status: "pending" | "confirmed" | "expired" | "unknown";
  channel_status: number;
  txs: Array<unknown>;
  receiver_amount: string;
  sender_amount: string;
  sender_currency?: string;
  address?: string;
  valid_until?: string;
}

/**
 * Create a deposit transaction
 */
export async function createDeposit(
  params: DepositParams
): Promise<CashierResponse> {
  const data: Record<string, string> = {
    provider: params.provider,
    amount: String(params.amount),
  };

  // Add optional params
  if (params.symbol) data.symbol = params.symbol;
  if (params.address) data.address = params.address;

  // Add any additional provider-specific params
  for (const [key, value] of Object.entries(params)) {
    if (
      !["provider", "amount", "symbol", "address"].includes(key) &&
      value !== undefined
    ) {
      data[key] = String(value);
    }
  }

  return apiPost<CashierResponse>("/api/v1/deposit/validate", data);
}

/**
 * Create a withdrawal transaction
 */
export async function createWithdrawal(
  params: WithdrawParams
): Promise<CashierResponse> {
  const data: Record<string, string> = {
    provider: params.provider,
    amount: String(params.amount),
    acct_passwd: params.password,
  };

  // Add optional params
  if (params.address) data.address = params.address;
  if (params.network) data.network = params.network;
  if (params.symbol) data.symbol = params.symbol;

  return apiPost<CashierResponse>("/api/v1/withdraw/validate", data);
}

/**
 * Check ionBlock deposit status
 */
export async function checkIonBlockStatus(
  channelId: string
): Promise<IonBlockStatusResponse> {
  return apiGet<IonBlockStatusResponse>(
    `/api/v1/deposit/ionblock/status?channel_id=${encodeURIComponent(channelId)}`
  );
}
