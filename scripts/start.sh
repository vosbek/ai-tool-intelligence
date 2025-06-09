#!/bin/bash
# start.sh - Start the AI Tool Intelligence platform

echo "🚀 Starting AI Tool Intelligence Platform..."

# Check if backend dependencies are installed
if [ ! -d "../backend/venv" ]; then
    echo "❌ Backend not set up. Run ./setup.sh first"
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "../frontend/node_modules" ]; then
    echo "❌ Frontend not set up. Run ./setup.sh first"
    exit 1
fi

# Start backend
echo "Starting Flask backend..."
cd ../backend
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Creating .env from template - PLEASE CONFIGURE YOUR AWS CREDENTIALS!"
    cp .env.example .env
    echo ""
    echo "🔧 IMPORTANT: Edit backend/.env with your AWS credentials before using the research features"
    echo ""
fi

python app.py &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to start
sleep 5

# Start frontend
echo "Starting React frontend..."
cd ../frontend
npm start &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

echo ""
echo "✅ Platform started successfully!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:5000"
echo ""
echo "📖 Next steps:"
echo "1. Configure AWS credentials in backend/.env"
echo "2. Enable Claude 3.7 Sonnet access in AWS Bedrock console"
echo "3. Open http://localhost:3000 to start adding tools"
echo ""
echo "Press Ctrl+C to stop both services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for processes
wait