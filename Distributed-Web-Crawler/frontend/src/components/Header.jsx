import React from "react";
import { Sparkles, Home, Wifi, WifiOff } from "lucide-react";

export default function Header({ isInitialState, apiStatus, handleGoHome }) {
  return (
    <header className="app-header">
      <div className="header-left">
        <div className="logo-section" onClick={handleGoHome}>
          <div className="logo-icon-wrapper">
            <Sparkles className="logo-icon animate-pulse" />
          </div>
          <h1>AetherSearch</h1>
        </div>
        {!isInitialState && (
          <button className="home-btn" onClick={handleGoHome} aria-label="Go to home page" title="Home">
            <Home size={18} />
            <span>Home</span>
          </button>
        )}
      </div>
      
      {/* Status Dot */}
      <div className="status-badge">
        {apiStatus === "checking" && (
          <span className="badge checking">
            <span className="dot dot-pulse"></span> Connecting to API...
          </span>
        )}
        {apiStatus === "online" && (
          <span className="badge online">
            <Wifi size={14} className="badge-icon" /> Engine Online
          </span>
        )}
        {apiStatus === "offline" && (
          <span className="badge offline">
            <WifiOff size={14} className="badge-icon" /> Engine Offline
          </span>
        )}
      </div>
    </header>
  );
}
