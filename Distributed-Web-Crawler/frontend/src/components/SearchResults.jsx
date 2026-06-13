import React from "react";
import { ExternalLink } from "lucide-react";
import Favicon from "./Favicon";

export default function SearchResults({
  query,
  results,
  totalResults,
  searchTime,
  activeTab,
  setActiveTab,
  sortBy,
  setSortBy,
  performSearch
}) {
  if (!results) return null;

  // Safe HTML escaping that preserves <em> highlighting tags
  const renderSafeSnippet = (snippet) => {
    if (!snippet) return { __html: "" };
    const escaped = String(snippet)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");

    const highlighted = escaped
      .replace(/&lt;em&gt;/g, '<em class="highlight">')
      .replace(/&lt;\/em&gt;/g, "</em>");

    return { __html: highlighted };
  };

  const getFilteredResults = () => {
    if (!results) return [];
    if (activeTab === "All") return results;
    if (activeTab === "Books") {
      return results.filter(r => r.url.includes("books.toscrape.com"));
    }
    if (activeTab === "Pages") {
      return results.filter(r => !r.url.includes("books.toscrape.com"));
    }
    return results;
  };

  const getGroupedDomains = () => {
    if (!results) return {};
    const grouped = {};
    results.forEach(result => {
      let hostname = "Other";
      try {
        hostname = new URL(result.url).hostname;
      } catch (e) {
        // Fallback
      }
      if (!grouped[hostname]) {
        grouped[hostname] = [];
      }
      grouped[hostname].push(result);
    });
    return grouped;
  };

  const filteredResults = getFilteredResults();
  const groupedDomains = getGroupedDomains();
  const domainsCount = Object.keys(groupedDomains).length;

  return (
    <>
      <div className="search-tabs-container">
        <div className="search-tabs">
          {["All", "Pages", "Books", "Domains"].map((tab) => (
            <button
              key={tab}
              className={`tab-item ${activeTab === tab ? "active" : ""}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </button>
          ))}
        </div>
        <div className="search-stats-container">
          <div className="search-stats">
            {activeTab === "Domains" ? (
              `About ${domainsCount} ${domainsCount === 1 ? "domain" : "domains"} (${searchTime} seconds)`
            ) : (
              `About ${totalResults} ${totalResults === 1 ? "result" : "results"} (${searchTime} seconds)`
            )}
          </div>
          {activeTab !== "Domains" && (
            <div className="sort-container">
              <span className="sort-label">Sort by:</span>
              <select
                className="sort-select"
                value={sortBy}
                onChange={(e) => {
                  const newSort = e.target.value;
                  setSortBy(newSort);
                  performSearch(query, 1, newSort);
                }}
              >
                <option value="relevance">Relevance</option>
                <option value="title">Title (A-Z)</option>
                <option value="url">URL (A-Z)</option>
              </select>
            </div>
          )}
        </div>
      </div>

      <div className="results-list">
        {filteredResults.length === 0 && activeTab !== "Domains" ? (
          <div className="no-results-card">
            <p className="no-results-notice">
              Your search - <strong>{query}</strong> - did not match any documents in <strong>{activeTab}</strong>.
            </p>
            <div className="no-results-suggestions">
              <p className="suggestions-header">Suggestions:</p>
              <ul>
                {activeTab !== "All" && (
                  <li>Try switching to the <strong>All</strong> tab to view matches in other categories.</li>
                )}
                <li>Make sure that all words are spelled correctly.</li>
                <li>Try different keywords.</li>
                <li>Try more general keywords.</li>
              </ul>
            </div>
          </div>
        ) : activeTab === "Domains" ? (
          domainsCount === 0 ? (
            <div className="no-results-card">
              <p className="no-results-notice">
                Your search - <strong>{query}</strong> - did not match any domains.
              </p>
            </div>
          ) : (
            <div className="domains-grid">
              {Object.entries(groupedDomains).map(([domain, pages], idx) => (
                <div key={idx} className="domain-group-card">
                  <div className="domain-group-header">
                    <div className="domain-icon-title">
                      <div className="domain-favicon-wrapper">
                        <Favicon domain={domain} size={16} />
                      </div>
                      <h3 className="domain-group-name">{domain}</h3>
                    </div>
                    <span className="domain-match-badge">
                      {pages.length} {pages.length === 1 ? "page" : "pages"}
                    </span>
                  </div>
                  <div className="domain-pages-list">
                    {pages.map((page, pIdx) => {
                      const safeUrl = (page.url.startsWith("http://") || page.url.startsWith("https://"))
                        ? page.url
                        : "#";
                      return (
                        <div key={pIdx} className="domain-page-item">
                          <a
                            href={safeUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="domain-page-link"
                          >
                            <span className="domain-page-title">{page.title || "Untitled Document"}</span>
                            <ExternalLink size={12} className="domain-page-arrow" />
                          </a>
                          <p 
                            className="domain-page-snippet"
                            dangerouslySetInnerHTML={renderSafeSnippet(page.snippet)}
                          />
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )
        ) : (
          filteredResults.map((result, idx) => {
            const safeUrl = (result.url.startsWith("http://") || result.url.startsWith("https://"))
              ? result.url
              : "#";
            
            let hostname = result.url;
            let breadcrumbs = result.url;
            try {
              const parsed = new URL(result.url);
              hostname = parsed.hostname;
              const paths = parsed.pathname.split("/").filter(Boolean);
              breadcrumbs = hostname + (paths.length ? " › " + paths.join(" › ") : "");
            } catch (e) {
              // Fallback
            }

            return (
              <article key={idx} className="result-card">
                <div className="result-site-info">
                  <div className="site-icon-wrapper">
                    <Favicon domain={hostname} size={12} />
                  </div>
                  <div className="site-meta">
                    <span className="site-hostname">{hostname}</span>
                    <span className="site-breadcrumbs">{breadcrumbs}</span>
                  </div>
                </div>

                <h3 className="result-title-container">
                  <a
                    href={safeUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="result-title"
                  >
                    {result.title || "Untitled Document"}
                    <ExternalLink size={13} className="link-arrow" />
                  </a>
                </h3>
                
                <p
                  className="result-snippet"
                  dangerouslySetInnerHTML={renderSafeSnippet(result.snippet)}
                />
              </article>
            );
          })
        )}
      </div>
    </>
  );
}
