import React, { useState, useEffect } from "react";
import { motion } from "motion/react";
import { Clock, DollarSign } from "lucide-react";

interface LotteryDraw {
  name: string;
  nextDraw: Date;
  jackpot: string;
  color: string;
  emoji: string;
}

interface DrawCountdownProps {
  onPlayNow?: () => void;
}

export function DrawCountdown({ onPlayNow }: DrawCountdownProps) {
  const [timeLeft, setTimeLeft] = useState<{ [key: string]: string }>({});

  // Mock upcoming draws (in a real app, these would come from an API)
  const upcomingDraws: LotteryDraw[] = [
    {
      name: "Powerball",
      nextDraw: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000), // 2 days from now
      jackpot: "$485 Million",
      color: "from-red-500 to-pink-600",
      emoji: "🔴"
    },
    {
      name: "Mega Millions",
      nextDraw: new Date(Date.now() + 4 * 24 * 60 * 60 * 1000), // 4 days from now
      jackpot: "$312 Million",
      color: "from-yellow-400 to-orange-500",
      emoji: "🟡"
    },
    {
      name: "EuroMillions",
      nextDraw: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000), // 1 day from now
      jackpot: "€127 Million",
      color: "from-blue-500 to-purple-600",
      emoji: "🔵"
    }
  ];

  useEffect(() => {
    const updateCountdowns = () => {
      const newTimeLeft: { [key: string]: string } = {};
      
      upcomingDraws.forEach((draw) => {
        const now = new Date().getTime();
        const distance = draw.nextDraw.getTime() - now;

        if (distance > 0) {
          const days = Math.floor(distance / (1000 * 60 * 60 * 24));
          const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
          const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
          const seconds = Math.floor((distance % (1000 * 60)) / 1000);

          newTimeLeft[draw.name] = `${days}d ${hours}h ${minutes}m ${seconds}s`;
        } else {
          newTimeLeft[draw.name] = "Draw in progress!";
        }
      });

      setTimeLeft(newTimeLeft);
    };

    updateCountdowns();
    const interval = setInterval(updateCountdowns, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-4 md:p-8"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
    >
      <div className="flex items-center gap-2 md:gap-3 mb-4 md:mb-6">
        <Clock className="text-green-400" size={24} />
        <h3 className="text-xl md:text-3xl font-bold text-white">
          Next Draws Countdown
        </h3>
      </div>

      <p className="text-white/70 mb-4 md:mb-8 text-sm md:text-base">
        Don't miss out! Here are the upcoming major lottery draws and their current jackpots.
      </p>

      <div className="space-y-3 md:space-y-4">
        {upcomingDraws.map((draw, idx) => (
          <motion.div
            key={draw.name}
            className="bg-gradient-to-r from-slate-900/50 to-slate-800/50 border border-white/10 rounded-xl p-4 md:p-6 hover:border-white/20 transition-all"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            whileHover={{ scale: 1.02 }}
          >
            <div className="flex items-start justify-between mb-3 md:mb-4">
              <div className="flex items-center gap-2 md:gap-3">
                <span className="text-2xl md:text-4xl">{draw.emoji}</span>
                <div>
                  <h4 className="text-base md:text-xl font-bold text-white">{draw.name}</h4>
                  <p className="text-white/60 text-xs md:text-sm">
                    {draw.nextDraw.toLocaleDateString('en-US', {
                      weekday: 'long',
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
              </div>
              
              <div className="text-right">
                <div className="flex items-center gap-1 md:gap-2 mb-1">
                  <DollarSign className="text-green-400" size={16} />
                  <span className={`text-lg md:text-2xl font-bold bg-gradient-to-r ${draw.color} bg-clip-text text-transparent`}>
                    {draw.jackpot}
                  </span>
                </div>
                <p className="text-white/50 text-xs">Est. Jackpot</p>
              </div>
            </div>

            {/* Countdown Display */}
            <div className="bg-black/30 rounded-lg p-3 md:p-4">
              <div className="flex items-center justify-between">
                <span className="text-white/70 text-xs md:text-base">Time Until Draw:</span>
                <motion.span
                  className="text-cyan-400 font-mono font-bold text-sm md:text-lg"
                  key={timeLeft[draw.name]}
                  initial={{ scale: 1.1, color: "#22d3ee" }}
                  animate={{ scale: 1, color: "#22d3ee" }}
                  transition={{ duration: 0.3 }}
                >
                  {timeLeft[draw.name] || "Calculating..."}
                </motion.span>
              </div>
            </div>

            {/* Play Now Button */}
            <motion.button
              className={`w-full mt-3 md:mt-4 px-4 md:px-6 py-2.5 md:py-3 bg-gradient-to-r ${draw.color} rounded-full font-bold text-white text-sm md:text-base shadow-lg transition-all hover:brightness-110 active:scale-95`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onPlayNow}
            >
              Bet on {draw.name}
            </motion.button>
          </motion.div>
        ))}
      </div>

      <motion.div
        className="mt-4 md:mt-6 bg-gradient-to-r from-purple-900/30 to-pink-900/30 border border-purple-500/30 rounded-xl p-3 md:p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <p className="text-white/80 text-xs md:text-sm text-center">
          <span className="font-bold text-purple-400">Pro Tip:</span> Jackpots grow larger when not won! 
          The bigger the jackpot, the more excitement, but remember the odds stay the same.
        </p>
      </motion.div>
    </motion.div>
  );
}