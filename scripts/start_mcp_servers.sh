#!/usr/bin/env bash

################################################################################
# MCP Servers Startup Script (Linux/macOS/WSL)
#
# This script starts all MCP servers in the background, monitors their health,
# and provides status reporting with colored output.
#
# Usage:
#   ./scripts/start_mcp_servers.sh [start|stop|status|restart]
#
# Requirements:
#   - Node.js (for Gmail server)
#   - netstat or ss (for port checking)
#
# Logs:
#   - mcp_servers/logs/YYYY-MM-DD.log
#   - Individual server logs in mcp_servers/logs/[server-name].log
#
################################################################################

set -e  # Exit on error

# =============================================================================
# CONFIGURATION
# =============================================================================

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Log directory
LOG_DIR="$PROJECT_ROOT/mcp_servers/logs"
TIMESTAMP=$(date +%Y-%m-%d)
MAIN_LOG="$LOG_DIR/$TIMESTAMP.log"
PID_DIR="$LOG_DIR/pids"

# Server configurations
declare -A SERVERS=(
    ["gmail"]="node mcp_servers/email/server.js"
)

declare -A SERVER_PORTS=(
    ["gmail"]="0"  # stdio servers don't use ports
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

# Print colored message
print_color() {
    local color=$1
    shift
    echo -e "${color}$*${NC}"
}

# Print section header
print_header() {
    echo ""
    print_color "$CYAN" "=========================================="
    print_color "$CYAN" "$1"
    print_color "$CYAN" "=========================================="
    echo ""
}

# Print success message
print_success() {
    print_color "$GREEN" "✓ $1"
}

# Print error message
print_error() {
    print_color "$RED" "✗ $1"
}

# Print warning message
print_warning() {
    print_color "$YELLOW" "⚠ $1"
}

# Print info message
print_info() {
    print_color "$BLUE" "ℹ $1"
}

# Log message to file
log_message() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$MAIN_LOG"
}

# Ensure directories exist
ensure_directories() {
    mkdir -p "$LOG_DIR"
    mkdir -p "$PID_DIR"

    # Create log file if it doesn't exist
    touch "$MAIN_LOG"

    log_message "INFO" "Directories initialized"
}

