import React from 'react';

const CyberCard = ({ children, className = '', glow = 'cyan', interactive = false }) => {
  const glowStyles = {
    cyan: 'hover:shadow-neon-cyan hover:border-cyber-neonCyan/50',
    purple: 'hover:shadow-neon-purple hover:border-cyber-neonPurple/50',
    pink: 'hover:shadow-neon-pink hover:border-cyber-neonPink/50',
  };

  const interactiveClasses = interactive 
    ? `transition-all duration-300 cursor-pointer ${glowStyles[glow]} transform hover:-translate-y-1`
    : '';

  return (
    <div className={`glass-panel p-6 ${interactiveClasses} ${className}`}>
      {children}
    </div>
  );
};

export default CyberCard;
