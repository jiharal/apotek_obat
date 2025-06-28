#!/bin/bash

# Startup script for Apotek Obat Price Extractor
# Usage: ./start.sh [dev|prod|stop|logs]

set -e

case "$1" in
    "dev"|"")
        echo "🚀 Starting in development mode..."
        docker-compose up --build
        ;;
    "prod")
        echo "🚀 Starting in production mode with Nginx..."
        docker-compose --profile production up --build -d
        echo "✅ Application started at http://localhost"
        ;;
    "stop")
        echo "🛑 Stopping application..."
        docker-compose down
        echo "✅ Application stopped"
        ;;
    "logs")
        echo "📋 Showing application logs..."
        docker-compose logs -f
        ;;
    "restart")
        echo "🔄 Restarting application..."
        docker-compose down
        docker-compose up --build -d
        echo "✅ Application restarted"
        ;;
    "clean")
        echo "🧹 Cleaning up Docker resources..."
        docker-compose down -v
        docker system prune -f
        echo "✅ Cleanup completed"
        ;;
    "backup")
        echo "💾 Creating backup..."
        timestamp=$(date +%Y%m%d_%H%M%S)
        tar -czf "backup_apotek_obat_${timestamp}.tar.gz" pbf/ data/ 2>/dev/null || echo "⚠️  Some directories might not exist yet"
        echo "✅ Backup created: backup_apotek_obat_${timestamp}.tar.gz"
        ;;
    *)
        echo "📖 Usage: $0 [dev|prod|stop|logs|restart|clean|backup]"
        echo ""
        echo "Commands:"
        echo "  dev      - Start in development mode (default)"
        echo "  prod     - Start in production mode with Nginx"
        echo "  stop     - Stop the application"
        echo "  logs     - Show application logs"
        echo "  restart  - Restart the application"
        echo "  clean    - Clean up Docker resources"
        echo "  backup   - Create backup of data directories"
        exit 1
        ;;
esac