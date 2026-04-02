import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/globals.css'
import App from './App.tsx'
import { loadBootstrap } from "./bootstrap"
import { BootstrapContext } from "./context/BootstrapContext"

async function start() {
  const bootstrap = await loadBootstrap()

  // ✅ bind Django → browser chrome
  if (bootstrap.domain?.name) {
    document.title = bootstrap.domain.name
  }

  createRoot(
    document.getElementById("root")!
  ).render(
    <StrictMode>
      <BootstrapContext.Provider value={bootstrap}>
        <App />
      </BootstrapContext.Provider>
    </StrictMode>
  )
}

start()
