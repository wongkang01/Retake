# Deployment Log: CI/CD Pipeline Failures & Attempts

This document tracks the attempts made to deploy the Retake backend to Railway and the challenges encountered during the CI/CD process.

## Summary of Attempts

| Attempt | Issue Faced | Root Cause | Resolution |
| :--- | :--- | :--- | :--- |
| 1 | `uv.lock` not found | `uv.lock` was in `.gitignore` and not committed. | Removed from `.gitignore` and committed. |
| 2 | `librandr2` not found | Typo in package name (`libxrandr2`) and missing dependencies for Playwright. | Switched to `playwright install-deps`. |
| 3 | `README.md` not found | `pyproject.toml` required `README.md` which wasn't copied into the Docker image. | Added `README.md` to `COPY` instruction. |
| 4 | Build Context Confusion | Mismatch between Railway root context and Dockerfile subdirectory expectations. | Switched to `context = "."` in `railway.toml` and updated Dockerfile paths. |
| 5 | Build Context Confusion | Mismatch between Railway root context and Dockerfile subdirectory expectations. | Switched to `context = "."` in `railway.toml` and updated Dockerfile paths. |
| 6 | `pyproject.toml` not found | With `context = "backend"`, the build failed to locate the config file despite being in the same folder. | (Unresolved) Likely requires setting "Root Directory" in Railway UI. |
| 7 | `dockerfilePath` mismatch | `dockerfilePath = "backend/Dockerfile"` was relative to repo root, not the context. With `context = "backend"`, Railway looked for `backend/backend/Dockerfile`. | Changed `dockerfilePath` to `"Dockerfile"` (relative to context). Added `backend/.dockerignore`. |
| 8 | Railway ignores `context` | Railway does not respect `context = "backend"` in `railway.toml`, looks for Dockerfile in repo root. | Removed `context`, use `dockerfilePath = "backend/Dockerfile"`, updated Dockerfile COPY paths to use `backend/` prefix. |

## Detailed Breakdown
...
### 4. Build Context & Pathing
**Challenge**: The project is a monorepo structure (`backend/` and `frontend/`).
- **Attempt 5**: Railway was building from the root, but the Dockerfile was written as if it were inside `backend/`.
- **Attempt 6**: Switched `railway.toml` context to `backend`. However, the build engine still reported that `pyproject.toml` was not found. This suggests that the `context` setting in `railway.toml` may not be sufficient on its own without also setting the **Root Directory** in the Railway service settings UI.

## Recommendations for Future Deployments
1. **Always use a .dockerignore**: Prevent multi-hundred megabyte contexts (like node_modules or .git) from being sent to the builder.
2. **UI Settings over Config**: For monorepos, setting the "Root Directory" in the Railway Dashboard is often more reliable than the `context` key in `railway.toml`.
3. **Path Awareness**: If the Root Directory is set to `backend`, the Dockerfile should `COPY . .`. If it is set to `.`, it should `COPY backend/ .`.
