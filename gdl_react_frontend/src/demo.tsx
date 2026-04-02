/**
 * Standalone Demo Page for WebSocket Ticket Generation
 * 
 * This page demonstrates the ticket generation system independently
 * from the main app. Access at /demo route.
 */

import React from 'react';
import { ThemeProvider } from './sportslotto/contexts/ThemeContext';
import { BootstrapProvider } from './contexts/BootstrapContext';
import { TicketGeneratorDemo } from './components/TicketGeneratorDemo';

export default function DemoPage() {
  return (
    <ThemeProvider>
      <BootstrapProvider>
        <TicketGeneratorDemo />
      </BootstrapProvider>
    </ThemeProvider>
  );
}
