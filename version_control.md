# Automated Versioning System

Our project uses an automated versioning system based on Git hooks. This system ensures that our version numbers are consistently updated throughout the development process.

## Version Format

We use Semantic Versioning (SemVer) in the format of MAJOR.MINOR.PATCH.

## Git Hooks

### pre-commit

- Triggers on every commit
- Increments the PATCH version
- Adds the updated version file to the commit

### post-merge

- Triggers after merging into the main branch
- Increments the MINOR version
- Creates a new commit with the updated version

### pre-push

- Triggers before pushing to the main branch
- Increments the PATCH version
- Creates a new commit with the updated version

### post-release

- Must be manually triggered after a release
- Increments the MAJOR version
- Creates a new commit with the updated version

## Versioning Process

1. Regular commits: PATCH version is incremented (e.g., 1.0.0 -> 1.0.1)
2. Merges to main: MINOR version is incremented (e.g., 1.0.1 -> 1.1.0)
3. Pushes to main: PATCH version is incremented (e.g., 1.1.0 -> 1.1.1)
4. After release: MAJOR version is incremented (e.g., 1.1.1 -> 2.0.0)

## Manual Version Update

If you need to manually update the version, you can use the `increment_version.sh` script:
