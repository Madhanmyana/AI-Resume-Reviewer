# AI Resume Reviewer Frontend

React + TypeScript + Vite implementation of the approved visual prototype.

## Run

```bash
npm install
npm run dev
```

## Backend connection

The current frontend works with mock data so you can test the UI immediately.

When your FastAPI API is ready, edit `src/api/resumeApi.ts` and replace the mocked return with your real `fetch()` call.

Expected env variable:

```env
VITE_API_BASE_URL=http://localhost:8000
```
