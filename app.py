from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import datetime
from functools import wraps
import csv
import io
import config

app = Flask(__name__)
app.secret_key = '852ff3e9bb3dc38aacfc56eb8014833b66248138d724557a9349fbb5e2cd5394'

TEMPLATE = 'merged_expense_tracker.html'  # <- your single merged file in templates/

# ============ Database Connection ============
def get_db():
    return mysql.connector.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE
    )

# ============ Auth Decorator ============
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ============ Auth Routes ============
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('register'))

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT 1 FROM users WHERE username=%s OR email=%s", (username, email))
        if cursor.fetchone():
            flash('Username or email already exists.', 'danger')
            conn.close()
            return redirect(url_for('register'))

        hashed_pwd = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_pwd)
        )
        conn.commit()
        user_id = cursor.lastrowid

        default_categories = ['Food', 'Transport', 'Shopping', 'Bills', 'Entertainment', 'Health', 'Other']
        for cat in default_categories:
            cursor.execute("INSERT INTO categories (user_id, name) VALUES (%s, %s)", (user_id, cat))
        conn.commit()
        conn.close()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template(TEMPLATE, page='register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template(TEMPLATE, page='login')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ============ Dashboard & Home ============
@app.route('/')
@login_required
def dashboard():
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM transactions WHERE user_id=%s", (user_id,))
    total = cursor.fetchone()['total']

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) AS month_total
        FROM transactions
        WHERE user_id=%s
          AND MONTH(date) = MONTH(CURRENT_DATE())
          AND YEAR(date) = YEAR(CURRENT_DATE())
    """, (user_id,))
    month_total = cursor.fetchone()['month_total']

    cursor.execute("SELECT COUNT(*) AS count FROM transactions WHERE user_id=%s", (user_id,))
    txn_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) AS count FROM categories WHERE user_id=%s", (user_id,))
    cat_count = cursor.fetchone()['count']

    cursor.execute("""
        SELECT t.txn_id, c.name as category, t.amount, t.date, t.note
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.user_id = %s
        ORDER BY t.date DESC, t.txn_id DESC
        LIMIT 5
    """, (user_id,))
    recent = cursor.fetchall()

    cursor.execute("""
        SELECT c.name, SUM(t.amount) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.user_id = %s
        GROUP BY c.name
        ORDER BY total DESC
    """, (user_id,))
    category_data = cursor.fetchall()

    cursor.execute("""
        SELECT DATE_FORMAT(date, '%Y-%m') as month, SUM(amount) as total
        FROM transactions
        WHERE user_id = %s AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)
        GROUP BY month
        ORDER BY month
    """, (user_id,))
    monthly_data = cursor.fetchall()

    conn.close()

    return render_template(
        TEMPLATE,
        page='dashboard',
        total=float(total),
        month_total=float(month_total),
        txn_count=txn_count,
        cat_count=cat_count,
        recent=recent,
        category_data=category_data,
        monthly_data=monthly_data
    )

# ============ Expenses ============
@app.route('/expenses')
@login_required
def expenses():
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    category_filter = request.args.get('category', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    search = request.args.get('search', '')

    query = """
        SELECT t.txn_id, t.category_id, c.name as category, t.amount, t.date, t.note
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.user_id = %s
    """
    params = [user_id]

    if category_filter:
        query += " AND c.category_id = %s"
        params.append(category_filter)

    if date_from:
        query += " AND t.date >= %s"
        params.append(date_from)

    if date_to:
        query += " AND t.date <= %s"
        params.append(date_to)

    if search:
        query += " AND (t.note LIKE %s OR c.name LIKE %s)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term])

    query += " ORDER BY t.date DESC, t.txn_id DESC"

    cursor.execute(query, params)
    txns = cursor.fetchall()

    cursor.execute("SELECT * FROM categories WHERE user_id=%s ORDER BY name", (user_id,))
    categories = cursor.fetchall()

    total = sum(float(t['amount']) for t in txns)
    conn.close()

    return render_template(
        TEMPLATE,
        page='expenses',
        txns=txns,
        categories=categories,
        total=total,
        category_filter=category_filter,
        date_from=date_from,
        date_to=date_to,
        search=search
    )

@app.route('/add-expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        category_id = request.form['category_id']
        amount = request.form['amount']
        date_str = request.form['date']
        note = request.form.get('note', '').strip()

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")

            cursor.execute("""
                INSERT INTO transactions (user_id, category_id, amount, date, note)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, category_id, amount, date_str, note))
            conn.commit()
            conn.close()

            flash('Expense added successfully!', 'success')
            return redirect(url_for('expenses'))
        except Exception as e:
            conn.close()
            flash(f'Error adding expense: {str(e)}', 'danger')
            return redirect(url_for('add_expense'))

    cursor.execute("SELECT * FROM categories WHERE user_id=%s ORDER BY name", (user_id,))
    categories = cursor.fetchall()
    conn.close()

    today = datetime.now().strftime('%Y-%m-%d')
    return render_template(TEMPLATE, page='add_expense', categories=categories, today=today)

