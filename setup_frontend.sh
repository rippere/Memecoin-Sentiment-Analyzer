#!/bin/bash
# Frontend Setup Script
# Run this to create the Next.js frontend

echo "=== Setting up Memecoin Dashboard Frontend ==="

# Create frontend directory
mkdir -p frontend
cd frontend

# Initialize Next.js with TypeScript and Tailwind
echo "Creating Next.js project..."
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --no-git

# Install additional dependencies
echo "Installing dependencies..."
npm install recharts @tanstack/react-query axios date-fns lucide-react

# Install shadcn/ui
echo "Setting up shadcn/ui..."
npx shadcn-ui@latest init -y

# Install common shadcn components
npx shadcn-ui@latest add card button tabs table badge

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To start development:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "To start the API:"
echo "  cd api"
echo "  pip install -r requirements.txt"
echo "  python main.py"
echo ""
