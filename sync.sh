if [ -z "$1" ]; then
  echo "Error: Commit message required."
  exit 1
fi

git add .
git commit -m "$1"
git push origin main