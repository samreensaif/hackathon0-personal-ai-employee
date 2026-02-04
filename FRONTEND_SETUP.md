# Frontend Setup Guide - Next.js + FastAPI

Complete guide to setting up and running the Personal AI Employee frontend.

---

## 📦 What Was Created

### Backend API (FastAPI)
**Location:** `api/server.py`

A REST API that connects the Next.js frontend to the Python task management system.

**Endpoints:**
- `GET /api/stats` - Dashboard statistics
- `GET /api/tasks` - Get all tasks (with filters)
- `GET /api/tasks/{id}` - Get specific task
- `POST /api/tasks` - Create new task
- `POST /api/tasks/{id}/action` - Approve/reject/complete task
- `GET /api/reports/latest` - Get latest CEO briefing
- `POST /api/reports/generate` - Generate new briefing
- `GET /api/logs/today` - Get today's activity logs

### Frontend (Next.js 14)
**Location:** `frontend/`

A modern, responsive web interface built with:
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client
- **React Markdown** - Markdown rendering

**Pages:**
1. **Dashboard** (`/`) - Overview with stats and recent tasks
2. **All Tasks** (`/tasks`) - Filterable task list
3. **Create Task** (`/create`) - Task creation form
4. **CEO Report** (`/reports`) - Executive briefing viewer

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+ (you already have this)
python --version

# Node.js 18+ and npm
node --version
npm --version
```

If you don't have Node.js, download from: https://nodejs.org/

### Step 1: Install Python Dependencies

```bash
# Install FastAPI and Uvicorn
pip install fastapi uvicorn

# Or if that doesn't work:
python -m pip install fastapi uvicorn
```

### Step 2: Start the Backend API

```bash
# From project root
cd api
python server.py

# API will run on http://localhost:8000
# Visit http://localhost:8000/docs for interactive API documentation
```

Leave this terminal running.

### Step 3: Install Frontend Dependencies

```bash
# Open a NEW terminal
cd frontend

# Install dependencies (this may take a few minutes)
npm install
```

### Step 4: Configure Environment

```bash
# Create environment file
cp .env.local.example .env.local

# The default settings should work:
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 5: Start the Frontend

```bash
# Still in frontend/ directory
npm run dev

# Frontend will run on http://localhost:3000
```

### Step 6: Open in Browser

Visit **http://localhost:3000**

You should see the Personal AI Employee dashboard!

---

## 📊 Features

### 1. Dashboard Page (`/`)

**Features:**
- Real-time task statistics
- Pending approval tasks (with approve/reject buttons)
- High priority tasks
- Quick action buttons

**Statistics Displayed:**
- Total Tasks
- Pending Approval
- High Priority
- Completed

### 2. All Tasks Page (`/tasks`)

**Features:**
- View all tasks across folders
- Filter by folder (Inbox, Needs Action, High Priority, etc.)
- Filter by priority (High, Normal, Low)
- Task cards with actionable buttons
- Responsive grid layout

**Task Actions:**
- **Approve** - Move from Pending Approval to Approved
- **Reject** - Move to Rejected folder
- **Complete** - Mark task as done

### 3. Create Task Page (`/create`)

**Features:**
- Task title input
- Description textarea
- Priority selection (High/Normal/Low)
- Auto-categorization hints
- Example tasks for guidance

**Auto-Categorization:**
Tasks are automatically categorized based on keywords:
- **Auto-complete:** "reminder", "note", "FYI" → Done
- **Approval:** "email", "payment", "send" → Pending Approval
- **High Priority:** "urgent", "ASAP", "critical" → High Priority

### 4. CEO Report Page (`/reports`)

**Features:**
- View latest CEO weekly briefing
- Beautiful Markdown rendering
- Generate new reports on-demand
- Executive summary with metrics
- Recommendations and insights

---

## 🎨 UI Components

### TaskCard Component

Displays individual tasks with:
- Priority badge (High/Normal/Low)
- Category badge
- Folder icon
- Created date
- Action buttons (context-aware)

### Navigation Component

Top navigation bar with:
- Logo and branding
- Page links (Dashboard, Tasks, Create, Reports)
- Silver Tier badge
- Responsive mobile menu

---

## 📱 Responsive Design

The frontend is fully responsive and works on:
- **Desktop** (1920px+) - Full features
- **Tablet** (768px-1919px) - Optimized layout
- **Mobile** (320px-767px) - Mobile-friendly UI

---

## 🔧 Development

### Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Dashboard (/)
│   │   ├── tasks/
│   │   │   └── page.tsx        # All Tasks (/tasks)
│   │   ├── create/
│   │   │   └── page.tsx        # Create Task (/create)
│   │   └── reports/
│   │       └── page.tsx        # CEO Report (/reports)
│   ├── components/             # Reusable components
│   │   ├── Navigation.tsx      # Top nav bar
│   │   └── TaskCard.tsx        # Task display card
│   ├── lib/
│   │   └── api.ts              # API client
│   └── types/
│       └── task.ts             # TypeScript types
├── public/                     # Static assets
├── package.json                # Dependencies
├── tsconfig.json               # TypeScript config
├── tailwind.config.ts          # Tailwind CSS config
└── next.config.js              # Next.js config
```

### Available Scripts

```bash
# Development server (with hot reload)
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Adding New Features

