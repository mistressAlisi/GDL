import { createContext, useContext } from "react"
import type { BootstrapPayload } from "../bootstrap"

export const BootstrapContext = createContext<BootstrapPayload | null>(null)

export function useBootstrap() {
  const ctx = useContext(BootstrapContext)
  if (!ctx) {
    throw new Error("useBootstrap must be used inside BootstrapProvider")
  }
  return ctx
}
