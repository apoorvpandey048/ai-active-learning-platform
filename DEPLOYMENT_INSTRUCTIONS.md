Deployment steps for free-tier hosting (Hugging Face Spaces for backend, Vercel for frontend)

Prerequisites
- Hugging Face account and a Space repository created (free tier). Note the repo id: <username>/<space-name>.
- Hugging Face token with repo:write permissions stored as GitHub secret HUGGING_FACE_TOKEN.
- (Optional) Vercel account and a project created; add VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID as GitHub secrets.

Backend (Hugging Face Space)
1. Ensure backend/main.py and backend/requirements.txt are present. main.py preloads models synchronously.
2. On your GitHub repo, create a branch named hf-space. Push this branch and the deploy workflow will build and push files to the Space repo specified in the HF_SPACE_REPO secret.
3. Create secrets in GitHub: HUGGING_FACE_TOKEN and HF_SPACE_REPO (format: username/space-name).
4. Push to the hf-space branch:
   git checkout -b hf-space
   git add backend main.py backend/requirements.txt .github/workflows/deploy_backend_hf.yml
   git commit -m "Prepare HF Space deployment"
   git push origin hf-space --force
5. The Actions job will push the contents to your Hugging Face Space and trigger a build there. The Space will run `python backend/main.py` per Procfile.

Frontend (Vercel)
1. In GitHub, add secrets VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID (from your Vercel project settings).
2. On main branch, Actions will build the frontend and call `vercel --prod` to deploy the static build.
3. Configure env var in Vercel for the frontend build: REACT_APP_BACKEND_URL=https://<your-space>.hf.space (the HF Space public URL). This value is used by frontend at build time.

Notes and caveats
- Hugging Face Spaces free tier provides CPU-only builds and limited RAM — large HF models may exceed these limits. Consider using small models (the defaults are moderately sized) or use remote inference APIs instead.
- Automatic model downloads may fail due to disk/memory limits on free tiers. If you run into quota errors on HF Spaces, consider switching to hosted inference APIs or upgrading to a paid plan.
- Vercel free tier supports static React builds; ensure environment variable REACT_APP_BACKEND_URL is set in Vercel.
