# Quick Start: Production Deployment

## ✅ What's Done

All production configuration files have been created:
- ✅ `smartcampus/settings_production.py` - Production settings
- ✅ `nginx.conf` - Web server configuration
- ✅ `gunicorn_config.py` - Application server configuration
- ✅ `smartcampus.service` - Systemd service file
- ✅ `env.example` - Environment variables template
- ✅ `DEPLOYMENT.md` - Full deployment guide

## ⚠️ Important: Can't Run Production Setup on Windows

**You're currently on Windows**, but production deployment requires:
- **Linux server** (Ubuntu, Debian, CentOS, etc.)
- **Nginx** (Linux web server - not available on Windows)
- **Gunicorn** (Linux WSGI server)
- **Systemd** (Linux service manager)

### What You Can Do Now (Windows):
1. ✅ **Test locally** with development settings: `python manage.py runserver`
2. ✅ **Prepare files** - All configuration files are ready
3. ✅ **Review and customize** the configuration files
4. ✅ **Set up environment variables** using `env.example`

### What Needs Linux Server:
1. ❌ **Nginx** - Only runs on Linux/Unix
2. ❌ **Gunicorn** - Designed for Linux production
3. ❌ **Systemd service** - Linux service manager

## 📋 How to Use These Files in Production

### Step 1: Transfer Files to Linux Server
Upload your entire project to a Linux server (via FTP, SCP, Git, etc.)

### Step 2: Customize Configuration Files

**A. Update `env.example` → `.env`:**
```bash
cp env.example .env
nano .env  # Edit with your actual values
```

**B. Update `nginx.conf`:**
- Replace `yourdomain.com` with your actual domain
- Update SSL certificate paths
- Update static/media file paths

**C. Update `gunicorn_config.py`:**
- Verify socket path: `/var/run/gunicorn/smartcampus.sock`
- Update log file paths
- Set user/group if needed

**D. Update `smartcampus.service`:**
- Update paths to match your server
- Verify virtual environment path

### Step 3: Follow DEPLOYMENT.md
The `DEPLOYMENT.md` file has complete step-by-step instructions.

## 🔧 Current Status

### ✅ Ready to Deploy:
- All configuration files created
- Production settings configured
- Security settings enabled
- Environment variable support added

### ⚠️ Needs Customization:
- Domain names in `nginx.conf`
- File paths in all config files
- Environment variables in `.env`
- SSL certificate installation

### ❌ Can't Test on Windows:
- Nginx configuration
- Gunicorn setup
- Systemd service
- Production deployment

## 🚀 Deployment Checklist

Before deploying to production:

- [ ] Linux server with root/sudo access
- [ ] Domain name configured
- [ ] SSL certificate obtained (Let's Encrypt)
- [ ] MySQL database created
- [ ] Redis installed and running
- [ ] All files uploaded to server
- [ ] `.env` file created with actual values
- [ ] `nginx.conf` customized for your domain
- [ ] `gunicorn_config.py` paths verified
- [ ] `smartcampus.service` paths verified
- [ ] Followed `DEPLOYMENT.md` instructions

## 📝 Testing Locally (Windows)

You can still test the application locally:

```bash
# Use development settings (current setup)
python manage.py runserver

# To test production settings (will fail without .env):
# Set environment variable:
set DJANGO_SETTINGS_MODULE=smartcampus.settings_production
python manage.py check --deploy
```

## 🔍 File Locations in Production

When deployed, files should be at:
```
/var/www/smartcampus/          # Application root
├── smartcampus/
│   └── settings_production.py  # Production settings
├── nginx.conf                  # Copy to /etc/nginx/sites-available/
├── gunicorn_config.py          # In project root
├── smartcampus.service         # Copy to /etc/systemd/system/
└── .env                        # Environment variables (NEVER commit)
```

## ❓ Common Questions

**Q: Can I test production setup on Windows?**
A: No, Nginx and Gunicorn require Linux. Use `runserver` for local testing.

**Q: Will these files work as-is?**
A: No, you need to customize domain names, paths, and environment variables.

**Q: How do I know if it's production-ready?**
A: Follow the checklist in `DEPLOYMENT.md` and test on a staging server first.

**Q: Can I deploy to cloud services?**
A: Yes! These files work with:
- AWS EC2
- DigitalOcean Droplets
- Linode
- Azure VMs
- Any Linux VPS

## 📞 Next Steps

1. **Review** all configuration files
2. **Customize** for your domain and server
3. **Set up** a Linux server (VPS, cloud, etc.)
4. **Follow** `DEPLOYMENT.md` step-by-step
5. **Test** in staging before production

---

**Summary:** Files are ready, but production deployment requires a Linux server. You can prepare everything now and deploy when you have server access.

