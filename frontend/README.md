# AI Travel Agent - Frontend

Modern, beautiful React/Next.js frontend for the AI Travel Agent.

## Features

- 🎨 **UI**: Gradient backgrounds, glassmorphism, smooth animations
- 📱 **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- ⚡ **Real-time Planning**: Live updates during trip planning
- 🎭 **Smooth Animations**: Framer Motion for delightful interactions
- 🎯 **Comprehensive Forms**: All travel parameters (purpose, party size, budget, etc.)

## Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Visit: `http://localhost:3000`

## Backend Connection

Make sure the FastAPI backend is running:

```bash
# In the root directory (parent of frontend)
source venv/bin/activate
uvicorn api.server:app --reload --port 8000
```

## Environment Variables

Create `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Technologies

- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe code
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Animations
- **Lucide React**: Beautiful icons
- **Axios**: HTTP client
