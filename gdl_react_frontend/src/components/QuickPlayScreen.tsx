import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, ChevronLeft, ChevronRight, ChevronDown, ChevronUp, Star, Trash2, ShoppingCart, Sparkles, Check, Calendar, Edit2 } from 'lucide-react';
import { LotteryGame, lotteryGames } from '../data/lotteryData';
import { useCart } from '../contexts/CartContext';
import { getBetOptionsForPickType, calculatePotentialWinnings } from '../data/betRules';
import { useProfile } from '../contexts/ProfileContext';
import { useTranslation, getMonthNames, getDayNames } from '../utils/translations';
import { ProfileDrawer } from './profile/ProfileDrawer';

interface QuickPlayScreenProps {
  onClose: () => void;
  onOpenCart: () => void;
  onOpenProfile: () => void;
}

interface QuickPlaySelection {
  lottery: LotteryGame;
  numbers: number[][];
  betType: 'straight' | 'box';
  betAmount: number;
  selectedBonusBets: { betId: string; amount: number }[];
  scheduleMode: 'daysToRun' | 'selectDates';
  daysToRunStartDate: Date | null;
  daysToRun: number;
  selectedDates: Date[];
}

interface FavoriteNumbers {
  lotteryId: number;
  numbers: number[][];
  name: string;
}

interface FavoriteLottery {
  lottery: LotteryGame;
}

interface CartTicket {
  id: string;
  lottery: LotteryGame;
  numbers: number[][];
  betType: 'straight' | 'box';
  betAmount: number;
  bonusBets: { betId: string; amount: number }[];
  drawDate: Date;
  daysToRun: number;
  totalCost: number;
}

