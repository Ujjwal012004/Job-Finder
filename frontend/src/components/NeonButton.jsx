import React from 'react';

const NeonButton = ({ children, onClick, variant = 'cyan', type = 'button', fullWidth = false, className = '', disabled = false }) => {
  const baseStyles = `relative group inline-flex items-center justify-center px-6 py-2.5 font-display font-semibold tracking-wide transition-all duration-300 rounded overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed ${fullWidth ? 'w-full' : ''}`;
  
  const variants = {
    cyan: `bg-cyber-gray text-cyber-neonCyan border border-cyber-neonCyan/50 hover:bg-cyber-neonCyan hover:text-cyber-black hover:shadow-neon-cyan`,
    purple: `bg-cyber-gray text-cyber-neonPurple border border-cyber-neonPurple/50 hover:bg-cyber-neonPurple hover:text-cyber-black hover:shadow-neon-purple`,
    pink: `bg-cyber-gray text-cyber-neonPink border border-cyber-neonPink/50 hover:bg-cyber-neonPink hover:text-cyber-black hover:shadow-neon-pink`,
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${variants[variant]} ${className}`}
    >
      <span className="relative z-10 flex items-center gap-2">{children}</span>
      {/* Glitch overlay on hover */}
      <div className="absolute inset-0 h-full w-full opacity-0 group-hover:opacity-20 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPjxyZWN0IHdpZHRoPSI0IiBoZWlnaHQ9IjQiIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSIvPjwvc3ZnPg==')] transition-opacity duration-300"></div>
    </button>
  );
};

export default NeonButton;
