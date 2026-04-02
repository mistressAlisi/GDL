export interface LotteryGame {
  id: number;
  name: string;
  state: string;
  stateAbbr: string;
  pickType: 2 | 3 | 4 | 5;
  drawTime: string;
  drawDays: string[];
  nextDraw: string;
  jackpot: number;
}

export interface BonusPack {
  id: string;
  name: string;
  description: string;
  cost: number;
  requiresUniqueNumbers?: boolean;
  requiresRepeats?: number;
  allowedPickTypes: number[];
}

export interface CartItem {
  id: string;
  lottery: LotteryGame;
  numbers: number[][];
  betType: string;
  betAmount: number;
  bonusBets?: { betId: string; amount: number }[];
  bonusPacks?: string[]; // Legacy support
  daysToRun: number;
  scheduleMode: string;
  totalCost: number;
  timestamp: number;
}

export const bonusPacks: BonusPack[] = [
  {
    id: "straight-3way",
    name: "Straight/3-Way Box",
    description: "Win with exact order OR any order (2 numbers can repeat)",
    cost: 330,
    requiresRepeats: 2,
    allowedPickTypes: [3, 4]
  },
  {
    id: "straight-6way",
    name: "Straight/6-Way Box",
    description: "Win with exact order OR any order (all unique numbers)",
    cost: 80,
    requiresUniqueNumbers: true,
    allowedPickTypes: [3, 4]
  },
  {
    id: "3way-box",
    name: "3-Way Box",
    description: "Win with any order (2 numbers can repeat)",
    cost: 165,
    requiresRepeats: 2,
    allowedPickTypes: [3, 4]
  },
  {
    id: "6way-box",
    name: "6-Way Box",
    description: "Win with any order (all unique numbers required)",
    cost: 40,
    requiresUniqueNumbers: true,
    allowedPickTypes: [3, 4]
  },
  {
    id: "back-pair",
    name: "Back Pair",
    description: "Match the last 2 digits in exact order",
    cost: 25,
    allowedPickTypes: [3, 4, 5]
  },
  {
    id: "front-pair",
    name: "Front Pair",
    description: "Match the first 2 digits in exact order",
    cost: 25,
    allowedPickTypes: [3, 4, 5]
  },
  {
    id: "first-digit",
    name: "First Digit",
    description: "Match the first digit only",
    cost: 10,
    allowedPickTypes: [2, 3, 4, 5]
  }
];

