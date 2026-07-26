# Deploy the intelligence gateway to Catalyst AppSail

This service is the API used by the Slate dashboard. Deploy from the repository root so the service has access to `query/`, `track1_dataset.json`, and `lid.176.ftz`.

## AppSail settings

- Runtime: Python 3.11
- Build path: repository root
- Startup command: `sh -c 'python3 -m uvicorn query.api:app --host 0.0.0.0 --port ${X_ZOHO_CATALYST_LISTEN_PORT}'`
- Health check: `/health`

Install the packages in the root `requirements.txt` as part of the AppSail build bundle. Do not upload `.env`; enter the values from `.env.example` in AppSail's environment-variable settings instead.

After AppSail provides its public URL, add that URL as `NEXT_PUBLIC_API_BASE_URL` in Slate's environment-variable settings and redeploy the Slate frontend. Set `FRONTEND_ORIGINS` in AppSail to the Slate frontend URL to allow browser requests.
