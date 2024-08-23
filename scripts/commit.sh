#!/bin/bash

# Check if a commit message was provided
if [ -z "$1" ]; then
  echo "Usage: $0 <new commit message>"
  exit 1
fi

# Get the new commit message from the first argument
new_commit_message="$1"

# Amend the last commit with the new commit message
git commit --amend -m "$new_commit_message"

# Get the SHA of the amended commit
new_commit_hash=$(git rev-parse HEAD)

# Get the SHA of the previous commit before the amendment
old_commit_hash=$(git rev-parse HEAD~1)

# Replace the old commit with the new one
git replace "$old_commit_hash" "$new_commit_hash"

# Force push to the current branch
git push --force

echo "Replaced commit $old_commit_hash with $new_commit_hash and pushed to the current branch."
