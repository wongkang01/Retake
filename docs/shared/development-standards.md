# Development Standards

## Coding Conventions
- **TypeScript**: Use strict typing and Zod schemas for all API interactions.
- **React**: Favor functional components and TanStack Query for data fetching.
- **Python**: Use Pydantic models for request validation and FastAPI dependency injection.

## Project Structure
- `src/components/dashboard/`: UI implementation.
- `docs/`: Specification and tracking.
- `reference_archive/`: Legacy v1 Python logic.

## Testing
- **E2E**: Critical workflows (Find -> Analyze) must be verified via Playwright.
- **Unit**: All processing logic (e.g., timestamp calculation) requires 90% coverage.