@app.route('/edit-expense/<int:txn_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(txn_id):
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM transactions WHERE txn_id=%s AND user_id=%s", (txn_id, user_id))
    txn = cursor.fetchone()

    if not txn:
        flash('Transaction not found.', 'danger')
        conn.close()
        return redirect(url_for('expenses'))

    if request.method == 'POST':
        category_id = request.form['category_id']
        amount = request.form['amount']
        date_str = request.form['date']
        note = request.form.get('note', '').strip()

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")

            cursor.execute("""
                UPDATE transactions
                SET category_id=%s, amount=%s, date=%s, note=%s
                WHERE txn_id=%s AND user_id=%s
            """, (category_id, amount, date_str, note, txn_id, user_id))
            conn.commit()
            conn.close()

            flash('Expense updated successfully!', 'success')
            return redirect(url_for('expenses'))
        except Exception as e:
            conn.close()
            flash(f'Error updating expense: {str(e)}', 'danger')
            return redirect(url_for('edit_expense', txn_id=txn_id))

    cursor.execute("SELECT * FROM categories WHERE user_id=%s ORDER BY name", (user_id,))
    categories = cursor.fetchall()
    conn.close()

    return render_template(TEMPLATE, page='edit_expense', txn=txn, categories=categories)

@app.route('/delete-expense/<int:txn_id>')
@login_required
def delete_expense(txn_id):
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE txn_id=%s AND user_id=%s", (txn_id, user_id))
    conn.commit()
    conn.close()

    flash('Expense deleted successfully!', 'danger')
    return redirect(url_for('expenses'))

# ============ Categories ============
@app.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            flash('Category name is required.', 'danger')
        else:
            cursor.execute("SELECT 1 FROM categories WHERE user_id=%s AND name=%s", (user_id, name))
            if cursor.fetchone():
                flash('Category already exists.', 'warning')
            else:
                cursor.execute("INSERT INTO categories (user_id, name) VALUES (%s, %s)", (user_id, name))
                conn.commit()
                flash('Category added successfully!', 'success')

    cursor.execute("""
        SELECT c.category_id, c.name, COUNT(t.txn_id) as txn_count, COALESCE(SUM(t.amount), 0) as total
        FROM categories c
        LEFT JOIN transactions t ON c.category_id = t.category_id AND t.user_id = %s
        WHERE c.user_id = %s
        GROUP BY c.category_id, c.name
        ORDER BY c.name
    """, (user_id, user_id))
    cats = cursor.fetchall()

    conn.close()
    return render_template(TEMPLATE, page='categories', categories=cats)

@app.route('/delete-category/<int:cat_id>')
@login_required
def delete_category(cat_id):
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM transactions WHERE category_id=%s AND user_id=%s", (cat_id, user_id))
    count = cursor.fetchone()[0]

    if count > 0:
        flash('Cannot delete category with existing transactions.', 'danger')
    else:
        cursor.execute("DELETE FROM categories WHERE category_id=%s AND user_id=%s", (cat_id, user_id))
        conn.commit()
        flash('Category deleted successfully!', 'success')

    conn.close()
    return redirect(url_for('categories'))

# ============ Reports ============
@app.route('/reports')
@login_required
def reports():
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT DATE_FORMAT(date, '%Y-%m') as month,
               DATE_FORMAT(date, '%M %Y') as month_name,
               COUNT(*) as count,
               SUM(amount) as total
        FROM transactions
        WHERE user_id = %s AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
        GROUP BY month, month_name
        ORDER BY month DESC
    """, (user_id,))
    monthly = cursor.fetchall()

    cursor.execute("""
        SELECT c.name, COUNT(t.txn_id) as count, SUM(t.amount) as total
        FROM categories c
        LEFT JOIN transactions t ON c.category_id = t.category_id AND t.user_id = %s
        WHERE c.user_id = %s
        GROUP BY c.name
        HAVING count > 0
        ORDER BY total DESC
    """, (user_id, user_id))
    cat_rows = cursor.fetchall()

    cursor.execute("""
        SELECT t.amount, t.date, c.name as category, t.note
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.user_id = %s
        ORDER BY t.amount DESC
        LIMIT 10
    """, (user_id,))
    top_expenses = cursor.fetchall()

    conn.close()
    return render_template(
        TEMPLATE,
        page='reports',
        monthly=monthly,
        categories=cat_rows,
        top_expenses=top_expenses
    )

# ============ Budgets ============
@app.route('/budgets', methods=['GET', 'POST'])
@login_required
def budgets():
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        category_id = request.form.get('category_id')
        amount = float(request.form['amount'])
        period = request.form['period']  # monthly, weekly, yearly

        cursor.execute("""
            SELECT 1 FROM budgets WHERE user_id=%s AND category_id=%s AND period=%s
        """, (user_id, category_id, period))

        if cursor.fetchone():
            cursor.execute("""
                UPDATE budgets SET amount=%s WHERE user_id=%s AND category_id=%s AND period=%s
            """, (amount, user_id, category_id, period))
            flash('Budget updated successfully!', 'success')
        else:
            cursor.execute("""
                INSERT INTO budgets (user_id, category_id, amount, period)
                VALUES (%s, %s, %s, %s)
            """, (user_id, category_id, amount, period))
            flash('Budget created successfully!', 'success')
        conn.commit()

    cursor.execute("""
        SELECT b.budget_id, b.amount as budget_amount, b.period,
               c.name as category,
               COALESCE(SUM(t.amount), 0) as spent
        FROM budgets b
        JOIN categories c ON b.category_id = c.category_id
        LEFT JOIN transactions t ON b.category_id = t.category_id
            AND t.user_id = %s
            AND (
                (b.period = 'monthly' AND MONTH(t.date) = MONTH(CURRENT_DATE()) AND YEAR(t.date) = YEAR(CURRENT_DATE()))
                OR (b.period = 'yearly'  AND YEAR(t.date)  = YEAR(CURRENT_DATE()))
                OR (b.period = 'weekly'  AND YEARWEEK(t.date) = YEARWEEK(CURRENT_DATE()))
            )
        WHERE b.user_id = %s
        GROUP BY b.budget_id, b.amount, b.period, c.name
    """, (user_id, user_id))
    budget_list = cursor.fetchall()

    for budget in budget_list:
        budget['spent'] = float(budget['spent'])
        budget['budget_amount'] = float(budget['budget_amount'])
        budget['percentage'] = (budget['spent'] / budget['budget_amount'] * 100) if budget['budget_amount'] > 0 else 0.0
        budget['status'] = 'danger' if budget['percentage'] >= 100 else ('warning' if budget['percentage'] >= 80 else 'success')

    cursor.execute("SELECT * FROM categories WHERE user_id=%s ORDER BY name", (user_id,))
    categories = cursor.fetchall()

    conn.close()
    return render_template(TEMPLATE, page='budgets', budgets=budget_list, categories=categories)

@app.route('/delete-budget/<int:budget_id>')
@login_required
def delete_budget(budget_id):
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM budgets WHERE budget_id=%s AND user_id=%s", (budget_id, user_id))
    conn.commit()
    conn.close()
    flash('Budget deleted successfully!', 'info')
    return redirect(url_for('budgets'))

# ============ CSV Export ============
@app.route('/export-csv')
@login_required
def export_csv():
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT t.date, c.name as category, t.amount, t.note
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.user_id = %s
        ORDER BY t.date DESC
    """, (user_id,))
    txns = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Category', 'Amount', 'Note'])
    for txn in txns:
        writer.writerow([txn['date'], txn['category'], txn['amount'], txn['note'] or ''])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'expenses_{datetime.now().strftime("%Y%m%d")}.csv'
    )

# ============ Chart API ============
@app.route('/api/chart-data')
@login_required
def chart_data():
    user_id = session['user_id']
    chart_type = request.args.get('type', 'category')

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if chart_type == 'category':
        cursor.execute("""
            SELECT c.name, SUM(t.amount) as total
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            WHERE t.user_id = %s
            GROUP BY c.name
            ORDER BY total DESC
        """, (user_id,))
        data = cursor.fetchall()
    else:  # 'monthly'
        cursor.execute("""
            SELECT DATE_FORMAT(date, '%Y-%m') as month, SUM(amount) as total
            FROM transactions
            WHERE user_id = %s AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
            GROUP BY month
            ORDER BY month
        """, (user_id,))
        data = cursor.fetchall()

    conn.close()
    return jsonify(data)

# ============ Run ============
if __name__ == '__main__':
    app.run(debug=True)
