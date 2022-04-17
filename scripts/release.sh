#!/usr/bin/env bash

patchlevel="${1:-patch}"

if ! [[ "$patchlevel" =~ ^(major|minor|patch)$ ]]; then
    echo "Patchlevel must be one of major|minor|patch"
    exit 1
fi
if [ -z "$(git status --porcelain)" ]; then
    echo Repository is clean
else
    echo Repository is dirty, please commit before releasing
    exit 1
fi

current_branch=$((git symbolic-ref HEAD 2>/dev/null || echo "(unnamed branch)")|cut -d/ -f3-)
if [ "$current_branch" != "develop" ]; then
    echo "You are not on develop branch, please switch to develop before releasing"
    exit 1
fi

version=$(python scripts/version_bump.py --release-type "$patchlevel" 2>&1)

echo "Bump version to ${version}"

exit 1
git commit -am "Bump version to ${version}"
git tag -a "v${version}" -m "Release ${version}"

git checkout trunk
git merge develop
git push --tags origin trunk develop

git checkout develop
