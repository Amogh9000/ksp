# KSP Intelligence Platform

A robust, component-based Next.js application built for the KSP (Karnataka State Police) Intelligence Dashboard.

## Overview
This repository contains the Next.js migration of the KSP Intelligence Platform, transforming the legacy static HTML/Alpine.js architecture into a scalable, high-performance React application utilizing the App Router.

### Key Features
- **Bilingual Interface**: Seamless translation toggle between Kannada and English managed via React state.
- **Modern Dashboard Architecture**: A complex, high-fidelity 3-column brutalist layout tailored for intelligence operations.
- **Interactive Matrix & Telemetry**: Live investigation matrices, threat feeds, and interactive command consoles.
- **Component-based Design**: Reusable, modular Tailwind CSS components for scalable architecture without legacy dependencies.
- **Production-Ready**: Hydration-safe state generation, optimized layout loading, and modern React principles.

## Repository Structure
- `/frontend`: The core Next.js application (App Router, Tailwind CSS, React Hooks).
- `/backend`: Scaffolded directory reserved for future backend services, microservices, or APIs.

## Getting Started

### Prerequisites
- Node.js (v18 or newer)
- npm, yarn, pnpm, or bun

### Running the Frontend locally

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies** (if you haven't already):
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Access the Console:**
   Open [http://localhost:3000](http://localhost:3000) in your browser to view the Intelligence Console.

## Technologies Used
- Next.js (App Router)
- React
- Tailwind CSS
- TypeScript/JavaScript
