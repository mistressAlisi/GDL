import React, { createContext, useContext, useState, ReactNode } from 'react';

export type ThemeType = 'default' | 'purple' | 'magenta' | 'cyan' | 'green' | 'orange';

export interface Theme {
  id: ThemeType;
  name: string;
  gradient: string;
  cardBorder: string;
  cardBg: string;
  cardGlow: string;
  accentColor: string;
  buttonGradient: string;
  // Background gradients (triads/quintets for harmony)
  backgroundGradient: string;
  // Glassmorphism elements
  glassOverlay: string;
  glassHighlight: string;
}

export const themes: Record<ThemeType, Theme> = {
  default: {
    id: 'default',
    name: 'Default (Purple)',
    gradient: 'linear-gradient(135deg, #6B46C1 0%, #9333EA 50%, #A855F7 100%)',
    cardBorder: 'rgba(168, 85, 247, 0.8)',
    cardBg: 'rgba(107, 70, 193, 0.2)',
    cardGlow: 'rgba(168, 85, 247, 0.6)',
    accentColor: '#A855F7',
    buttonGradient: 'linear-gradient(135deg, rgba(168, 85, 247, 0.8) 0%, rgba(236, 72, 153, 0.8) 50%, rgba(251, 146, 60, 0.8) 100%)',
    // Triad: Purple, Orange, Teal - creates vibrant harmony
    backgroundGradient: 'linear-gradient(135deg, #1e1b4b 0%, #4c1d95 20%, #581c87 40%, #7c2d12 60%, #ea580c 80%, #0f766e 100%)',
    glassOverlay: 'rgba(139, 92, 246, 0.05)',
    glassHighlight: 'rgba(168, 85, 247, 0.15)'
  },
  purple: {
    id: 'purple',
    name: 'Royal Purple',
    gradient: 'linear-gradient(135deg, #581C87 0%, #7C3AED 50%, #A78BFA 100%)',
    cardBorder: 'rgba(124, 58, 237, 0.8)',
    cardBg: 'rgba(88, 28, 135, 0.3)',
    cardGlow: 'rgba(124, 58, 237, 0.6)',
    accentColor: '#7C3AED',
    buttonGradient: 'linear-gradient(135deg, #7C3AED 0%, #A78BFA 100%)',
    // Quintet: Deep Purple, Violet, Indigo, Navy, Deep Blue
    backgroundGradient: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 20%, #4c1d95 40%, #581c87 60%, #3730a3 80%, #1e3a8a 100%)',
    glassOverlay: 'rgba(124, 58, 237, 0.05)',
    glassHighlight: 'rgba(167, 139, 250, 0.15)'
  },
  magenta: {
    id: 'magenta',
    name: 'Hot Magenta',
    gradient: 'linear-gradient(135deg, #BE185D 0%, #DB2777 50%, #F472B6 100%)',
    cardBorder: 'rgba(236, 72, 153, 0.8)',
    cardBg: 'rgba(190, 24, 93, 0.3)',
    cardGlow: 'rgba(236, 72, 153, 0.6)',
    accentColor: '#EC4899',
    buttonGradient: 'linear-gradient(135deg, #DB2777 0%, #F472B6 100%)',
    // Triad: Magenta, Deep Purple, Amber - passionate harmony
    backgroundGradient: 'linear-gradient(135deg, #500724 0%, #831843 20%, #be185d 40%, #4c1d95 60%, #6b21a8 80%, #92400e 100%)',
    glassOverlay: 'rgba(236, 72, 153, 0.05)',
    glassHighlight: 'rgba(244, 114, 182, 0.15)'
  },
  cyan: {
    id: 'cyan',
    name: 'Electric Cyan',
    gradient: 'linear-gradient(135deg, #0891B2 0%, #06B6D4 50%, #22D3EE 100%)',
    cardBorder: 'rgba(6, 182, 212, 0.8)',
    cardBg: 'rgba(8, 145, 178, 0.3)',
    cardGlow: 'rgba(6, 182, 212, 0.6)',
    accentColor: '#06B6D4',
    buttonGradient: 'linear-gradient(135deg, #0891B2 0%, #22D3EE 100%)',
    // Quintet: Deep Teal, Cyan, Sky Blue, Indigo, Navy - oceanic harmony
    backgroundGradient: 'linear-gradient(135deg, #164e63 0%, #155e75 20%, #0e7490 40%, #0891b2 60%, #0284c7 80%, #1e3a8a 100%)',
    glassOverlay: 'rgba(6, 182, 212, 0.05)',
    glassHighlight: 'rgba(34, 211, 238, 0.15)'
  },
  green: {
    id: 'green',
    name: 'Emerald Green',
    gradient: 'linear-gradient(135deg, #047857 0%, #10B981 50%, #34D399 100%)',
    cardBorder: 'rgba(16, 185, 129, 0.8)',
    cardBg: 'rgba(4, 120, 87, 0.3)',
    cardGlow: 'rgba(16, 185, 129, 0.6)',
    accentColor: '#10B981',
    buttonGradient: 'linear-gradient(135deg, #047857 0%, #34D399 100%)',
    // Triad: Emerald, Teal, Forest Green - natural harmony
    backgroundGradient: 'linear-gradient(135deg, #14532d 0%, #166534 20%, #047857 40%, #0f766e 60%, #115e59 80%, #1e3a8a 100%)',
    glassOverlay: 'rgba(16, 185, 129, 0.05)',
    glassHighlight: 'rgba(52, 211, 153, 0.15)'
  },
  orange: {
    id: 'orange',
    name: 'Golden Orange',
    gradient: 'linear-gradient(135deg, #C2410C 0%, #EA580C 50%, #FB923C 100%)',
    cardBorder: 'rgba(251, 146, 60, 0.8)',
    cardBg: 'rgba(194, 65, 12, 0.3)',
    cardGlow: 'rgba(251, 146, 60, 0.6)',
    accentColor: '#FB923C',
    buttonGradient: 'linear-gradient(135deg, #EA580C 0%, #FB923C 100%)',
    // Quintet: Deep Orange, Amber, Yellow, Brown, Red-Orange - sunset harmony
    backgroundGradient: 'linear-gradient(135deg, #7c2d12 0%, #9a3412 20%, #c2410c 40%, #d97706 60%, #92400e 80%, #991b1b 100%)',
    glassOverlay: 'rgba(251, 146, 60, 0.05)',
    glassHighlight: 'rgba(251, 191, 36, 0.15)'
  }
};

interface ThemeContextType {
  currentTheme: ThemeType;
  theme: Theme;
  setTheme: (theme: ThemeType) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [currentTheme, setCurrentTheme] = useState<ThemeType>('default');

  return (
    <ThemeContext.Provider
      value={{
        currentTheme,
        theme: themes[currentTheme],
        setTheme: setCurrentTheme
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}