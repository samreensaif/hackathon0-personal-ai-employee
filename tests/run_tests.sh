#!/usr/bin/env bash

################################################################################
# Test Runner Script for Gmail MCP Server
#
# This script provides convenient commands for running different test suites.
#
# Usage:
#   ./tests/run_tests.sh [command] [options]
#
# Commands:
#   all           - Run all mock tests (safe for CI/CD)
#   integration   - Run integration tests (requires Gmail API)
#   coverage      - Run tests with coverage report
#   quick         - Run quick tests only (skip slow tests)
#   failed        - Re-run last failed tests
#   specific      - Run specific test by name
#   watch         - Run tests on file changes
#   clean         - Clean test artifacts
#
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Project paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEST_DIR="$SCRIPT_DIR"

# Print colored message
print_color() {
    local color=$1
    shift
    echo -e "${color}$*${NC}"
}

print_header() {
    echo ""
    print_color "$BLUE" "=========================================="
    print_color "$BLUE" "$1"
    print_color "$BLUE" "=========================================="
    echo ""
}

print_success() {
    print_color "$GREEN" "✓ $1"
}

print_error() {
    print_color "$RED" "✗ $1"
}

print_info() {
    print_color "$YELLOW" "ℹ $1"
}

# Check dependencies
check_dependencies() {
    if ! command -v pytest &> /dev/null; then
        print_error "pytest not found. Installing dependencies..."
        pip install -r "$TEST_DIR/requirements.txt"
    fi
}

# Run all mock tests
cmd_all() {
    print_header "Running All Mock Tests"
    cd "$PROJECT_ROOT"
    pytest tests/test_email_mcp.py -v "$@"
}

# Run integration tests
cmd_integration() {
    print_header "Running Integration Tests"
    print_info "This requires real Gmail API access"
    cd "$PROJECT_ROOT"
    pytest tests/test_email_mcp.py -v --run-integration "$@"
}

# Run with coverage
cmd_coverage() {
    print_header "Running Tests with Coverage"
    cd "$PROJECT_ROOT"
    pytest tests/test_email_mcp.py -v \
        --cov=mcp_servers/email \
        --cov-report=html \
        --cov-report=term-missing \
        "$@"

    print_success "Coverage report generated: htmlcov/index.html"
}

# Run quick tests (skip slow)
cmd_quick() {
    print_header "Running Quick Tests"
    cd "$PROJECT_ROOT"
    pytest tests/test_email_mcp.py -v -m "not slow" "$@"
}

# Re-run failed tests
cmd_failed() {
    print_header "Re-running Failed Tests"
    cd "$PROJECT_ROOT"
    pytest tests/test_email_mcp.py -v --lf "$@"
}

# Run specific test
cmd_specific() {
    if [ -z "$1" ]; then
        print_error "Please specify test name"
        echo "Example: ./tests/run_tests.sh specific TestDraftEmail::test_draft_email_success"
        exit 1
    fi

    print_header "Running Specific Test: $1"
    cd "$PROJECT_ROOT"
    pytest "tests/test_email_mcp.py::$1" -v "${@:2}"
}

# Watch mode (requires pytest-watch)
cmd_watch() {
    print_header "Running Tests in Watch Mode"
    cd "$PROJECT_ROOT"

    if ! command -v ptw &> /dev/null; then
        print_info "Installing pytest-watch..."
        pip install pytest-watch
    fi

    ptw tests/test_email_mcp.py -- -v "$@"
}

# Clean test artifacts
cmd_clean() {
    print_header "Cleaning Test Artifacts"

    rm -rf "$PROJECT_ROOT/htmlcov"
    rm -rf "$PROJECT_ROOT/.pytest_cache"
    rm -rf "$PROJECT_ROOT/.coverage"
    rm -rf "$PROJECT_ROOT/tests/__pycache__"
    rm -rf "$PROJECT_ROOT/tests/*.pyc"

    print_success "Test artifacts cleaned"
}

# Show usage
show_usage() {
    cat << EOF
${BLUE}Gmail MCP Server Test Runner${NC}

${YELLOW}USAGE:${NC}
    $0 [COMMAND] [OPTIONS]

${YELLOW}COMMANDS:${NC}
    all           Run all mock tests (safe for CI/CD)
    integration   Run integration tests (requires Gmail API)
    coverage      Run tests with coverage report
    quick         Run quick tests only (skip slow tests)
    failed        Re-run last failed tests
    specific      Run specific test by name
    watch         Run tests on file changes
    clean         Clean test artifacts
    help          Show this help message

${YELLOW}OPTIONS:${NC}
    -v, --verbose         Verbose output
    -s, --capture=no      Show print statements
    -x, --exitfirst       Stop on first failure
    -k EXPRESSION         Run tests matching expression
    --pdb                 Drop into debugger on failure

${YELLOW}EXAMPLES:${NC}
    # Run all mock tests
    $0 all

    # Run with verbose output
    $0 all -v

    # Run integration tests
    $0 integration

    # Run tests with coverage
    $0 coverage

    # Run specific test
    $0 specific TestDraftEmail::test_draft_email_success

    # Run quick tests only
    $0 quick

    # Re-run failed tests
    $0 failed

    # Run in watch mode
    $0 watch

    # Run tests matching pattern
    $0 all -k "draft"

    # Clean artifacts
    $0 clean

${YELLOW}MARKERS:${NC}
    integration   Tests requiring real Gmail API
    slow          Slow-running tests
    rate_limit    Rate limiting tests

${YELLOW}FILTER BY MARKER:${NC}
    # Only integration tests
    $0 all -m integration

    # Exclude integration tests
    $0 all -m "not integration"

    # Only slow tests
    $0 all -m slow

EOF
}

# Main entry point
main() {
    # Check dependencies
    check_dependencies

    # Parse command
    local command=${1:-all}
    shift || true

    case "$command" in
        all)
            cmd_all "$@"
            ;;
        integration)
            cmd_integration "$@"
            ;;
        coverage)
            cmd_coverage "$@"
            ;;
        quick)
            cmd_quick "$@"
            ;;
        failed)
            cmd_failed "$@"
            ;;
        specific)
            cmd_specific "$@"
            ;;
        watch)
            cmd_watch "$@"
            ;;
        clean)
            cmd_clean
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

# Run main
main "$@"
