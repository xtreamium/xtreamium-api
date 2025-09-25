#!/bin/bash

set -e

# Change to the project root directory (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default version bump type
BUMP_TYPE="patch"

print_status "Working directory: $(pwd)"

# Cleanup function to restore pyproject.toml if script exits unexpectedly
cleanup() {
    if [ -f "~pyproject.toml" ]; then
        print_warning "Script interrupted. Restoring original pyproject.toml..."
        mv ~pyproject.toml pyproject.toml
        print_success "Original pyproject.toml restored"
    fi
}

# Set up trap to call cleanup on script exit
trap cleanup EXIT

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show help
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Create a new release by incrementing the version in pyproject.toml and publishing to GitHub.

OPTIONS:
    -h, --help      Show this help message and exit
    -M, --major     Increment major version (X.0.0)
    -m, --minor     Increment minor version (X.Y.0)
    -p, --patch     Increment patch version (X.Y.Z) [default]

EXAMPLES:
    $(basename "$0")              # Increment patch version (default)
    $(basename "$0") --patch      # Increment patch version
    $(basename "$0") --minor      # Increment minor version
    $(basename "$0") --major      # Increment major version

DESCRIPTION:
    This script will:
    1. Check for uncommitted changes (must be clean)
    2. Read current version from pyproject.toml
    3. Increment the specified version component
    4. Update pyproject.toml with new version
    5. Run tests to verify the project works
    6. Commit the version change to git
    7. Create and push a git tag
    8. Create a GitHub release (if gh CLI is available)

REQUIREMENTS:
    - Git repository with remote configured
    - Python 3.12+ (for reading/updating pyproject.toml)
    - Clean working directory (no uncommitted changes)
    - GitHub CLI (gh) for automatic release creation (optional)

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -M|--major)
            BUMP_TYPE="major"
            shift
            ;;
        -m|--minor)
            BUMP_TYPE="minor"
            shift
            ;;
        -p|--patch)
            BUMP_TYPE="patch"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository"
    exit 1
fi

# Check if we have uncommitted changes
# Refresh the index first to avoid false positives
git update-index --refresh >/dev/null 2>&1 || true

if ! git diff-index --quiet HEAD --; then
    print_error "You have uncommitted changes. Please commit or stash them before creating a release."
    print_status "Run 'git status' to see the changes."
    exit 1
fi

# Check if pyproject.toml exists
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found in current directory"
    exit 1
fi

# Check if gh CLI is installed for GitHub releases
if ! command -v gh &> /dev/null; then
    print_warning "GitHub CLI (gh) not found. Release will be created without GitHub CLI."
    USE_GH=false
else
    USE_GH=true
fi

# Get current version from pyproject.toml
CURRENT_VERSION=$(python3 -c "
try:
    import tomllib
    with open('pyproject.toml', 'rb') as f:
        data = tomllib.load(f)
except ImportError:
    # Fallback for Python < 3.11
    try:
        import tomli
        with open('pyproject.toml', 'rb') as f:
            data = tomli.load(f)
    except ImportError:
        # Final fallback using regex
        import re
        with open('pyproject.toml', 'r') as f:
            content = f.read()
        match = re.search(r'version = \"([^\"]+)\"', content)
        if match:
            print(match.group(1))
            exit()
        else:
            print('ERROR: Could not parse version from pyproject.toml')
            exit(1)
print(data['project']['version'])
")
print_status "Current version: $CURRENT_VERSION"
print_status "Bump type: $BUMP_TYPE"

# Split version into parts
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

# Calculate new version based on bump type
case $BUMP_TYPE in
    major)
        NEW_MAJOR=$((MAJOR + 1))
        NEW_MINOR=0
        NEW_PATCH=0
        NEW_VERSION="$NEW_MAJOR.$NEW_MINOR.$NEW_PATCH"
        ;;
    minor)
        NEW_MAJOR=$MAJOR
        NEW_MINOR=$((MINOR + 1))
        NEW_PATCH=0
        NEW_VERSION="$NEW_MAJOR.$NEW_MINOR.$NEW_PATCH"
        ;;
    patch)
        NEW_MAJOR=$MAJOR
        NEW_MINOR=$MINOR
        NEW_PATCH=$((PATCH + 1))
        NEW_VERSION="$NEW_MAJOR.$NEW_MINOR.$NEW_PATCH"
        ;;
    *)
        print_error "Invalid bump type: $BUMP_TYPE"
        exit 1
        ;;
esac

print_status "New version will be: $NEW_VERSION ($BUMP_TYPE bump)"

# Ask for confirmation
read -p "Do you want to create release $NEW_VERSION? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Release creation cancelled"
    exit 0
