import os

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_decorator = '''def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_type' not in session or 'user_id' not in session:
                flash("Please log in to access this page.", "error")
                return redirect(url_for('login'))
            if session.get('user_type') not in roles:
                flash("You do not have permission to view this page.", "error")
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator'''

new_decorator = '''def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'hotel_id' not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function'''

content = content.replace(old_decorator, new_decorator)
content = content.replace("@role_required('hotel')", "@login_required")
content = content.replace("hotel_id = session.get('user_id')", "hotel_id = session.get('hotel_id')")
content = content.replace("hotel_id = session['user_id']", "hotel_id = session['hotel_id']")

# Also revert the login function back to its original state
import re
login_pattern = re.compile(r"@app\.route\('/login', methods=\['GET', 'POST'\]\)\ndef login\(\):.*?(?=@app\.route\('/logout'\))", re.DOTALL)
original_login = '''@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_id = request.form['login_id'].strip()
        password = request.form['password']

        with get_db() as conn:
            cur = conn.cursor()
            # Can login with email or Hotel ID
            cur.execute("SELECT * FROM hotels WHERE email = ? OR id = ?", (login_id, login_id))
            user = cur.fetchone()

            if user is None:
                flash("Account not found", "error")
            elif not check_password_hash(user['password_hash'], password):
                flash("Wrong Password", "error")
            else:
                session['hotel_id'] = user['id']
                session['hotel_name'] = user['hotel_name']
                return redirect(url_for('dashboard'))

    return render_template('login.html')

'''
content = login_pattern.sub(original_login, content)

# Revert signup function's status field since they don't want approvals
signup_pattern = re.compile(r"INSERT INTO hotels \(id, hotel_name, owner_name, email, phone, hotel_type, address, password_hash, status\)\s*VALUES \(\?, \?, \?, \?, \?, \?, \?, \?, 'Pending'\)")
content = signup_pattern.sub("INSERT INTO hotels (id, hotel_name, owner_name, email, phone, hotel_type, address, password_hash)\n                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)", content)
content = content.replace('Your account is Pending Admin Approval.', 'You can now log in.')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
