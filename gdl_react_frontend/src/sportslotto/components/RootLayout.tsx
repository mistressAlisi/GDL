import React from 'react';
import { Outlet } from 'react-router';
import { ThemeProvider } from '../contexts/ThemeContext';
import { AuthProvider } from '../contexts/AuthContext';
import { CartProvider } from '../contexts/CartContext';

export function RootLayout() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <CartProvider>
          <Outlet />
        </CartProvider>
      </ThemeProvider>
    </AuthProvider>
  );
}