import os

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

ngo_auth_block = '''
def ngo_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'ngo_id' not in session:
            flash("Please log in as NGO to access this page.", "error")
            return redirect(url_for('ngo_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/ngo/signup', methods=['GET', 'POST'])
def ngo_signup():
    if request.method == 'POST':
        name = request.form['name'].strip()
        contact = request.form['contact'].strip()
        phone = request.form['phone'].strip()
        email = request.form['email'].strip()
        address = request.form['address'].strip()
        pwd = request.form['password']
        
        # Simple geocoding stub
        lat, lon = 20.0, 78.0
        
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM ngos")
            count = cur.fetchone()[0] + 1
            ngo_id = f"N{count:03d}"
            
            try:
                cur.execute("INSERT INTO ngos (id, name, contact_person, phone, email, location, password_hash, lat, lon) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (ngo_id, name, contact, phone, email, address, generate_password_hash(pwd), lat, lon))
                conn.commit()
                flash("NGO Registration successful! Please log in.", "success")
                return redirect(url_for('ngo_login'))
            except sqlite3.IntegrityError:
                flash("Email already registered.", "error")
                
    return render_template('ngo_signup.html')

@app.route('/ngo/login', methods=['GET', 'POST'])
def ngo_login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        pwd = request.form['password']
        
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM ngos WHERE email = ?", (email,))
            ngo = cur.fetchone()
            
            if ngo and check_password_hash(ngo['password_hash'], pwd):
                session.clear()
                session['ngo_id'] = ngo['id']
                session['ngo_name'] = ngo['name']
                session['user_type'] = 'ngo'
                flash(f"Welcome back, {ngo['name']}!", "success")
                return redirect(url_for('ngo_dashboard'))
            else:
                flash("Invalid credentials.", "error")
                
    return render_template('ngo_login.html')

@app.route('/ngo/dashboard')
@ngo_login_required
def ngo_dashboard():
    ngo_id = session['ngo_id']
    with get_db() as conn:
        cur = conn.cursor()
        # Active alerts assigned to this NGO or broadcasted
        cur.execute("""
            SELECT a.id, a.hotel_id, h.hotel_name, h.lat, h.lon, h.phone, a.predicted_waste, a.reserved_kg, a.status 
            FROM alerts a 
            JOIN hotels h ON a.hotel_id = h.id 
            WHERE (a.ngo_id = ? OR a.ngo_id IS NULL) AND a.status = 'Pending'
        """, (ngo_id,))
        active_alerts = cur.fetchall()
        
    return render_template('ngo_dashboard.html', ngo_name=session.get('ngo_name'), active_alerts=active_alerts)
'''

# Check if already added
if 'def ngo_login_required' not in content:
    # Insert before if __name__ == '__main__':
    parts = content.split("if __name__ == '__main__':")
    if len(parts) == 2:
        new_content = parts[0] + ngo_auth_block + "\nif __name__ == '__main__':" + parts[1]
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully injected NGO Auth")
