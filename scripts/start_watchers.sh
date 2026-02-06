#!/bin/bash
#
# Quick start script for Watcher Manager
#
# Usage:
#   ./scripts/start_watchers.sh          # Start all watchers
#   ./scripts/start_watchers.sh stop     # Stop all watchers
#   ./scripts/start_watchers.sh status   # Check status
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "=================================="
echo "AI Employee Watcher Manager"
echo "=================================="
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# Parse command
COMMAND="${1:-start}"

case "$COMMAND" in
    start)
        echo "Starting watcher manager..."
        echo ""

        # Check if rich is installed
        if ! python -c "import rich" 2>/dev/null; then
            echo -e "${YELLOW}[WARNING] 'rich' not installed${NC}"
            echo "For beautiful dashboard, install with: pip install rich"
            echo ""
        fi

        # Start manager
        python scripts/watcher_manager.py
        ;;

    stop)
        echo "Stopping all watchers..."
        python scripts/watcher_manager.py --stop
        ;;

    status)
        echo "Checking watcher status..."
        echo ""
        python scripts/watcher_manager.py --status
        ;;

    config)
        echo "Current configuration:"
        echo ""
        python scripts/watcher_manager.py --config
        ;;

    *)
        echo -e "${RED}[ERROR] Unknown command: $COMMAND${NC}"
        echo ""
        echo "Usage:"
        echo "  $0 [start|stop|status|config]"
        echo ""
        exit 1
        ;;
esac
