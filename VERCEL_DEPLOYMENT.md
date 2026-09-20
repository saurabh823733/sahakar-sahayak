# Sahakar Sahayak — Vercel Deployment

This package is prepared for a single Vercel project containing the Next.js frontend and FastAPI backend.

## Structure
- `app/` — Next.js app
- `api/index.py` — Vercel FastAPI entrypoint
- `backend/` — Sahakar Sahayak FastAPI application
- `requirements.txt` — Python dependencies

## Local check
1. `npm install`
2. `npm run dev`

For the combined Vercel layout, the frontend uses same-origin `/api` requests.

## Deploy
1. Create a GitHub repository and push this folder.
2. In Vercel, choose **Add New → Project** and import the GitHub repository.
3. Keep the project root at the repository root and use the detected Next.js settings.
4. Deploy.

## Demo persistence note
On Vercel, SQLite is redirected to `/tmp` and uploads are written to `/tmp` when `VERCEL` is set. These are ephemeral demo storage, not durable production storage. For production persistence, replace SQLite with a hosted database and replace local uploads with durable object storage.

## Demo disclosure
The application retains its existing DEMO / GUIDANCE ONLY disclosures. Government submissions and official status checks are not connected.
