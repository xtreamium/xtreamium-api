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

# Cleanup function to restore package.json if script exits unexpectedly
cleanup() {
    if [ -f "~package.json" ]; then
        print_warning "Script interrupted. Restoring original package.json..."
        mv ~package.json package.json
        print_success "Original package.json restored"
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

Create a new release by incrementing the version in package.json and publishing to GitHub.

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
    2. Read current version from package.json
    3. Increment the specified version component
    4. Update package.json with new version
    5. Build the project to verify it works
    6. Commit the version change to git
    7. Create and push a git tag
    8. Create a GitHub release (if gh CLI is available)

REQUIREMENTS:
    - Git repository with remote configured
    - Node.js (for reading/updating package.json)
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

# Check if package.json exists
if [ ! -f "package.json" ]; then
    print_error "package.json not found in current directory"
    exit 1
fi

# Check if gh CLI is installed for GitHub releases
if ! command -v gh &> /dev/null; then
    print_warning "GitHub CLI (gh) not found. Release will be created without GitHub CLI."
    USE_GH=false
else
    USE_GH=true
fi

# Get current version from package.json
CURRENT_VERSION=$(node -p "require('./package.json').version")
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

# Update package.json version
print_status "Updating package.json version to $NEW_VERSION"

# Create a backup of the original package.json
cp package.json ~package.json

if command -v node &> /dev/null; then
    node -e "
        const fs = require('fs');
        const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
        pkg.version = '$NEW_VERSION';
        fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
    "
else
    # Fallback using sed (less reliable but works without Node.js)
    sed -i.bak "s/\"version\": \"$CURRENT_VERSION\"/\"version\": \"$NEW_VERSION\"/" package.json
    rm package.json.bak
fi

print_success "Updated package.json version"

# Build the project to ensure everything works
print_status "Building project to verify everything works..."
BUILD_SUCCESS=true

if command -v bun &> /dev/null; then
    if ! bun run build; then
        BUILD_SUCCESS=false
    fi
else
    if ! npm run build; then
        BUILD_SUCCESS=false
    fi
fi

# Check if build failed and restore backup if needed
if [ "$BUILD_SUCCESS" = false ]; then
    print_error "Build failed! Restoring original package.json..."
    mv ~package.json package.json
    print_error "Package.json has been restored to original state"
    print_error "Please fix the build issues before creating a release"
    exit 1
fi

# Remove backup since build succeeded
rm ~package.json
print_success "Build completed successfully"

# Commit the version change
print_status "Committing version change"
git add package.json
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

Release v$NEW_VERSION

### Changes since v$CURRENT_VERSION:
$(git log v$CURRENT_VERSION..HEAD --pretty=format:'- %s (%h)' --no-merges)

**Full Changelog**: https://github.com/xtreamium/xtreamium-web/compare/v$CURRENT_VERSION...v$NEW_VERSION"

    if gh release create "v$NEW_VERSION" \
        --title "Release v$NEW_VERSION" \
        --notes "$RELEASE_NOTES" \
        --latest; then
        print_success "GitHub release v$NEW_VERSION created successfully"
        print_status "Release URL: https://github.com/xtreamium/xtreamium-web/releases/tag/v$NEW_VERSION"
    else
        print_error "Failed to create GitHub release. You can create it manually at:"
        print_error "https://github.com/xtreamium/xtreamium-web/releases/new?tag=v$NEW_VERSION"
    fi
else
    print_warning "GitHub CLI not available. Please create the release manually at:"
    print_warning "https://github.com/xtreamium/xtreamium-web/releases/new?tag=v$NEW_VERSION"
fi

# Clear the trap since we completed successfully
trap - EXIT

print_success "Release process completed!"
print_status "Version $NEW_VERSION has been:"
print_status "  ✓ Updated in package.json"
print_status "  ✓ Committed to git"
print_status "  ✓ Tagged as v$NEW_VERSION"
print_status "  ✓ Pushed to remote repository"
if [ "$USE_GH" = true ]; then
    print_status "  ✓ Published as GitHub release"
else
    print_status "  ⚠ GitHub release needs to be created manually"
fi