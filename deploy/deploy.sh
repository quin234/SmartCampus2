#!/bin/bash

###############################################################################
# SmartCampus Production Deployment Script
# 
# This script handles safe deployment of SmartCampus to production servers
# with comprehensive error handling, logging, and rollback capabilities.
#
# Usage: ./deploy/deploy.sh [--force] [--skip-backup]
###############################################################################

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEPLOY_DIR="$SCRIPT_DIR"
BACKUP_DIR="$DEPLOY_DIR/backups"
LOG_FILE="$DEPLOY_DIR/deploy.log"
LAST_COMMIT_FILE="$DEPLOY_DIR/.last_deployed_commit"
VENV_PATH="${VENV_PATH:-/var/www/smartcampus/venv}"
APP_PATH="${APP_PATH:-/var/www/smartcampus}"
SERVICE_NAME="${SERVICE_NAME:-smartcampus}"
DB_NAME="${DB_NAME:-smartcampus}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Flags
FORCE_DEPLOY=false
SKIP_BACKUP=false

###############################################################################
# Helper Functions
###############################################################################

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() {
    log "INFO" "$@"
    echo -e "${GREEN}[INFO]${NC} $@"
}

log_warn() {
    log "WARN" "$@"
    echo -e "${YELLOW}[WARN]${NC} $@"
}

log_error() {
    log "ERROR" "$@"
    echo -e "${RED}[ERROR]${NC} $@" >&2
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "Required command '$1' not found. Please install it first."
        exit 1
    fi
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    check_command python3
    check_command pip3
    check_command mysql
    check_command systemctl
    
    # Check if running as correct user or with sudo
    if [ "$EUID" -ne 0 ] && ! sudo -n true 2>/dev/null; then
        log_error "This script requires sudo privileges or root access."
        exit 1
    fi
    
    # Check if app directory exists
    if [ ! -d "$APP_PATH" ]; then
        log_error "Application directory not found: $APP_PATH"
        exit 1
    fi
    
    # Check if virtual environment exists
    if [ ! -d "$VENV_PATH" ]; then
        log_warn "Virtual environment not found: $VENV_PATH"
        log_info "Creating virtual environment..."
        python3 -m venv "$VENV_PATH"
    fi
    
    log_info "Prerequisites check passed."
}

backup_database() {
    if [ "$SKIP_BACKUP" = true ]; then
        log_warn "Skipping database backup (--skip-backup flag set)"
        return 0
    fi
    
    log_info "Creating database backup..."
    
    local backup_file="$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"
    
    # Get database credentials from .env file
    if [ ! -f "$APP_PATH/.env" ]; then
        log_error ".env file not found at $APP_PATH/.env"
        return 1
    fi
    
    source "$APP_PATH/.env"
    
    # Backup database
    if mysqldump -u "${DB_USER:-root}" -p"${DB_PASSWORD}" \
        --single-transaction \
        --routines \
        --triggers \
        "$DB_NAME" > "$backup_file" 2>/dev/null; then
        log_info "Database backup created: $backup_file"
        
        # Compress backup
        gzip "$backup_file"
        log_info "Backup compressed: ${backup_file}.gz"
    else
        log_error "Database backup failed!"
        return 1
    fi
}

backup_code() {
    if [ "$SKIP_BACKUP" = true ]; then
        log_warn "Skipping code backup (--skip-backup flag set)"
        return 0
    fi
    
    log_info "Creating code backup..."
    
    local backup_file="$BACKUP_DIR/code_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    mkdir -p "$BACKUP_DIR"
    
    # Backup current code (excluding venv, media, staticfiles)
    if tar -czf "$backup_file" \
        -C "$APP_PATH" \
        --exclude='venv' \
        --exclude='media' \
        --exclude='staticfiles' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.git' \
        . 2>/dev/null; then
        log_info "Code backup created: $backup_file"
    else
        log_error "Code backup failed!"
        return 1
    fi
}

backup_env() {
    if [ "$SKIP_BACKUP" = true ]; then
        return 0
    fi
    
    log_info "Backing up .env file..."
    
    if [ -f "$APP_PATH/.env" ]; then
        cp "$APP_PATH/.env" "$BACKUP_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)"
        log_info ".env file backed up"
    else
        log_warn ".env file not found, skipping backup"
    fi
}

check_git_status() {
    log_info "Checking git status..."
    
    cd "$APP_PATH"
    
    if [ ! -d ".git" ]; then
        log_warn "Not a git repository, skipping git checks"
        return 0
    fi
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        if [ "$FORCE_DEPLOY" = false ]; then
            log_error "Uncommitted changes detected. Use --force to deploy anyway."
            exit 1
        else
            log_warn "Uncommitted changes detected, but --force flag is set"
        fi
    fi
    
    # Get current commit
    CURRENT_COMMIT=$(git rev-parse HEAD)
    log_info "Current commit: $CURRENT_COMMIT"
    
    # Check if we should pull
    git fetch origin
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u})
    
    if [ "$LOCAL" != "$REMOTE" ]; then
        log_info "Remote changes detected. Will pull latest changes."
    else
        log_info "Already up to date with remote."
    fi
}