fi

# Update pyproject.toml version
print_status "Updating pyproject.toml version to $NEW_VERSION"

# Create a backup of the original pyproject.toml
cp pyproject.toml ~pyproject.toml

# Update version in pyproject.toml using Python
python3 -c "
import re

# Read the file
with open('pyproject.toml', 'r') as f:
    content = f.read()

# Replace the version line
content = re.sub(r'version = \"[^\"]+\"', f'version = \"$NEW_VERSION\"', content)

# Write back to file
with open('pyproject.toml', 'w') as f:
    f.write(content)
"

print_success "Updated pyproject.toml version"

# Run tests to ensure everything works
print_status "Running tests to verify the project works..."
TEST_SUCCESS=true

# Install dependencies if needed (in case this is run in a fresh environment)
if [ ! -d ".venv" ] && [ ! -f "requirements.txt" ]; then
    print_status "Installing project dependencies..."
    if ! pip install -e .; then
        print_warning "Failed to install dependencies, tests may fail"
    fi
fi

# Run pytest
if command -v pytest &> /dev/null; then
    if ! pytest --tb=short -v; then
        TEST_SUCCESS=false
    fi
else
    print_warning "pytest not found, running python -m pytest instead"
    if ! python -m pytest --tb=short -v; then
        TEST_SUCCESS=false
    fi
fi

# Check if tests failed and restore backup if needed
if [ "$TEST_SUCCESS" = false ]; then
    print_error "Tests failed! Restoring original pyproject.toml..."
    mv ~pyproject.toml pyproject.toml
    print_error "pyproject.toml has been restored to original state"
    print_error "Please fix the test failures before creating a release"
    exit 1
fi

# Remove backup since tests succeeded
rm ~pyproject.toml
print_success "Tests completed successfully"

# Commit the version change
print_status "Committing version change"
git add pyproject.toml
git commit -m "chore: bump version to $NEW_VERSION"

# Create git tag
print_status "Creating git tag v$NEW_VERSION"
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"

# Push changes and tags
print_status "Pushing changes and tags to remote"
git push origin $(git branch --show-current)
git push origin "v$NEW_VERSION"

print_success "Git tag v$NEW_VERSION created and pushed"

# Create GitHub release
if [ "$USE_GH" = true ]; then
    print_status "Creating GitHub release"
    
    # Generate release notes (basic changelog)
    RELEASE_NOTES="## What's Changed

Release v$NEW_VERSION"

    # Try to generate changelog from previous version
    if git rev-parse "v$CURRENT_VERSION" >/dev/null 2>&1; then
        # Previous version tag exists
        CHANGELOG=$(git log v$CURRENT_VERSION..HEAD --pretty=format:'- %s (%h)' --no-merges 2>/dev/null || echo "- Initial release")
        RELEASE_NOTES="$RELEASE_NOTES

### Changes since v$CURRENT_VERSION:
$CHANGELOG

**Full Changelog**: https://github.com/xtreamium/xtreamium-api/compare/v$CURRENT_VERSION...v$NEW_VERSION"
    else
        # No previous version tag, get recent commits
        RECENT_COMMITS=$(git log --oneline -10 --pretty=format:'- %s (%h)' 2>/dev/null || echo "- Initial release")
        RELEASE_NOTES="$RELEASE_NOTES

### Recent Changes:
$RECENT_COMMITS"
    fi

    if gh release create "v$NEW_VERSION" \
        --title "Release v$NEW_VERSION" \
        --notes "$RELEASE_NOTES" \
        --latest; then
        print_success "GitHub release v$NEW_VERSION created successfully"
        print_status "Release URL: https://github.com/xtreamium/xtreamium-api/releases/tag/v$NEW_VERSION"
    else
        print_error "Failed to create GitHub release. You can create it manually at:"
        print_error "https://github.com/xtreamium/xtreamium-api/releases/new?tag=v$NEW_VERSION"
    fi
else
    print_warning "GitHub CLI not available. Please create the release manually at:"
    print_warning "https://github.com/xtreamium/xtreamium-api/releases/new?tag=v$NEW_VERSION"
fi

# Clear the trap since we completed successfully
trap - EXIT

print_success "Release process completed!"
print_status "Version $NEW_VERSION has been:"
print_status "  ✓ Updated in pyproject.toml"
print_status "  ✓ Committed to git"
print_status "  ✓ Tagged as v$NEW_VERSION"
print_status "  ✓ Pushed to remote repository"
if [ "$USE_GH" = true ]; then
    print_status "  ✓ Published as GitHub release"
else
    print_status "  ⚠ GitHub release needs to be created manually"
fi