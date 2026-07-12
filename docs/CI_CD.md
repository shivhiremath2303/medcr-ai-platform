# CI/CD & Supply Chain Security Documentation

This document describes the production-grade CI/CD pipeline and software supply chain security measures implemented for the MEDCR AI Platform.

## CI/CD Architecture

The platform uses GitHub Actions to automate building, testing, scanning, and validating every change.

### Workflows

1.  **Continuous Integration (`ci.yml`)**
    *   Triggered on push/PR to `main` and `develop`.
    *   Executes the full test suite using `pytest`.
    *   Generates coverage reports and enforces a coverage threshold (80%).
    *   Uses Redis service container for integration tests.

2.  **Code Quality (`quality.yml`)**
    *   Enforces coding standards using:
        *   **Ruff:** High-performance Python linter.
        *   **Black:** Opinionated code formatter.
        *   **isort:** Import sort order.
        *   **MyPy:** Static type checking.

3.  **Security Scanning (`security.yml`)**
    *   **pip-audit:** Scans Python dependencies for known vulnerabilities (CVEs).
    *   **Trivy (FS):** Scans the filesystem for security misconfigurations and vulnerabilities.
    *   **SBOM Generation:** Produces a CycloneDX Software Bill of Materials.

4.  **Docker Validation (`docker.yml`)**
    *   Builds the production Docker image.
    *   Validates `docker-compose.yml` configuration.
    *   Performs a startup smoke test and health check.
    *   **Trivy (Image):** Scans the built Docker image for vulnerabilities.

5.  **Release Preparation (`release.yml`)**
    *   Automates GitHub Release creation when a version tag (`v*`) is pushed.
    *   Generates release notes automatically.

## Software Supply Chain Security

*   **SBOM:** A `sbom.json` is generated for every build to provide transparency into dependencies.
*   **Vulnerability Scanning:** Automated scanning of both dependencies and container images.
*   **Reproducible Builds:** Docker-based builds ensure consistent environments across CI and production.
*   **Shift-Left Security:** Security scans run early in the PR process.

## Quality Gates

PRs are blocked from merging if:
*   Any unit or integration test fails.
*   Code coverage falls below 80%.
*   Linting, formatting, or type checking fails.
*   CRITICAL or HIGH security vulnerabilities are detected.
*   Docker build or health checks fail.

## Secrets Management

Sensitive information (API keys, credentials) are managed via GitHub Secrets and never hardcoded in the repository. Environment variables are used to inject these secrets during runtime.
