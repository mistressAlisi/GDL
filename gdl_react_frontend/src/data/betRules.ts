// Bet Rules and Payout Structure for BETANY LOTTO

export interface BetOption {
  id: string;
  name: string;
  description: string;
  trueOdds: string;
  payout: number; // Payout for $1 bet
  minBet: number; // Minimum bet amount
  pickTypes: (2 | 3 | 4 | 5)[]; // Which pick types this bet is available for
  isCombo?: boolean; // Whether this is a combo bet
  comboCost?: number; // Fixed cost for combo bets
  comboIncludes?: string[]; // Which bet types are included in the combo
}

// Standard Bet Types
export const standardBets: BetOption[] = [
  // ==================== PICK 2 BETS ====================
  {
    id: 'pick2-straight',
    name: 'Pick 2',
    description: 'Match both numbers in exact order',
    trueOdds: '100/1',
    payout: 85,
    minBet: 1,
    pickTypes: [2]
  },
  {
    id: 'pick2-first-ball',
    name: 'First Ball',
    description: 'Match the first number drawn',
    trueOdds: '10/1',
    payout: 8,
    minBet: 1,
    pickTypes: [2]
  },
  {
    id: 'pick2-second-ball',
    name: 'Second Ball',
    description: 'Match the second number drawn',
    trueOdds: '10/1',
    payout: 8,
    minBet: 1,
    pickTypes: [2]
  },
  
  // ==================== PICK 3 BETS ====================
  {
    id: 'pick3-straight',
    name: 'Pick 3',
    description: 'Match all 3 numbers in exact order',
    trueOdds: '1000/1',
    payout: 850,
    minBet: 1,
    pickTypes: [3]
  },
  {
    id: 'pick3-first-two',
    name: 'First Two',
    description: 'Match the first two numbers in exact order',
    trueOdds: '100/1',
    payout: 85,
    minBet: 1,
    pickTypes: [3]
  },
  {
    id: 'pick3-last-two',
    name: 'Last Two',
    description: 'Match the last two numbers in exact order',
    trueOdds: '100/1',
    payout: 85,
    minBet: 1,
    pickTypes: [3]
  },
  {
    id: 'pick3-first-ball',
    name: 'First Ball',
    description: 'Match the first number drawn',
    trueOdds: '10/1',
    payout: 8,
    minBet: 1,
    pickTypes: [3]
  },
  {
    id: 'pick3-second-ball',
    name: 'Second Ball',
    description: 'Match the second number drawn',
    trueOdds: '10/1',
    payout: 8,
    minBet: 1,
    pickTypes: [3]
  },
  {
    id: 'pick3-third-ball',
    name: 'Third Ball',
    description: 'Match the third number drawn',
    trueOdds: '10/1',
    payout: 8,
    minBet: 1,
    pickTypes: [3]
  },
  
  // ==================== PICK 4 BETS ====================
  {
    id: 'pick4-straight',
    name: 'Pick 4',
    description: 'Match all 4 numbers in exact order',
    trueOdds: '10000/1',
    payout: 8500,
    minBet: 1,
    pickTypes: [4]
  },
  {
    id: 'pick4-first-two',
    name: 'First Two',
    description: 'Match the first two numbers in exact order',
    trueOdds: '100/1',
    payout: 85,
    minBet: 1,
    pickTypes: [4]
  },
  {
    id: 'pick4-last-two',
    name: 'Last Two',
    description: 'Match the last two numbers in exact order',
    trueOdds: '100/1',
    payout: 85,
    minBet: 1,
    pickTypes: [4]
  },
  {
    id: 'pick4-first-ball',
    name: 'First Ball',
    description: 'Match the first number drawn',
    trueOdds: '10/1',
    payout: 8,
    minBet: 1,
    pickTypes: [4]
  },
  {
    id: 'pick4-second-ball',
    name: 'Second Ball',
    description: 'Match the second number drawn',
    trueOdds: '10/1',
    payout: 8,
    minBet: 1,
    pickTypes: [4]
  },
  {
    id: 'pick4-third-ball',
    name: 'Third Ball',
    description: 'Match the third number drawn',
    trueOdds: '10/1',
    payout: 8,
    minBet: 1,
    pickTypes: [4]
  },
  
  // ==================== PICK 5 BETS ====================
  {
    id: 'pick5-straight',
    name: 'Pick 5',
    description: 'Match all 5 numbers in exact order',
    trueOdds: '100000/1',
    payout: 85000,
    minBet: 1,
    pickTypes: [5]
  },
  {
    id: 'pick5-first-two',
    name: 'First Two',
    description: 'Match the first two numbers in exact order',
    trueOdds: '100/1',
    payout: 85,
    minBet: 1,
    pickTypes: [5]
  },
  {
    id: 'pick5-last-two',
    name: 'Last Two',
    description: 'Match the last two numbers in exact order',
    trueOdds: '100/1',
    payout: 85,
    minBet: 1,
    pickTypes: [5]
  },
  {
    id: 'pick5-middle-three',
    name: 'Middle Three',
    description: 'Match the middle three numbers in exact order',
    trueOdds: '1000/1',
    payout: 850,
    minBet: 1,
    pickTypes: [5]
  },
  {
    id: 'pick5-first-ball',
    name: 'First Ball',
    description: 'Match the first number drawn',
    trueOdds: '10/1',
    payout: 8,
    minBet: 1,
    pickTypes: [5]
  },
  {
    id: 'pick5-second-ball',
    name: 'Second Ball',
    description: 'Match the second number drawn',
    trueOdds: '10/1',
    payout: 8,
    minBet: 1,
    pickTypes: [5]
  },
  {
    id: 'pick5-third-ball',
    name: 'Third Ball',
    description: 'Match the third number drawn',
    trueOdds: '10/1',
    payout: 8,
    minBet: 1,
    pickTypes: [5]
  },
  {
    id: 'pick5-fourth-ball',
    name: 'Fourth Ball',
    description: 'Match the fourth number drawn',
    trueOdds: '10/1',
    payout: 8,
    minBet: 1,
    pickTypes: [5]
  },
  {
    id: 'pick5-fifth-ball',
    name: 'Fifth Ball',
    description: 'Match the fifth number drawn',
    trueOdds: '10/1',
    payout: 8,
    minBet: 1,
    pickTypes: [5]
  }
];

