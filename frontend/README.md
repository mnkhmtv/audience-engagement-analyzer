# Lecture Analysis Frontend

Production-ready React + Vite frontend for the FastAPI lecture analysis backend.

## Features

- **Authentication**: JWT-based login/signup with automatic token refresh
- **Lecture Management**: Upload, list, and view lectures
- **Video Analysis**: Real-time status polling with automatic refresh
- **Analytics Dashboard**: 
  - Attention and engagement metrics
  - Emotion distribution charts
  - Peak/dip moments analysis
  - AI-powered improvement suggestions
- **Developer Tools**: Manual video analysis in dev mode

## Prerequisites

- Node.js 16+ and npm/yarn
- FastAPI backend running on http://localhost:8000

## Installation

\`\`\`bash
# Clone and install dependencies
npm install

# Create .env.local file
cat > .env.local << EOF
VITE_API_URL=http://localhost:8000
EOF
\`\`\`

## Development

\`\`\`bash
# Start dev server (http://localhost:3000)
npm run dev

# Run tests
npm test

# Build for production
npm run build

# Preview production build
npm run preview
\`\`\`

## Environment Variables

Create `.env.local`:

\`\`\`
VITE_API_URL=http://localhost:8000  # FastAPI backend URL
\`\`\`

## Project Structure

\`\`\`
src/
├── api/              # API client and endpoints
├── components/       # React components
│   ├── auth/        # Login/signup forms
│   ├── lectures/    # Lecture management
│   ├── analysis/    # Analysis visualization
│   └── dev/         # Developer tools
├── hooks/           # Custom React hooks
├── pages/           # Page components
├── types/           # TypeScript interfaces
├── utils/           # Utilities (JWT, storage)
└── styles/          # Global CSS
\`\`\`

## API Integration

The frontend expects the following FastAPI endpoints:

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/signin` - User login
- `POST /auth/refresh` - Token refresh

### Lectures
- `GET /lectures` - List all lectures
- `GET /lectures/{id}` - Get lecture details
- `POST /lectures/upload` - Upload new lecture
- `GET /lectures/{id}/analysis` - Get analysis results

### Analysis (Dev)
- `POST /analysis/video` - Analyze video manually

## Features Breakdown

### Authentication Flow
- Automatic token refresh before expiration
- JWT stored in localStorage
- Protected routes redirect to login

### Upload Flow
1. User enters title, subject, and selects video
2. Video uploaded to backend
3. Automatic redirect to detail page
4. Status polling starts

### Analysis Display
- Real-time polling updates while processing
- Once complete, shows:
  - Metric cards (attention, engagement, score)
  - Emotion distribution bar chart
  - Peak and dip moments
  - Improvement suggestions

### Developer Panel
- Only visible in development mode
- Allows manual video analysis
- Shows full API response for debugging

## Testing

Basic tests included for:
- JWT utilities
- Auth flows
- Component rendering

\`\`\`bash
npm test
npm test:ui  # Interactive test UI
\`\`\`

## Deployment

\`\`\`bash
# Build production bundle
npm run build

# Output in dist/ directory
# Deploy to Vercel, Netlify, or any static host
\`\`\`

### Vercel Deployment

\`\`\`bash
vercel --prod
\`\`\`

### Docker Deployment

\`\`\`dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm ci && npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
\`\`\`

## Troubleshooting

### CORS Issues
- Ensure FastAPI backend has CORS enabled
- Check `VITE_API_URL` environment variable

### Token Refresh Fails
- Check backend token refresh endpoint
- Verify refresh token hasn't expired
- Clear localStorage and re-login

### Analysis Not Updating
- Check browser console for polling errors
- Verify lecture ID is correct
- Ensure video processing is active on backend

## Performance Optimizations

- React Query for request caching (can be added)
- Code splitting for routes
- Image optimization
- Lazy loading components

## Security

- JWT tokens stored in localStorage (consider httpOnly cookies for production)
- CORS validation on backend
- Input validation on forms
- XSS protection via React

## License

MIT
