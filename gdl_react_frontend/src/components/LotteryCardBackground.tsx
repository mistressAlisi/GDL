import React from "react";
import { motion } from "motion/react";

interface LotteryCardBackgroundProps {
  variant?: 'default' | 'premium';
}

export function LotteryCardBackground({ variant = 'default' }: LotteryCardBackgroundProps) {
  return (
    <>
      {/* Rich casino-style gradient with deeper colors */}
      <div 
        className="absolute inset-0"
        style={{
          background: variant === 'premium'
            ? "linear-gradient(135deg, #0a0510 0%, #150820 25%, #1f0d35 50%, #2a1148 75%, #35155d 100%)"
            : "linear-gradient(135deg, #1a0b2e 0%, #2d1654 25%, #4a1d7e 50%, #6b2aa8 75%, #8b3fc9 100%)"
        }}
      />
      
      {/* Gold Vegas-style border accent */}
      <div 
        className="absolute inset-0 rounded-xl"
        style={{
          background: variant === 'premium'
            ? "linear-gradient(135deg, rgba(251, 191, 36, 0.5) 0%, transparent 40%, transparent 60%, rgba(251, 191, 36, 0.5) 100%)"
            : "linear-gradient(135deg, rgba(251, 191, 36, 0.3) 0%, transparent 40%, transparent 60%, rgba(251, 191, 36, 0.3) 100%)",
          border: variant === 'premium'
            ? "2px solid rgba(251, 191, 36, 0.6)"
            : "2px solid rgba(251, 191, 36, 0.4)"
        }}
      />
      
      {/* Animated shimmer effect */}
      <motion.div 
        className="absolute inset-0 opacity-30 rounded-xl"
        style={{
          background: "linear-gradient(110deg, transparent 0%, transparent 40%, rgba(251, 191, 36, 0.8) 50%, transparent 60%, transparent 100%)",
          backgroundSize: "200% 100%"
        }}
        animate={{
          backgroundPosition: ["200% 0", "-200% 0"]
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "linear"
        }}
      />
      
      {/* Red/Pink casino accent glow */}
      <div 
        className="absolute inset-0 opacity-20 rounded-xl"
        style={{
          background: "radial-gradient(circle at 20% 80%, rgba(236, 72, 153, 0.6) 0%, transparent 50%)"
        }}
      />
      
      {/* Enhanced glass morphism with stronger border */}
      <div 
        className="absolute inset-0 rounded-xl"
        style={{
          background: variant === 'premium' ? "rgba(255, 255, 255, 0.05)" : "rgba(255, 255, 255, 0.08)",
          backdropFilter: "blur(8px)",
          border: variant === 'premium' 
            ? "1px solid rgba(255, 255, 255, 0.4)"
            : "1px solid rgba(255, 255, 255, 0.3)",
          boxShadow: variant === 'premium'
            ? "0 8px 32px rgba(139, 92, 246, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.3), 0 0 40px rgba(251, 191, 36, 0.3)"
            : "0 8px 32px rgba(139, 92, 246, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2)"
        }}
      />
      
      {/* Corner highlights for premium feel */}
      <div className="absolute top-0 left-0 w-12 h-12 rounded-tl-xl opacity-40"
        style={{
          background: variant === 'premium'
            ? "radial-gradient(circle at top left, rgba(251, 191, 36, 1), transparent 70%)"
            : "radial-gradient(circle at top left, rgba(251, 191, 36, 0.8), transparent 70%)"
        }}
      />
      <div className="absolute bottom-0 right-0 w-12 h-12 rounded-br-xl opacity-40"
        style={{
          background: variant === 'premium'
            ? "radial-gradient(circle at bottom right, rgba(251, 191, 36, 1), transparent 70%)"
            : "radial-gradient(circle at bottom right, rgba(251, 191, 36, 0.8), transparent 70%)"
        }}
      />
    </>
  );
}