// Combo Bets
export const comboBets: BetOption[] = [
  {
    id: 'pick2-combo',
    name: 'P2 Combo',
    description: 'Includes Pick 2, 1st Ball, and 2nd Ball',
    trueOdds: 'Combo',
    payout: 0, // Calculated based on individual bets
    minBet: 3,
    comboCost: 3,
    isCombo: true,
    comboIncludes: ['pick2-straight', 'pick2-first-ball', 'pick2-second-ball'],
    pickTypes: [2]
  },
  {
    id: 'pick3-combo',
    name: 'P3 Combo',
    description: 'Includes Pick 3, First 2, Last 2, and First Ball',
    trueOdds: 'Combo',
    payout: 0, // Calculated based on individual bets
    minBet: 4,
    comboCost: 4,
    isCombo: true,
    comboIncludes: ['pick3-straight', 'pick3-first-two', 'pick3-last-two', 'pick3-first-ball'],
    pickTypes: [3]
  },
  {
    id: 'pick4-combo',
    name: 'P4 Combo',
    description: 'Includes Pick 4, First 2, Last 2, and First Ball',
    trueOdds: 'Combo',
    payout: 0, // Calculated based on individual bets
    minBet: 4,
    comboCost: 4,
    isCombo: true,
    comboIncludes: ['pick4-straight', 'pick4-first-two', 'pick4-last-two', 'pick4-first-ball'],
    pickTypes: [4]
  },
  {
    id: 'pick5-combo',
    name: 'P5 Combo',
    description: 'Includes Pick 5, First 2, Last 2, Middle 3, and First Ball',
    trueOdds: 'Combo',
    payout: 0, // Calculated based on individual bets
    minBet: 5,
    comboCost: 5,
    isCombo: true,
    comboIncludes: ['pick5-straight', 'pick5-first-two', 'pick5-last-two', 'pick5-middle-three', 'pick5-first-ball'],
    pickTypes: [5]
  }
];

// Helper function to get all bet options for a specific pick type
export function getBetOptionsForPickType(pickType: 2 | 3 | 4 | 5): BetOption[] {
  const standard = standardBets.filter(bet => bet.pickTypes.includes(pickType));
  const combo = comboBets.filter(bet => bet.pickTypes.includes(pickType));
  return [...standard, ...combo];
}

// Helper function to get standard bets only (excluding combos)
export function getStandardBetsForPickType(pickType: 2 | 3 | 4 | 5): BetOption[] {
  return standardBets.filter(bet => bet.pickTypes.includes(pickType));
}

// Helper function to get combo bets only
export function getComboBetsForPickType(pickType: 2 | 3 | 4 | 5): BetOption[] {
  return comboBets.filter(bet => bet.pickTypes.includes(pickType));
}

// Helper function to calculate potential winnings
export function calculatePotentialWinnings(betOption: BetOption, betAmount: number): number {
  if (betOption.isCombo) {
    // For combo bets, calculate based on included bets
    let totalWinnings = 0;
    betOption.comboIncludes?.forEach(includedBetId => {
      const includedBet = standardBets.find(b => b.id === includedBetId);
      if (includedBet) {
        totalWinnings += includedBet.payout * 1; // Each combo bet is $1 per component
      }
    });
    return totalWinnings;
  }
  return betOption.payout * betAmount;
}

// Helper function to get bet display name
export function getBetDisplayName(betOption: BetOption): string {
  return betOption.name;
}

// Helper function to group bets by category
export function groupBetsByCategory(pickType: 2 | 3 | 4 | 5) {
  const allBets = getBetOptionsForPickType(pickType);
  
  return {
    straight: allBets.filter(b => b.id.includes('-straight')),
    positional: allBets.filter(b => 
      (b.id.includes('-first-two') || b.id.includes('-last-two') || 
       b.id.includes('-middle-three'))
    ),
    singleBall: allBets.filter(b => b.id.includes('-ball')),
    combo: allBets.filter(b => b.isCombo)
  };
}
