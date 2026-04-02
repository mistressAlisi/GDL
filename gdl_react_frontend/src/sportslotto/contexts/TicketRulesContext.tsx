import React, { createContext, useContext, useState, ReactNode } from 'react';

export type Sport = 'tennis' | 'us-sports' | 'soccer' | 'ncaa-basketball';

export type Timeframe = 48 | 42 | 36 | 30 | 24 | 18 | 12;

export interface TicketRules {
  selectedSports: Sport[];
  timeframe: Timeframe;
}

interface TicketRulesContextType {
  rules: TicketRules;
  updateSports: (sports: Sport[]) => void;
  updateTimeframe: (timeframe: Timeframe) => void;
  toggleSport: (sport: Sport) => void;
  isAllSportsSelected: () => boolean;
  toggleAllSports: () => void;
}

const TicketRulesContext = createContext<TicketRulesContextType | undefined>(undefined);

const ALL_SPORTS: Sport[] = ['tennis', 'us-sports', 'soccer', 'ncaa-basketball'];

export const TicketRulesProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [rules, setRules] = useState<TicketRules>({
    selectedSports: ALL_SPORTS, // All sports selected by default
    timeframe: 24, // Default to 24 hours
  });

  const updateSports = (sports: Sport[]) => {
    setRules(prev => ({ ...prev, selectedSports: sports }));
  };

  const updateTimeframe = (timeframe: Timeframe) => {
    setRules(prev => ({ ...prev, timeframe }));
  };

  const toggleSport = (sport: Sport) => {
    setRules(prev => {
      const isSelected = prev.selectedSports.includes(sport);
      const newSports = isSelected
        ? prev.selectedSports.filter(s => s !== sport)
        : [...prev.selectedSports, sport];
      
      // Ensure at least one sport is selected
      return {
        ...prev,
        selectedSports: newSports.length > 0 ? newSports : [sport]
      };
    });
  };

  const isAllSportsSelected = () => {
    return ALL_SPORTS.every(sport => rules.selectedSports.includes(sport));
  };

  const toggleAllSports = () => {
    if (isAllSportsSelected()) {
      // Don't allow deselecting all sports
      return;
    } else {
      updateSports(ALL_SPORTS);
    }
  };

  return (
    <TicketRulesContext.Provider
      value={{
        rules,
        updateSports,
        updateTimeframe,
        toggleSport,
        isAllSportsSelected,
        toggleAllSports,
      }}
    >
      {children}
    </TicketRulesContext.Provider>
  );
};

export const useTicketRules = () => {
  const context = useContext(TicketRulesContext);
  if (context === undefined) {
    throw new Error('useTicketRules must be used within a TicketRulesProvider');
  }
  return context;
};
