# Deployment Guide - Google Cloud Run

This guide covers deploying the Legal Assistant Chainlit app to Google Cloud Run with CI/CD.

## 🏗️ Infrastructure Setup (Already Completed)

The following has been set up for you:

- ✅ Google Cloud Project: `legalai-462213`
- ✅ Enabled APIs: Cloud Run, Cloud Build, Artifact Registry
- ✅ Artifact Registry repository: `legal-assistant`
- ✅ Service Account: `github-actions-sa` with necessary permissions
- ✅ Service Account Key: `github-actions-key.json` (⚠️ Keep secure!)

## 🔐 GitHub Secrets Setup

You need to add these secrets to your GitHub repository:

1. Go to your GitHub repository
2. Navigate to **Settings** > **Secrets and Variables** > **Actions**
3. Add the following secrets:

### Required Secrets:

| Secret Name | Description | How to Get |
|------------|-------------|------------|
| `GCP_SA_KEY` | Service account JSON key | Copy contents of `github-actions-key.json` |
| `GOOGLE_API_KEY` | Your Gemini API key | From Google AI Studio |
| `LITERAL_API_KEY` | Your Literal AI API key | From Literal AI dashboard |
| `CHAINLIT_AUTH_SECRET` | Generated secret | From your `.env` file |
| `OAUTH_GOOGLE_CLIENT_ID` | Google OAuth Client ID | From Google Cloud Console |
| `OAUTH_GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret | From Google Cloud Console |
| `CHAINLIT_URL` | Your app's public URL | Set after first deployment |

### Getting the Service Account Key:

```bash
cat github-actions-key.json
```

Copy the entire JSON content and paste it as the `GCP_SA_KEY` secret.

## 🚀 Manual Deployment (Testing)

To test deployment manually before setting up CI/CD:

```bash
./deploy.sh
```

This will:
1. 📦 Build the Docker image
2. 📤 Push to Artifact Registry  
3. 🚢 Deploy to Cloud Run
4. 🌐 Output the service URL

## 🔄 CI/CD Deployment

Once secrets are configured, the app will automatically deploy when you:

- Push to `main` or `master` branch
- The GitHub Action will:
  1. Build and push Docker image
  2. Deploy to Cloud Run with environment variables
  3. Output the service URL

## 🌐 OAuth Redirect URI Configuration

After your first deployment, you'll get a Cloud Run URL like:
```
https://legal-assistant-xxxxx-uc.a.run.app
```

**Important**: Update your Google OAuth configuration:

1. Go to [Google Cloud Console](https://console.cloud.google.com) > APIs & Services > Credentials
2. Edit your OAuth 2.0 Client ID
3. Add your Cloud Run URL to **Authorized redirect URIs**:
   ```
   https://your-cloud-run-url/auth/oauth/google/callback
   ```
4. Add the service URL as `CHAINLIT_URL` secret in GitHub

## 📊 Environment Variables in Cloud Run

The deployment sets these environment variables automatically:

- `GOOGLE_API_KEY` - Gemini API access
- `LITERAL_AI_API_KEY` - Conversation monitoring  
- `CHAINLIT_AUTH_SECRET` - Session security
- `OAUTH_GOOGLE_CLIENT_ID` - OAuth authentication
- `OAUTH_GOOGLE_CLIENT_SECRET` - OAuth authentication
- `CHAINLIT_URL` - App's public URL
- `PORT` - Cloud Run provides this automatically

## 🔧 Monitoring & Logs

- **Cloud Run Console**: Monitor service health, metrics, and logs
- **Literal AI Dashboard**: View conversation analytics
- **GitHub Actions**: Check deployment logs and status

## 🛠️ Troubleshooting

### Common Issues:

1. **OAuth Callback URL Mismatch**
   - Ensure redirect URI in Google Console matches your Cloud Run URL

2. **Environment Variables Missing**
   - Check GitHub secrets are properly set
   - Verify secret names match exactly

3. **Build Failures**
   - Check Dockerfile syntax
   - Ensure all dependencies in requirements.txt

4. **Permission Errors**
   - Verify service account has required roles
   - Check GCP_SA_KEY secret is valid JSON

### Useful Commands:

```bash
# View Cloud Run services
gcloud run services list --project=legalai-462213

# View service logs
gcloud logs tail --service=legal-assistant --project=legalai-462213

# Update environment variables
gcloud run services update legal-assistant \
  --set-env-vars="NEW_VAR=value" \
  --region=us-central1 \
  --project=legalai-462213
```

## 📈 Scaling Configuration

Current configuration:
- **Memory**: 2GB
- **CPU**: 1 vCPU  
- **Min Instances**: 0 (scales to zero)
- **Max Instances**: 10
- **Concurrency**: 80 requests per instance
- **Timeout**: 300 seconds

Adjust these in `deploy.sh` or `.github/workflows/deploy.yml` as needed. 