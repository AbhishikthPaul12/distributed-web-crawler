# AetherSearch UI: React Search Engine Dashboard

This directory houses the frontend user interface for **AetherSearch**, a glassmorphic React dashboard built with Vite. The client provides a high-fidelity interface for querying the backend search API, visualizing domain footprints, displaying autocomplete suggestions, and presenting paginated search results with smooth micro-animations.

##  Technology Stack
- **Framework**: React 19 (Functional components, hooks)
- **Build Tooling**: Vite 8
- **Styling**: Vanilla CSS (Premium glassmorphic stylesheet with HSL dark-mode palettes)
- **Icons**: Lucide React

##  Directory Structure
```text
frontend/
├── Dockerfile                  # Container definition for local dev/prod staging
├── .dockerignore               # Container build exclusion patterns
├── .gitignore                  # Git tracking exclusion patterns
├── package.json                # Project dependencies and script runner configurations
├── vite.config.js              # Vite bundler parameters
├── public/                     # Static client-side assets
└── src/
    ├── App.jsx                 # Application layout orchestrator
    ├── App.css                 # Global glassmorphic design and style declarations
    ├── index.css               # Basic browser resets
    ├── main.jsx                # Application entrypoint
    ├── components/             # Reusable UI presentation layers
    │   ├── Favicon.jsx         # Domain icon visualizers with fallback routines
    │   ├── Header.jsx          # Header, navigation, and connection status alerts
    │   ├── SearchBar.jsx       # Input field, debounced search suggestions, keyboard capture
    │   ├── SuggestedQueries.jsx# Quick-click search tag pills
    │   ├── SearchResults.jsx   # Results categorizer tabs and layout cards
    │   ├── Pagination.jsx      # Google-style paginator controls
    │   └── SkeletonLoading.jsx # Loading state wireframe animation cards
    └── hooks/                  # Custom application hooks
        └── useSearchState.js   # Centralized UI state container, autocomplete debouncing, and API abort controllers
```

##  Client Architecture
The frontend leverages a strict separation of concerns model:
- **Presentation Layer (`src/components/`)**: Focuses purely on styling and rendering inputs passed via React props.
- **State Management & Network Layer (`src/hooks/useSearchState.js`)**: Encapsulates all query states, pagination records, autocompletion arrays, debounced API calls, and HTTP fetch cycles using `AbortController` instances to cancel racing operations.
- **Root Orchestration (`src/App.jsx`)**: Instantiates the state hook and injects parameters down the component hierarchy.

##  Local Development Setup

### Prerequisite
Ensure [Node.js](https://nodejs.org) (v18.0 or higher) is installed on your host machine.

### Installation
From the `frontend` folder:
```bash
npm install
```

### Dev Server
To launch Vite's hot-reload server:
```bash
npm run dev
```
Navigate to [http://localhost:5173](http://localhost:5173) in your browser.

### Production Build
To compile static production-ready bundles inside `./dist`:
```bash
npm run build
```

---