pull_latest_code() {
    log_info "Pulling latest code from repository..."
    
    cd "$APP_PATH"
    
    if [ ! -d ".git" ]; then
        log_warn "Not a git repository, skipping pull"
        return 0
    fi
    
    # Store previous commit for rollback
    PREVIOUS_COMMIT=$(git rev-parse HEAD)
    echo "$PREVIOUS_COMMIT" > "$LAST_COMMIT_FILE.prev"
    
    # Pull latest changes
    if git pull origin main 2>&1 | tee -a "$LOG_FILE"; then
        NEW_COMMIT=$(git rev-parse HEAD)
        log_info "Code updated. New commit: $NEW_COMMIT"
        echo "$NEW_COMMIT" > "$LAST_COMMIT_FILE"
    else
        log_error "Failed to pull latest code!"
        return 1
    fi
}

install_dependencies() {
    log_info "Installing/updating Python dependencies..."
    
    source "$VENV_PATH/bin/activate"
    
    if [ ! -f "$APP_PATH/requirements.txt" ]; then
        log_error "requirements.txt not found!"
        return 1
    fi
    
    if pip install --upgrade pip && \
       pip install -r "$APP_PATH/requirements.txt" 2>&1 | tee -a "$LOG_FILE"; then
        log_info "Dependencies installed successfully"
    else
        log_error "Failed to install dependencies!"
        return 1
    fi
}

run_migrations() {
    log_info "Running database migrations..."
    
    source "$VENV_PATH/bin/activate"
    cd "$APP_PATH"
    
    # Check for pending migrations
    if python manage.py showmigrations --plan | grep -q "\[ \]"; then
        log_info "Pending migrations detected. Running migrations..."
        
        if python manage.py migrate --noinput 2>&1 | tee -a "$LOG_FILE"; then
            log_info "Migrations completed successfully"
        else
            log_error "Migration failed!"
            return 1
        fi
    else
        log_info "No pending migrations"
    fi
}

collect_static() {
    log_info "Collecting static files..."
    
    source "$VENV_PATH/bin/activate"
    cd "$APP_PATH"
    
    if python manage.py collectstatic --noinput --clear 2>&1 | tee -a "$LOG_FILE"; then
        log_info "Static files collected successfully"
    else
        log_error "Failed to collect static files!"
        return 1
    fi
}

restart_service() {
    log_info "Restarting $SERVICE_NAME service..."
    
    if sudo systemctl restart "$SERVICE_NAME" 2>&1 | tee -a "$LOG_FILE"; then
        sleep 2
        
        # Check service status
        if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
            log_info "Service restarted successfully"
        else
            log_error "Service failed to start!"
            sudo systemctl status "$SERVICE_NAME" | tee -a "$LOG_FILE"
            return 1
        fi
    else
        log_error "Failed to restart service!"
        return 1
    fi
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check service status
    if ! sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        log_error "Service is not running!"
        return 1
    fi
    
    # Check if we can import Django
    source "$VENV_PATH/bin/activate"
    cd "$APP_PATH"
    
    if python -c "import django; django.setup()" 2>&1 | tee -a "$LOG_FILE"; then
        log_info "Django imports successfully"
    else
        log_error "Django import failed!"
        return 1
    fi
    
    log_info "Deployment verification passed"
}

rollback() {
    log_error "Deployment failed! Initiating rollback..."
    
    cd "$APP_PATH"
    
    # Restore previous commit if available
    if [ -f "$LAST_COMMIT_FILE.prev" ]; then
        PREVIOUS_COMMIT=$(cat "$LAST_COMMIT_FILE.prev")
        log_info "Rolling back to commit: $PREVIOUS_COMMIT"
        
        if [ -d ".git" ]; then
            git reset --hard "$PREVIOUS_COMMIT"
        fi
    fi
    
    # Restart service
    restart_service
    
    log_warn "Rollback completed. Please check the logs and fix issues before retrying."
}

cleanup_old_backups() {
    log_info "Cleaning up old backups (keeping last 10)..."
    
    # Keep last 10 database backups
    ls -t "$BACKUP_DIR"/db_backup_*.sql.gz 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true
    
    # Keep last 10 code backups
    ls -t "$BACKUP_DIR"/code_backup_*.tar.gz 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true
    
    log_info "Cleanup completed"
}

###############################################################################
# Main Deployment Function
###############################################################################

main() {
    log_info "=========================================="
    log_info "Starting SmartCampus Deployment"
    log_info "=========================================="
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                FORCE_DEPLOY=true
                shift
                ;;
            --skip-backup)
                SKIP_BACKUP=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Usage: $0 [--force] [--skip-backup]"
                exit 1
                ;;
        esac
    done
    
    # Create log file
    touch "$LOG_FILE"
    
    # Trap errors for rollback
    trap 'rollback; exit 1' ERR
    
    # Run deployment steps
    check_prerequisites
    check_git_status
    backup_database || log_warn "Database backup failed, continuing anyway..."
    backup_code || log_warn "Code backup failed, continuing anyway..."
    backup_env
    pull_latest_code
    install_dependencies
    run_migrations
    collect_static
    restart_service
    verify_deployment
    cleanup_old_backups
    
    # Clear error trap on success
    trap - ERR
    
    log_info "=========================================="
    log_info "Deployment completed successfully!"
    log_info "=========================================="
    
    # Show service status
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
}

# Run main function
main "$@"

