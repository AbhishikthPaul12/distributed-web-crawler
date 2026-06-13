import React from "react";
import { ShieldAlert } from "lucide-react";
import "./App.css";

// Import custom hook and modular sub-components
import useSearchState from "./hooks/useSearchState";
import Header from "./components/Header";
import SearchBar from "./components/SearchBar";
import SuggestedQueries from "./components/SuggestedQueries";
import SearchResults from "./components/SearchResults";
import Pagination from "./components/Pagination";
import SkeletonLoading from "./components/SkeletonLoading";

function App() {
  const {
    query,
    setQuery,
    results,
    loading,
    searchTime,
    error,
    apiStatus,
    activeTab,
    setActiveTab,
    totalResults,
    currentPage,
    sortBy,
    setSortBy,
    suggestions,
    showSuggestions,
    setShowSuggestions,
    activeSuggestionIndex,
    setActiveSuggestionIndex,
    suggestionsRef,
    inputRef,
    performSearch,
    handleSearch,
    handleClear,
    handleInputChange,
    handleSuggestionClick,
    handleInputKeyDown,
    handlePageChange,
    handleGoHome,
    pageSize
  } = useSearchState();

  const isInitialState = results === null && !loading && !error;

  return (
    <div className={`app-container ${isInitialState ? "initial-centered" : "results-layout"}`}>
      {/* Background decoration */}
      <div className="glow-orb orb-1"></div>
      <div className="glow-orb orb-2"></div>

      {/* Header section (logo, home, API status) */}
      <Header
        isInitialState={isInitialState}
        apiStatus={apiStatus}
        handleGoHome={handleGoHome}
      />

      {/* Main search container */}
      <main className="search-container">
        <SearchBar
          query={query}
          isInitialState={isInitialState}
          showSuggestions={showSuggestions}
          suggestions={suggestions}
          activeSuggestionIndex={activeSuggestionIndex}
          inputRef={inputRef}
          suggestionsRef={suggestionsRef}
          handleSearch={handleSearch}
          handleInputChange={handleInputChange}
          handleInputKeyDown={handleInputKeyDown}
          handleClear={handleClear}
          handleSuggestionClick={handleSuggestionClick}
          setActiveSuggestionIndex={setActiveSuggestionIndex}
          setShowSuggestions={setShowSuggestions}
        />

        {isInitialState && (
          <SuggestedQueries
            setQuery={setQuery}
            setSortBy={setSortBy}
            performSearch={performSearch}
          />
        )}

        {/* Error Alert Box */}
        {error && (
          <div className="error-alert">
            <ShieldAlert className="error-icon" />
            <span>{error}</span>
          </div>
        )}

        {/* Skeleton loading state */}
        {loading && <SkeletonLoading />}

        {/* Search Results List */}
        {!loading && !error && (
          <SearchResults
            query={query}
            results={results}
            totalResults={totalResults}
            searchTime={searchTime}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            sortBy={sortBy}
            setSortBy={setSortBy}
            performSearch={performSearch}
          />
        )}

        {/* Pagination Controls */}
        {!loading && !error && activeTab !== "Domains" && (
          <Pagination
            totalResults={totalResults}
            currentPage={currentPage}
            pageSize={pageSize}
            handlePageChange={handlePageChange}
          />
        )}
      </main>

      {/* Footer explaining crawler technology */}
      {isInitialState && (
        <footer className="initial-footer">
          <div className="footer-links">
            <span>AetherSearch Engine v1.1.0</span>
            <span className="footer-dot">•</span>
            <span>Distributed Crawler Status: Active</span>
            <span className="footer-dot">•</span>
            <span>Secure Node Connection</span>
          </div>
        </footer>
      )}
    </div>
  );
}

export default App;
