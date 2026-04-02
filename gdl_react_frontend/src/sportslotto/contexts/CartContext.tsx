import React, { createContext, useContext, useState, ReactNode } from 'react';

interface CartContextType {
  cartCount: number;
  setCartCount: (count: number) => void;
  incrementCart: () => void;
  decrementCart: () => void;
  resetCart: () => void;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const [cartCount, setCartCount] = useState(0);

  const incrementCart = () => {
    setCartCount(prev => prev + 1);
  };

  const decrementCart = () => {
    setCartCount(prev => Math.max(0, prev - 1));
  };

  const resetCart = () => {
    setCartCount(0);
  };

  return (
    <CartContext.Provider
      value={{
        cartCount,
        setCartCount,
        incrementCart,
        decrementCart,
        resetCart,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within CartProvider');
  }
  return context;
}
