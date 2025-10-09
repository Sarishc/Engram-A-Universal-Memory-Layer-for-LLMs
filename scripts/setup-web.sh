#!/bin/bash

# Engram Web UI Setup Script
set -e

echo "🚀 Setting up Engram Web UI..."

# Check if we're in the right directory
if [ ! -f "apps/web/package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Navigate to web app directory
cd apps/web

echo "📦 Installing dependencies..."
npm install

echo "🔧 Setting up environment..."
if [ ! -f ".env.local" ]; then
    cp .env.local.example .env.local
    echo "✅ Created .env.local from example"
    echo "⚠️  Please edit .env.local with your API configuration"
else
    echo "✅ .env.local already exists"
fi

echo "🔍 Running linting..."
npm run lint || echo "⚠️  Linting found some issues (non-fatal)"

echo "🎨 Formatting code..."
npm run format

echo "🏗️  Building project..."
npm run build

echo "🧪 Running tests..."
npm run test || echo "⚠️  Some tests may have failed (check your API connection)"

echo ""
echo "✅ Web UI setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit apps/web/.env.local with your API configuration"
echo "2. Start the development server: npm run dev"
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "🐳 Or use Docker:"
echo "docker-compose up web"
echo ""
echo "📚 For more information, see apps/web/README.md"