export const lotteryGames: LotteryGame[] = [
  // California
  { id: 1, name: "CA Daily 3 Midday", state: "California", stateAbbr: "CA", pickType: 3, drawTime: "12:30 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 12:30 PM", jackpot: 500 },
  { id: 2, name: "CA Daily 3 Evening", state: "California", stateAbbr: "CA", pickType: 3, drawTime: "6:30 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 6:30 PM", jackpot: 500 },
  { id: 3, name: "CA Daily 4", state: "California", stateAbbr: "CA", pickType: 4, drawTime: "6:30 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 6:30 PM", jackpot: 5000 },
  
  // New York
  { id: 4, name: "NY Numbers Midday", state: "New York", stateAbbr: "NY", pickType: 3, drawTime: "12:20 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 12:20 PM", jackpot: 500 },
  { id: 5, name: "NY Numbers Evening", state: "New York", stateAbbr: "NY", pickType: 3, drawTime: "10:30 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 10:30 PM", jackpot: 500 },
  { id: 6, name: "NY Win 4 Midday", state: "New York", stateAbbr: "NY", pickType: 4, drawTime: "12:20 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 12:20 PM", jackpot: 5000 },
  { id: 7, name: "NY Win 4 Evening", state: "New York", stateAbbr: "NY", pickType: 4, drawTime: "10:30 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 10:30 PM", jackpot: 5000 },
  
  // Texas
  { id: 8, name: "TX Daily 4 Day", state: "Texas", stateAbbr: "TX", pickType: 4, drawTime: "12:27 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 12:27 PM", jackpot: 5000 },
  { id: 9, name: "TX Daily 4 Evening", state: "Texas", stateAbbr: "TX", pickType: 4, drawTime: "6:27 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 6:27 PM", jackpot: 5000 },
  { id: 10, name: "TX Daily 4 Night", state: "Texas", stateAbbr: "TX", pickType: 4, drawTime: "10:12 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 10:12 PM", jackpot: 5000 },
  { id: 11, name: "TX Pick 3 Day", state: "Texas", stateAbbr: "TX", pickType: 3, drawTime: "12:27 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 12:27 PM", jackpot: 500 },
  { id: 12, name: "TX Pick 3 Evening", state: "Texas", stateAbbr: "TX", pickType: 3, drawTime: "6:27 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 6:27 PM", jackpot: 500 },
  { id: 13, name: "TX Pick 3 Night", state: "Texas", stateAbbr: "TX", pickType: 3, drawTime: "10:12 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 10:12 PM", jackpot: 500 },
  
  // Florida
  { id: 14, name: "FL Pick 2 Midday", state: "Florida", stateAbbr: "FL", pickType: 2, drawTime: "1:30 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 1:30 PM", jackpot: 50 },
  { id: 15, name: "FL Pick 2 Evening", state: "Florida", stateAbbr: "FL", pickType: 2, drawTime: "9:45 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 9:45 PM", jackpot: 50 },
  { id: 16, name: "FL Pick 3 Midday", state: "Florida", stateAbbr: "FL", pickType: 3, drawTime: "1:30 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 1:30 PM", jackpot: 500 },
  { id: 17, name: "FL Pick 3 Evening", state: "Florida", stateAbbr: "FL", pickType: 3, drawTime: "9:45 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 9:45 PM", jackpot: 500 },
  { id: 18, name: "FL Pick 4 Midday", state: "Florida", stateAbbr: "FL", pickType: 4, drawTime: "1:30 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 1:30 PM", jackpot: 5000 },
  { id: 19, name: "FL Pick 4 Evening", state: "Florida", stateAbbr: "FL", pickType: 4, drawTime: "9:45 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 9:45 PM", jackpot: 5000 },
  { id: 20, name: "FL Pick 5 Midday", state: "Florida", stateAbbr: "FL", pickType: 5, drawTime: "1:30 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 1:30 PM", jackpot: 50000 },
  
  // Illinois
  { id: 21, name: "IL Pick 3 Midday", state: "Illinois", stateAbbr: "IL", pickType: 3, drawTime: "12:40 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 12:40 PM", jackpot: 500 },
  { id: 22, name: "IL Pick 3 Evening", state: "Illinois", stateAbbr: "IL", pickType: 3, drawTime: "9:22 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 9:22 PM", jackpot: 500 },
  { id: 23, name: "IL Pick 4 Midday", state: "Illinois", stateAbbr: "IL", pickType: 4, drawTime: "12:40 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 12:40 PM", jackpot: 5000 },
  { id: 24, name: "IL Pick 4 Evening", state: "Illinois", stateAbbr: "IL", pickType: 4, drawTime: "9:22 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 9:22 PM", jackpot: 5000 },
  
  // Pennsylvania
  { id: 25, name: "PA Pick 2 Day", state: "Pennsylvania", stateAbbr: "PA", pickType: 2, drawTime: "1:35 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 1:35 PM", jackpot: 50 },
  { id: 26, name: "PA Pick 2 Evening", state: "Pennsylvania", stateAbbr: "PA", pickType: 2, drawTime: "6:59 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 6:59 PM", jackpot: 50 },
  { id: 27, name: "PA Pick 3 Day", state: "Pennsylvania", stateAbbr: "PA", pickType: 3, drawTime: "1:35 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 1:35 PM", jackpot: 500 },
  { id: 28, name: "PA Pick 3 Evening", state: "Pennsylvania", stateAbbr: "PA", pickType: 3, drawTime: "6:59 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 6:59 PM", jackpot: 500 },
  { id: 29, name: "PA Pick 4 Day", state: "Pennsylvania", stateAbbr: "PA", pickType: 4, drawTime: "1:35 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 1:35 PM", jackpot: 5000 },
  { id: 30, name: "PA Pick 4 Evening", state: "Pennsylvania", stateAbbr: "PA", pickType: 4, drawTime: "6:59 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 6:59 PM", jackpot: 5000 },
  { id: 31, name: "PA Pick 5 Day", state: "Pennsylvania", stateAbbr: "PA", pickType: 5, drawTime: "1:35 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Today 1:35 PM", jackpot: 50000 },
  
  // Ohio
  { id: 32, name: "OH Pick 3 Midday", state: "Ohio", stateAbbr: "OH", pickType: 3, drawTime: "12:29 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 12:29 PM", jackpot: 500 },
  { id: 33, name: "OH Pick 3 Evening", state: "Ohio", stateAbbr: "OH", pickType: 3, drawTime: "7:29 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 7:29 PM", jackpot: 500 },
  { id: 34, name: "OH Pick 4 Midday", state: "Ohio", stateAbbr: "OH", pickType: 4, drawTime: "12:29 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 12:29 PM", jackpot: 5000 },
  { id: 35, name: "OH Pick 4 Evening", state: "Ohio", stateAbbr: "OH", pickType: 4, drawTime: "7:29 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 7:29 PM", jackpot: 5000 },
  { id: 36, name: "OH Pick 5 Midday", state: "Ohio", stateAbbr: "OH", pickType: 5, drawTime: "12:29 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 12:29 PM", jackpot: 50000 },
  
  // Georgia
  { id: 37, name: "GA Cash 3 Midday", state: "Georgia", stateAbbr: "GA", pickType: 3, drawTime: "12:29 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 12:29 PM", jackpot: 500 },
  { id: 38, name: "GA Cash 3 Evening", state: "Georgia", stateAbbr: "GA", pickType: 3, drawTime: "6:59 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 6:59 PM", jackpot: 500 },
  { id: 39, name: "GA Cash 4 Midday", state: "Georgia", stateAbbr: "GA", pickType: 4, drawTime: "12:29 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 12:29 PM", jackpot: 5000 },
  { id: 40, name: "GA Cash 4 Evening", state: "Georgia", stateAbbr: "GA", pickType: 4, drawTime: "6:59 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 6:59 PM", jackpot: 5000 },
  
  // Michigan
  { id: 41, name: "MI Daily 3 Midday", state: "Michigan", stateAbbr: "MI", pickType: 3, drawTime: "12:59 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 12:59 PM", jackpot: 500 },
  { id: 42, name: "MI Daily 3 Evening", state: "Michigan", stateAbbr: "MI", pickType: 3, drawTime: "7:29 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 7:29 PM", jackpot: 500 },
  { id: 43, name: "MI Daily 4 Midday", state: "Michigan", stateAbbr: "MI", pickType: 4, drawTime: "12:59 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 12:59 PM", jackpot: 5000 },
  { id: 44, name: "MI Daily 4 Evening", state: "Michigan", stateAbbr: "MI", pickType: 4, drawTime: "7:29 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 7:29 PM", jackpot: 5000 },
  
  // North Carolina
  { id: 45, name: "NC Pick 3 Day", state: "North Carolina", stateAbbr: "NC", pickType: 3, drawTime: "3:00 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 3:00 PM", jackpot: 500 },
  { id: 46, name: "NC Pick 3 Evening", state: "North Carolina", stateAbbr: "NC", pickType: 3, drawTime: "11:22 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 11:22 PM", jackpot: 500 },
  { id: 47, name: "NC Pick 4 Day", state: "North Carolina", stateAbbr: "NC", pickType: 4, drawTime: "3:00 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 3:00 PM", jackpot: 5000 },
  { id: 48, name: "NC Pick 4 Evening", state: "North Carolina", stateAbbr: "NC", pickType: 4, drawTime: "11:22 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 11:22 PM", jackpot: 5000 },
  
  // New Jersey
  { id: 49, name: "NJ Pick 3 Midday", state: "New Jersey", stateAbbr: "NJ", pickType: 3, drawTime: "12:59 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 12:59 PM", jackpot: 500 },
  { id: 50, name: "NJ Pick 3 Evening", state: "New Jersey", stateAbbr: "NJ", pickType: 3, drawTime: "7:57 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 7:57 PM", jackpot: 500 },
  { id: 51, name: "NJ Pick 4 Midday", state: "New Jersey", stateAbbr: "NJ", pickType: 4, drawTime: "12:59 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 12:59 PM", jackpot: 5000 },
  { id: 52, name: "NJ Pick 4 Evening", state: "New Jersey", stateAbbr: "NJ", pickType: 4, drawTime: "7:57 PM", drawDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], nextDraw: "Tomorrow 7:57 PM", jackpot: 5000 },
];

