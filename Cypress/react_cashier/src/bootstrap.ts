// src/bootstrap.ts

export interface Provider {
  module: string // e.g. "cashier.providers.ionBlock"
  name: string // Display name
  min: number
  max: number
  fees: number
}

export interface BootstrapPayload {
  vhost: {
    uuid: string
    name: string
  }
  domain: {
    fqdn: string
    name: string
    icon: string | null
  }
  features: Record<string, unknown>
  appearance: {
    theme: unknown | null
  }
  session: {
    authenticated: boolean
    is_manager: boolean
  }
  account?: {
    uuid: string
    username: string
    balance: number
    locale: string | null
    timezone: string | null
  }
  providers?: {
    deposit: Provider[]
    withdrawal: Provider[]
  }
}

let cachedBootstrap: BootstrapPayload | null = null

export async function loadBootstrap(): Promise<BootstrapPayload> {
  if (cachedBootstrap) {
    return cachedBootstrap
  }

  const res = await fetch("/api/v1/bootstrap", {
    credentials: "include",
  })

  if (!res.ok) {
    throw new Error("Failed to load bootstrap")
  }

  const data = (await res.json()) as BootstrapPayload
  cachedBootstrap = data
  return data
}

/**
 * Clear the cached bootstrap data (call after transactions to refresh balance)
 */
export function clearBootstrapCache(): void {
  cachedBootstrap = null
}

/**
 * Force reload bootstrap data
 */
export async function reloadBootstrap(): Promise<BootstrapPayload> {
  clearBootstrapCache()
  return loadBootstrap()
}
