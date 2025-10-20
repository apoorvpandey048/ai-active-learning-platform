import React from 'react';

export default function Spinner({ size = 18, style = {} }) {
  const s = {
    display: 'inline-block',
    width: size,
    height: size,
    border: '3px solid rgba(0,0,0,0.1)',
    borderTop: '3px solid #444',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    ...style,
  };

  return (
    <span>
      <span style={s} />
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </span>
  );
}
