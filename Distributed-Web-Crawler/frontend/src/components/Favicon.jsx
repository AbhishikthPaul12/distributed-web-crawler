import React, { useState } from "react";
import { Globe } from "lucide-react";

export default function Favicon({ domain, size = 16 }) {
  const [error, setError] = useState(false);
  
  if (error || !domain || domain === "Other") {
    return <Globe size={size} className="site-icon fallback-globe" />;
  }
  
  return (
    <img
      src={`https://www.google.com/s2/favicons?sz=${size * 2}&domain=${domain}`}
      alt=""
      className="site-favicon"
      style={{ width: size, height: size, borderRadius: '2px', objectFit: 'contain' }}
      onError={() => setError(true)}
    />
  );
}
