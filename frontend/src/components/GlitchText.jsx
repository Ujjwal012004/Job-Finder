import React from 'react';

const GlitchText = ({ text, className = '', as: Component = 'h1' }) => {
  return (
    <Component 
      className={`text-glitch font-display font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyber-neonCyan to-cyber-neonPurple ${className}`}
      data-text={text}
    >
      {text}
    </Component>
  );
};

export default GlitchText;
