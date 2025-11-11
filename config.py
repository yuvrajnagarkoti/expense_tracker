"""
Configuration file for Expense Tracker Application
Modify environment variables instead of editing this file in production.
"""

import os

# ==========================================
# Database Configuration
# ==========================================
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'root')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'expense_tracker_db')

# Connection Pool Settings (Optional)
POOL_NAME = os.getenv('POOL_NAME', 'expense_tracker_pool')
POOL_SIZE = int(os.getenv('POOL_SIZE', 5))

# ==========================================
# Application Settings
# ==========================================
DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-secret-key-in-production')

# ==========================================
# Session Configuration
# ==========================================
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')

# ==========================================
# File Upload Settings
# ==========================================
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')

# ==========================================
# Pagination
# ==========================================
ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', 20))

# ==========================================
# Date Formats
# ==========================================
DATE_FORMAT = '%Y-%m-%d'          # For storage
DISPLAY_DATE_FORMAT = '%d %b %Y'  # For UI display
