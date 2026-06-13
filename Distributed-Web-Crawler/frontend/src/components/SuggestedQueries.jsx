import React from "react";

export default function SuggestedQueries({ setQuery, setSortBy, performSearch }) {
  const suggestedTerms = ["Philosophy", "Science", "Romance", "World", "History", "Inspiration", "Mystery"];

  return (
    <div className="suggested-searches">
      <span className="suggested-label">Suggested Queries:</span>
      <div className="suggested-buttons">
        {suggestedTerms.map((term) => (
          <button
            key={term}
            type="button"
            className="suggested-btn"
            onClick={() => {
              setQuery(term);
              setSortBy("relevance");
              performSearch(term, 1, "relevance");
            }}
          >
            {term}
          </button>
        ))}
      </div>
    </div>
  );
}
