import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface SimpleCarouselProps {
  children: React.ReactNode[];
  autoplay?: boolean;
  autoplaySpeed?: number;
  slidesToShow?: number;
  responsive?: Array<{
    breakpoint: number;
    settings: {
      slidesToShow: number;
    };
  }>;
}

export function SimpleCarousel({ 
  children, 
  autoplay = true, 
  autoplaySpeed = 4000,
  slidesToShow = 3,
  responsive = []
}: SimpleCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [slidesPerView, setSlidesPerView] = useState(slidesToShow);
  const totalSlides = children.length;
  const maxIndex = Math.max(0, totalSlides - slidesPerView);

  // Handle responsive breakpoints
  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      let newSlidesPerView = slidesToShow;
      
      // Sort responsive settings by breakpoint (descending)
      const sortedResponsive = [...responsive].sort((a, b) => b.breakpoint - a.breakpoint);
      
      for (const setting of sortedResponsive) {
        if (width <= setting.breakpoint) {
          newSlidesPerView = setting.settings.slidesToShow;
        }
      }
      
      setSlidesPerView(newSlidesPerView);
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [slidesToShow, responsive]);

  // Autoplay functionality
  useEffect(() => {
    if (!autoplay) return;

    const interval = setInterval(() => {
      setCurrentIndex((prev) => {
        const next = prev + 1;
        return next > maxIndex ? 0 : next;
      });
    }, autoplaySpeed);

    return () => clearInterval(interval);
  }, [autoplay, autoplaySpeed, maxIndex]);

  const goToSlide = (index: number) => {
    setCurrentIndex(Math.max(0, Math.min(index, maxIndex)));
  };

  const goToPrevious = () => {
    setCurrentIndex((prev) => (prev === 0 ? maxIndex : prev - 1));
  };

  const goToNext = () => {
    setCurrentIndex((prev) => (prev >= maxIndex ? 0 : prev + 1));
  };

  // Calculate the number of dots
  const dotCount = Math.ceil(totalSlides / slidesPerView);

  return (
    <div className="relative">
      {/* Main carousel container */}
      <div className="overflow-hidden">
        <motion.div
          className="flex"
          animate={{
            x: `-${currentIndex * (100 / slidesPerView)}%`,
          }}
          transition={{
            type: "spring",
            stiffness: 300,
            damping: 30,
          }}
        >
          {children.map((child, index) => (
            <div
              key={index}
              className="flex-shrink-0"
              style={{ width: `${100 / slidesPerView}%` }}
            >
              {child}
            </div>
          ))}
        </motion.div>
      </div>

      {/* Navigation arrows - hidden on mobile */}
      {slidesPerView < totalSlides && (
        <>
          <button
            onClick={goToPrevious}
            className="hidden md:flex absolute left-0 top-1/2 -translate-y-1/2 -translate-x-12 lg:-translate-x-14 z-10 w-10 h-10 lg:w-12 lg:h-12 items-center justify-center bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20 rounded-full text-white transition-all"
            aria-label="Previous slide"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>
          <button
            onClick={goToNext}
            className="hidden md:flex absolute right-0 top-1/2 -translate-y-1/2 translate-x-12 lg:translate-x-14 z-10 w-10 h-10 lg:w-12 lg:h-12 items-center justify-center bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20 rounded-full text-white transition-all"
            aria-label="Next slide"
          >
            <ChevronRight className="w-6 h-6" />
          </button>
        </>
      )}

      {/* Dots navigation */}
      <div className="flex justify-center items-center space-x-2 mt-8">
        {Array.from({ length: dotCount }).map((_, index) => (
          <button
            key={index}
            onClick={() => goToSlide(index * Math.floor(slidesPerView))}
            className={`transition-all ${
              Math.floor(currentIndex / slidesPerView) === index
                ? 'w-8 h-2 bg-cyan-500'
                : 'w-2 h-2 bg-white/30 hover:bg-white/50'
            } rounded-full`}
            aria-label={`Go to slide ${index + 1}`}
          />
        ))}
      </div>
    </div>
  );
}
