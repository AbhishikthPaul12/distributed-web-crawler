import React from "react";
import { Search, Sparkles, X } from "lucide-react";

export default function SearchBar({
  query,
  isInitialState,
  showSuggestions,
  suggestions,
  activeSuggestionIndex,
  inputRef,
  suggestionsRef,
  handleSearch,
  handleInputChange,
  handleInputKeyDown,
  handleClear,
  handleSuggestionClick,
  setActiveSuggestionIndex,
  setShowSuggestions
}) {
  return (
    <>
      {isInitialState && (
        <div className="search-hero">
          <div className="hero-logo">
            <Sparkles className="hero-logo-icon" />
          </div>
          <h2 className="hero-title">AetherSearch</h2>
          <p className="hero-subtitle">
            Explore the decentralized index scoured by our high-performance distributed crawling pipeline.
          </p>
        </div>
      )}

      <form onSubmit={handleSearch} className="search-form">
        <div className="search-input-wrapper" ref={inputRef}>
          <Search className="search-input-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search indexed pages, titles, or categories..."
            value={query}
            onChange={handleInputChange}
            onKeyDown={handleInputKeyDown}
            onFocus={() => {
              if (suggestions.length > 0) setShowSuggestions(true);
            }}
          />
          {query && (
            <button type="button" className="clear-btn" onClick={handleClear}>
              <X size={18} />
            </button>
          )}

          {/* Autocomplete Dropdown */}
          {showSuggestions && suggestions.length > 0 && (
            <div className="autocomplete-dropdown" ref={suggestionsRef}>
              {suggestions.map((suggestion, idx) => (
                <div
                  key={idx}
                  className={`suggestion-item ${idx === activeSuggestionIndex ? "active" : ""}`}
                  onMouseDown={() => handleSuggestionClick(suggestion)}
                  onMouseEnter={() => setActiveSuggestionIndex(idx)}
                >
                  <Search size={14} className="suggestion-icon" />
                  <span className="suggestion-text">{suggestion.title}</span>
                </div>
              ))}
            </div>
          )}
        </div>
        <button type="submit" className="search-submit-btn">
          Search
        </button>
      </form>
    </>
  );
}
