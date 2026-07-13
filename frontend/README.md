# Legal AI Platform - Enterprise Frontend

This is the production-grade frontend for the Legal AI Platform, built with Next.js 15, React 19, and Tailwind CSS.

## 🚀 Key Features
- **Unified Analysis Workspace:** Timeline, Clause Comparison, and Conflict Viewer.
- **AI Investigation Terminal:** Deep reasoning chat with evidence citations.
- **Enterprise Admin Console:** Real-time system health and infrastructure monitoring.
- **Command Palette (Ctrl+K):** Global search and rapid navigation.
- **Accessibility & UX:** Full ARIA compliance, responsive design, and dark mode support.

## 📦 Getting Started

### Prerequisites
- Node.js 18+
- npm 9+

### Installation
```bash
npm install
```

### Development
```bash
npm run dev
```

### Build for Production
```bash
npm run build
npm run start
```

## 🧪 Testing Infrastructure
We use a robust testing suite to ensure enterprise reliability.

| Test Type | Tool | Command |
|-----------|------|---------|
| Unit / Integration | Vitest + RTL | `npm run test` |
| End-to-End | Playwright | `npm run e2e` |
| Coverage | Vitest Coverage | `npm run test:coverage` |
| Type Check | TypeScript | `npm run type-check` |

## 🛠 Project Structure
```text
src/
  app/            # Next.js App Router (Pages & Layouts)
  core/           # Base configurations, API clients, utilities
  features/       # Feature-sliced modules (Auth, Chat, Admin, etc.)
  shared/         # Reusable UI components, hooks, and providers
  tests/          # Unit and integration test suites
e2e/              # Playwright end-to-end scenarios
```

## 🛡 Quality & Security
- **Lighthouse Targets:** 100/100/100/90 (Performance/A11y/Best Practices/SEO)
- **Security:** CSRF protection, secure JWT handling, and Markdown sanitization.
- **Error Handling:** Global Error Boundaries and Network Awareness.
