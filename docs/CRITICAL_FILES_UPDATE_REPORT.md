# 🔴 CRITICAL FILES UPDATE REPORT
## Files That MUST Be Checked/Modified Before Updating

**Current Running Code:** Commit `1618c50`  
**Latest Remote Code:** Commit `fabb8c4`

---

## 🚨 CRITICAL ISSUE #1: WSGI Configuration

### **File: `smartcampus/wsgi.py`**

**CURRENT (Running):**
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcampus.settings_production')
```

**LATEST (Remote - UPDATED):**
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcampus.settings_production')
```

**✅ FIXED:** The latest version has been updated to use **production settings** by default!

**Impact if updated without fixing:**
- ❌ App will use development database credentials (root user)
- ❌ DEBUG mode might be enabled
- ❌ Security settings will be disabled
- ❌ Database connection will fail (we already fixed this issue)
- ❌ Production environment variables won't be loaded

**ACTION REQUIRED:**
✅ **No action needed** - The file has been updated to use production settings by default.

However, **verify** line 17 in `smartcampus/wsgi.py` shows:
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcampus.settings_production')
```

**OR** ensure your systemd service file has (this will override wsgi.py):
```ini
Environment="DJANGO_SETTINGS_MODULE=smartcampus.settings_production"
```

---

## ✅ SAFE FILES (No Changes)

These critical files have **NO DIFFERENCES** between current and latest:

1. **`smartcampus/settings_production.py`** - ✅ No changes
2. **`smartcampus/settings.py`** - ✅ No changes  
3. **`requirements.txt`** - ✅ No changes
4. **`gunicorn_config.py`** - ✅ No changes
5. **`smartcampus.service`** - ✅ No changes (but check your actual systemd file at `/etc/systemd/system/smartcampus.service`)

---

## 📋 FILES TO VERIFY AFTER UPDATE

### 1. **Systemd Service File**
**Location:** `/etc/systemd/system/smartcampus.service`

**Check:**
- ✅ `Environment="DJANGO_SETTINGS_MODULE=smartcampus.settings_production"` is set
- ✅ `EnvironmentFile=/home/django/apps/SmartCampus_p/.env` is set
- ✅ Working directory is correct
- ✅ User/Group permissions are correct

**Current service file shows:**
```ini
Environment="DJANGO_SETTINGS_MODULE=smartcampus.settings_production"
```
This is correct and will override wsgi.py, but it's safer to fix wsgi.py too.

---

### 2. **Environment File (.env)**
**Location:** `/home/django/apps/SmartCampus_p/.env`

**Verify these are set correctly:**
- ✅ `SECRET_KEY` - Must be set
- ✅ `DEBUG=False` - Must be False in production
- ✅ `ALLOWED_HOSTS` - Must include your domains
- ✅ `DB_NAME` - Database name
- ✅ `DB_USER` - Database user (SmartCampusApp)
- ✅ `DB_PASSWORD` - Database password
- ✅ `DB_HOST` - Database host
- ✅ `DB_PORT` - Database port
- ✅ `STATIC_ROOT` - Static files path
- ✅ `MEDIA_ROOT` - Media files path

**Note:** `.env` file is not in git, so it won't be overwritten, but verify it exists and is correct.

---

### 3. **Gunicorn Configuration**
**Location:** `/etc/gunicorn/smartcampus.py` (or project `gunicorn_config.py`)

**Check:**
- ✅ Socket path: `unix:/var/run/gunicorn/smartcampus.sock`
- ✅ Log paths are correct
- ✅ Worker count is appropriate
- ✅ User/Group settings (if set)

**Status:** ✅ No changes in latest version

---

### 4. **Nginx Configuration**
**Location:** `/etc/nginx/sites-available/smartcampus` (or project `nginx.conf`)

**Check:**
- ✅ `server_name` includes your domains
- ✅ `proxy_pass` points to correct socket
- ✅ Static files location matches `STATIC_ROOT`
- ✅ Media files location matches `MEDIA_ROOT`
- ✅ SSL certificates (if using HTTPS)

**Note:** Nginx config is not in git repository, verify manually.

---

## 🔍 DATABASE MIGRATIONS

### **Status:** ✅ No new migrations detected

**Check after update:**
```bash
cd /home/django/apps/SmartCampus_p
source /home/django/apps/venv/bin/activate
python manage.py showmigrations --plan | grep "\[ \]"
```

If any unapplied migrations are found, run:
```bash
python manage.py migrate
```

---

## 📦 DEPENDENCIES

### **requirements.txt** - ✅ No changes

**Current dependencies:**
- Django>=5.1.1
- mysqlclient>=2.2.0
- Pillow>=10.0.0
- cryptography>=41.0.0
- requests>=2.31.0
- gunicorn>=21.2.0
- django-redis>=5.4.0
- python-decouple>=3.8
- whitenoise>=6.6.0

**After update, verify:**
```bash
source /home/django/apps/venv/bin/activate
pip install -r requirements.txt
```

---

## 🔄 UPDATE CHECKLIST

Before updating, ensure:

- [ ] Backup database
- [ ] Backup current code
- [ ] Backup `.env` file
- [ ] Note current commit: `1618c50`

After updating:

- [ ] **VERIFY:** Check `smartcampus/wsgi.py` line 17 uses `settings_production` (should already be correct)
- [ ] Verify `.env` file still exists and is correct
- [ ] Check systemd service file configuration
- [ ] Run database migrations (if any)
- [ ] Install/update Python dependencies
- [ ] Collect static files: `python manage.py collectstatic --noinput`
- [ ] Restart service: `sudo systemctl restart smartcampus`
- [ ] Check service status: `sudo systemctl status smartcampus`
- [ ] Check logs: `sudo journalctl -u smartcampus -n 50`
- [ ] Test application functionality
- [ ] Verify database connection works
- [ ] Test new features (lecturer cards, fee item deletion, etc.)

---

## 🎯 QUICK FIX SCRIPT

**Note:** The `wsgi.py` file has been updated in the codebase to use `settings_production` by default. However, if you're updating from an older version, verify line 17 shows:

```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcampus.settings_production')
```

If it shows `smartcampus.settings` instead, run this to fix it:

```bash
cd /home/django/apps/SmartCampus_p
sed -i "s/smartcampus.settings'/smartcampus.settings_production'/g" smartcampus/wsgi.py
# Or manually edit the file
```

Then restart:
```bash
sudo systemctl restart smartcampus.service
```

---

## 📊 SUMMARY

### Files That Need Manual Fix:
1. **`smartcampus/wsgi.py`** - ✅ **VERIFY** (should already be set to `settings_production`, but verify after update)

### Files That Are Safe:
- ✅ `smartcampus/settings_production.py` - No changes
- ✅ `smartcampus/settings.py` - No changes
- ✅ `requirements.txt` - No changes
- ✅ `gunicorn_config.py` - No changes

### Files to Verify (Not in Git):
- ⚠️ `/etc/systemd/system/smartcampus.service` - Verify manually
- ⚠️ `/etc/nginx/sites-available/smartcampus` - Verify manually
- ⚠️ `.env` file - Verify it exists and is correct

---

## 🚨 MOST CRITICAL ACTION

**After updating, the #1 priority is to VERIFY `smartcampus/wsgi.py` line 17 uses `settings_production`.**

The file has been updated in the codebase, but always verify after pulling the latest code to ensure it wasn't accidentally changed.

---

**Generated:** $(date)  
**Current Commit:** 1618c50  
**Target Commit:** fabb8c4

