import React from "react";

export default function SkeletonLoading() {
  return (
    <div className="results-list">
      {[1, 2, 3].map((n) => (
        <div key={n} className="skeleton-card">
          <div className="skeleton-line breadcrumb"></div>
          <div className="skeleton-line title"></div>
          <div className="skeleton-line snippet"></div>
          <div className="skeleton-line snippet short"></div>
        </div>
      ))}
    </div>
  );
}
