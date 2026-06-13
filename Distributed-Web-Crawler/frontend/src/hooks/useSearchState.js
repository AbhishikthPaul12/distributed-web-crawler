import { useState, useEffect, useRef, useCallback } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";
const PAGE_SIZE = 10;

export default function useSearchState() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchTime, setSearchTime] = useState(0);
  const [error, setError] = useState("");
  const [apiStatus, setApiStatus] = useState("checking"); // "checking" | "online" | "offline"
  const [activeTab, setActiveTab] = useState("All");

  // Pagination state
  const [totalResults, setTotalResults] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [sortBy, setSortBy] = useState("relevance");

  // Autocomplete state
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [activeSuggestionIndex, setActiveSuggestionIndex] = useState(-1);
  
  const suggestionsRef = useRef(null);
  const inputRef = useRef(null);
  const debounceTimerRef = useRef(null);
  const activeSearchControllerRef = useRef(null);
  const activeAutocompleteControllerRef = useRef(null);

  // Check API health status on mount
  useEffect(() => {
    const checkApi = async () => {
      try {
        const response = await fetch(`${API_URL}/`);
        if (response.ok) {
          setApiStatus("online");
        } else {
          setApiStatus("offline");
        }
      } catch (err) {
        setApiStatus("offline");
      }
    };
    checkApi();

    // Cleanup abort controllers on unmount
    return () => {
      if (activeSearchControllerRef.current) activeSearchControllerRef.current.abort();
      if (activeAutocompleteControllerRef.current) activeAutocompleteControllerRef.current.abort();
    };
  }, []);

  // Dynamic browser tab title
  useEffect(() => {
    if (results !== null && query.trim()) {
      document.title = `${query.trim()} - AetherSearch`;
    } else {
      document.title = "AetherSearch | Distributed Search Engine";
    }
  }, [query, results]);

  // Close autocomplete dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(e.target) &&
        inputRef.current &&
        !inputRef.current.contains(e.target)
      ) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Debounced autocomplete fetch
  const fetchSuggestions = useCallback((searchText) => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    if (!searchText || searchText.trim().length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      if (activeAutocompleteControllerRef.current) {
        activeAutocompleteControllerRef.current.abort();
        activeAutocompleteControllerRef.current = null;
      }
      return;
    }

    debounceTimerRef.current = setTimeout(async () => {
      if (activeAutocompleteControllerRef.current) {
        activeAutocompleteControllerRef.current.abort();
      }
      const controller = new AbortController();
      activeAutocompleteControllerRef.current = controller;

      try {
        const res = await fetch(
          `${API_URL}/autocomplete?q=${encodeURIComponent(searchText.trim())}`,
          { signal: controller.signal }
        );
        const data = await res.json();
        setSuggestions(data);
        setShowSuggestions(data.length > 0);
        setActiveSuggestionIndex(-1);
      } catch (err) {
        if (err.name !== "AbortError") {
          setSuggestions([]);
          setShowSuggestions(false);
        }
      } finally {
        if (activeAutocompleteControllerRef.current === controller) {
          activeAutocompleteControllerRef.current = null;
        }
      }
    }, 250);
  }, []);

  const performSearch = async (searchTerm, page = 1, sort = sortBy) => {
    const cleanQuery = searchTerm.trim();

    if (!cleanQuery) {
      setError("Please enter a search query.");
      return;
    }

    if (activeAutocompleteControllerRef.current) {
      activeAutocompleteControllerRef.current.abort();
      activeAutocompleteControllerRef.current = null;
    }

    if (activeSearchControllerRef.current) {
      activeSearchControllerRef.current.abort();
    }
    const controller = new AbortController();
    activeSearchControllerRef.current = controller;

    setError("");
    setLoading(true);
    setResults(null);
    setActiveTab("All");
    setShowSuggestions(false);

    const startTime = performance.now();

    try {
      const response = await fetch(
        `${API_URL}/search?q=${encodeURIComponent(cleanQuery)}&page=${page}&size=${PAGE_SIZE}&sort=${sort}`,
        { signal: controller.signal }
      );
      const data = await response.json();

      const endTime = performance.now();
      setSearchTime(((endTime - startTime) / 1000).toFixed(3));

      if (!response.ok || data.error) {
        setError(data.error || "An error occurred during search.");
      } else {
        setResults(data.results);
        setTotalResults(data.total);
        setCurrentPage(data.page);
      }
    } catch (err) {
      if (err.name !== "AbortError") {
        console.error(err);
        setError("Failed to connect to the search server.");
      }
    } finally {
      if (activeSearchControllerRef.current === controller) {
        activeSearchControllerRef.current = null;
        setLoading(false);
      }
    }
  };

  const handleSearch = (e) => {
    if (e) e.preventDefault();
    setCurrentPage(1);
    performSearch(query, 1, sortBy);
  };

  const handleClear = () => {
    setQuery("");
    setError("");
    setSuggestions([]);
    setShowSuggestions(false);
  };

  const handleInputChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    fetchSuggestions(value);
  };

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion.title);
    setShowSuggestions(false);
    setSuggestions([]);
    setSortBy("relevance");
    performSearch(suggestion.title, 1, "relevance");
  };

  const handleInputKeyDown = (e) => {
    if (!showSuggestions || suggestions.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveSuggestionIndex((prev) =>
        prev < suggestions.length - 1 ? prev + 1 : 0
      );
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveSuggestionIndex((prev) =>
        prev > 0 ? prev - 1 : suggestions.length - 1
      );
    } else if (e.key === "Enter" && activeSuggestionIndex >= 0) {
      e.preventDefault();
      handleSuggestionClick(suggestions[activeSuggestionIndex]);
    } else if (e.key === "Escape") {
      setShowSuggestions(false);
    }
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    performSearch(query, page, sortBy);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleGoHome = () => {
    setResults(null);
    setQuery("");
    setError("");
    setTotalResults(0);
    setCurrentPage(1);
    setSuggestions([]);
    setShowSuggestions(false);
    setActiveTab("All");
    setSortBy("relevance");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return {
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
    pageSize: PAGE_SIZE
  };
}
