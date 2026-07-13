# Contributing to Legal AI Platform (Frontend)

Thank you for contributing to the Legal AI Platform! This document provides guidelines for maintaining high quality, security, and accessibility across the frontend.

## 🛠 Tech Stack
- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript 5+
- **Styling:** Tailwind CSS + shadcn/ui
- **State Management:** Zustand (Global) + TanStack Query (Server State)
- **Testing:** Vitest (Unit) + Playwright (E2E)

## 🏗 Architecture Rules
- **Feature-based structure:** Keep logic related to a feature within its respective folder in `src/features`.
- **Clean Architecture:** Domain logic should stay separate from UI components.
- **Type Safety:** Ensure all props, API responses, and state objects are strictly typed.
- **Accessibility:** Use semantic HTML and ARIA labels. Every interactive element must be keyboard accessible.

## 🧪 Testing
We maintain high coverage to ensure release stability.

### Unit & Integration Tests
Run tests using Vitest:
```bash
npm run test
```
Generate coverage report:
```bash
npm run test:coverage
```

### End-to-End (E2E) Tests
Run Playwright tests:
```bash
npm run e2e
```

## 💅 Code Quality
- **Linting:** `npm run lint`
- **Formatting:** `npm run format`
- **Type Checking:** `npm run type-check`

Before pushing, ensure all checks pass to maintain the production-ready state of the `main` branch.

## 🔒 Security
- Never expose environment variables or secrets in the client-side code.
- Use `useMemo` and `useCallback` for expensive computations to avoid re-render performance bottlenecks.
- Sanitize any user-generated content before rendering (ReactMarkdown is used for AI responses).