# Check if a process is running by PID
is_process_running() {
    local pid=$1
    if ps -p "$pid" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Get PID for a server
get_server_pid() {
    local server_name=$1
    local pid_file="$PID_DIR/${server_name}.pid"

    if [ -f "$pid_file" ]; then
        cat "$pid_file"
    else
        echo ""
    fi
}

# Check if server is running
is_server_running() {
    local server_name=$1
    local pid=$(get_server_pid "$server_name")

    if [ -n "$pid" ] && is_process_running "$pid"; then
        return 0
    else
        return 1
    fi
}

# Start a single server
start_server() {
    local server_name=$1
    local command=${SERVERS[$server_name]}
    local pid_file="$PID_DIR/${server_name}.pid"
    local log_file="$LOG_DIR/${server_name}.log"

    print_info "Starting $server_name..."
    log_message "INFO" "Starting server: $server_name"

    # Check if already running
    if is_server_running "$server_name"; then
        print_warning "$server_name is already running (PID: $(get_server_pid $server_name))"
        log_message "WARN" "$server_name already running"
        return 0
    fi

    # Change to project root
    cd "$PROJECT_ROOT"

    # Start the server in background
    # Redirect stdout and stderr to log file
    nohup $command >> "$log_file" 2>&1 &
    local pid=$!

    # Save PID
    echo "$pid" > "$pid_file"

    # Wait a moment and check if it's still running
    sleep 2

    if is_process_running "$pid"; then
        print_success "$server_name started successfully (PID: $pid)"
        log_message "INFO" "$server_name started with PID: $pid"
        return 0
    else
        print_error "$server_name failed to start"
        log_message "ERROR" "$server_name failed to start"

        # Show last few lines of log
        if [ -f "$log_file" ]; then
            print_error "Last 5 lines of log:"
            tail -n 5 "$log_file" | sed 's/^/  /'
        fi

        # Remove PID file
        rm -f "$pid_file"
        return 1
    fi
}

# Stop a single server
stop_server() {
    local server_name=$1
    local pid=$(get_server_pid "$server_name")
    local pid_file="$PID_DIR/${server_name}.pid"

    print_info "Stopping $server_name..."
    log_message "INFO" "Stopping server: $server_name"

    if [ -z "$pid" ]; then
        print_warning "$server_name is not running (no PID file)"
        return 0
    fi

    if ! is_process_running "$pid"; then
        print_warning "$server_name is not running (stale PID)"
        rm -f "$pid_file"
        return 0
    fi

    # Try graceful shutdown first
    kill "$pid" 2>/dev/null || true

    # Wait up to 10 seconds for graceful shutdown
    local count=0
    while is_process_running "$pid" && [ $count -lt 10 ]; do
        sleep 1
        ((count++))
    done

    # Force kill if still running
    if is_process_running "$pid"; then
        print_warning "Forcing shutdown of $server_name..."
        kill -9 "$pid" 2>/dev/null || true
        sleep 1
    fi

    # Check if stopped
    if ! is_process_running "$pid"; then
        print_success "$server_name stopped"
        log_message "INFO" "$server_name stopped"
        rm -f "$pid_file"
        return 0
    else
        print_error "Failed to stop $server_name"
        log_message "ERROR" "Failed to stop $server_name"
        return 1
    fi
}

# Get server status
get_server_status() {
    local server_name=$1
    local pid=$(get_server_pid "$server_name")

    printf "  ${BOLD}%-15s${NC}" "$server_name"

    if [ -z "$pid" ]; then
        printf "${RED}%-12s${NC}" "STOPPED"
        printf "%-10s" "-"
        printf "%-30s" "-"
    elif is_process_running "$pid"; then
        printf "${GREEN}%-12s${NC}" "RUNNING"
        printf "%-10s" "$pid"

        # Get process uptime (macOS and Linux compatible)
        if command -v ps &> /dev/null; then
            local uptime=$(ps -o etime= -p "$pid" 2>/dev/null | tr -d ' ' || echo "N/A")
            printf "%-30s" "$uptime"
        else
            printf "%-30s" "N/A"
        fi
    else
        printf "${YELLOW}%-12s${NC}" "CRASHED"
        printf "%-10s" "$pid (stale)"
        printf "%-30s" "-"
    fi

    echo ""
}

# Health check for a server
health_check_server() {
    local server_name=$1

    if is_server_running "$server_name"; then
        # For stdio servers, just check if process is alive
        # For HTTP servers, you could add actual HTTP health checks here
        return 0
    else
        return 1
    fi
}

# =============================================================================
# MAIN COMMANDS
# =============================================================================

# Start all servers
cmd_start() {
    print_header "Starting MCP Servers"

    ensure_directories

    local failed=0
    for server_name in "${!SERVERS[@]}"; do
        if ! start_server "$server_name"; then
            ((failed++))
        fi
    done

    echo ""

    if [ $failed -eq 0 ]; then
        print_success "All servers started successfully"
        log_message "INFO" "All servers started"
        return 0
    else
        print_error "$failed server(s) failed to start"
        log_message "ERROR" "$failed servers failed to start"
        return 1
    fi
}

# Stop all servers
cmd_stop() {
    print_header "Stopping MCP Servers"

    local failed=0
    for server_name in "${!SERVERS[@]}"; do
        if ! stop_server "$server_name"; then
            ((failed++))
        fi
    done

    echo ""

    if [ $failed -eq 0 ]; then
        print_success "All servers stopped"
        log_message "INFO" "All servers stopped"
        return 0
    else
        print_error "$failed server(s) failed to stop"
        log_message "ERROR" "$failed servers failed to stop"
        return 1
    fi
}

# Show server status
cmd_status() {
    print_header "MCP Servers Status"

    printf "  ${BOLD}%-15s %-12s %-10s %-30s${NC}\n" "SERVER" "STATUS" "PID" "UPTIME"
    print_color "$CYAN" "  $(printf '%.0s-' {1..70})"

    for server_name in "${!SERVERS[@]}"; do
        get_server_status "$server_name"
    done

    echo ""

    # Show log file locations
    print_info "Logs:"
    echo "  Main log: $MAIN_LOG"
    for server_name in "${!SERVERS[@]}"; do
        echo "  $server_name: $LOG_DIR/${server_name}.log"
    done

    echo ""
}

# Restart servers
cmd_restart() {
    print_header "Restarting MCP Servers"

    cmd_stop
    sleep 2
    cmd_start
}

# Health check
cmd_health() {
    print_header "Health Check"

    local unhealthy=0
    for server_name in "${!SERVERS[@]}"; do
        printf "  Checking $server_name... "
        if health_check_server "$server_name"; then
            print_success "Healthy"
        else
            print_error "Unhealthy"
            ((unhealthy++))
        fi
    done

    echo ""

    if [ $unhealthy -eq 0 ]; then
        print_success "All servers healthy"
        return 0
    else
        print_error "$unhealthy server(s) unhealthy"
        return 1
    fi
}

# Show logs
cmd_logs() {
    local server_name=${1:-}

    if [ -z "$server_name" ]; then
        print_info "Showing main log (last 50 lines):"
        echo ""
        tail -n 50 "$MAIN_LOG"
    else
        local log_file="$LOG_DIR/${server_name}.log"
        if [ -f "$log_file" ]; then
            print_info "Showing $server_name log (last 50 lines):"
            echo ""
            tail -n 50 "$log_file"
        else
            print_error "Log file not found: $log_file"
            return 1
        fi
    fi
}

# Show usage
show_usage() {
    cat << EOF
${BOLD}MCP Servers Management Script${NC}

${BOLD}USAGE:${NC}
    $0 [COMMAND] [OPTIONS]

${BOLD}COMMANDS:${NC}
    start       Start all MCP servers
    stop        Stop all MCP servers
    restart     Restart all MCP servers
    status      Show status of all servers
    health      Run health checks on all servers
    logs [name] Show logs (all or specific server)
    help        Show this help message

${BOLD}EXAMPLES:${NC}
    $0 start              # Start all servers
    $0 stop               # Stop all servers
    $0 status             # Show server status
    $0 logs gmail         # Show gmail server logs
    $0 restart            # Restart all servers

${BOLD}LOG FILES:${NC}
    Main log:     $MAIN_LOG
    Server logs:  $LOG_DIR/[server-name].log
    PID files:    $PID_DIR/[server-name].pid

${BOLD}SERVERS:${NC}
$(for server in "${!SERVERS[@]}"; do echo "    - $server"; done)

EOF
}

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

main() {
    # Check if running as root (not recommended)
    if [ "$EUID" -eq 0 ]; then
        print_warning "Running as root is not recommended"
    fi

    # Parse command
    local command=${1:-status}
    shift || true

    case "$command" in
        start)
            cmd_start
            ;;
        stop)
            cmd_stop
            ;;
        restart)
            cmd_restart
            ;;
        status)
            cmd_status
            ;;
        health)
            cmd_health
            ;;
        logs)
            cmd_logs "$@"
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
