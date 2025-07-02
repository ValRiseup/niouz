#!/bin/bash

echo "🚀 Starting both AI News platforms..."

# Start the AI platform in the background
echo "📡 Starting AI Platform on port 5177..."
cd /Users/valentinnavaron/Desktop/AI-NEWS
npm run dev &
AI_PID=$!

# Wait a moment
sleep 2

# Start the Politics platform in the background  
echo "🏛️ Starting Politics Platform on port 5178..."
cd /Users/valentinnavaron/Desktop/AI-NEWS/AI-NEWS-POLITICS
npm run dev &
POLITICS_PID=$!

echo ""
echo "✅ Both platforms are starting up!"
echo "🤖 AI Platform: http://localhost:5177"
echo "🏛️ Politics Platform: http://localhost:5178"
echo ""
echo "Use the category selector in the header to switch between platforms"
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop the servers
trap "kill $AI_PID $POLITICS_PID 2>/dev/null; exit" INT
wait 