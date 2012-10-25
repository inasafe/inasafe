[[ -n "$1" ]] || { echo "Usage: ./git-log-since.sh commitHash"; exit 0 ; }
git log $1..HEAD --pretty=format:"%an; %s"