export const QuickPlayScreen: React.FC<QuickPlayScreenProps> = ({ onClose, onOpenCart, onOpenProfile }) => {
  const { addToCart, getCartCount, clearCart } = useCart();
  const { userProfile, profileDrawerOpen, setProfileDrawerOpen, addTicket } = useProfile();
  const t = useTranslation(userProfile.language);
  
  // Detect mobile
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  
  React.useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  // States
  const [hasFavorites, setHasFavorites] = useState(false);
  const [expandedStates, setExpandedStates] = useState<Set<string>>(new Set());
  const [selectedLotteries, setSelectedLotteries] = useState<LotteryGame[]>([]);
  const [currentLotteryIndex, setCurrentLotteryIndex] = useState(0);
  const [selections, setSelections] = useState<QuickPlaySelection[]>([]);
  const [addMode, setAddMode] = useState<'current' | 'all'>('current');
  
  // Track pending amounts for bonus bets (typed but not yet added)
  const [pendingBonusBetAmounts, setPendingBonusBetAmounts] = useState<{ [betId: string]: string }>({});
  
  const [favoriteNumbers, setFavoriteNumbers] = useState<FavoriteNumbers[]>([]);
  const [favoriteLotteries, setFavoriteLotteries] = useState<FavoriteLottery[]>([]);
  const [showFavoritesModal, setShowFavoritesModal] = useState(false);
  const [showChangeSelection, setShowChangeSelection] = useState(false);

  // Ref for lottery buttons to scroll into view
  const lotteryButtonRefs = React.useRef<{ [key: number]: HTMLButtonElement | null }>({});

  // Quick Buy states
  const [showQuickBuyModal, setShowQuickBuyModal] = useState(false);
  const [hasSavedPayment, setHasSavedPayment] = useState(true); // Simulate saved payment
  const [purchaseSuccess, setPurchaseSuccess] = useState(false);

  // Calendar state
  const [currentMonth, setCurrentMonth] = useState(new Date());

  // Scroll current lottery into view when index changes
  React.useEffect(() => {
    if (lotteryButtonRefs.current[currentLotteryIndex]) {
      lotteryButtonRefs.current[currentLotteryIndex]?.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest'
      });
    }
  }, [currentLotteryIndex]);

  // Group lotteries by state
  const lotteryByState = lotteryGames.reduce((acc, lottery) => {
    if (!acc[lottery.stateAbbr]) {
      acc[lottery.stateAbbr] = [];
    }
    acc[lottery.stateAbbr].push(lottery);
    return acc;
  }, {} as Record<string, LotteryGame[]>);

  const states = Object.keys(lotteryByState).sort();

  const toggleState = (stateAbbr: string) => {
    const newExpanded = new Set(expandedStates);
    if (newExpanded.has(stateAbbr)) {
      newExpanded.delete(stateAbbr);
    } else {
      newExpanded.add(stateAbbr);
    }
    setExpandedStates(newExpanded);
  };

  const toggleLotterySelection = (lottery: LotteryGame) => {
    const isSelected = selectedLotteries.some(l => l.id === lottery.id);
    if (isSelected) {
      setSelectedLotteries(selectedLotteries.filter(l => l.id !== lottery.id));
      setSelections(selections.filter(s => s.lottery.id !== lottery.id));
    } else {
      setSelectedLotteries([...selectedLotteries, lottery]);
      setSelections([...selections, {
        lottery,
        numbers: Array(lottery.pickType).fill(null).map(() => []),
        betType: 'straight',
        betAmount: 1,
        selectedBonusBets: [],
        scheduleMode: 'daysToRun',
        daysToRunStartDate: new Date(),
        daysToRun: 7,
        selectedDates: []
      }]);
    }
  };

  const currentSelection = selections[currentLotteryIndex];
  const currentLottery = selectedLotteries[currentLotteryIndex];

  const updateCurrentNumbers = (rowIndex: number, number: number) => {
    if (!currentSelection) return;
    
    const newNumbers = [...currentSelection.numbers];
    const row = [...newNumbers[rowIndex]];
    
    if (row.includes(number)) {
      newNumbers[rowIndex] = row.filter(n => n !== number);
    } else {
      if (row.length < 10) {
        newNumbers[rowIndex] = [...row, number];
      }
    }
    
    const newSelections = [...selections];
    newSelections[currentLotteryIndex] = {
      ...currentSelection,
      numbers: newNumbers
    };
    setSelections(newSelections);
  };

  const generateLuckyNumbers = () => {
    if (!currentLottery || !currentSelection) return;
    
    const newNumbers = Array(currentLottery.pickType).fill(null).map(() => {
      const count = Math.floor(Math.random() * 2) + 2; // 2-3 numbers (less aggressive for mobile)
      const luckyNums: number[] = [];
      while (luckyNums.length < count) {
        const num = Math.floor(Math.random() * 10);
        if (!luckyNums.includes(num)) {
          luckyNums.push(num);
        }
      }
      return luckyNums.sort((a, b) => a - b);
    });
    
    const newSelections = [...selections];
    newSelections[currentLotteryIndex] = {
      ...currentSelection,
      numbers: newNumbers
    };
    setSelections(newSelections);
  };

  const addToFavoriteNumbers = () => {
    if (!currentLottery || !currentSelection) return;
    
    const favorite: FavoriteNumbers = {
      lotteryId: currentLottery.id,
      numbers: currentSelection.numbers,
      name: `${currentLottery.name} - ${currentSelection.numbers.map(row => row.join('')).join('-')}`
    };
    
    setFavoriteNumbers([...favoriteNumbers, favorite]);
  };

  const loadFavoriteNumbers = (favorite: FavoriteNumbers) => {
    if (!currentSelection) return;
    
    const newSelections = [...selections];
    newSelections[currentLotteryIndex] = {
      ...currentSelection,
      numbers: favorite.numbers
    };
    setSelections(newSelections);
    setShowFavoritesModal(false);
  };

  const addToFavoriteLotteries = () => {
    if (selectedLotteries.length === 0) return;
    
    // Add each selected lottery individually
    const newFavorites = selectedLotteries
      .filter(lottery => !favoriteLotteries.some(fav => fav.lottery.id === lottery.id))
      .map(lottery => ({ lottery }));
    
    setFavoriteLotteries([...favoriteLotteries, ...newFavorites]);
  };

  const loadFavoriteLottery = (favorite: FavoriteLottery) => {
    // Check if lottery is already selected
    if (!selectedLotteries.some(l => l.id === favorite.lottery.id)) {
      toggleLotterySelection(favorite.lottery);
    }
  };

  const updateCurrentBetAmount = (amount: number) => {
    if (!currentSelection) return;
    const newSelections = [...selections];
    newSelections[currentLotteryIndex] = {
      ...currentSelection,
      betAmount: amount
    };
    setSelections(newSelections);
  };

  const addCurrentBonusBet = (betId: string, minAmount: number) => {
    if (!currentSelection) return;
    const amount = pendingBonusBetAmounts[betId]
      ? Math.max(minAmount, parseInt(pendingBonusBetAmounts[betId]) || minAmount)
      : minAmount;
    
    const newSelections = [...selections];
    newSelections[currentLotteryIndex] = {
      ...currentSelection,
      selectedBonusBets: [...currentSelection.selectedBonusBets, { betId, amount }]
    };
    setSelections(newSelections);
    
    // Clear pending amount
    setPendingBonusBetAmounts(prev => {
      const newPending = { ...prev };
      delete newPending[betId];
      return newPending;
    });
  };

  const removeCurrentBonusBet = (betId: string) => {
    if (!currentSelection) return;
    const newSelections = [...selections];
    newSelections[currentLotteryIndex] = {
      ...currentSelection,
      selectedBonusBets: currentSelection.selectedBonusBets.filter(b => b.betId !== betId)
    };
    setSelections(newSelections);
    
    // Clear pending amount
    setPendingBonusBetAmounts(prev => {
      const newPending = { ...prev };
      delete newPending[betId];
      return newPending;
    });
  };

  const handlePendingBonusBetAmountChange = (betId: string, value: string) => {
    setPendingBonusBetAmounts(prev => ({
      ...prev,
      [betId]: value
    }));
  };

  const updateCurrentBonusBetAmount = (betId: string, value: string, minAmount: number) => {
    if (!currentSelection) return;
    
    if (value === '') {
      const newSelections = [...selections];
      newSelections[currentLotteryIndex] = {
        ...currentSelection,
        selectedBonusBets: currentSelection.selectedBonusBets.map(bet =>
          bet.betId === betId ? { ...bet, amount: minAmount } : bet
        )
      };
      setSelections(newSelections);
      return;
    }
    
    const numValue = parseInt(value);
    if (!isNaN(numValue)) {
      const newSelections = [...selections];
      newSelections[currentLotteryIndex] = {
        ...currentSelection,
        selectedBonusBets: currentSelection.selectedBonusBets.map(bet =>
          bet.betId === betId ? { ...bet, amount: Math.max(minAmount, numValue) } : bet
        )
      };
      setSelections(newSelections);
    }
  };

  // Generate all combinations from a selection
  const generateCombinations = (numbers: number[][]): number[][] => {
    if (numbers.length === 0 || numbers.some(row => row.length === 0)) {
      return [];
    }
    
    const result: number[][] = [[]];
    
    for (const row of numbers) {
      const temp: number[][] = [];
      for (const combo of result) {
        for (const num of row) {
          temp.push([...combo, num]);
        }
      }
      result.length = 0;
      result.push(...temp);
    }
    
    return result;
  };

  // Get draw dates based on mode
  const getDrawDates = (): Date[] => {
    if (!currentSelection) return [];
    
    if (currentSelection.scheduleMode === 'daysToRun') {
      if (!currentSelection.daysToRunStartDate) return [];
      const dates: Date[] = [];
      for (let i = 0; i < currentSelection.daysToRun; i++) {
        const date = new Date(currentSelection.daysToRunStartDate);
        date.setDate(currentSelection.daysToRunStartDate.getDate() + i);
        dates.push(date);
      }
      return dates;
    } else {
      return currentSelection.selectedDates;
    }
  };

  const addCurrentToCart = () => {
    if (!currentSelection || !currentLottery) {
      console.log('Cannot add to cart: no selection or lottery');
      return;
    }
    
    const combinations = generateCombinations(currentSelection.numbers);
    if (combinations.length === 0) {
      console.log('Cannot add to cart: no valid combinations');
      return;
    }
    
    const drawDates = getDrawDates();
    if (drawDates.length === 0) {
      console.log('Cannot add to cart: no draw dates');
      return;
    }
    
    console.log('Adding to cart:', { 
      lottery: currentLottery.name,
      combinations: combinations.length, 
      drawDates: drawDates.length,
      totalItems: combinations.length * drawDates.length
    });
    
    combinations.forEach(combo => {
      drawDates.forEach(date => {
        const baseCost = currentSelection.betAmount;
        const bonusCost = currentSelection.selectedBonusBets.reduce((total, bet) => {
          const betOption = getBetOptionsForPickType(currentLottery.pickType as 2 | 3 | 4 | 5).find(b => b.id === bet.betId);
          if (betOption?.isCombo) {
            return total + (betOption.comboCost || 0);
          }
          return total + bet.amount;
        }, 0);
        
        // Convert combo to 2D array format for CartPanel compatibility
        const numbers2D = combo.map(num => [num]);
        
        addToCart({
          id: `qp-${Date.now()}-${Math.random()}`,
          lottery: currentLottery,
          numbers: numbers2D,
          betType: currentSelection.betType,
          betAmount: currentSelection.betAmount,
          bonusBets: currentSelection.selectedBonusBets,
          drawDate: date,
          daysToRun: 1,
          totalCost: baseCost + bonusCost
        });
      });
    });
    
    console.log('Successfully added items to cart');
  };

  const addAllToCart = () => {
    selections.forEach((sel, index) => {
      const combinations = generateCombinations(sel.numbers);
      if (combinations.length === 0) return;
      
      const drawDates = getSelectionDrawDates(sel);
      if (drawDates.length === 0) return;
      
      combinations.forEach(combo => {
        drawDates.forEach(date => {
          const baseCost = sel.betAmount;
          const bonusCost = sel.selectedBonusBets.reduce((total, bet) => {
            const betOption = getBetOptionsForPickType(sel.lottery.pickType as 2 | 3 | 4 | 5).find(b => b.id === bet.betId);
            if (betOption?.isCombo) {
              return total + (betOption.comboCost || 0);
            }
            return total + bet.amount;
          }, 0);
          
          // Convert combo to 2D array format for CartPanel compatibility
          const numbers2D = combo.map(num => [num]);
          
          addToCart({
            id: `qp-all-${Date.now()}-${Math.random()}`,
            lottery: sel.lottery,
            numbers: numbers2D,
            betType: sel.betType,
            betAmount: sel.betAmount,
            bonusBets: sel.selectedBonusBets,
            drawDate: date,
            daysToRun: 1,
            totalCost: baseCost + bonusCost
          });
        });
      });
    });
  };

  const handleAddToCart = () => {
    console.log('handleAddToCart called, mode:', addMode);
    if (addMode === 'current') {
      addCurrentToCart();
    } else {
      addAllToCart();
    }
    
    // Reset everything after adding to cart
    console.log('Resetting QuickPlay board');
    setSelections([]);
    setSelectedLotteries([]);
    setCurrentLotteryIndex(0);
    setAddMode('current');
    
    // Open cart after adding items
    console.log('Opening cart panel');
    onOpenCart();
  };

  const handleQuickBuy = () => {
    console.log('handleQuickBuy called, mode:', addMode);
    
    // Show confirmation modal directly (payment not required for current version)
    setShowQuickBuyModal(true);
  };

  const confirmQuickBuy = () => {
    console.log('Confirming quick buy, mode:', addMode);
    console.log('Current selection:', currentSelection);
    console.log('All selections:', selections);
    
    // Process purchase (in real app, this would call payment API)
    setShowQuickBuyModal(false);
    setPurchaseSuccess(true);
    
    // Save tickets to ProfileContext
    const selectionsToProcess = addMode === 'current' && currentSelection 
      ? [currentSelection] 
      : selections;

    console.log('Selections to process:', selectionsToProcess);

    selectionsToProcess.forEach((selection) => {
      const drawDates = selection.scheduleMode === 'selectDates' 
        ? selection.selectedDates 
        : Array.from({ length: selection.daysToRun }, (_, i) => {
            const date = new Date(selection.daysToRunStartDate || new Date());
            date.setDate(date.getDate() + i);
            return date;
          });

      console.log('Draw dates:', drawDates);

      // Generate all combinations from the selected numbers
      const combinations = generateCombinations(selection.numbers);
      console.log('Generated combinations:', combinations);

      // Create a ticket for each combination and draw date
      combinations.forEach((combination) => {
        drawDates.forEach((drawDate) => {
          const ticketId = `ticket_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
          const ticket = {
            id: ticketId,
            ticketNumber: `QP-${ticketId.slice(-8).toUpperCase()}`,
            lottery: selection.lottery.name,
            state: selection.lottery.stateAbbr,
            pickType: selection.lottery.pickType,
            numbers: combination,
            betType: selection.betType === 'box' ? 'boxed' as const : 'straight' as const,
            betAmount: selection.betAmount,
            bonusBets: selection.selectedBonusBets || [],
            drawDate: new Date(drawDate),
            status: 'open' as const,
            outcome: 'pending' as const,
            createdAt: new Date()
          };
          
          console.log('Adding ticket:', ticket);
          addTicket(ticket);
        });
      });
    });
    
    // Clear the cart after purchase
    clearCart();
    
    // Reset board after purchase
    setTimeout(() => {
      setSelections([]);
      setSelectedLotteries([]);
      setCurrentLotteryIndex(0);
      setAddMode('current');
      setPurchaseSuccess(false);
    }, 3000);
  };

  const calculateQuickBuyTotal = () => {
    if (addMode === 'current') {
      if (!currentSelection) return 0;
      const combinations = generateCombinations(currentSelection.numbers);
      const drawDates = getDrawDates();
      const baseCost = combinations.length * drawDates.length * currentSelection.betAmount;
      const bonusCost = currentSelection.selectedBonusBets.reduce((total, bet) => {
        const betOption = getBetOptionsForPickType(currentLottery?.pickType as 2 | 3 | 4 | 5).find(b => b.id === bet.betId);
        if (betOption?.isCombo) {
          return total + (betOption.comboCost || 0);
        }
        return total + bet.amount;
      }, 0) * drawDates.length;
      return baseCost + bonusCost;
    } else {
      let total = 0;
      selections.forEach(sel => {
        const combinations = generateCombinations(sel.numbers);
        const drawDates = getSelectionDrawDates(sel);
        const baseCost = combinations.length * drawDates.length * sel.betAmount;
        const bonusCost = sel.selectedBonusBets.reduce((subtotal, bet) => {
          const betOption = getBetOptionsForPickType(sel.lottery.pickType as 2 | 3 | 4 | 5).find(b => b.id === bet.betId);
          if (betOption?.isCombo) {
            return subtotal + (betOption.comboCost || 0);
          }
          return subtotal + bet.amount;
        }, 0) * drawDates.length;
        total += baseCost + bonusCost;
      });
      return total;
    }
  };

  const calculateTicketCount = () => {
    if (addMode === 'current') {
      if (!currentSelection) return 0;
      const combinations = generateCombinations(currentSelection.numbers);
      const drawDates = getDrawDates();
      return combinations.length * drawDates.length;
    } else {
      let count = 0;
      selections.forEach(sel => {
        const combinations = generateCombinations(sel.numbers);
        const drawDates = getSelectionDrawDates(sel);
        count += combinations.length * drawDates.length;
      });
      return count;
    }
  };

  const toggleDateSelection = (date: Date) => {
    if (!currentSelection) return;
    
    const dateStr = date.toDateString();
    const existingIndex = currentSelection.selectedDates.findIndex(d => d.toDateString() === dateStr);
    
    const newSelections = [...selections];
    if (existingIndex >= 0) {
      newSelections[currentLotteryIndex].selectedDates = currentSelection.selectedDates.filter((_, i) => i !== existingIndex);
    } else {
      newSelections[currentLotteryIndex].selectedDates = [...currentSelection.selectedDates, date].sort((a, b) => a.getTime() - b.getTime());
    }
    setSelections(newSelections);
  };

  const isDateSelected = (date: Date) => {
    if (!currentSelection) return false;
    return currentSelection.selectedDates.some(d => d.toDateString() === date.toDateString());
  };

  const selectStartDate = (date: Date) => {
    if (!currentSelection) return;
    
    const newSelections = [...selections];
    newSelections[currentLotteryIndex].daysToRunStartDate = date;
    setSelections(newSelections);
  };

  const updateScheduleMode = (mode: 'daysToRun' | 'selectDates') => {
    if (!currentSelection) return;
    
    const newSelections = [...selections];
    newSelections[currentLotteryIndex].scheduleMode = mode;
    setSelections(newSelections);
  };

  const updateDaysToRun = (days: number) => {
    if (!currentSelection) return;
    
    const newSelections = [...selections];
    newSelections[currentLotteryIndex].daysToRun = days;
    setSelections(newSelections);
  };

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    return { daysInMonth, startingDayOfWeek };
  };

  // Get lottery draw schedule from lottery data
  const getLotteryDrawDays = (lottery: LotteryGame): number[] => {
    // Convert day names to day numbers (0=Sunday, 6=Saturday)
    const dayMap: Record<string, number> = {
      'Sun': 0,
      'Mon': 1,
      'Tue': 2,
      'Wed': 3,
      'Thu': 4,
      'Fri': 5,
      'Sat': 6
    };
    
    return lottery.drawDays.map(day => dayMap[day]).filter(d => d !== undefined);
  };

  // Check if a date has a draw for selected lotteries
  const hasDrawOnDate = (date: Date): boolean => {
    if (selectedLotteries.length === 0) return false;
    const dayOfWeek = date.getDay();
    return selectedLotteries.some(lottery => 
      getLotteryDrawDays(lottery).includes(dayOfWeek)
    );
  };

  // Get draw info for a specific date
  const getDrawInfo = (date: Date): string[] => {
    const dayOfWeek = date.getDay();
    return selectedLotteries
      .filter(lottery => getLotteryDrawDays(lottery).includes(dayOfWeek))
      .map(lottery => lottery.name);
  };

  const renderCalendar = () => {
    const { daysInMonth, startingDayOfWeek } = getDaysInMonth(currentMonth);
    const days = [];
    const today = new Date();
    const drawDates = getDrawDates();
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(<div key={`empty-${i}`} className="aspect-square" />);
    }
    
    // Add cells for each day of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
      const isPast = date < today && date.toDateString() !== today.toDateString();
      const isSelected = currentSelection?.scheduleMode === 'selectDates' 
        ? isDateSelected(date)
        : currentSelection?.daysToRunStartDate?.toDateString() === date.toDateString();
      const isInRange = currentSelection?.scheduleMode === 'daysToRun' && currentSelection?.daysToRunStartDate && (() => {
        const start = new Date(currentSelection.daysToRunStartDate);
        start.setHours(0, 0, 0, 0);
        const end = new Date(currentSelection.daysToRunStartDate);
        end.setDate(end.getDate() + currentSelection.daysToRun - 1);
        end.setHours(23, 59, 59, 999);
        const checkDate = new Date(date);
        checkDate.setHours(12, 0, 0, 0);
        return checkDate.getTime() >= start.getTime() && checkDate.getTime() <= end.getTime();
      })();
      const hasDraw = hasDrawOnDate(date);
      const drawInfo = getDrawInfo(date);
      
      days.push(
        <div key={day} className="relative group">
          <button
            onClick={() => {
              if (isPast) return;
              if (currentSelection?.scheduleMode === 'daysToRun') {
                selectStartDate(date);
              } else {
                toggleDateSelection(date);
              }
            }}
            disabled={isPast}
            className={`w-full aspect-square rounded-lg text-xs md:text-sm font-bold transition-all relative ${ 
              isSelected || isInRange
                ? 'bg-gradient-to-br from-yellow-400 to-orange-500 text-black shadow-lg z-10'
                : isPast
                ? 'bg-white/5 text-white/30 cursor-not-allowed'
                : hasDraw
                ? 'bg-purple-500/30 text-white hover:bg-purple-500/50 border border-purple-400/50'
                : 'bg-white/10 text-white hover:bg-white/20'
            }`}
          >
            <div className="flex flex-col items-center justify-center h-full">
              <span>{day}</span>
              {hasDraw && !isPast && (
                <span className="text-[8px] md:text-[10px] text-yellow-400">●</span>
              )}
            </div>
          </button>
          
          {/* Tooltip on hover */}
          {hasDraw && !isPast && drawInfo.length > 0 && (
            <div className="hidden group-hover:block absolute bottom-full left-1/2 -translate-x-1/2 mb-1 z-20 w-max max-w-[200px]">
              <div className="bg-black/90 text-white text-[10px] rounded px-2 py-1 border border-white/20">
                <div className="font-bold mb-0.5">Draws:</div>
                {drawInfo.map((name, i) => (
                  <div key={i} className="truncate">{name}</div>
                ))}
              </div>
            </div>
          )}
        </div>
      );
    }
    
    return days;
  };

  const calculateTotalCombinations = () => {
    return selections.reduce((total, sel) => {
      if (sel.numbers.every(row => row.length > 0)) {
        return total + sel.numbers.reduce((prod, row) => prod * row.length, 1);
      }
      return total;
    }, 0);
  };

  const getSelectionDrawDates = (selection: QuickPlaySelection): Date[] => {
    if (selection.scheduleMode === 'daysToRun') {
      if (!selection.daysToRunStartDate) return [];
      const dates: Date[] = [];
      for (let i = 0; i < selection.daysToRun; i++) {
        const date = new Date(selection.daysToRunStartDate);
        date.setDate(selection.daysToRunStartDate.getDate() + i);
        dates.push(date);
      }
      return dates;
    } else {
      return selection.selectedDates;
    }
  };

  const calculateTotalCost = () => {
    return selections.reduce((total, sel) => {
      if (sel.numbers.every(row => row.length > 0)) {
        const combinations = sel.numbers.reduce((prod, row) => prod * row.length, 1);
        const drawDates = getSelectionDrawDates(sel);
        const baseCost = combinations * sel.betAmount * drawDates.length;
        const bonusCost = sel.selectedBonusBets.reduce((subtotal, bet) => {
          const betOption = getBetOptionsForPickType(sel.lottery.pickType as 2 | 3 | 4 | 5).find(b => b.id === bet.betId);
          if (betOption?.isCombo) {
            return subtotal + (betOption.comboCost || 0);
          }
          return subtotal + bet.amount;
        }, 0) * combinations * drawDates.length;
        return total + baseCost + bonusCost;
      }
      return total;
    }, 0);
  };

  const calculateTotalTickets = () => {
    return selections.reduce((total, sel) => {
      if (sel.numbers.every(row => row.length > 0)) {
        const combinations = sel.numbers.reduce((prod, row) => prod * row.length, 1);
        const drawDates = getSelectionDrawDates(sel);
        return total + (combinations * drawDates.length);
      }
      return total;
    }, 0);
  };

  // Get breakdown by lottery
  const getLotteryBreakdown = () => {
    return selections.map((sel, index) => {
      const combinations = sel.numbers.every(row => row.length > 0) 
        ? sel.numbers.reduce((prod, row) => prod * row.length, 1)
        : 0;
      const drawDates = getSelectionDrawDates(sel);
      const tickets = combinations * drawDates.length;
      const baseCost = combinations * sel.betAmount * drawDates.length;
      const bonusCost = sel.selectedBonusBets.reduce((subtotal, bet) => {
        const betOption = getBetOptionsForPickType(sel.lottery.pickType as 2 | 3 | 4 | 5).find(b => b.id === bet.betId);
        if (betOption?.isCombo) {
          return subtotal + (betOption.comboCost || 0);
        }
        return subtotal + bet.amount;
      }, 0) * combinations * drawDates.length;
      const totalCost = baseCost + bonusCost;

      return {
        index,
        lottery: sel.lottery,
        combinations,
        draws: drawDates.length,
        tickets,
        cost: totalCost,
        isComplete: sel.numbers.every(row => row.length > 0) && drawDates.length > 0
      };
    });
  };

  const monthNames = getMonthNames(userProfile.language);
  const dayNames = getDayNames(userProfile.language);

  return (
    <div className="fixed inset-0 z-50 bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 bg-black/40 backdrop-blur-md border-b border-white/10 p-2 md:p-4 flex items-center justify-between z-30">
        <h1 className="text-xl md:text-2xl lg:text-3xl font-bold text-white flex items-center gap-2">
          <svg 
            className="w-6 h-6 md:w-8 md:h-8 lg:w-10 lg:h-10" 
            viewBox="0 0 24 24" 
            fill="none" 
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <linearGradient id="quickPlayGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#fbbf24" />
                <stop offset="50%" stopColor="#f97316" />
                <stop offset="100%" stopColor="#ec4899" />
              </linearGradient>
            </defs>
            {/* Lightning bolt */}
            <path 
              d="M13 2L3 14h8l-1 8 10-12h-8l1-8z" 
              fill="url(#quickPlayGradient)"
              stroke="url(#quickPlayGradient)"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            {/* Sparkle effects */}
            <circle cx="19" cy="5" r="1.5" fill="#fbbf24" opacity="0.8" />
            <circle cx="5" cy="19" r="1" fill="#ec4899" opacity="0.6" />
            <circle cx="20" cy="20" r="1" fill="#f97316" opacity="0.7" />
          </svg>
          <span className="bg-gradient-to-r from-yellow-400 via-orange-500 to-pink-500 bg-clip-text text-transparent">
            {t('quickPlay')}
          </span>
        </h1>
        <div className="flex items-center gap-2">
          <button
            onClick={onOpenCart}
            className="relative flex items-center gap-2 px-3 md:px-4 py-2 bg-white/10 backdrop-blur-md border border-white/20 rounded-lg hover:bg-white/20 transition-all text-white shadow-lg"
          >
            <ShoppingCart className="w-4 h-4 md:w-5 md:h-5" />
            <span className="hidden md:inline text-sm">{t('cart')}</span>
            {getCartCount() > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-black text-xs font-bold">
                {getCartCount()}
              </span>
            )}
          </button>
          <button
            onClick={() => setProfileDrawerOpen(true)}
            className="flex items-center gap-2 px-3 md:px-4 py-2 bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-md border-2 border-purple-400/50 rounded-lg hover:border-purple-400 transition-all text-white shadow-lg"
          >
            <svg className="w-4 h-4 md:w-5 md:h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            <span className="hidden md:inline text-sm">{t('profile')}</span>
          </button>
          <button
            onClick={onClose}
            className="p-1.5 md:p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 md:w-6 md:h-6 text-white" />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="pt-16 md:pt-20 pb-4 px-2 md:px-4 h-full overflow-y-auto">
        <div className="max-w-[1800px] mx-auto grid grid-cols-1 lg:grid-cols-3 gap-3 md:gap-4">
          
          {/* LEFT COLUMN - Lottery Selection + Number Selection */}
          <div className="lg:col-span-2 space-y-3 md:space-y-4">
            
            {/* Section 1: Lottery Selection */}
            <div className="bg-white/5 backdrop-blur-md rounded-xl border border-white/10 p-3 md:p-4">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-base md:text-lg font-bold text-white flex items-center gap-2">
                  <span className="w-5 h-5 md:w-6 md:h-6 rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 flex items-center justify-center text-black text-xs md:text-sm font-bold">1</span>
                  {t('lotterySelection')}
                </h2>
                
                {selectedLotteries.length > 0 && (
                  <button
                    onClick={addToFavoriteLotteries}
                    className="flex items-center gap-1 px-2 md:px-3 py-1.5 md:py-2 bg-gradient-to-r from-yellow-500 to-orange-600 hover:from-yellow-600 hover:to-orange-700 rounded-lg transition-all shadow-lg"
                    title="Save Lottery Selection"
                  >
                    <svg className="w-3.5 h-3.5 md:w-4 md:h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" fill="currentColor" />
                      <path d="M12 11V8M10.5 9.5h3" stroke="black" strokeWidth="1.5" strokeLinecap="round" />
                    </svg>
                    <span className="text-white text-[10px] md:text-xs font-bold">{t('saveFavorite')}</span>
                  </button>
                )}
              </div>
              
              {/* Favorite Lotteries Display */}
              {favoriteLotteries.length > 0 && (
                <div className="mb-3 p-2 md:p-3 bg-gradient-to-br from-yellow-500/10 to-orange-500/10 border border-yellow-500/30 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Star className="w-3.5 h-3.5 md:w-4 md:h-4 text-yellow-400 fill-yellow-400" />
                    <span className="text-yellow-400 font-bold text-xs md:text-sm">{t('favoriteLotteries')}</span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-1.5 md:gap-2">
                    {favoriteLotteries.map((fav, idx) => (
                      <button
                        key={idx}
                        onClick={() => loadFavoriteLottery(fav)}
                        className={`relative group text-left px-2 py-2 rounded-lg transition-all text-xs ${
                          selectedLotteries.some(l => l.id === fav.lottery.id)
                            ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-black font-bold'
                            : 'bg-white/5 hover:bg-white/10 text-white border border-white/10'
                        }`}
                      >
                        <div className="truncate font-bold text-[10px] md:text-xs mb-0.5">{fav.lottery.name}</div>
                        <div className="flex items-center gap-1">
                          <span className="px-1 py-0.5 bg-black/20 rounded text-[9px] md:text-[10px] font-bold">
                            {fav.lottery.stateAbbr}
                          </span>
                          <span className="px-1 py-0.5 bg-black/20 rounded text-[9px] md:text-[10px] font-bold">
                            P{fav.lottery.pickType}
                          </span>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setFavoriteLotteries(favoriteLotteries.filter((_, i) => i !== idx));
                          }}
                          className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 p-0.5 bg-red-500 hover:bg-red-600 rounded transition-all"
                        >
                          <X className="w-2.5 h-2.5 md:w-3 md:h-3 text-white" />
                        </button>
                      </button>
                    ))}
                  </div>
                </div>
              )}
              
              {(!hasFavorites || showChangeSelection) ? (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2 max-h-[60vh] md:max-h-96 overflow-y-auto">
                  {states.map(stateAbbr => (
                    <div key={stateAbbr} className="bg-white/5 rounded-lg overflow-hidden border border-white/10">
                      <button
                        onClick={() => toggleState(stateAbbr)}
                        className="w-full flex items-center justify-between px-2 md:px-3 py-2 bg-gradient-to-r from-blue-600/40 to-purple-600/40 hover:from-blue-600/60 hover:to-purple-600/60 transition-colors"
                      >
                        <span className="text-white font-bold text-xs md:text-sm">{stateAbbr}</span>
                        {expandedStates.has(stateAbbr) ? (
                          <ChevronUp className="w-3 h-3 md:w-4 md:h-4 text-white flex-shrink-0" />
                        ) : (
                          <ChevronDown className="w-3 h-3 md:w-4 md:h-4 text-white flex-shrink-0" />
                        )}
                      </button>
                      
                      {expandedStates.has(stateAbbr) && (
                        <div className="p-1.5 space-y-1">
                          {lotteryByState[stateAbbr].map(lottery => (
                            <button
                              key={lottery.id}
                              onClick={() => toggleLotterySelection(lottery)}
                              className={`w-full text-left px-2 py-1.5 rounded transition-all text-xs ${
                                selectedLotteries.some(l => l.id === lottery.id)
                                  ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-black font-bold'
                                  : 'bg-white/5 hover:bg-white/10 text-white'
                              }`}
                            >
                              <div className="truncate">{lottery.name}</div>
                              <div className="text-[10px] opacity-70">Pick {lottery.pickType}</div>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2 md:gap-3 mb-3">
                    {selectedLotteries.map(lottery => (
                      <div
                        key={lottery.id}
                        className="bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg p-2 md:p-3 border border-white/20"
                      >
                        <div className="flex items-center gap-1 mb-1">
                          <span className="px-1.5 py-0.5 bg-black/40 rounded text-white text-[10px] md:text-xs font-bold">
                            Pick {lottery.pickType}
                          </span>
                          <span className="px-1.5 py-0.5 bg-blue-500 rounded text-white text-[10px] md:text-xs font-bold">
                            {lottery.stateAbbr}
                          </span>
                        </div>
                        <p className="text-white font-bold text-xs md:text-sm truncate">{lottery.name}</p>
                      </div>
                    ))}
                  </div>
                  <button
                    onClick={() => setShowChangeSelection(!showChangeSelection)}
                    className="w-full px-3 md:px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white text-sm transition-colors"
                  >
                    {t('changeSelection')}
                  </button>
                </div>
              )}
              
              {selectedLotteries.length > 0 && !showChangeSelection && (
                <div className="mt-3 flex flex-wrap gap-1.5 md:gap-2">
                  {selectedLotteries.map(lottery => (
                    <div
                      key={lottery.id}
                      className="px-2 md:px-3 py-1 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full text-black text-[10px] md:text-xs font-bold flex items-center gap-1.5"
                    >
                      <span className="truncate max-w-[100px] md:max-w-none">{lottery.name}</span>
                      <button
                        onClick={() => toggleLotterySelection(lottery)}
                        className="hover:bg-black/20 rounded-full p-0.5 flex-shrink-0"
                      >
                        <X className="w-2.5 h-2.5 md:w-3 md:h-3" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Compact Bet Calculator */}
            <div className="sticky top-0 lg:relative lg:top-auto z-20 bg-gradient-to-r from-purple-900/60 to-pink-900/60 backdrop-blur-md rounded-lg border border-yellow-400/30 p-2 md:p-3 shadow-lg">
              {/* Summary Row */}
              <div className="flex items-center justify-between gap-2 md:gap-4 flex-wrap mb-2">
                {/* Total Tickets */}
                <div className="flex items-center gap-1.5 md:gap-2">
                  <svg className="w-4 h-4 md:w-5 md:h-5 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="6" width="18" height="12" rx="2" />
                    <path d="M3 10h18M7 6v12M17 6v12" />
                    <circle cx="10" cy="14" r="1" fill="currentColor" />
                    <circle cx="14" cy="14" r="1" fill="currentColor" />
                  </svg>
                  <span className="text-white/50 text-[10px] md:text-xs">Tickets:</span>
                  {calculateTotalTickets() > 0 ? (
                    <span className="text-white text-xs md:text-sm font-bold">{calculateTotalTickets()}</span>
                  ) : (
                    <span className="text-red-400 text-xs md:text-sm font-bold">✕</span>
                  )}
                </div>
                
                {/* Combinations */}
                <div className="flex items-center gap-1.5 md:gap-2">
                  <svg className="w-4 h-4 md:w-5 md:h-5 text-purple-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="3" width="7" height="7" rx="1" />
                    <rect x="14" y="3" width="7" height="7" rx="1" />
                    <rect x="3" y="14" width="7" height="7" rx="1" />
                    <rect x="14" y="14" width="7" height="7" rx="1" />
                  </svg>
                  <span className="text-white/50 text-[10px] md:text-xs">Combos:</span>
                  {calculateTotalCombinations() > 0 ? (
                    <span className="text-blue-400 text-xs md:text-sm font-bold">{calculateTotalCombinations()}</span>
                  ) : (
                    <span className="text-red-400 text-xs md:text-sm font-bold">✕</span>
                  )}
                </div>
                
                {/* Total Cost */}
                <div className="flex items-center gap-1.5 md:gap-2 bg-black/40 px-2 md:px-3 py-1 rounded-full border border-yellow-400/30">
                  <svg className="w-4 h-4 md:w-5 md:h-5 text-yellow-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M12 6v12M9 9h6M9 15h6" strokeLinecap="round" />
                  </svg>
                  <span className="text-white/50 text-[10px] md:text-xs">Total:</span>
                  {calculateTotalCost() > 0 ? (
                    <span className="text-yellow-400 text-sm md:text-base font-bold">${calculateTotalCost().toFixed(2)}</span>
                  ) : (
                    <span className="text-red-400 text-sm md:text-base font-bold">✕</span>
                  )}
                </div>
              </div>

              {/* Lottery Breakdown */}
              {getLotteryBreakdown().length > 0 && (
                <div className="border-t border-white/10 pt-2 space-y-1">
                  <div className="text-white/50 text-xs mb-2">Lotteries:</div>
                  
                  {/* Mobile: Show only current lottery with navigation arrows */}
                  <div className="md:hidden">
                    {getLotteryBreakdown().length > 0 && (() => {
                      const breakdown = getLotteryBreakdown()[currentLotteryIndex];
                      if (!breakdown) return null;
                      
                      return (
                        <div className="relative">
                          {/* Navigation arrows */}
                          {currentLotteryIndex > 0 && (
                            <button
                              onClick={() => setCurrentLotteryIndex(currentLotteryIndex - 1)}
                              className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-3 z-10 w-6 h-6 rounded-full bg-black/80 backdrop-blur-md border border-white/20 flex items-center justify-center hover:bg-white/20 transition-all"
                            >
                              <ChevronLeft className="w-3 h-3 text-white" />
                            </button>
                          )}
                          
                          {currentLotteryIndex < getLotteryBreakdown().length - 1 && (
                            <button
                              onClick={() => setCurrentLotteryIndex(currentLotteryIndex + 1)}
                              className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-3 z-10 w-6 h-6 rounded-full bg-black/80 backdrop-blur-md border border-white/20 flex items-center justify-center hover:bg-white/20 transition-all"
                            >
                              <ChevronRight className="w-3 h-3 text-white" />
                            </button>
                          )}
                          
                          <div className="w-full flex items-center justify-between gap-2 px-3 py-2 rounded-lg bg-yellow-400/20 border border-yellow-400/50 shadow-lg">
                            <div className="flex items-center gap-2 min-w-0 flex-1">
                              <span className="text-xs font-bold truncate text-white">
                                {breakdown.lottery.name}
                              </span>
                            </div>
                            <div className="flex items-center gap-2 flex-shrink-0">
                              <span className={`text-[10px] ${breakdown.isComplete ? 'text-blue-400' : 'text-white/40'}`}>
                                {breakdown.tickets > 0 ? `${breakdown.tickets}t` : '—'}
                              </span>
                              <span className={`text-[10px] ${breakdown.isComplete ? 'text-green-400' : 'text-white/40'}`}>
                                {breakdown.draws > 0 ? `${breakdown.draws}d` : '—'}
                              </span>
                              <span className={`text-xs font-bold ${breakdown.isComplete ? 'text-yellow-400' : 'text-white/40'}`}>
                                {breakdown.cost > 0 ? `$${breakdown.cost.toFixed(2)}` : '—'}
                              </span>
                            </div>
                          </div>
                          
                          {/* Page indicator */}
                          <div className="flex items-center justify-center gap-1 mt-2">
                            {getLotteryBreakdown().map((_, idx) => (
                              <div
                                key={idx}
                                className={`h-1 rounded-full transition-all ${
                                  idx === currentLotteryIndex
                                    ? 'bg-yellow-400 w-4'
                                    : 'bg-white/30 w-1'
                                }`}
                              />
                            ))}
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                  
                  {/* Desktop: Show all lotteries in scrollable list */}
                  <div className="hidden md:block max-h-48 overflow-y-auto space-y-1.5 pr-1 lottery-scrollbar">
                    {getLotteryBreakdown().map((breakdown) => (
                      <button
                        key={breakdown.index}
                        ref={(el) => (lotteryButtonRefs.current[breakdown.index] = el)}
                        onClick={() => setCurrentLotteryIndex(breakdown.index)}
                        className={`w-full flex items-center justify-between gap-2 px-3 py-2 rounded-lg transition-all ${
                          breakdown.index === currentLotteryIndex
                            ? 'bg-yellow-400/20 border border-yellow-400/50 shadow-lg'
                            : 'bg-white/5 hover:bg-white/10 border border-white/10'
                        }`}
                      >
                        <div className="flex items-center gap-2 min-w-0 flex-1">
                          <span className={`text-xs font-bold truncate ${
                            breakdown.isComplete ? 'text-white' : 'text-white/50'
                          }`}>
                            {breakdown.lottery.name}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 flex-shrink-0">
                          <span className={`text-[10px] ${breakdown.isComplete ? 'text-blue-400' : 'text-white/40'}`}>
                            {breakdown.tickets > 0 ? `${breakdown.tickets}t` : '—'}
                          </span>
                          <span className={`text-[10px] ${breakdown.isComplete ? 'text-green-400' : 'text-white/40'}`}>
                            {breakdown.draws > 0 ? `${breakdown.draws}d` : '—'}
                          </span>
                          <span className={`text-xs font-bold ${breakdown.isComplete ? 'text-yellow-400' : 'text-white/40'}`}>
                            {breakdown.cost > 0 ? `$${breakdown.cost.toFixed(2)}` : '—'}
                          </span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Section 2: Number Selection Slider */}
            {selectedLotteries.length > 0 && (
              <div className="bg-white/5 backdrop-blur-md rounded-xl border border-white/10 p-3 md:p-4">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-base md:text-lg font-bold text-white flex items-center gap-2">
                    <span className="w-5 h-5 md:w-6 md:h-6 rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 flex items-center justify-center text-black text-xs md:text-sm font-bold">2</span>
                    <span className="lg:hidden">{t('numberSelection')}</span>
                    <span className="hidden lg:inline">{t('numberSelection')}</span>
                  </h2>
                  
                  {selectedLotteries.length > 1 && (
                    <div className="hidden md:flex items-center gap-1.5 md:gap-2">
                      <button
                        onClick={() => setCurrentLotteryIndex(Math.max(0, currentLotteryIndex - 1))}
                        disabled={currentLotteryIndex === 0}
                        className="p-1.5 md:p-2 bg-white/10 hover:bg-white/20 rounded-lg disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                      >
                        <ChevronLeft className="w-4 h-4 md:w-5 md:h-5 text-white" />
                      </button>
                      <span className="text-white text-xs md:text-sm">
                        {currentLotteryIndex + 1} / {selectedLotteries.length}
                      </span>
                      <button
                        onClick={() => setCurrentLotteryIndex(Math.min(selectedLotteries.length - 1, currentLotteryIndex + 1))}
                        disabled={currentLotteryIndex === selectedLotteries.length - 1}
                        className="p-1.5 md:p-2 bg-white/10 hover:bg-white/20 rounded-lg disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                      >
                        <ChevronRight className="w-4 h-4 md:w-5 md:h-5 text-white" />
                      </button>
                    </div>
                  )}
                </div>

                {currentLottery && currentSelection && (
                  <div className="flex flex-col">
                    {/* Lottery Header - Always first */}
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4 bg-gradient-to-r from-purple-600/40 to-pink-600/40 rounded-lg p-2 md:p-3 border border-purple-400/30 order-1 lg:order-none">
                      <div>
                        <h3 className="text-white font-bold text-sm md:text-base">{currentLottery.name}</h3>
                        <div className="flex items-center gap-1.5 md:gap-2 mt-1">
                          <span className="px-1.5 md:px-2 py-0.5 bg-gradient-to-r from-yellow-400 to-orange-500 rounded text-black text-[10px] md:text-xs font-bold">
                            Pick {currentLottery.pickType}
                          </span>
                          <span className="px-1.5 md:px-2 py-0.5 bg-blue-500 rounded text-white text-[10px] md:text-xs font-bold">
                            {currentLottery.stateAbbr}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-1.5 md:gap-2">
                        <button
                          onClick={generateLuckyNumbers}
                          className="flex items-center gap-1 px-2 md:px-3 py-1.5 md:py-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 rounded-lg transition-all shadow-lg"
                          title="Generate Lucky Numbers"
                        >
                          <svg className="w-4 h-4 md:w-5 md:h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="currentColor" strokeLinecap="round" strokeLinejoin="round" />
                            <circle cx="12" cy="12" r="1" fill="black" />
                            <circle cx="9" cy="10" r="0.5" fill="black" />
                            <circle cx="15" cy="10" r="0.5" fill="black" />
                            <circle cx="10" cy="14" r="0.5" fill="black" />
                            <circle cx="14" cy="14" r="0.5" fill="black" />
                          </svg>
                          <span className="text-white text-[10px] md:text-xs font-bold">{t('luckyPick')}</span>
                        </button>
                        <button
                          onClick={addToFavoriteNumbers}
                          className="flex items-center gap-1 px-2 md:px-3 py-1.5 md:py-2 bg-gradient-to-r from-yellow-500 to-orange-600 hover:from-yellow-600 hover:to-orange-700 rounded-lg transition-all shadow-lg"
                          title="Add to Favorites"
                        >
                          <svg className="w-4 h-4 md:w-5 md:h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" fill="currentColor" />
                            <path d="M12 11V8M10.5 9.5h3" stroke="black" strokeWidth="1.5" strokeLinecap="round" />
                          </svg>
                          <span className="text-white text-[10px] md:text-xs font-bold">{t('saveNumbers')}</span>
                        </button>
                        <button
                          onClick={() => setShowFavoritesModal(true)}
                          className="flex items-center gap-1 px-2 md:px-3 py-1.5 md:py-2 bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 rounded-lg transition-all shadow-lg"
                          title="Show Favorites"
                        >
                          <svg className="w-4 h-4 md:w-5 md:h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <rect x="3" y="3" width="18" height="18" rx="2" fill="currentColor" />
                            <path d="M9 12l2 2 4-4" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            <circle cx="17" cy="7" r="3" fill="#FFD700" stroke="black" strokeWidth="1" />
                            <path d="M17 6v2M16 7h2" stroke="black" strokeWidth="1" strokeLinecap="round" />
                          </svg>
                          <span className="text-white text-[10px] md:text-xs font-bold">Saved</span>
                        </button>
                      </div>
                    </div>

                    {/* Mobile Only: Time Selection - Order 6 */}
                    <div className="lg:hidden mb-4 bg-black/20 rounded-lg p-3 border border-white/10 order-6">
                      <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                        <span className="w-4 h-4 rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 flex items-center justify-center text-black text-[10px] font-bold">6</span>
                        {t('calendarSchedule')}
                      </h3>
                      
                      <div className="space-y-2">
                        <div className="flex gap-2">
                          <button
                            onClick={() => updateScheduleMode('daysToRun')}
                            className={`flex-1 px-3 py-1.5 rounded-lg font-bold text-xs transition-all ${
                              currentSelection?.scheduleMode === 'daysToRun'
                                ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-black'
                                : 'bg-white/10 text-white hover:bg-white/20'
                            }`}
                          >
                            {t('daysToRun')}
                          </button>
                          <button
                            onClick={() => updateScheduleMode('selectDates')}
                            className={`flex-1 px-3 py-1.5 rounded-lg font-bold text-xs transition-all ${
                              currentSelection?.scheduleMode === 'selectDates'
                                ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-black'
                                : 'bg-white/10 text-white hover:bg-white/20'
                            }`}
                          >
                            {t('selectDates')}
                          </button>
                        </div>

                        {currentSelection?.scheduleMode === 'daysToRun' ? (
                          <div>
                            <label className="text-white text-xs mb-2 block">{t('numberOfDays')}:</label>
                            <input
                              type="number"
                              min="1"
                              max="30"
                              value={currentSelection?.daysToRun || 7}
                              onChange={(e) => updateDaysToRun(parseInt(e.target.value) || 1)}
                              className="w-full px-3 py-2 mb-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm font-bold focus:outline-none focus:ring-2 focus:ring-yellow-400"
                            />
                            
                            <p className="text-white/70 text-[10px] mb-2 text-center">
                              Select start date - runs {currentSelection?.daysToRun || 7} consecutive days
                            </p>
                            
                            <div className="bg-white/5 rounded-lg p-2">
                              <div className="flex items-center justify-between mb-2">
                                <button
                                  onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))}
                                  className="p-1 bg-white/10 hover:bg-white/20 rounded transition-colors"
                                >
                                  <ChevronLeft className="w-3 h-3 text-white" />
                                </button>
                                <span className="text-white text-xs font-bold">
                                  {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
                                </span>
                                <button
                                  onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))}
                                  className="p-1 bg-white/10 hover:bg-white/20 rounded transition-colors"
                                >
                                  <ChevronRight className="w-3 h-3 text-white" />
                                </button>
                              </div>
                              
                              <div className="grid grid-cols-7 gap-0.5 mb-1">
                                {dayNames.map((day, i) => (
                                  <div key={i} className="text-center text-white/50 text-[10px] font-bold py-1">
                                    {day.charAt(0)}
                                  </div>
                                ))}
                              </div>
                              
                              <div className="grid grid-cols-7 gap-0.5">
                                {renderCalendar()}
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div>
                            <p className="text-white/70 text-[10px] mb-2 text-center">
                              Select individual dates - each runs once
                            </p>
                            
                            <div className="bg-white/5 rounded-lg p-2">
                              <div className="flex items-center justify-between mb-2">
                                <button
                                  onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))}
                                  className="p-1 bg-white/10 hover:bg-white/20 rounded transition-colors"
                                >
                                  <ChevronLeft className="w-3 h-3 text-white" />
                                </button>
                                <span className="text-white text-xs font-bold">
                                  {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
                                </span>
                                <button
                                  onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))}
                                  className="p-1 bg-white/10 hover:bg-white/20 rounded transition-colors"
                                >
                                  <ChevronRight className="w-3 h-3 text-white" />
                                </button>
                              </div>
                              
                              <div className="grid grid-cols-7 gap-0.5 mb-1">
                                {dayNames.map((day, i) => (
                                  <div key={i} className="text-center text-white/50 text-[10px] font-bold py-1">
                                    {day.charAt(0)}
                                  </div>
                                ))}
                              </div>
                              
                              <div className="grid grid-cols-7 gap-0.5">
                                {renderCalendar()}
                              </div>
                              
                              <p className="text-white/70 text-[10px] mt-2 text-center">
                                {currentSelection?.selectedDates.length || 0} date{currentSelection?.selectedDates.length !== 1 ? 's' : ''} selected
                              </p>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Mobile Only: Bet Amount - Order 4 */}
                    <div className="lg:hidden mb-4 bg-black/20 rounded-lg p-3 border border-white/10 order-4">
                      <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                        <span className="w-4 h-4 rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 flex items-center justify-center text-black text-[10px] font-bold">4</span>
                        {t('betAmount')}
                      </h3>
                      
                      <input
                        type="number"
                        min="0.5"
                        step="0.5"
                        value={currentSelection.betAmount}
                        onChange={(e) => updateCurrentBetAmount(parseFloat(e.target.value) || 1)}
                        className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-lg font-bold focus:outline-none focus:ring-2 focus:ring-yellow-400"
                      />
                    </div>

                    {/* Mobile Only: Bonus Bets - Order 5 */}
                    <div className="lg:hidden mb-4 bg-black/20 rounded-lg p-3 border border-white/10 order-5">
                      <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                        <span className="w-4 h-4 rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 flex items-center justify-center text-black text-[10px] font-bold">5</span>
                        Bonus Bets
                      </h3>
                      
                      <div className="space-y-1.5 max-h-32 overflow-y-auto">
                        {getBetOptionsForPickType(currentLottery.pickType as 2 | 3 | 4 | 5)
                          .filter(bet => !bet.id.includes('-straight'))
                          .map(bet => {
                            const isSelected = currentSelection.selectedBonusBets.some(b => b.betId === bet.id);
                            const selectedBet = currentSelection.selectedBonusBets.find(b => b.betId === bet.id);
                            const betAmount = selectedBet?.amount || bet.minBet;
                            const potentialWin = isSelected ? calculatePotentialWinnings(bet, betAmount) : 0;
                            return (
                              <div
                                key={bet.id}
                                className={`w-full rounded-lg transition-all ${
                                  isSelected
                                    ? 'bg-gradient-to-r from-yellow-400 to-orange-500 p-2'
                                    : 'bg-white/10 p-1.5'
                                }`}
                              >
                                <div className="flex items-center justify-between mb-1">
                                  <span className={`text-xs font-bold truncate ${isSelected ? 'text-black' : 'text-white'}`}>
                                    {bet.name}
                                  </span>
                                  {bet.isCombo && !isSelected && (
                                    <span className="text-[10px] text-white/70 flex-shrink-0 ml-2">
                                      ${bet.comboCost}
                                    </span>
                                  )}
                                </div>
                                
                                {!isSelected && !bet.isCombo && (
                                  <div className="space-y-1">
                                    <div className="flex items-center gap-1">
                                      <label className="text-[9px] text-white/70 whitespace-nowrap">Amount:</label>
                                      <div className="flex items-center flex-1 bg-white/10 rounded border border-white/20 overflow-hidden">
                                        <span className="text-white text-[10px] px-1">$</span>
                                        <input
                                          type="number"
                                          min={bet.minBet}
                                          step="1"
                                          value={pendingBonusBetAmounts[bet.id] || ''}
                                          onChange={(e) => handlePendingBonusBetAmountChange(bet.id, e.target.value)}
                                          onClick={(e) => e.stopPropagation()}
                                          className="flex-1 bg-transparent text-white px-1 py-0.5 text-[10px] font-bold focus:outline-none"
                                          placeholder={`${bet.minBet}`}
                                        />
                                      </div>
                                    </div>
                                    <button
                                      onClick={() => addCurrentBonusBet(bet.id, bet.minBet)}
                                      className="w-full py-1 rounded bg-white/10 text-white/70 hover:bg-white/20 font-semibold text-[10px] transition-all"
                                    >
                                      Add
                                    </button>
                                  </div>
                                )}
                                
                                {isSelected && !bet.isCombo && (
                                  <div className="space-y-1">
                                    <div className="flex items-center gap-1">
                                      <label className="text-[9px] text-black/70 whitespace-nowrap">Amount:</label>
                                      <div className="flex items-center flex-1 bg-black/20 rounded border border-black/30 overflow-hidden">
                                        <span className="text-black text-[10px] px-1">$</span>
                                        <input
                                          type="number"
                                          min={bet.minBet}
                                          step="1"
                                          value={betAmount}
                                          onChange={(e) => updateCurrentBonusBetAmount(bet.id, e.target.value, bet.minBet)}
                                          onClick={(e) => e.stopPropagation()}
                                          className="flex-1 bg-transparent text-black px-1 py-0.5 text-[10px] font-bold focus:outline-none"
                                        />
                                      </div>
                                    </div>
                                    <div className="flex items-center justify-between px-1 py-0.5 bg-black/20 rounded">
                                      <span className="text-[9px] text-black/70">Win:</span>
                                      <span className="text-[10px] text-black font-bold">${potentialWin.toFixed(2)}</span>
                                    </div>
                                    <button
                                      onClick={() => removeCurrentBonusBet(bet.id)}
                                      className="w-full py-1 rounded bg-gradient-to-r from-yellow-400 to-orange-500 text-black hover:shadow-lg font-semibold text-[10px] transition-all"
                                    >
                                      Remove
                                    </button>
                                  </div>
                                )}
                                
                                {!isSelected && bet.isCombo && (
                                  <button
                                    onClick={() => addCurrentBonusBet(bet.id, bet.comboCost || 0)}
                                    className="w-full py-1 rounded bg-white/10 text-white/70 hover:bg-white/20 font-semibold text-[10px] transition-all"
                                  >
                                    Add
                                  </button>
                                )}
                                
                                {isSelected && bet.isCombo && (
                                  <div className="space-y-1">
                                    <div className="px-1.5 py-0.5 bg-black/20 rounded">
                                      <span className="text-[9px] text-black/70">Bundle: ${bet.comboCost}</span>
                                    </div>
                                    <button
                                      onClick={() => removeCurrentBonusBet(bet.id)}
                                      className="w-full py-1 rounded bg-gradient-to-r from-yellow-400 to-orange-500 text-black hover:shadow-lg font-semibold text-[10px] transition-all"
                                    >
                                      Remove
                                    </button>
                                  </div>
                                )}
                              </div>
                            );
                          })}
                      </div>
                    </div>

                    {/* Bet Type - Order 2 */}
                    <div className="mb-3 md:mb-4 order-2">
                      <label className="text-white text-xs md:text-sm font-semibold mb-2 block">Bet Type:</label>
                      <div className="flex gap-2">
                        <button
                          onClick={() => {
                            const newSelections = [...selections];
                            newSelections[currentLotteryIndex] = {
                              ...currentSelection,
                              betType: 'straight'
                            };
                            setSelections(newSelections);
                          }}
                          className={`flex-1 px-3 md:px-4 py-1.5 md:py-2 rounded-lg font-bold text-xs md:text-sm transition-all ${
                            currentSelection.betType === 'straight'
                              ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-black'
                              : 'bg-white/10 text-white hover:bg-white/20'
                          }`}
                        >
                          Straight
                        </button>
                        <button
                          onClick={() => {
                            const newSelections = [...selections];
                            newSelections[currentLotteryIndex] = {
                              ...currentSelection,
                              betType: 'box'
                            };
                            setSelections(newSelections);
                          }}
                          className={`flex-1 px-3 md:px-4 py-1.5 md:py-2 rounded-lg font-bold text-xs md:text-sm transition-all ${
                            currentSelection.betType === 'box'
                              ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-black'
                              : 'bg-white/10 text-white hover:bg-white/20'
                          }`}
                        >
                          Box
                        </button>
                      </div>
                    </div>

                    {/* Number Grid - Order 3 */}
                    <div className="space-y-2 md:space-y-3 order-3">
                      {currentSelection.numbers.map((row, rowIndex) => (
                        <div key={rowIndex}>
                          <label className="text-white text-xs md:text-sm mb-1.5 md:mb-2 block">Position {rowIndex + 1}:</label>
                          <div className="grid grid-cols-5 sm:grid-cols-10 gap-1.5 md:gap-2">
                            {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map(num => (
                              <button
                                key={num}
                                onClick={() => updateCurrentNumbers(rowIndex, num)}
                                className={`aspect-square rounded-lg font-bold text-base md:text-lg transition-all ${
                                  row.includes(num)
                                    ? 'bg-gradient-to-br from-yellow-400 to-orange-500 text-black shadow-lg shadow-yellow-400/50 scale-105'
                                    : 'bg-white/10 text-white hover:bg-white/20'
                                }`}
                              >
                                {num}
                              </button>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Add Mode Selection and Cart Button - Order 7 */}
                    <div className="mt-3 md:mt-4 order-7">
                      <div className="flex gap-2 mb-2">
                        <button
                          onClick={() => setAddMode('current')}
                          className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg transition-all ${
                            addMode === 'current'
                              ? 'bg-white/20 border border-white/30'
                              : 'bg-white/5 border border-white/10 hover:bg-white/10'
                          }`}
                        >
                          <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                            addMode === 'current' ? 'border-yellow-400' : 'border-white/30'
                          }`}>
                            {addMode === 'current' && (
                              <div className="w-2 h-2 rounded-full bg-yellow-400" />
                            )}
                          </div>
                          <span className="text-white text-xs font-bold">{t('currentTicket')}</span>
                        </button>
                        <button
                          onClick={() => setAddMode('all')}
                          className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg transition-all ${
                            addMode === 'all'
                              ? 'bg-white/20 border border-white/30'
                              : 'bg-white/5 border border-white/10 hover:bg-white/10'
                          }`}
                        >
                          <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                            addMode === 'all' ? 'border-yellow-400' : 'border-white/30'
                          }`}>
                            {addMode === 'all' && (
                              <div className="w-2 h-2 rounded-full bg-yellow-400" />
                            )}
                          </div>
                          <span className="text-white text-xs font-bold">{t('allTickets')}</span>
                        </button>
                      </div>

                      <div className="flex gap-2">
                        <button
                          onClick={handleAddToCart}
                          disabled={
                            addMode === 'current'
                              ? !currentSelection || !currentSelection.numbers.every(row => row.length > 0) || getDrawDates().length === 0
                              : selections.length === 0 || !selections.every(sel => sel.numbers.every(row => row.length > 0) && getSelectionDrawDates(sel).length > 0)
                          }
                          className="flex-1 px-4 py-2.5 md:py-3 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 rounded-lg text-white font-bold text-sm md:text-base disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                          {t('addToCart')}
                        </button>
                        <button
                          onClick={handleQuickBuy}
                          disabled={
                            addMode === 'current'
                              ? !currentSelection || !currentSelection.numbers.every(row => row.length > 0) || getDrawDates().length === 0
                              : selections.length === 0 || !selections.every(sel => sel.numbers.every(row => row.length > 0) && getSelectionDrawDates(sel).length > 0)
                          }
                          className="flex-1 px-4 py-2.5 md:py-3 bg-gradient-to-r from-yellow-400 to-orange-500 hover:from-yellow-500 hover:to-orange-600 rounded-lg text-black font-bold text-sm md:text-base disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-yellow-400/30"
                        >
                          ⚡ {t('quickBuyNow')}
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* RIGHT COLUMN - Settings and Cart */}
          <div className="space-y-3 md:space-y-4">
            
            {/* Section 3: Time Selection (Desktop/Tablet Only) */}
            <div className="hidden lg:block bg-white/5 backdrop-blur-md rounded-xl border border-white/10 p-3 md:p-4">
              <h2 className="text-base md:text-lg font-bold text-white mb-3 flex items-center gap-2">
                <span className="w-5 h-5 md:w-6 md:h-6 rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 flex items-center justify-center text-black text-xs md:text-sm font-bold">3</span>
                {t('calendarSchedule')}
              </h2>
              
              <div className="space-y-2 md:space-y-3">
                <div className="flex gap-2">
                  <button
                    onClick={() => updateScheduleMode('daysToRun')}
                    className={`flex-1 px-2 md:px-3 py-1.5 md:py-2 rounded-lg text-xs md:text-sm font-bold transition-all ${
                      currentSelection?.scheduleMode === 'daysToRun'
                        ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-black'
                        : 'bg-white/10 text-white hover:bg-white/20'
                    }`}
                  >
                    {t('daysToRun')}
                  </button>
                  <button
                    onClick={() => updateScheduleMode('selectDates')}
                    className={`flex-1 px-2 md:px-3 py-1.5 md:py-2 rounded-lg text-xs md:text-sm font-bold transition-all ${
                      currentSelection?.scheduleMode === 'selectDates'
                        ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-black'
                        : 'bg-white/10 text-white hover:bg-white/20'
                    }`}
                  >
                    {t('selectDates')}
                  </button>
                </div>
                
                {currentSelection?.scheduleMode === 'daysToRun' ? (
                  <div>
                    <label className="text-white text-xs md:text-sm mb-2 block">{t('numberOfDays')}:</label>
                    <input
                      type="number"
                      min="1"
                      max="30"
                      value={currentSelection?.daysToRun || 7}
                      onChange={(e) => updateDaysToRun(parseInt(e.target.value) || 1)}
                      className="w-full px-3 md:px-4 py-2 mb-2 md:mb-3 bg-white/10 border border-white/20 rounded-lg text-white text-sm md:text-base focus:outline-none focus:ring-2 focus:ring-yellow-400"
                    />
                    
                    <p className="text-white/70 text-[10px] md:text-xs mb-2 text-center">
                      Select start date - runs {currentSelection?.daysToRun || 7} consecutive days
                    </p>
                    
                    <div className="flex items-center justify-between mb-2">
                      <button
                        onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))}
                        className="p-1 bg-white/10 hover:bg-white/20 rounded transition-colors"
                      >
                        <ChevronLeft className="w-3 h-3 md:w-4 md:h-4 text-white" />
                      </button>
                      <span className="text-white text-xs md:text-sm font-bold">
                        {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
                      </span>
                      <button
                        onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))}
                        className="p-1 bg-white/10 hover:bg-white/20 rounded transition-colors"
                      >
                        <ChevronRight className="w-3 h-3 md:w-4 md:h-4 text-white" />
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-7 gap-0.5 md:gap-1 mb-1 md:mb-2">
                      {dayNames.map((day, i) => (
                        <div key={i} className="text-center text-white/50 text-[10px] md:text-xs font-bold py-1">
                          {day.charAt(0)}
                        </div>
                      ))}
                    </div>
                    
                    <div className="grid grid-cols-7 gap-0.5 md:gap-1">
                      {renderCalendar()}
                    </div>
                  </div>
                ) : (
                  <div>
                    <p className="text-white/70 text-[10px] md:text-xs mb-2 text-center">
                      Select individual dates - each runs once
                    </p>
                    
                    <div className="flex items-center justify-between mb-2">
                      <button
                        onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))}
                        className="p-1 bg-white/10 hover:bg-white/20 rounded transition-colors"
                      >
                        <ChevronLeft className="w-3 h-3 md:w-4 md:h-4 text-white" />
                      </button>
                      <span className="text-white text-xs md:text-sm font-bold">
                        {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
                      </span>
                      <button
                        onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))}
                        className="p-1 bg-white/10 hover:bg-white/20 rounded transition-colors"
                      >
                        <ChevronRight className="w-3 h-3 md:w-4 md:h-4 text-white" />
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-7 gap-0.5 md:gap-1 mb-1 md:mb-2">
                      {dayNames.map((day, i) => (
                        <div key={i} className="text-center text-white/50 text-[10px] md:text-xs font-bold py-1">
                          {day.charAt(0)}
                        </div>
                      ))}
                    </div>
                    
                    <div className="grid grid-cols-7 gap-0.5 md:gap-1">
                      {renderCalendar()}
                    </div>
                    
                    <p className="text-white/70 text-[10px] md:text-xs mt-2 text-center">
                      {currentSelection?.selectedDates.length || 0} date{currentSelection?.selectedDates.length !== 1 ? 's' : ''} selected
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Section 4: Bet Amount (Per Lottery) - Desktop/Tablet Only */}
            {currentLottery && currentSelection && (
              <div className="hidden lg:block bg-white/5 backdrop-blur-md rounded-xl border border-white/10 p-3 md:p-4">
                <h2 className="text-base md:text-lg font-bold text-white mb-3 flex items-center gap-2">
                  <span className="w-5 h-5 md:w-6 md:h-6 rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 flex items-center justify-center text-black text-xs md:text-sm font-bold">4</span>
                  {t('betAmount')}
                  <span className="text-xs text-white/60">({currentLottery.name})</span>
                </h2>
                
                <input
                  type="number"
                  min="0.5"
                  step="0.5"
                  value={currentSelection.betAmount}
                  onChange={(e) => updateCurrentBetAmount(parseFloat(e.target.value) || 1)}
                  className="w-full px-3 md:px-4 py-2 md:py-3 bg-white/10 border border-white/20 rounded-lg text-white text-lg md:text-xl font-bold focus:outline-none focus:ring-2 focus:ring-yellow-400"
                />
              </div>
            )}

            {/* Section 5: Bonus Bets (Per Lottery) - Desktop/Tablet Only */}
            {currentLottery && currentSelection && (
              <div className="hidden lg:block bg-white/5 backdrop-blur-md rounded-xl border border-white/10 p-3 md:p-4">
                <h2 className="text-base md:text-lg font-bold text-white mb-3 flex items-center gap-2">
                  <span className="w-5 h-5 md:w-6 md:h-6 rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 flex items-center justify-center text-black text-xs md:text-sm font-bold">5</span>
                  {t('bonusBets')}
                  <span className="text-xs text-white/60">({currentLottery.name})</span>
                </h2>
                
                <div className="space-y-1.5 md:space-y-2 max-h-32 md:max-h-40 overflow-y-auto">
                  {getBetOptionsForPickType(currentLottery.pickType as 2 | 3 | 4 | 5)
                    .filter(bet => !bet.id.includes('-straight'))
                    .map(bet => {
                      const isSelected = currentSelection.selectedBonusBets.some(b => b.betId === bet.id);
                      const selectedBet = currentSelection.selectedBonusBets.find(b => b.betId === bet.id);
                      const betAmount = selectedBet?.amount || bet.minBet;
                      const potentialWin = isSelected ? calculatePotentialWinnings(bet, betAmount) : 0;
                      return (
                        <div
                          key={bet.id}
                          className={`w-full rounded-lg transition-all ${
                            isSelected
                              ? 'bg-gradient-to-r from-yellow-400 to-orange-500 p-2 md:p-2.5'
                              : 'bg-white/10 p-1.5 md:p-2'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-1.5">
                            <span className={`text-xs md:text-sm font-bold truncate ${isSelected ? 'text-black' : 'text-white'}`}>
                              {bet.name}
                            </span>
                            {bet.isCombo && !isSelected && (
                              <span className="text-[10px] md:text-xs text-white/70 flex-shrink-0 ml-2">
                                ${bet.comboCost}
                              </span>
                            )}
                          </div>
                          
                          {!isSelected && !bet.isCombo && (
                            <div className="space-y-1.5">
                              <div className="flex items-center gap-2">
                                <label className="text-[10px] md:text-xs text-white/70 whitespace-nowrap">Amount:</label>
                                <div className="flex items-center flex-1 bg-white/10 rounded border border-white/20 overflow-hidden">
                                  <span className="text-white text-xs md:text-sm px-1.5 md:px-2">$</span>
                                  <input
                                    type="number"
                                    min={bet.minBet}
                                    step="1"
                                    value={pendingBonusBetAmounts[bet.id] || ''}
                                    onChange={(e) => handlePendingBonusBetAmountChange(bet.id, e.target.value)}
                                    onClick={(e) => e.stopPropagation()}
                                    className="flex-1 bg-transparent text-white px-1 md:px-2 py-1 text-xs md:text-sm font-bold focus:outline-none"
                                    placeholder={`${bet.minBet}`}
                                  />
                                </div>
                              </div>
                              <button
                                onClick={() => addCurrentBonusBet(bet.id, bet.minBet)}
                                className="w-full py-1.5 rounded bg-white/10 text-white/70 hover:bg-white/20 font-semibold text-xs transition-all"
                              >
                                Add
                              </button>
                            </div>
                          )}
                          
                          {isSelected && !bet.isCombo && (
                            <div className="space-y-1.5">
                              <div className="flex items-center gap-2">
                                <label className="text-[10px] md:text-xs text-black/70 whitespace-nowrap">Amount:</label>
                                <div className="flex items-center flex-1 bg-black/20 rounded border border-black/30 overflow-hidden">
                                  <span className="text-black text-xs md:text-sm px-1.5 md:px-2">$</span>
                                  <input
                                    type="number"
                                    min={bet.minBet}
                                    step="1"
                                    value={betAmount}
                                    onChange={(e) => updateCurrentBonusBetAmount(bet.id, e.target.value, bet.minBet)}
                                    onClick={(e) => e.stopPropagation()}
                                    className="flex-1 bg-transparent text-black px-1 md:px-2 py-1 text-xs md:text-sm font-bold focus:outline-none"
                                  />
                                </div>
                              </div>
                              <div className="flex items-center justify-between px-2 py-1 bg-black/20 rounded">
                                <span className="text-[10px] md:text-xs text-black/70">Win:</span>
                                <span className="text-xs md:text-sm text-black font-bold">${potentialWin.toFixed(2)}</span>
                              </div>
                              <button
                                onClick={() => removeCurrentBonusBet(bet.id)}
                                className="w-full py-1.5 rounded bg-gradient-to-r from-yellow-400 to-orange-500 text-black hover:shadow-lg font-semibold text-xs transition-all"
                              >
                                Remove
                              </button>
                            </div>
                          )}
                          
                          {!isSelected && bet.isCombo && (
                            <button
                              onClick={() => addCurrentBonusBet(bet.id, bet.comboCost || 0)}
                              className="w-full py-1.5 rounded bg-white/10 text-white/70 hover:bg-white/20 font-semibold text-xs transition-all"
                            >
                              Add
                            </button>
                          )}
                          
                          {isSelected && bet.isCombo && (
                            <div className="space-y-1.5">
                              <div className="px-2 py-1 bg-black/20 rounded">
                                <span className="text-[10px] md:text-xs text-black/70">Bundle: ${bet.comboCost}</span>
                              </div>
                              <button
                                onClick={() => removeCurrentBonusBet(bet.id)}
                                className="w-full py-1.5 rounded bg-gradient-to-r from-yellow-400 to-orange-500 text-black hover:shadow-lg font-semibold text-xs transition-all"
                              >
                                Remove
                              </button>
                            </div>
                          )}
                        </div>
                      );
                    })}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Favorite Numbers Modal */}
      <AnimatePresence>
        {showFavoritesModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setShowFavoritesModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-gradient-to-br from-purple-900 to-blue-900 rounded-2xl p-4 md:p-6 max-w-md w-full border border-white/20 max-h-[80vh] overflow-y-auto"
            >
              <h3 className="text-lg md:text-xl font-bold text-white mb-3 md:mb-4">Favorite Numbers</h3>
              
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {favoriteNumbers.map((fav, idx) => (
                  <div key={idx} className="bg-white/10 rounded-lg p-2 md:p-3 border border-white/10">
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="text-white text-xs md:text-sm font-bold truncate">{fav.name}</p>
                        <p className="text-yellow-400 text-[10px] md:text-xs truncate">
                          {fav.numbers.map(row => row.join('')).join('-')}
                        </p>
                      </div>
                      <div className="flex gap-1.5 md:gap-2 flex-shrink-0">
                        <button
                          onClick={() => loadFavoriteNumbers(fav)}
                          className="px-2 md:px-3 py-1 bg-green-500 hover:bg-green-600 rounded text-white text-[10px] md:text-xs font-bold transition-colors"
                        >
                          Load
                        </button>
                        <button
                          onClick={() => setFavoriteNumbers(favoriteNumbers.filter((_, i) => i !== idx))}
                          className="p-1 bg-red-500 hover:bg-red-600 rounded transition-colors"
                        >
                          <Trash2 className="w-3 h-3 md:w-4 md:h-4 text-white" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
              <button
                onClick={() => setShowFavoritesModal(false)}
                className="w-full mt-3 md:mt-4 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white font-bold text-sm md:text-base transition-colors"
              >
                Close
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Quick Buy Confirmation Modal */}
      <AnimatePresence>
        {showQuickBuyModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[70] flex items-center justify-center p-4"
            onClick={() => setShowQuickBuyModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-gradient-to-br from-purple-900 to-blue-900 rounded-2xl p-6 md:p-8 max-w-md w-full border-2 border-yellow-400/50 shadow-2xl"
            >
              <div className="text-center mb-6">
                <div className="w-16 h-16 md:w-20 md:h-20 mx-auto mb-4 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center">
                  <span className="text-3xl md:text-4xl">⚡</span>
                </div>
                <h2 className="text-2xl md:text-3xl font-bold text-white mb-2">Confirm Quick Buy</h2>
                <p className="text-white/70 text-sm md:text-base">
                  {addMode === 'current' ? 'Purchase current ticket' : `Purchase ${calculateTicketCount()} tickets`} instantly
                </p>
              </div>

              <div className="bg-black/40 rounded-xl p-4 mb-6 border border-white/10">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-white/70 text-sm">Tickets:</span>
                  <span className="text-white font-bold">{calculateTicketCount()}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/70 text-sm">Total Cost:</span>
                  <span className="text-yellow-400 font-bold text-xl">${calculateQuickBuyTotal().toFixed(2)}</span>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowQuickBuyModal(false)}
                  className="flex-1 px-4 py-3 bg-white/10 hover:bg-white/20 rounded-lg text-white font-bold transition-all"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmQuickBuy}
                  className="flex-1 px-4 py-3 bg-gradient-to-r from-yellow-400 to-orange-500 hover:from-yellow-500 hover:to-orange-600 rounded-lg text-black font-bold transition-all shadow-lg shadow-yellow-400/30"
                >
                  Confirm Purchase
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Purchase Success Modal */}
      <AnimatePresence>
        {purchaseSuccess && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[70] flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.5, opacity: 0 }}
              className="bg-gradient-to-br from-green-900 to-emerald-900 rounded-2xl p-6 md:p-8 max-w-md w-full border-2 border-green-400/50 shadow-2xl text-center"
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                className="w-20 h-20 md:w-24 md:h-24 mx-auto mb-4 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center"
              >
                <span className="text-4xl md:text-5xl">✓</span>
              </motion.div>
              <h2 className="text-2xl md:text-3xl font-bold text-white mb-2">Purchase Successful!</h2>
              <p className="text-white/70 text-sm md:text-base mb-4">
                Your {calculateTicketCount()} {calculateTicketCount() === 1 ? 'ticket has' : 'tickets have'} been purchased
              </p>
              <div className="bg-black/40 rounded-xl p-4 border border-white/10">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-white/70">Tickets:</span>
                  <span className="text-white font-bold">{calculateTicketCount()}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/70">Total:</span>
                  <span className="text-green-400 font-bold text-lg">${calculateQuickBuyTotal().toFixed(2)}</span>
                </div>
              </div>
              <p className="text-white/50 text-xs mt-4">
                Resetting board...
              </p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Profile Drawer */}
      <ProfileDrawer isMobile={isMobile} />
    </div>
  );
};