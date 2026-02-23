# Frontend (React + Vite)

This folder contains the **frontend** application for the Sky Atmosphere Analyzer. It is a React 18 project bootstrapped with Vite and Tailwind CSS for styling.

## Features

- SPA using React Router for navigation
- Tailwind CSS utility-first styling
- Layout component with mobile-friendly sidebar
- API service for inference and results

## Getting Started

### Prerequisites

- Node.js v18+ / npm or Yarn installed

### Installation

```bash
# from the client directory
npm install     # or yarn
```

### Development

Run the dev server with hot reload:

```bash
npm run dev     # or yarn dev
```

Open `http://localhost:5173` in your browser.

### Build

To produce a production build:

```bash
npm run build   # or yarn build
```

The output will live in `dist/`.

### Preview

You can preview the production build locally:

```bash
npm run preview
```

## Project Structure

- `src/` – source code
  - `components/` – reusable UI components
  - `routes/` – page-level components
  - `src/services/api.ts` – HTTP clients for backend
  - `lib/` – utility modules
- `public/` – static assets
- `vite.config.ts` – Vite configuration

## Notes

This frontend pairs with the server located in `../server`. Ensure the backend is running to make API requests.

