# Docker Best Practices 2026

## Overview
Docker continues to be the leading containerization platform. These best practices ensure secure, efficient, and maintainable container images.

## Key Best Practices

### 1. Use Multi-Stage Builds
- Split Dockerfile instructions into distinct stages
- Create reusable stages for images with shared components
- Reduces final image size significantly
- Enables parallel build execution

### 2. Choose the Right Base Image
- Use **Docker Official Images** - curated, documented, regularly updated
- Look for **Verified Publisher** badges on Docker Hub
- Prefer minimal images like Alpine (under 6MB)
- Consider using two base images: one for build/test, slimmer for production

### 3. Rebuild Images Often
- Use `--pull` flag to get fresh base images
- Use `--no-cache` for clean builds
- Combine both: `docker build --pull --no-cache`
- Pin base image versions for security (use digests)

### 4. Exclude with .dockerignore
- Create `.dockerignore` file similar to `.gitignore`
- Exclude files not relevant to the build (e.g., `*.md`, `.git`)

### 5. Create Ephemeral Containers
- Containers should be stoppable, destroyable, and rebuildable
- Follow The Twelve-Factor App methodology
- Minimal setup and configuration

### 6. Don't Install Unnecessary Packages
- Avoid extra packages "just in case"
- Reduces complexity, dependencies, file size, and build time

### 7. Decouple Applications
- Each container = one concern
- Easier horizontal scaling and reuse
- Example: separate containers for web app, database, cache

### 8. Sort Multi-Line Arguments
- Alphanumerically sort for easier maintenance
- Makes PRs easier to read and review

### 9. Leverage Build Cache
- Understand cache invalidation rules
- Order instructions from least to most frequently changing

### 10. Pin Base Image Versions
- Use specific tags or digests for reproducibility
- Example: `alpine:3.21@sha256:a8560b36...`
- Use Docker Scout for automated base image updates

### 11. Build and Test in CI
- Automate builds with GitHub Actions or similar
- Automatically build and tag on pull requests

## Dockerfile Instruction Tips

### FROM
- Use current official images
- Alpine recommended for minimal size

### LABEL
- Add labels for project organization, licensing
- Combine multiple labels into single instruction

### RUN
- Chain commands with `&&`
- Use backslashes for line continuation
- Clean up in same layer: `rm -rf /var/lib/apt/lists/*`

### CMD vs ENTRYPOINT
- CMD: default command, easily overridden
- ENTRYPOINT: configure container execution

### WORKDIR
- Use absolute paths
- Create if it doesn't exist

---

*Generated: 2026-03-14*
