#!/bin/bash

# Umami Analytics Setup Script
# This script helps set up Umami analytics server for Mentora

echo "🚀 Setting up Umami Analytics for Mentora..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Generate a random APP_SECRET
APP_SECRET=$(openssl rand -hex 32)

# Create .env file for Umami
cat > umami.env << EOF
DATABASE_URL=postgresql://umami:umami@db:5432/umami
DATABASE_TYPE=postgresql
APP_SECRET=${APP_SECRET}
EOF

echo "✅ Generated Umami configuration"

# Start Umami services
echo "🐳 Starting Umami services..."
docker-compose -f umami-docker-compose.yml --env-file umami.env up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check if Umami is running
if curl -f http://localhost:3001/api/heartbeat > /dev/null 2>&1; then
    echo "✅ Umami is running successfully!"
    echo ""
    echo "📊 Umami Analytics Dashboard: http://localhost:3001"
    echo "👤 Default login: admin / umami"
    echo ""
    echo "🔧 Next steps:"
    echo "1. Login to Umami dashboard"
    echo "2. Create a new website"
    echo "3. Copy the website ID"
    echo "4. Update frontend/.env with your website ID:"
    echo "   VITE_UMAMI_WEBSITE_ID=your-website-id-here"
    echo "   VITE_UMAMI_SRC=http://localhost:3001/script.js"
    echo ""
else
    echo "❌ Umami failed to start. Check logs with:"
    echo "docker-compose -f umami-docker-compose.yml logs"
fi