export const getAvailableBonusPacks = (pickType: number, numbers: number[][]): BonusPack[] => {
  return bonusPacks.filter(pack => {
    if (!pack.allowedPickTypes.includes(pickType)) return false;
    
    // Check if numbers meet requirements
    const flatNumbers = numbers.flat();
    
    if (pack.requiresUniqueNumbers && !hasUniqueNumbers(flatNumbers)) {
      return false;
    }
    
    if (pack.requiresRepeats && !hasRepeatingNumbers(flatNumbers, pack.requiresRepeats)) {
      return false;
    }
    
    return true;
  });
};

// All US States + DC + Puerto Rico (52 total)
export interface StateInfo {
  abbr: string;
  name: string;
  lotteryCount: number;
}

export const allStates: StateInfo[] = [
  { abbr: "AL", name: "Alabama", lotteryCount: 0 },
  { abbr: "AK", name: "Alaska", lotteryCount: 0 },
  { abbr: "AZ", name: "Arizona", lotteryCount: 0 },
  { abbr: "AR", name: "Arkansas", lotteryCount: 0 },
  { abbr: "CA", name: "California", lotteryCount: 3 },
  { abbr: "CO", name: "Colorado", lotteryCount: 0 },
  { abbr: "CT", name: "Connecticut", lotteryCount: 0 },
  { abbr: "DE", name: "Delaware", lotteryCount: 0 },
  { abbr: "FL", name: "Florida", lotteryCount: 7 },
  { abbr: "GA", name: "Georgia", lotteryCount: 4 },
  { abbr: "HI", name: "Hawaii", lotteryCount: 0 },
  { abbr: "ID", name: "Idaho", lotteryCount: 0 },
  { abbr: "IL", name: "Illinois", lotteryCount: 4 },
  { abbr: "IN", name: "Indiana", lotteryCount: 0 },
  { abbr: "IA", name: "Iowa", lotteryCount: 0 },
  { abbr: "KS", name: "Kansas", lotteryCount: 0 },
  { abbr: "KY", name: "Kentucky", lotteryCount: 0 },
  { abbr: "LA", name: "Louisiana", lotteryCount: 0 },
  { abbr: "ME", name: "Maine", lotteryCount: 0 },
  { abbr: "MD", name: "Maryland", lotteryCount: 0 },
  { abbr: "MA", name: "Massachusetts", lotteryCount: 0 },
  { abbr: "MI", name: "Michigan", lotteryCount: 4 },
  { abbr: "MN", name: "Minnesota", lotteryCount: 0 },
  { abbr: "MS", name: "Mississippi", lotteryCount: 0 },
  { abbr: "MO", name: "Missouri", lotteryCount: 0 },
  { abbr: "MT", name: "Montana", lotteryCount: 0 },
  { abbr: "NE", name: "Nebraska", lotteryCount: 0 },
  { abbr: "NV", name: "Nevada", lotteryCount: 0 },
  { abbr: "NH", name: "New Hampshire", lotteryCount: 0 },
  { abbr: "NJ", name: "New Jersey", lotteryCount: 4 },
  { abbr: "NM", name: "New Mexico", lotteryCount: 0 },
  { abbr: "NY", name: "New York", lotteryCount: 4 },
  { abbr: "NC", name: "North Carolina", lotteryCount: 4 },
  { abbr: "ND", name: "North Dakota", lotteryCount: 0 },
  { abbr: "OH", name: "Ohio", lotteryCount: 5 },
  { abbr: "OK", name: "Oklahoma", lotteryCount: 0 },
  { abbr: "OR", name: "Oregon", lotteryCount: 0 },
  { abbr: "PA", name: "Pennsylvania", lotteryCount: 7 },
  { abbr: "PR", name: "Puerto Rico", lotteryCount: 0 },
  { abbr: "RI", name: "Rhode Island", lotteryCount: 0 },
  { abbr: "SC", name: "South Carolina", lotteryCount: 0 },
  { abbr: "SD", name: "South Dakota", lotteryCount: 0 },
  { abbr: "TN", name: "Tennessee", lotteryCount: 0 },
  { abbr: "TX", name: "Texas", lotteryCount: 6 },
  { abbr: "UT", name: "Utah", lotteryCount: 0 },
  { abbr: "VT", name: "Vermont", lotteryCount: 0 },
  { abbr: "VA", name: "Virginia", lotteryCount: 0 },
  { abbr: "WA", name: "Washington", lotteryCount: 0 },
  { abbr: "WV", name: "West Virginia", lotteryCount: 0 },
  { abbr: "WI", name: "Wisconsin", lotteryCount: 0 },
  { abbr: "WY", name: "Wyoming", lotteryCount: 0 },
  { abbr: "DC", name: "Washington DC", lotteryCount: 0 },
];

export const getStateCount = (stateAbbr: string): number => {
  return lotteryGames.filter(game => game.stateAbbr === stateAbbr).length;
};

export const getLotteriesByState = (stateAbbr: string): LotteryGame[] => {
  return lotteryGames.filter(game => game.stateAbbr === stateAbbr);
};

export const getUpcomingLotteries = (limit: number = 20): LotteryGame[] => {
  // Sort by next draw time (simplified - in production would parse actual times)
  return [...lotteryGames].slice(0, limit);
};

export const statesWithLotteries = Array.from(new Set(lotteryGames.map(g => g.stateAbbr))).sort();

export const hasUniqueNumbers = (numbers: number[]): boolean => {
  return new Set(numbers).size === numbers.length;
};

export const hasRepeatingNumbers = (numbers: number[], minRepeats: number): boolean => {
  const counts = numbers.reduce((acc, num) => {
    acc[num] = (acc[num] || 0) + 1;
    return acc;
  }, {} as Record<number, number>);
  
  return Object.values(counts).some(count => count >= minRepeats);
};