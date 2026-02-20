# JobDone Deployment Guide - Iteration 5

This guide covers deploying JobDone to **Render** (recommended) or **Railway**.

## Prerequisites

- Git repository (GitHub, GitLab, or Bitbucket)
- Supabase project with PostgreSQL database
- Email account for SMTP (Gmail, SendGrid, etc.)

---

## Option 1: Deploy to Render (Recommended)

### Step 1: Prepare Your Repository

1. Ensure all changes are committed and pushed to your Git repository
2. Verify `requirements.txt`, `Procfile`, and `runtime.txt` are in the root directory

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub/GitLab/Bitbucket
3. Connect your repository

### Step 3: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your repository
3. Configure:
   - **Name**: `jobdone` (or your preferred name)
   - **Region**: Choose closest to Ireland (e.g., Frankfurt)
   - **Branch**: `main` (or your main branch)
   - **Root Directory**: Leave empty (root)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn core.wsgi:application`

### Step 4: Set Environment Variables

In Render dashboard → **Environment** tab, add:

```
SECRET_KEY=your-secret-key-here-generate-a-new-one
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_URL=your-supabase-connection-string
CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com
CORS_ALLOW_ALL_ORIGINS=False

# Email (SMTP) - Optional but recommended
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@jobdone.com
```

**Important:**
- Generate a new `SECRET_KEY`: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- Get `DATABASE_URL` from Supabase: Project Settings → Database → Connection string (use "Connection pooling")
- For Gmail SMTP, use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will build and deploy automatically
3. Wait for deployment to complete (usually 5-10 minutes)
4. Your app will be live at `https://your-app-name.onrender.com`

### Step 6: Run Migrations

After first deployment, run migrations:

1. In Render dashboard → **Shell** tab
2. Run: `python manage.py migrate`
3. Create superuser: `python manage.py createsuperuser`

---

## Option 2: Deploy to Railway

### Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub

### Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository

### Step 3: Configure

Railway auto-detects Django. Add environment variables:

```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=*.railway.app
DATABASE_URL=your-supabase-connection-string
CSRF_TRUSTED_ORIGINS=https://your-app-name.railway.app
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Step 4: Deploy

Railway will auto-deploy. After deployment:
1. Run migrations: `railway run python manage.py migrate`
2. Create superuser: `railway run python manage.py createsuperuser`

---

## Post-Deployment Checklist

- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Test login/registration
- [ ] Test job posting and requests
- [ ] Test photo uploads (verify media files are accessible)
- [ ] Test email notifications (if SMTP configured)
- [ ] Verify HTTPS is working (should be automatic on Render/Railway)
- [ ] Update Supabase RLS policies if needed (for API security)

---

## Media Files (User Uploads)

**Current setup:** Media files are stored on the server filesystem (`MEDIA_ROOT`). This works but has limitations:
- Files are lost if the server restarts (on free tiers)
- Not scalable for production

**Recommended for production:** Use **Supabase Storage** or **AWS S3** for media files. This requires:
1. Setting up Supabase Storage bucket or S3 bucket
2. Installing `django-storages` package
3. Updating `settings.py` to use cloud storage backend

**For Iteration 5:** The current filesystem approach is acceptable for demonstration, but document this as a limitation/improvement for future iterations.

---

## Troubleshooting

### Static files not loading
- Ensure `collectstatic` runs during build
- Check `STATIC_ROOT` and `STATIC_URL` in settings
- Verify WhiteNoise middleware is enabled

### Database connection errors
- Verify `DATABASE_URL` is correct (use Supabase connection pooling URL)
- Check Supabase project is not paused
- Ensure IP allowlist in Supabase allows Render/Railway IPs (or disable IP restrictions for testing)

### CSRF errors
- Add your production domain to `CSRF_TRUSTED_ORIGINS`
- Ensure `ALLOWED_HOSTS` includes your domain

### Email not sending
- Verify SMTP credentials are correct
- For Gmail, use App Password (not regular password)
- Check `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are set

---

## Security Notes

- Never commit `.env` files or `SECRET_KEY` to Git
- Use environment variables for all sensitive data
- Keep `DEBUG=False` in production
- Regularly update dependencies (`pip list --outdated`)

---

## References

- [Render Django Deployment](https://render.com/docs/deploy-django)
- [Railway Django Deployment](https://docs.railway.app/guides/django)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Supabase Storage](https://supabase.com/docs/guides/storage)
