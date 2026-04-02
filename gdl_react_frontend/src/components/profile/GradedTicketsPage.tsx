import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Calendar, Filter, ChevronDown, ChevronUp, ChevronLeft, ChevronRight, Loader2, Trophy, XCircle, TrendingUp, TrendingDown } from 'lucide-react';
import { useProfile, Ticket } from '../../contexts/ProfileContext';
import { Calendar as CalendarComponent } from '../ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '../ui/popover';
import { Button } from '../ui/button';

const statesList = ['NY', 'CA', 'TX', 'FL', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI'];

const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }).format(date);
};

type OutcomeFilter = 'all' | 'win' | 'loss';

export const GradedTicketsPage: React.FC = () => {
  const { tickets } = useProfile();
  const gradedTickets = tickets.filter(t => t.status === 'graded');
  
  // Date range state
  const [startDate, setStartDate] = useState<Date>(new Date(Date.now() - 30 * 86400000)); // 30 days back
  const [endDate, setEndDate] = useState<Date>(new Date());
  
  // Filter state - default to show winners
  const [outcomeFilter, setOutcomeFilter] = useState<OutcomeFilter>('win');
  const [selectedPickTypes, setSelectedPickTypes] = useState<number[]>([2, 3, 4, 5]);
  const [selectedStates, setSelectedStates] = useState<string[]>(statesList);
  const [showPickTypeFilter, setShowPickTypeFilter] = useState(false);
  const [showStateFilter, setShowStateFilter] = useState(false);

  // Filter tickets
  const filteredTickets = useMemo(() => {
    return gradedTickets.filter(ticket => {
      const ticketDate = new Date(ticket.createdAt);
      const isInDateRange = ticketDate >= startDate && ticketDate <= endDate;
      const isPickTypeMatch = selectedPickTypes.includes(ticket.pickType);
      const isStateMatch = selectedStates.includes(ticket.state);
      const isOutcomeMatch = outcomeFilter === 'all' || ticket.outcome === outcomeFilter;
      
      return isInDateRange && isPickTypeMatch && isStateMatch && isOutcomeMatch;
    });
  }, [gradedTickets, startDate, endDate, selectedPickTypes, selectedStates, outcomeFilter]);

  // Group tickets by pick type
  const groupedTickets = useMemo(() => {
    const groups: { [key: number]: Ticket[] } = {};
    [2, 3, 4, 5].forEach(pickType => {
      groups[pickType] = filteredTickets.filter(t => t.pickType === pickType);
    });
    return groups;
  }, [filteredTickets]);

  // Calculate stats
  const stats = useMemo(() => {
    const wins = filteredTickets.filter(t => t.outcome === 'win');
    const losses = filteredTickets.filter(t => t.outcome === 'loss');
    const totalWinAmount = wins.reduce((sum, t) => sum + (t.winAmount || 0), 0);
    const totalBetAmount = filteredTickets.reduce((sum, t) => sum + t.betAmount, 0);
    const netProfit = totalWinAmount - totalBetAmount;
    
    return {
      totalTickets: filteredTickets.length,
      wins: wins.length,
      losses: losses.length,
      totalWinAmount,
      totalBetAmount,
      netProfit,
      winRate: filteredTickets.length > 0 ? (wins.length / filteredTickets.length * 100).toFixed(1) : '0',
    };
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

  // Collapsible state for each pick type
  const [expandedPickTypes, setExpandedPickTypes] = useState<number[]>([2, 3, 4, 5]);

  const togglePickTypeExpansion = (pickType: number) => {
    setExpandedPickTypes(prev =>
      prev.includes(pickType)
        ? prev.filter(p => p !== pickType)
        : [...prev, pickType]
    );
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
            Graded Tickets
          </h1>
          <p className="text-white/70">Review your betting history and results</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-4">
            <div className="text-white/70 text-sm mb-1">Total Tickets</div>
            <div className="text-2xl font-bold text-white">{stats.totalTickets}</div>
          </div>
          <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-xl p-4">
            <div className="text-green-300 text-sm mb-1 flex items-center gap-1">
              <Trophy size={14} /> Wins
            </div>
            <div className="text-2xl font-bold text-green-300">{stats.wins}</div>
            <div className="text-xs text-green-300/70 mt-1">${stats.totalWinAmount.toFixed(2)}</div>
          </div>
          <div className="bg-gradient-to-br from-red-500/20 to-pink-500/20 border border-red-500/30 rounded-xl p-4">
            <div className="text-red-300 text-sm mb-1">Losses</div>
            <div className="text-2xl font-bold text-red-300">{stats.losses}</div>
          </div>
          <div className={`rounded-xl p-4 ${
            stats.netProfit >= 0 
              ? 'bg-gradient-to-br from-yellow-500/20 to-orange-500/20 border border-yellow-500/30' 
              : 'bg-gradient-to-br from-red-500/20 to-pink-500/20 border border-red-500/30'
          }`}>
            <div className="text-white/90 text-sm mb-1 flex items-center gap-1">
              {stats.netProfit >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
              Net Profit/Loss
            </div>
            <div className={`text-2xl font-bold ${stats.netProfit >= 0 ? 'text-yellow-300' : 'text-red-300'}`}>
              ${Math.abs(stats.netProfit).toFixed(2)}
            </div>
            <div className="text-xs text-white/60 mt-1">Win Rate: {stats.winRate}%</div>
          </div>
        </div>

        {/* Filters Section */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-4 md:p-6 mb-6">
          {/* Outcome Filter */}
          <div className="mb-4">
            <label className="block text-white/90 font-semibold mb-3">Show</label>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setOutcomeFilter('all')}
                className={`px-4 py-2 rounded-full font-semibold transition-all ${
                  outcomeFilter === 'all'
                    ? 'bg-gradient-to-r from-purple-400 to-pink-500 text-white shadow-lg shadow-purple-500/30'
                    : 'bg-white/10 text-white/70 hover:bg-white/20'
                }`}
              >
                All Tickets
              </button>
              <button
                onClick={() => setOutcomeFilter('win')}
                className={`px-4 py-2 rounded-full font-semibold transition-all ${
                  outcomeFilter === 'win'
                    ? 'bg-gradient-to-r from-green-400 to-emerald-500 text-white shadow-lg shadow-green-500/30'
                    : 'bg-white/10 text-white/70 hover:bg-white/20'
                }`}
              >
                Winners Only
              </button>
              <button
                onClick={() => setOutcomeFilter('loss')}
                className={`px-4 py-2 rounded-full font-semibold transition-all ${
                  outcomeFilter === 'loss'
                    ? 'bg-gradient-to-r from-red-400 to-pink-500 text-white shadow-lg shadow-red-500/30'
                    : 'bg-white/10 text-white/70 hover:bg-white/20'
                }`}
              >
                Losses Only
              </button>
            </div>
          </div>

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
          Showing {filteredTickets.length} ticket{filteredTickets.length !== 1 ? 's' : ''}
        </div>

        {/* Grouped Tickets Display */}
        {[2, 3, 4, 5].map(pickType => {
          const tickets = groupedTickets[pickType];
          if (tickets.length === 0) return null;
          
          const isExpanded = expandedPickTypes.includes(pickType);

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
                  <table className="w-full min-w-[900px]">
                    <thead>
                      <tr className="bg-white/5 border-b border-white/10">
                        <th className="px-2 md:px-4 py-2 md:py-3 text-left text-white/90 font-semibold text-xs md:text-base whitespace-nowrap">Ticket #</th>
                        <th className="px-2 md:px-4 py-2 md:py-3 text-left text-white/90 font-semibold text-xs md:text-base whitespace-nowrap">Lottery</th>
                        <th className="px-2 md:px-4 py-2 md:py-3 text-left text-white/90 font-semibold text-xs md:text-base whitespace-nowrap">State</th>
                        <th className="px-2 md:px-4 py-2 md:py-3 text-left text-white/90 font-semibold text-xs md:text-base whitespace-nowrap">Numbers</th>
                        <th className="px-2 md:px-4 py-2 md:py-3 text-left text-white/90 font-semibold text-xs md:text-base whitespace-nowrap">Type</th>
                        <th className="px-2 md:px-4 py-2 md:py-3 text-left text-white/90 font-semibold text-xs md:text-base whitespace-nowrap">Bet</th>
                        <th className="px-2 md:px-4 py-2 md:py-3 text-left text-white/90 font-semibold text-xs md:text-base whitespace-nowrap">Result</th>
                        <th className="px-2 md:px-4 py-2 md:py-3 text-left text-white/90 font-semibold text-xs md:text-base whitespace-nowrap">Win Amount</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tickets.map((ticket, index) => (
                        <motion.tr
                          key={ticket.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: Math.min(index * 0.02, 0.5) }}
                          className={`border-b border-white/5 hover:bg-white/5 transition-colors ${
                            ticket.outcome === 'win' ? 'bg-green-500/5' : ''
                          }`}
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
                              {/* Bonus Bets Info */}
                              {ticket.bonusBets && ticket.bonusBets.length > 0 && (
                                <div className="text-[9px] md:text-[10px] text-yellow-300 italic whitespace-nowrap">
                                  +{ticket.bonusBets.length} bonus {ticket.bonusBets.length === 1 ? 'bet' : 'bets'}
                                </div>
                              )}
                            </div>
                          </td>
                          <td className="px-2 md:px-4 py-2 md:py-3 text-white capitalize text-xs md:text-base whitespace-nowrap">{ticket.betType}</td>
                          <td className="px-2 md:px-4 py-2 md:py-3 text-white/80 text-xs md:text-base whitespace-nowrap">${ticket.betAmount.toFixed(2)}</td>
                          <td className="px-2 md:px-4 py-2 md:py-3">
                            {ticket.outcome === 'win' ? (
                              <span className="px-2 md:px-3 py-0.5 md:py-1 bg-green-500/30 text-green-300 rounded-full text-[10px] md:text-sm font-bold flex items-center gap-1 w-fit">
                                <Trophy size={12} className="md:w-[14px] md:h-[14px]" /> WIN
                              </span>
                            ) : (
                              <span className="px-2 md:px-3 py-0.5 md:py-1 bg-red-500/30 text-red-300 rounded-full text-[10px] md:text-sm font-bold w-fit">
                                LOSS
                              </span>
                            )}
                          </td>
                          <td className="px-2 md:px-4 py-2 md:py-3 font-bold text-xs md:text-base whitespace-nowrap">
                            {ticket.outcome === 'win' && ticket.winAmount ? (
                              <span className="text-green-400">${ticket.winAmount.toFixed(2)}</span>
                            ) : (
                              <span className="text-white/40">-</span>
                            )}
                          </td>
                        </motion.tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </motion.div>
              )}
            </div>
          );
        })}

        {/* Empty State */}
        {filteredTickets.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📊</div>
            <h3 className="text-xl font-bold text-white mb-2">No Graded Tickets</h3>
            <p className="text-white/60">No tickets found matching your filters.</p>
          </div>
        )}
      </motion.div>
    </div>
  );
};