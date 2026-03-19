#!/bin/bash
read -p "Enter commit message: " message
echo "Pushing changes to the repository..."
git add -A
git commit -m "$message"
git push origin main