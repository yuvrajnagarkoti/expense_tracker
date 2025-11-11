# 💰 Expense Tracker - Modern Flask Application

A beautiful, feature-rich expense tracking application built with Flask, MySQL, Bootstrap 5, and Chart.js. Track your expenses, set budgets, analyze spending patterns, and manage your finances with ease.

![Dashboard Preview](https://img.shields.io/badge/Version-2.0-blue) ![Flask](https://img.shields.io/badge/Flask-3.1.2-green) ![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.2-purple)

## ✨ Features

### 🔐 Authentication & Security
- **User Registration & Login** - Secure authentication system with password hashing
- **Session Management** - Protected routes with login requirements
- **Multi-user Support** - Each user has their own isolated data

### 💳 Expense Management
- **Add Expenses** - Quick expense entry with categories, amounts, dates, and notes
- **Edit Expenses** - Modify existing transactions
- **Delete Expenses** - Remove unwanted transactions with confirmation
- **Advanced Filtering** - Filter by category, date range, and search terms
- **CSV Export** - Download your expense data in CSV format

### 📊 Analytics & Reports
- **Interactive Dashboard** - Overview with key metrics and charts
- **Category Breakdown** - Pie charts showing spending by category
- **Monthly Trends** - Line charts displaying spending over time
- **Top Expenses** - View your highest expenditures
- **Detailed Reports** - Monthly and category-wise analysis

### 🎯 Budget Management
- **Set Budgets** - Create spending limits for categories
- **Budget Periods** - Weekly, monthly, or yearly budgets
- **Progress Tracking** - Visual progress bars with color-coded alerts
- **Budget Alerts** - Warnings when approaching or exceeding limits

### 🎨 Modern UI/UX
- **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- **Dark Mode** - Toggle between light and dark themes
- **Bootstrap 5** - Beautiful, modern interface with smooth animations
- **Chart.js Integration** - Interactive, animated charts
- **Icon Library** - Bootstrap Icons for visual clarity

### 📱 Additional Features
- **Category Management** - Create and organize custom categories
- **Search Functionality** - Quick search through expenses
- **Flash Messages** - User-friendly notifications
- **Form Validation** - Client and server-side validation
- **Auto-dismiss Alerts** - Clean, unobtrusive notifications

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL 5.7+ or MariaDB 10.3+
- pip (Python package manager)

### Installation

1. **Clone or Download the Project**
```bash
git clone <repository-url>
cd expense_tracker
```

2. **Create Virtual Environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Database**

Create a MySQL database:
```sql
CREATE DATABASE expense_tracker_db;
```

Update `config.py` with your database credentials:
```python
MYSQL_HOST = 'localhost'
MYSQL_USER = 'your_username'
MYSQL_PASSWORD = 'your_password'
MYSQL_DATABASE = 'expense_tracker_db'
```

5. **Initialize Database Schema**
```bash
mysql -u your_username -p expense_tracker_db < schema.sql
```

6. **Run the Application**
```bash
python app.py
```

7. **Access the Application**

Open your browser and navigate to: `http://localhost:5000`

## 📁 Project Structure

```
expense_tracker/
│
├── app.py                      # Main application file
├── config.py                   # Database configuration
├── schema.sql                  # Database schema
├── requirements.txt            # Python dependencies
├── README.md                   # Documentation
│
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navigation
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   ├── dashboard.html         # Main dashboard
│   ├── expenses.html          # Expense list with filters
│   ├── add_expense.html       # Add expense form
│   ├── edit_expense.html      # Edit expense form
│   ├── categories.html        # Category management
│   ├── budgets.html           # Budget management
│   └── reports.html           # Reports and analytics
│
└── static/                     # Static files (optional)
    └── style.css              # Additional custom styles
```

## 🗄️ Database Schema

### Tables

**users**
- `user_id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `password` (Hashed)
- `created_at`

**categories**
- `category_id` (Primary Key)
- `user_id` (Foreign Key)
- `name`
- `created_at`

**transactions**
- `txn_id` (Primary Key)
- `user_id` (Foreign Key)
- `category_id` (Foreign Key)
- `amount`
- `date`
- `note`
- `created_at`

**budgets**
- `budget_id` (Primary Key)
- `user_id` (Foreign Key)
- `category_id` (Foreign Key)
- `amount`
- `period` (weekly/monthly/yearly)
- `created_at`

## 🎯 Usage Guide

### Getting Started

1. **Register an Account**
   - Click "Register" on the login page
   - Fill in username, email, and password
   - Default categories are automatically created

2. **Add Your First Expense**
   - Click "Add Expense" from the dashboard
   - Select category, enter amount, date, and optional note
   - Submit to save

3. **View and Filter Expenses**
   - Navigate to "Expenses" to see all transactions
   - Use filters to narrow down results
   - Edit or delete expenses as needed

4. **Set Budgets**
   - Go to "Budgets" page
   - Select category and set spending limit
   - Choose period (weekly/monthly/yearly)
   - Track progress with visual indicators

5. **Analyze Spending**
   - Visit "Reports" for detailed analytics
   - View charts and spending patterns
   - Identify top expenses
   - Export data as CSV

### Tips for Best Results

- **Use descriptive notes** to remember what each expense was for
- **Create specific categories** for better organization
- **Set realistic budgets** based on your spending history
- **Review reports monthly** to identify spending trends
- **Export data regularly** for backup purposes

## 🎨 Customization

### Changing Colors

Edit the CSS variables in `templates/base.html`:
```css
:root {
    --primary-color: #6366f1;
    --secondary-color: #8b5cf6;
    --success-color: #10b981;
    --danger-color: #ef4444;
    --warning-color: #f59e0b;
}
```

### Adding New Categories

Categories can be added through the UI or directly in the database:
```sql
INSERT INTO categories (user_id, name) VALUES (1, 'New Category');
```

### Modifying Chart Colors

Update the color arrays in the chart JavaScript code in each template.

## 🔧 Configuration Options

### Secret Key (Important for Production!)
Change the secret key in `app.py`:
```python
app.secret_key = 'your-very-secret-random-string-here'
```

### Database Connection Pool
For better performance, consider using connection pooling:
```python
from mysql.connector import pooling

db_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **config
)
```

### Debug Mode
Disable debug mode in production:
```python
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

## 🚀 Deployment

### Deploy to Production

1. **Set Environment Variables**
```bash
export FLASK_ENV=production
export SECRET_KEY='your-secret-key'
```

2. **Use a Production Server (Gunicorn)**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

3. **Set Up Nginx (Reverse Proxy)**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. **Enable HTTPS with Let's Encrypt**
```bash
sudo certbot --nginx -d yourdomain.com
```

## 🐛 Troubleshooting

### Database Connection Errors
- Verify MySQL is running
- Check credentials in `config.py`
- Ensure database exists

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Activate virtual environment

### Chart Not Displaying
- Check browser console for JavaScript errors
- Ensure Chart.js CDN is accessible
- Verify data is being passed to templates

## 📈 Future Enhancements

Potential features to add:
- [ ] Recurring expenses
- [ ] Income tracking
- [ ] Multiple currency support
- [ ] Mobile app (React Native)
- [ ] Receipt photo uploads
- [ ] Sharing expenses with family
- [ ] Advanced analytics with ML
- [ ] Bank account integration
- [ ] Bill reminders
- [ ] Tax report generation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Built with ❤️ using Flask, MySQL, Bootstrap, and Chart.js

## 📞 Support

For issues, questions, or suggestions, please open an issue on the repository.

---

**Happy Expense Tracking! 💰📊**