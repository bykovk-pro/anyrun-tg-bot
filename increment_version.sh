#!/bin/bash

# Read current version
version=$(cat version.txt)

# Split version into components
IFS='.' read -ra ADDR <<< "$version"
major="${ADDR[0]}"
minor="${ADDR[1]}"
patch="${ADDR[2]}"

# Increment version based on the argument
case "$1" in
  major)
    major=$((major + 1))
    minor=0
    patch=0
    ;;
  minor)
    minor=$((minor + 1))
    patch=0
    ;;
  patch)
    patch=$((patch + 1))
    ;;
  *)
    echo "Invalid argument. Use 'major', 'minor', or 'patch'."
    exit 1
    ;;
esac

# Assemble new version
new_version="$major.$minor.$patch"

# Write new version to file
echo $new_version > version.txt

echo "Version bumped to $new_version"
