#!/bin/bash
# Docker Compose Manager for Elenchus Legal AI
# Manages production and development Docker environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
DEV_COMPOSE_FILE="docker-compose.dev.yml"
PROD_COMPOSE_FILE="docker-compose.yml"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Help function
show_help() {
    print_header "🐳 Docker Compose Manager for Elenchus Legal AI"
    echo ""
    echo "Usage: $0 <environment> <action> [options]"
    echo ""
    echo "Environments:"
    echo "  dev      - Development (MongoDB + RAG stack only)"
    echo "  prod     - Production (Full stack: MongoDB, Backend, Frontend, RAG)"
    echo ""
    echo "Actions:"
    echo "  up       - Start services"
    echo "  down     - Stop and remove services"
    echo "  restart  - Restart services"
    echo "  logs     - Show logs"
    echo "  status   - Show service status"
    echo "  clean    - Clean up volumes and networks"
    echo ""
    echo "Options:"
    echo "  --build  - Force rebuild images"
    echo "  --worker - Include RAG worker (development only)"
    echo ""
    echo "Examples:"
    echo "  $0 dev up              # Start development infrastructure"
    echo "  $0 dev up --worker     # Start development with RAG worker"
    echo "  $0 prod up --build     # Start production with rebuild"
    echo "  $0 dev logs            # Show development logs"
    echo "  $0 prod status         # Show production service status"
}

# Get Docker Compose file based on environment
get_compose_file() {
    local env=$1
    case $env in
        dev|development)
            echo $DEV_COMPOSE_FILE
            ;;
        prod|production)
            echo $PROD_COMPOSE_FILE
            ;;
        *)
            print_error "Unknown environment: $env"
            show_help
            exit 1
            ;;
    esac
}

# Start services
start_services() {
    local env=$1
    local compose_file=$(get_compose_file $env)
    local build_flag=""
    local profile_flags=""
    
    # Parse additional arguments
    shift
    while [[ $# -gt 0 ]]; do
        case $1 in
            --build)
                build_flag="--build"
                shift
                ;;
            --worker)
                if [[ $env == "dev" ]]; then
                    profile_flags="--profile worker"
                fi
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    print_header "🚀 Starting $env environment"
    print_status "Using compose file: $compose_file"
    
    if [[ -n $build_flag ]]; then
        print_status "Building images..."
    fi
    
    if [[ -n $profile_flags ]]; then
        print_status "Including additional profiles: $profile_flags"
    fi
    
    docker-compose -f $compose_file up -d $build_flag $profile_flags
    
    print_status "Services started successfully!"
    
    # Show service URLs
    echo ""
    if [[ $env == "dev" ]]; then
        print_header "🔗 Development Infrastructure URLs:"
        echo "  🗃️  MongoDB:        localhost:27018"
        echo "  🔍 Qdrant:         http://localhost:6333"
        echo "  🔄 Redis RAG:      localhost:6380"
        echo "  📊 RQ Dashboard:   http://localhost:9181"
        echo ""
        print_status "Ready for local development with devrun.sh"
    else
        print_header "🔗 Production Application URLs:"
        echo "  🌐 Frontend:       http://localhost:3001"
        echo "  🔧 Backend:        http://localhost:8001"
        echo "  📚 API Docs:       http://localhost:8001/docs"
        echo "  📊 RQ Dashboard:   http://localhost:9181"
    fi
}

# Stop services
stop_services() {
    local env=$1
    local compose_file=$(get_compose_file $env)
    
    print_header "🛑 Stopping $env environment"
    docker-compose -f $compose_file down
    print_status "Services stopped successfully!"
}

# Restart services
restart_services() {
    local env=$1
    local compose_file=$(get_compose_file $env)
    
    print_header "🔄 Restarting $env environment"
    docker-compose -f $compose_file restart
    print_status "Services restarted successfully!"
}

# Show logs
show_logs() {
    local env=$1
    local compose_file=$(get_compose_file $env)
    
    print_header "📝 Showing $env environment logs"
    docker-compose -f $compose_file logs -f --tail=100
}

# Show status
show_status() {
    local env=$1
    local compose_file=$(get_compose_file $env)
    
    print_header "📊 $env environment status"
    docker-compose -f $compose_file ps
}

# Clean up
cleanup() {
    local env=$1
    local compose_file=$(get_compose_file $env)
    
    print_warning "⚠️  This will remove all containers, volumes, and networks for $env environment"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_header "🧹 Cleaning up $env environment"
        docker-compose -f $compose_file down -v --remove-orphans
        print_status "Cleanup completed!"
    else
        print_status "Cleanup cancelled"
    fi
}

# Main script logic
if [[ $# -lt 2 ]]; then
    show_help
    exit 1
fi

ENV=$1
ACTION=$2

# Validate environment and action
case $ACTION in
    up|start)
        start_services $ENV "${@:3}"
        ;;
    down|stop)
        stop_services $ENV
        ;;
    restart)
        restart_services $ENV
        ;;
    logs)
        show_logs $ENV
        ;;
    status|ps)
        show_status $ENV
        ;;
    clean|cleanup)
        cleanup $ENV
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown action: $ACTION"
        show_help
        exit 1
        ;;
esac