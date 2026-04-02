import React, { useState, useMemo, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Calendar, Filter, ChevronDown, ChevronUp, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';
import { useProfile, Ticket } from '../../contexts/ProfileContext';
import { Calendar as CalendarComponent } from '../ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '../ui/popover';
import { Button } from '../ui/button';
import { bonusPacks } from '../../data/lotteryData';

const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }).format(date);
};

export const OpenTicketsPage: React.FC = () => {
  const { tickets } = useProfile();
  const openTickets = tickets.filter(t => t.status === 'open');
  
  // Dynamically get all unique states from open tickets
  const statesList = useMemo(() => {
    const uniqueStates = Array.from(new Set(openTickets.map(t => t.state))).sort();
    return uniqueStates.length > 0 ? uniqueStates : ['NY', 'CA', 'TX', 'FL', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI', 'NJ'];
  }, [openTickets]);
  
  // Date range state - default to 30 days back and 30 days forward to catch all tickets
  const [startDate, setStartDate] = useState<Date>(new Date(Date.now() - 30 * 86400000));
  const [endDate, setEndDate] = useState<Date>(new Date(Date.now() + 30 * 86400000));
  const [showCalendar, setShowCalendar] = useState(false);
  
  // Filter state - Initialize with all available states
  const [selectedPickTypes, setSelectedPickTypes] = useState<number[]>([2, 3, 4, 5]);
  const [selectedStates, setSelectedStates] = useState<string[]>([]);
  const [showPickTypeFilter, setShowPickTypeFilter] = useState(false);
  const [showStateFilter, setShowStateFilter] = useState(false);
  
  // Initialize selectedStates only once when statesList is first populated
  const hasInitialized = useRef(false);
  React.useEffect(() => {
    if (!hasInitialized.current && statesList.length > 0) {
      setSelectedStates(statesList);
      hasInitialized.current = true;
    }
  }, [statesList]);
  
  // Collapsible state for each pick type
  const [expandedPickTypes, setExpandedPickTypes] = useState<number[]>([2, 3, 4, 5]);
  
  // Track which tickets have expanded bonus bets
  const [expandedBonusBets, setExpandedBonusBets] = useState<Set<string>>(new Set());
  
  // Pagination state per pick type
  const [currentPages, setCurrentPages] = useState<{ [key: number]: number }>({
    2: 1, 3: 1, 4: 1, 5: 1
  });
  const [itemsPerPage, setItemsPerPage] = useState(50);
  const [isLoading, setIsLoading] = useState(false);

  // Filter tickets based on selections
  const filteredTickets = useMemo(() => {
    return openTickets.filter(ticket => {
      const ticketDate = new Date(ticket.createdAt);
      const isInDateRange = ticketDate >= startDate && ticketDate <= endDate;
      const isPickTypeMatch = selectedPickTypes.includes(ticket.pickType);
      const isStateMatch = selectedStates.includes(ticket.state);
      
      return isInDateRange && isPickTypeMatch && isStateMatch;
    });
  }, [openTickets, startDate, endDate, selectedPickTypes, selectedStates]);

  // Group tickets by pick type
  const groupedTickets = useMemo(() => {
    const groups: { [key: number]: Ticket[] } = {};
    [2, 3, 4, 5].forEach(pickType => {
      groups[pickType] = filteredTickets.filter(t => t.pickType === pickType);
    });
    return groups;
  }, [filteredTickets]);

  const togglePickType = (pickType: number) => {
    setSelectedPickTypes(prev => 
      prev.includes(pickType) 
        ? prev.filter(p => p !== pickType)
        : [...prev, pickType]
    );
  };

  const toggleState = (state: string) => {
    setSelectedStates(prev => 
      prev.includes(state)
        ? prev.filter(s => s !== state)
        : [...prev, state]
    );
  };

  const togglePickTypeExpansion = (pickType: number) => {
    setExpandedPickTypes(prev =>
      prev.includes(pickType)
        ? prev.filter(p => p !== pickType)
        : [...prev, pickType]
    );
  };

  const toggleBonusBets = (ticketId: string) => {
    setExpandedBonusBets(prev => {
      const newSet = new Set(prev);
      if (newSet.has(ticketId)) {
        newSet.delete(ticketId);
      } else {
        newSet.add(ticketId);
      }
      return newSet;
    });
  };

  const handlePageChange = (pickType: number, page: number) => {
    setCurrentPages(prev => ({
      ...prev,
      [pickType]: page
    }));
  };

  const handleItemsPerPageChange = (value: number) => {
    setItemsPerPage(value);
    setCurrentPages({ 2: 1, 3: 1, 4: 1, 5: 1 });
  };

  return (
    <div className="w-full h-full overflow-y-auto p-4 md:p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-7xl mx-auto"
      >
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-yellow-200 via-yellow-400 to-yellow-200 bg-clip-text text-transparent mb-2">
            Open Tickets
          </h1>
          <p className="text-white/70">View and manage your active bets</p>
        </div>

        {/* Filters Section */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-4 md:p-6 mb-6">
          {/* Date Range Filter */}
          <div className="mb-4">
            <label className="block text-white/90 font-semibold mb-3">Date Range</label>
            <div className="flex flex-col md:flex-row gap-3">
              <div className="flex-1">
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className="w-full justify-start text-left font-normal bg-white/5 border-white/20 hover:bg-white/10 text-white"
                    >
                      <Calendar className="mr-2 h-4 w-4" />
                      {formatDate(startDate)}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0 bg-slate-900/95 border-white/20">
                    <CalendarComponent
                      mode="single"
                      selected={startDate}
                      onSelect={(date) => date && setStartDate(date)}
                      initialFocus
                      className="rounded-md"
                    />
                  </PopoverContent>
                </Popover>
              </div>
              <div className="flex items-center justify-center text-white/60">to</div>
              <div className="flex-1">
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className="w-full justify-start text-left font-normal bg-white/5 border-white/20 hover:bg-white/10 text-white"
                    >
                      <Calendar className="mr-2 h-4 w-4" />
                      {formatDate(endDate)}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0 bg-slate-900/95 border-white/20">
                    <CalendarComponent
                      mode="single"
                      selected={endDate}
                      onSelect={(date) => date && setEndDate(date)}
                      initialFocus
                      className="rounded-md"
                    />
                  </PopoverContent>
                </Popover>
              </div>
            </div>
          </div>

          {/* Pick Type Filter */}
          <div className="mb-4">
            <button
              onClick={() => setShowPickTypeFilter(!showPickTypeFilter)}
              className="flex items-center justify-between w-full text-white/90 font-semibold mb-2 hover:text-white transition-colors"
            >
              <span>Filter by Pick Type</span>
              {showPickTypeFilter ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </button>
            {showPickTypeFilter && (
              <div className="flex flex-wrap gap-2">
                {[2, 3, 4, 5].map(pickType => (
                  <button
                    key={pickType}
                    onClick={() => togglePickType(pickType)}
                    className={`px-4 py-2 rounded-full font-semibold transition-all ${
                      selectedPickTypes.includes(pickType)
                        ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-black shadow-lg shadow-yellow-500/30'
                        : 'bg-white/10 text-white/70 hover:bg-white/20'
                    }`}
                  >
                    Pick {pickType}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* State Filter */}
          <div>
            <button
              onClick={() => setShowStateFilter(!showStateFilter)}
              className="flex items-center justify-between w-full text-white/90 font-semibold mb-2 hover:text-white transition-colors"
            >
              <span>Filter by State</span>
              {showStateFilter ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </button>
            {showStateFilter && (
              <div className="flex flex-wrap gap-2">
                {statesList.map(state => (
                  <button
                    key={state}
                    onClick={() => toggleState(state)}
                    className={`px-3 py-1.5 rounded-lg font-semibold text-sm transition-all ${
                      selectedStates.includes(state)
                        ? 'bg-gradient-to-r from-cyan-400 to-blue-500 text-white shadow-lg shadow-cyan-500/30'
                        : 'bg-white/10 text-white/70 hover:bg-white/20'
                    }`}
                  >
                    {state}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Results Count */}
        <div className="mb-4 text-white/70">
          Showing {filteredTickets.length} of {openTickets.length} total open ticket{openTickets.length !== 1 ? 's' : ''}
        </div>

        {/* Grouped Tickets Display */}
        {[2, 3, 4, 5].map(pickType => {
          const tickets = groupedTickets[pickType];
          if (tickets.length === 0) return null;
          
          const isExpanded = expandedPickTypes.includes(pickType);
          const currentPage = currentPages[pickType];
          const totalPages = Math.ceil(tickets.length / itemsPerPage);
          const startIndex = (currentPage - 1) * itemsPerPage;
          const endIndex = startIndex + itemsPerPage;
          const paginatedTickets = tickets.slice(startIndex, endIndex);

          return (
            <div key={pickType} className="mb-6">
              <button
                onClick={() => togglePickTypeExpansion(pickType)}
                className="w-full flex items-center justify-between bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl px-6 py-4 mb-4 hover:bg-white/15 transition-all"
              >
                <h2 className="text-2xl font-bold text-white">
                  Pick {pickType} ({tickets.length})
                </h2>
                {isExpanded ? <ChevronUp size={24} className="text-white" /> : <ChevronDown size={24} className="text-white" />}
              </button>
              
              {isExpanded && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl overflow-hidden"
                >
                  <div className="overflow-x-auto lottery-scrollbar">
                    <table className="w-full min-w-[800px]">
                      <thead>
                        <tr className="bg-white/5 border-b border-white/10">
                          <th className="px-2 md:px-4 py-2 md:py-3 text-left text-white/90 font-semibold text-xs md:text-base whitespace-nowrap">Ticket #</th>
                          <th className="px-2 md:px-4 py-2 md:py-3 text-left text-white/90 font-semibold text-xs md:text-base whitespace-nowrap">Lottery</th>
                          <th className="px-2 md:px-4 py-2 md:py-3 text-left text-white/90 font-semibold text-xs md:text-base whitespace-nowrap">State</th>
                          <th className="px-2 md:px-4 py-2 md:py-3 text-left text-white/90 font-semibold text-xs md:text-base whitespace-nowrap">Numbers</th>
                          <th className="px-2 md:px-4 py-2 md:py-3 text-left text-white/90 font-semibold text-xs md:text-base whitespace-nowrap">Type</th>
                          <th className="px-2 md:px-4 py-2 md:py-3 text-left text-white/90 font-semibold text-xs md:text-base whitespace-nowrap">Bet</th>
                          <th className="px-2 md:px-4 py-2 md:py-3 text-left text-white/90 font-semibold text-xs md:text-base whitespace-nowrap">Draw Date</th>
                        </tr>
                      </thead>
                      <tbody>
                        {paginatedTickets.map((ticket, index) => {
                          const isBonusBetsExpanded = expandedBonusBets.has(ticket.id);
                          return (
                            <React.Fragment key={ticket.id}>
                              <motion.tr
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: Math.min(index * 0.02, 0.5) }}
                                className="border-b border-white/5 hover:bg-white/5 transition-colors"
                              >
                                <td className="px-2 md:px-4 py-2 md:py-3 text-white font-mono text-[10px] md:text-sm whitespace-nowrap">{ticket.ticketNumber}</td>
                                <td className="px-2 md:px-4 py-2 md:py-3 text-white text-xs md:text-base">{ticket.lottery}</td>
                                <td className="px-2 md:px-4 py-2 md:py-3">
                                  <span className="px-1.5 md:px-2 py-0.5 md:py-1 bg-cyan-500/20 text-cyan-300 rounded text-[10px] md:text-sm font-semibold">
                                    {ticket.state}
                                  </span>
                                </td>
                                <td className="px-2 md:px-4 py-2 md:py-3">
                                  <div className="flex flex-col gap-1">
                                    <div className="flex gap-1">
                                      {ticket.numbers.map((num, i) => (
                                        <div
                                          key={i}
                                          className="w-6 h-6 md:w-8 md:h-8 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center text-black font-bold text-[10px] md:text-sm shadow-lg"
                                        >
                                          {num}
                                        </div>
                                      ))}
                                    </div>
                                    {/* Bonus Bets Info - Clickable */}
                                    {ticket.bonusBets && ticket.bonusBets.length > 0 && (
                                      <button
                                        onClick={() => toggleBonusBets(ticket.id)}
                                        className="text-[9px] md:text-[10px] text-yellow-300 italic hover:text-yellow-200 transition-colors flex items-center gap-1 cursor-pointer whitespace-nowrap"
                                      >
                                        <span>+{ticket.bonusBets.length} bonus {ticket.bonusBets.length === 1 ? 'bet' : 'bets'}</span>
                                        {isBonusBetsExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                                      </button>
                                    )}
                                  </div>
                                </td>
                                <td className="px-2 md:px-4 py-2 md:py-3 text-white capitalize text-xs md:text-base whitespace-nowrap">{ticket.betType}</td>
                                <td className="px-2 md:px-4 py-2 md:py-3 text-yellow-400 font-bold text-xs md:text-base whitespace-nowrap">${ticket.betAmount.toFixed(2)}</td>
                                <td className="px-2 md:px-4 py-2 md:py-3 text-white/80 text-[10px] md:text-base whitespace-nowrap">{formatDate(new Date(ticket.drawDate))}</td>
                              </motion.tr>
                              
                              {/* Expandable Bonus Bets Details Row */}
                              <AnimatePresence>
                                {isBonusBetsExpanded && ticket.bonusBets && ticket.bonusBets.length > 0 && (
                                  <motion.tr
                                    key={`${ticket.id}-bonus`}
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="bg-gradient-to-r from-purple-900/20 to-pink-900/20 border-b border-white/5"
                                  >
                                    <td colSpan={7} className="px-4 py-4">
                                      <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4 border border-white/10">
                                        <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
                                          <span className="text-lg">💎</span>
                                          <span>Bonus Bets Details</span>
                                        </h4>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                          {ticket.bonusBets.map((bonusBet, idx) => {
                                            const bonusPack = bonusPacks.find(p => p.id === bonusBet.betId);
                                            return (
                                              <div 
                                                key={idx}
                                                className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-400/20 rounded-lg p-3"
                                              >
                                                <div className="flex items-start justify-between gap-2">
                                                  <div className="flex-1">
                                                    <h5 className="text-white font-semibold text-sm mb-1">
                                                      {bonusPack?.name || bonusBet.betId}
                                                    </h5>
                                                    <p className="text-white/60 text-xs mb-2">
                                                      {bonusPack?.description || 'Bonus bet'}
                                                    </p>
                                                  </div>
                                                  <div className="text-right">
                                                    <div className="text-yellow-400 font-bold text-sm">
                                                      ${bonusBet.amount.toFixed(2)}
                                                    </div>
                                                    <div className="text-white/40 text-xs">bet</div>
                                                  </div>
                                                </div>
                                              </div>
                                            );
                                          })}
                                        </div>
                                        <div className="mt-3 pt-3 border-t border-white/10 flex justify-between items-center">
                                          <span className="text-white/70 text-sm">Total Bonus Bets:</span>
                                          <span className="text-yellow-400 font-bold">
                                            ${ticket.bonusBets.reduce((sum, bb) => sum + bb.amount, 0).toFixed(2)}
                                          </span>
                                        </div>
                                      </div>
                                    </td>
                                  </motion.tr>
                                )}
                              </AnimatePresence>
                            </React.Fragment>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                  <div className="flex items-center justify-between px-4 py-3 bg-white/5 border-t border-white/10">
                    <div className="flex items-center">
                      <label className="text-white/70 mr-2">Items per page:</label>
                      <select
                        value={itemsPerPage}
                        onChange={(e) => handleItemsPerPageChange(Number(e.target.value))}
                        className="bg-white/10 text-white/70 border border-white/20 rounded px-2 py-1"
                      >
                        <option value={25}>25</option>
                        <option value={50}>50</option>
                        <option value={100}>100</option>
                      </select>
                    </div>
                    <div className="flex items-center">
                      <button
                        onClick={() => handlePageChange(pickType, currentPage - 1)}
                        disabled={currentPage === 1}
                        className="text-white/70 hover:text-white transition-colors"
                      >
                        <ChevronLeft size={20} />
                      </button>
                      <span className="mx-2 text-white/70">
                        Page {currentPage} of {totalPages}
                      </span>
                      <button
                        onClick={() => handlePageChange(pickType, currentPage + 1)}
                        disabled={currentPage === totalPages}
                        className="text-white/70 hover:text-white transition-colors"
                      >
                        <ChevronRight size={20} />
                      </button>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          );
        })}

        {/* Empty State */}
        {filteredTickets.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🎫</div>
            <h3 className="text-xl font-bold text-white mb-2">No Open Tickets</h3>
            <p className="text-white/60">No tickets found matching your filters.</p>
          </div>
        )}
      </motion.div>
    </div>
  );
};