# 🚀 Expense Tracker - Complete Setup Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [Configuration](#configuration)
4. [First Run](#first-run)
5. [Troubleshooting](#troubleshooting)
6. [Production Deployment](#production-deployment)

---

## Prerequisites

Before starting, make sure you have:

### Required Software
- **Python 3.8 or higher**
  - Check: `python --version` or `python3 --version`
  - Download: https://www.python.org/downloads/

- **MySQL 5.7+ or MariaDB 10.3+**
  - Check: `mysql --version`
  - Download MySQL: https://dev.mysql.com/downloads/
  - Download MariaDB: https://mariadb.org/download/

- **pip (Python package manager)**
  - Usually comes with Python
  - Check: `pip --version`

### Optional (Recommended)
- **Git** for cloning the repository
- **Virtual environment** tool (venv or virtualenv)
- **MySQL Workbench** for database management

---

## Installation Steps

### Step 1: Get the Project Files

#### Option A: Download ZIP
1. Download the project as ZIP
2. Extract to your desired location
3. Open terminal/command prompt in the project folder

#### Option B: Clone with Git
```bash
git clone <repository-url>
cd expense_tracker
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask 3.1.2
- mysql-connector-python 9.5.0
- Werkzeug 3.1.3

### Step 4: Set Up MySQL Database

#### 4.1 Start MySQL
**Windows:** Start MySQL service from Services
**macOS:** `brew services start mysql`
**Linux:** `sudo systemctl start mysql`

#### 4.2 Login to MySQL
```bash
mysql -u root -p
```
Enter your MySQL root password.

#### 4.3 Create Database
```sql
CREATE DATABASE expense_tracker_db;
EXIT;
```

#### 4.4 Import Schema
```bash
mysql -u root -p expense_tracker_db < schema.sql
```
Enter your password when prompted.

**Verify tables were created:**
```bash
mysql -u root -p expense_tracker_db
```
```sql
SHOW TABLES;
```
You should see: `budgets`, `categories`, `transactions`, `users`

### Step 5: Configure Application

Edit `config.py` with your database credentials:

```python
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'              # Your MySQL username
MYSQL_PASSWORD = 'your_password' # Your MySQL password
MYSQL_DATABASE = 'expense_tracker_db'
```

**Important Security Note:**
Change the secret key in `app.py` line 9:
```python
app.secret_key = 'your-random-secret-key-here-change-me'
```

Generate a secure key:
```python
import secrets
print(secrets.token_hex(32))
```

---

## First Run

### Start the Application

```bash
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

### Access the Application

Open your web browser and go to:
```
http://localhost:5000
```

### Create Your First Account

1. You'll be redirected to the login page
2. Click **"Register here"**
3. Fill in the registration form:
   - Username: Choose a unique username
   - Email: Your email address
   - Password: At least 6 characters
   - Confirm Password: Must match
4. Click **"Register"**
5. You'll be redirected to login
6. Enter your credentials and click **"Login"**

### Add Your First Expense

1. Click **"Add Expense"** button on the dashboard
2. Select a category (default categories are auto-created)
3. Enter amount (e.g., 50.00)
4. Select date (defaults to today)
5. Add an optional note
6. Click **"Add Expense"**

🎉 **Congratulations!** You're now tracking expenses!

---

## Configuration

### Database Settings

**config.py** contains all database settings:

```python
MYSQL_HOST = 'localhost'      # Database server
MYSQL_USER = 'root'           # Username
MYSQL_PASSWORD = 'password'   # Password
MYSQL_DATABASE = 'expense_tracker_db'  # Database name
```

### Application Settings

In `app.py`, you can modify:

```python
# Secret key for sessions (CHANGE THIS!)
app.secret_key = 'your-secret-key'

# Debug mode (set to False in production)
if __name__ == '__main__':
    app.run(debug=True)
```

### Theme Preference

The app automatically saves your theme preference (light/dark) in browser localStorage. No configuration needed!

---

## Troubleshooting

### Common Issues & Solutions

#### Issue 1: "ModuleNotFoundError: No module named 'flask'"
**Solution:**
```bash
# Make sure virtual environment is activated
# Then reinstall dependencies
pip install -r requirements.txt
```

#### Issue 2: "Access denied for user 'root'@'localhost'"
**Solution:**
- Check MySQL username and password in `config.py`
- Verify MySQL is running: `mysql -u root -p`
- Reset MySQL password if needed

#### Issue 3: "Unknown database 'expense_tracker_db'"
**Solution:**
```bash
# Create the database
mysql -u root -p
CREATE DATABASE expense_tracker_db;
EXIT;

# Import schema
mysql -u root -p expense_tracker_db < schema.sql
```

#### Issue 4: Port 5000 already in use
**Solution:**
Change port in `app.py`:
```python
app.run(debug=True, port=5001)  # Use different port
```

#### Issue 5: Charts not displaying
**Solution:**
- Check internet connection (Chart.js loads from CDN)
- Check browser console for errors (F12)
- Ensure JavaScript is enabled

#### Issue 6: "Table doesn't exist" errors
**Solution:**
Re-import the schema:
```bash
mysql -u root -p expense_tracker_db < schema.sql
```

#### Issue 7: Registration fails silently
**Solution:**
- Check if username/email already exists
- Verify password meets requirements (6+ chars)
- Check MySQL connection

### Getting Help

If you encounter issues:
1. Check the error message in terminal
2. Look for error details in browser console (F12)
3. Verify all prerequisites are installed
4. Check database connection
5. Review the troubleshooting section above

---

## Production Deployment

### Preparation

1. **Change Secret Key**
```python
app.secret_key = 'super-secret-production-key-here'
```

2. **Disable Debug Mode**
```python
if __name__ == '__main__':
    app.run(debug=False)
```

3. **Update Database Credentials**
Use environment variables:
```python
import os
MYSQL_HOST = os.getenv('DB_HOST', 'localhost')
MYSQL_USER = os.getenv('DB_USER', 'root')
MYSQL_PASSWORD = os.getenv('DB_PASSWORD', '')
```

### Deploy with Gunicorn

1. **Install Gunicorn**
```bash
pip install gunicorn
```

2. **Run Application**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Deploy with Nginx (Reverse Proxy)

1. **Install Nginx**
```bash
# Ubuntu/Debian
sudo apt install nginx

# macOS
brew install nginx
```

2. **Configure Nginx**
Create `/etc/nginx/sites-available/expense-tracker`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /path/to/expense_tracker/static;
    }
}
```

3. **Enable Site**
```bash
sudo ln -s /etc/nginx/sites-available/expense-tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Enable HTTPS with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Run as System Service

Create `/etc/systemd/system/expense-tracker.service`:
```ini
[Unit]
Description=Expense Tracker Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/expense_tracker
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable expense-tracker
sudo systemctl start expense-tracker
```

---

## Testing Checklist

After setup, verify these features work:

- [ ] Registration page loads
- [ ] Can create new account
- [ ] Login works
- [ ] Dashboard displays statistics
- [ ] Charts render correctly
- [ ] Can add expense
- [ ] Can view expenses
- [ ] Filters work
- [ ] Can edit expense
- [ ] Can delete expense
- [ ] Categories page loads
- [ ] Can add category
- [ ] Budgets page works
- [ ] Can set budget
- [ ] Reports page displays
- [ ] CSV export works
- [ ] Dark mode toggle works
- [ ] Logout works

---

## Quick Command Reference

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create database
mysql -u root -p
CREATE DATABASE expense_tracker_db;

# Import schema
mysql -u root -p expense_tracker_db < schema.sql

# Run application
python app.py

# Deactivate virtual environment
deactivate
```

---

## Next Steps

After successful setup:

1. **Explore Features:** Try all pages and features
2. **Add Data:** Create categories, add expenses, set budgets
3. **Customize:** Modify colors, add features, personalize
4. **Backup:** Export your data regularly
5. **Share:** Deploy and share with others!

---

## Support

Need help? Check:
- README.md for feature documentation
- FEATURES.md for complete feature list
- Error messages in terminal
- Browser console (F12) for JavaScript errors

---

**Happy Expense Tracking! 💰✨**

*Last Updated: 2025*