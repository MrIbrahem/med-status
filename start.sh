
BRANCH_NAME="${1:-main}"

rm -rf repos/status && git clone https://github.com/MrIbrahem/status.git -b {$BRANCH_NAME} repos/status

python3 repos/status/start.py