1. **New Page:**
   - Create file in `src/app/your-page/page.tsx`
   - Add to navigation in `src/components/Navigation.tsx`

2. **New API Endpoint:**
   - Add to `api/server.py`
   - Add client method in `src/lib/api.ts`
   - Update types in `src/types/task.ts`

3. **New Component:**
   - Create in `src/components/YourComponent.tsx`
   - Import and use in pages

---

## 🔌 API Integration

### How It Works

1. **Frontend** makes HTTP requests to **Backend API**
2. **Backend API** reads/writes files in **AI_Employee_Vault/**
3. **Python scripts** process tasks and create plans
4. **Frontend** displays updated data

### Data Flow

```
User Action (Frontend)
  ↓
HTTP Request (Axios)
  ↓
FastAPI Endpoint (Backend)
  ↓
File System Operations (Vault)
  ↓
Python Task Processing
  ↓
JSON Response
  ↓
Frontend Update (React State)
  ↓
UI Refresh
```

### Creating a Task Example

```typescript
// Frontend (Create Task Page)
const newTask = {
  title: "Send client report",
  description: "Email Q1 report to client",
  priority: "normal"
};

await apiClient.createTask(newTask);

// Backend (FastAPI)
// 1. Receives request
// 2. Creates .md file in vault root
// 3. Watcher picks it up
// 4. Silver Tier processor categorizes
// 5. Task appears in appropriate folder
```

---

## 🐛 Troubleshooting

### Backend Won't Start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
pip install fastapi uvicorn
```

### Frontend Won't Start

**Error:** `Cannot find module 'next'`

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### API Connection Failed

**Error:** `Network Error` or `CORS Error`

**Solutions:**
1. Make sure backend is running on http://localhost:8000
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Restart both servers

### Tasks Not Appearing

**Solutions:**
1. Check backend terminal for errors
2. Verify `AI_Employee_Vault/` folder exists
3. Run `python scripts/runner_silver.py` manually
4. Refresh the frontend page

### Port Already in Use

**Error:** `Port 3000 is already in use`

**Solution:**
```bash
# Kill process on port 3000 (Windows)
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Use different port
npm run dev -- -p 3001
```

---

## 🚀 Production Deployment

### Backend (FastAPI)

**Option 1: Simple**
```bash
cd api
uvicorn server:app --host 0.0.0.0 --port 8000
```

**Option 2: With Gunicorn**
```bash
pip install gunicorn
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend (Next.js)

**Option 1: Vercel (Recommended)**
```bash
npm install -g vercel
cd frontend
vercel
```

**Option 2: Self-Hosted**
```bash
cd frontend
npm run build
npm start
```

**Option 3: Docker**
```dockerfile
# Dockerfile (in frontend/)
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

---

## 🔒 Security Considerations

### For Production

1. **Add Authentication:**
   - Implement JWT tokens
   - Add login/logout pages
   - Protect API endpoints

2. **Environment Variables:**
   - Never commit `.env.local`
   - Use environment-specific configs
   - Secure API keys

3. **CORS Configuration:**
   - Restrict allowed origins
   - Update in `api/server.py`

4. **Input Validation:**
   - Sanitize user inputs
   - Validate file paths
   - Limit file sizes

---

## 📊 Performance Tips

### Frontend Optimization

1. **Use Server Components** (already done where possible)
2. **Implement Loading States** (already done)
3. **Add Error Boundaries**
4. **Optimize Images** (use Next.js Image component)
5. **Enable Caching** (ISR, SWR)

### Backend Optimization

1. **Add Response Caching**
2. **Implement Rate Limiting**
3. **Use Background Jobs** for heavy operations
4. **Add Database** for faster queries (optional)

---

## 🎓 Learning Resources

### Next.js
- Official Docs: https://nextjs.org/docs
- Learn Tutorial: https://nextjs.org/learn

### FastAPI
- Official Docs: https://fastapi.tiangolo.com/
- Tutorial: https://fastapi.tiangolo.com/tutorial/

### Tailwind CSS
- Official Docs: https://tailwindcss.com/docs
- Playground: https://play.tailwindcss.com/

---

## ✅ Checklist

**Backend Setup:**
- [ ] Python 3.8+ installed
- [ ] FastAPI installed (`pip install fastapi uvicorn`)
- [ ] Backend running on http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/docs

**Frontend Setup:**
- [ ] Node.js 18+ installed
- [ ] Dependencies installed (`npm install`)
- [ ] Environment configured (`.env.local`)
- [ ] Frontend running on http://localhost:3000

**Functionality:**
- [ ] Dashboard loads with statistics
- [ ] Tasks page shows existing tasks
- [ ] Create task form works
- [ ] CEO report displays
- [ ] Approve/reject buttons work
- [ ] No console errors

---

## 🎉 You're All Set!

Your Personal AI Employee now has a beautiful, functional web interface!

**Next Steps:**
1. Create some tasks through the UI
2. Test the approval workflow
3. Generate a CEO briefing
4. Customize the styling to your preferences

**Need Help?**
- Check the troubleshooting section
- Review the API docs at http://localhost:8000/docs
- Examine the browser console for errors

---

**Built with ❤️ for Hackathon 0**
*Silver Tier MVP - Full Stack Edition*

