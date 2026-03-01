# Frontend (React + Vite)

This folder contains the **frontend** application for the Sky Atmosphere Analyzer. It is a React 18 project bootstrapped with Vite and Tailwind CSS for styling.

## Features

- SPA using React Router for navigation
- Tailwind CSS utility-first styling
- Layout component with mobile-friendly sidebar
- API service for inference and results
- Pagination support for results history

## Getting Started

### Prerequisites

- Node.js v18+ / npm or Yarn installed

### Installation

```bash
cd client
npm install
```

### Development

```bash
npm run dev
```

Open `http://localhost:5173` in your browser.

### Build

To produce a production build:

```bash
npm run build
```

The output will live in `dist/`.

### Docker

To build and serve with nginx:

```bash
npm run build
docker build -t sky-analyzer-client .
docker run -p 8080:80 sky-analyzer-client
```

### Preview

```bash
npm run preview
```

## API Endpoints

The frontend communicates with these backend endpoints:

- `POST /api/v1/analyze` – Upload and analyze sky images
- `GET /api/v1/results` – Get paginated analysis results

## Project Structure

- `src/` – source code
  - `components/` – reusable UI components
  - `routes/` – page-level components
  - `services/api.ts` – HTTP clients for backend
  - `lib/` – utility modules
- `public/` – static assets
- `vite.config.ts` – Vite configuration

## Running with Docker Compose

To run the full stack (frontend + backend), use Docker Compose from the project root:

```bash
docker-compose up --build
```

This starts the frontend on `http://localhost:80` and the backend on `http://localhost:8000`.

## Notes

This frontend pairs with the server located in `../server`. Ensure the backend is running to make API requests.
