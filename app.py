import sqlite3
import mailer
import re
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "super_secret_meal_connect_key" # Replace in production

DATABASE = 'mealconnect.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS hotels (
                id TEXT PRIMARY KEY,
                hotel_name TEXT NOT NULL,
                owner_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL,
                hotel_type TEXT NOT NULL,
                address TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                threshold_kg REAL DEFAULT 20.0,
                status TEXT DEFAULT 'Approved',
                lat REAL,
                lon REAL,
                guest_count INTEGER DEFAULT 100,
                email_notifications BOOLEAN DEFAULT 1
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS food_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hotel_id TEXT NOT NULL,
                entry_date DATE NOT NULL,
                prepared_kg REAL NOT NULL,
                consumed_kg REAL NOT NULL,
                waste_kg REAL NOT NULL,
                notes TEXT,
                FOREIGN KEY(hotel_id) REFERENCES hotels(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hotel_id TEXT NOT NULL,
                for_date DATE NOT NULL,
                predicted_waste REAL NOT NULL,
                threshold REAL NOT NULL,
                exceeded_flag BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(hotel_id) REFERENCES hotels(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS ngos (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                contact_person TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                location TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                status TEXT DEFAULT 'Approved',
                lat REAL,
                lon REAL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hotel_id TEXT NOT NULL,
                ngo_id TEXT,
                prediction_id INTEGER,
                expected_date DATE NOT NULL,
                predicted_waste REAL NOT NULL,
                reserved_kg REAL NOT NULL,
                status TEXT DEFAULT 'Pending',
                accepted_by_ngo_id TEXT,
                pickup_slot_start TEXT,
                pickup_slot_end TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(hotel_id) REFERENCES hotels(id),
                FOREIGN KEY(ngo_id) REFERENCES ngos(id),
                FOREIGN KEY(prediction_id) REFERENCES predictions(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id INTEGER NOT NULL,
                hotel_id TEXT NOT NULL,
                ngo_id TEXT NOT NULL,
                collection_date DATE NOT NULL,
                predicted_waste REAL,
                actual_waste REAL,
                reserved_kg REAL,
                collected_kg REAL NOT NULL,
                status TEXT DEFAULT 'Completed',
                FOREIGN KEY(alert_id) REFERENCES alerts(id),
                FOREIGN KEY(hotel_id) REFERENCES hotels(id),
                FOREIGN KEY(ngo_id) REFERENCES ngos(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS food_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hotel_id TEXT NOT NULL,
                entry_date DATE NOT NULL,
                dish_name TEXT NOT NULL,
                category TEXT,
                dietary_type TEXT,
                prepared_kg REAL NOT NULL,
                consumed_kg REAL NOT NULL,
                waste_kg REAL NOT NULL,
                FOREIGN KEY(hotel_id) REFERENCES hotels(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_type TEXT NOT NULL,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_type TEXT NOT NULL,
                from_id TEXT NOT NULL,
                to_type TEXT NOT NULL,
                to_id TEXT NOT NULL,
                alert_id INTEGER,
                rating INTEGER NOT NULL,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(alert_id) REFERENCES alerts(id)
            )
        ''')
        conn.commit()

# Initialize DB
init_db()

def generate_hotel_id(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM hotels ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    if row:
        last_id = row['id'] # e.g. H001
        num = int(last_id[1:]) + 1
        return f"H{num:03d}"
    return "H001"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'hotel_id' not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_global_vars():
    unread = 0
    if 'hotel_id' in session:
        try:
            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0", (session['hotel_id'],))
                row = cur.fetchone()
                if row:
                    unread = row[0]
        except:
            pass
    return dict(unread_notifications=unread)

# Routes
@app.route('/')
def index():
    return render_template('intro.html')

@app.route('/home/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        hotel_name = request.form['hotel_name'].strip()
        owner_name = request.form['owner_name'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        hotel_type = request.form['hotel_type']
        address = request.form['address'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        errors = []
        if not hotel_name or not owner_name or not email or not phone or not address:
            errors.append("All fields are required.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if not re.match(r'^\+?[\d\s-]{10,}$', phone):
            errors.append("Invalid phone number format.")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template('signup.html')

        password_hash = generate_password_hash(password)

        with get_db() as conn:
            # Check if email exists
            cur = conn.cursor()
            cur.execute("SELECT email FROM hotels WHERE email = ?", (email,))
            if cur.fetchone():
                flash("Email is already registered.", "error")
                return render_template('signup.html')

            hotel_id = generate_hotel_id(conn)
            try:
                conn.execute('''
                    INSERT INTO hotels (id, hotel_name, owner_name, email, phone, hotel_type, address, password_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (hotel_id, hotel_name, owner_name, email, phone, hotel_type, address, password_hash))
                conn.commit()
                flash(f"Registration successful! Your Hotel ID is {hotel_id}. You can now log in.", "success")
                return redirect(url_for('login'))
            except sqlite3.Error as e:
                flash("An error occurred during registration.", "error")
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    hotel_id = session.get('hotel_id')
    with get_db() as conn:
        cur = conn.cursor()
        # Get threshold
        cur.execute("SELECT threshold_kg FROM hotels WHERE id = ?", (hotel_id,))
        threshold = cur.fetchone()['threshold_kg']
        
        # Get latest 5 entries
        cur.execute("SELECT * FROM food_entries WHERE hotel_id = ? ORDER BY entry_date DESC LIMIT 5", (hotel_id,))
        recent_entries = cur.fetchall()
        
        # Calculate stats for today
        import datetime
        today = datetime.date.today().isoformat()
        cur.execute("SELECT SUM(prepared_kg) as t_prep, SUM(consumed_kg) as t_cons, SUM(waste_kg) as t_waste FROM food_entries WHERE hotel_id = ? AND entry_date = ?", (hotel_id, today))
        today_stats = cur.fetchone()
        
        prepared = today_stats['t_prep'] or 0
        consumed = today_stats['t_cons'] or 0
        waste = today_stats['t_waste'] or 0
        
        # Total entries
        cur.execute("SELECT COUNT(*) as cnt FROM food_entries WHERE hotel_id = ?", (hotel_id,))
        total_entries = cur.fetchone()['cnt']
        
        # Pending alerts (using 'Pending' matching our new schema)
        cur.execute("SELECT COUNT(*) as cnt FROM alerts WHERE hotel_id = ? AND status = 'Pending'", (hotel_id,))
        pending_alerts = cur.fetchone()['cnt']
        
        # Recent collection
        cur.execute("SELECT SUM(collected_kg) as total_coll FROM collections WHERE hotel_id = ?", (hotel_id,))
        collection_stats = cur.fetchone()
        collected = collection_stats['total_coll'] or 0

        # Mock ML prediction (Tomorrow's waste) based on today's waste + 5%
        predicted_waste = round(waste * 1.05, 1) if waste > 0 else 0
        prediction_status = "High waste expected" if predicted_waste > threshold else "Within threshold"
        
    return render_template('dashboard.html', 
                           hotel_id=hotel_id,
                           hotel_name=session.get('hotel_name'),
                           threshold=threshold,
                           recent_entries=recent_entries,
                           prepared=prepared,
                           consumed=consumed,
                           waste=waste,
                           total_entries=total_entries,
                           pending_alerts=pending_alerts,
                           collected=collected,
                           predicted_waste=predicted_waste,
                           prediction_status=prediction_status)

@app.route('/update_threshold', methods=['POST'])
@login_required
def update_threshold():
    hotel_id = session.get('hotel_id')
    new_threshold = request.form.get('threshold_kg', type=float)
    if new_threshold is not None:
        with get_db() as conn:
            conn.execute("UPDATE hotels SET threshold_kg = ? WHERE id = ?", (new_threshold, hotel_id))
            conn.commit()
        flash("Threshold updated successfully.", "success")
    return redirect(url_for('dashboard'))

@app.route('/food_entry', methods=['GET', 'POST'])
@login_required
def food_entry():
    hotel_id = session.get('hotel_id')
    edit_id = request.args.get('edit_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 5
    
    with get_db() as conn:
        cur = conn.cursor()
        
        if request.method == 'POST':
            entry_date = request.form.get('entry_date')
            prepared = request.form.get('prepared_kg', type=float)
            consumed = request.form.get('consumed_kg', type=float)
            notes = request.form.get('notes', '')
            
            if prepared is None or consumed is None or prepared < 0 or consumed < 0:
                flash("Values must be valid positive numbers.", "error")
                return redirect(url_for('food_entry'))
                
            if consumed > prepared:
                flash("Consumed amount cannot exceed prepared amount.", "error")
                return redirect(url_for('food_entry'))
                
            waste = round(prepared - consumed, 2)
            
            # Check if entry exists for this date
            cur.execute("SELECT id FROM food_entries WHERE hotel_id = ? AND entry_date = ?", (hotel_id, entry_date))
            existing = cur.fetchone()
            
            if existing:
                conn.execute("UPDATE food_entries SET prepared_kg=?, consumed_kg=?, waste_kg=?, notes=? WHERE id=?", 
                             (prepared, consumed, waste, notes, existing['id']))
                flash("Entry updated successfully.", "success")
            else:
                conn.execute("INSERT INTO food_entries (hotel_id, entry_date, prepared_kg, consumed_kg, waste_kg, notes) VALUES (?, ?, ?, ?, ?, ?)",
                             (hotel_id, entry_date, prepared, consumed, waste, notes))
                flash("Daily entry recorded successfully.", "success")
                
            conn.commit()
            return redirect(url_for('prediction'))
            
        # GET request handling
        edit_data = None
        if edit_id:
            cur.execute("SELECT * FROM food_entries WHERE id = ? AND hotel_id = ?", (edit_id, hotel_id))
            edit_data = cur.fetchone()
            
        # Pagination
        offset = (page - 1) * per_page
        cur.execute("SELECT COUNT(*) as cnt FROM food_entries WHERE hotel_id = ?", (hotel_id,))
        total_items = cur.fetchone()['cnt']
        total_pages = (total_items + per_page - 1) // per_page
        
        cur.execute("SELECT * FROM food_entries WHERE hotel_id = ? ORDER BY entry_date DESC LIMIT ? OFFSET ?", (hotel_id, per_page, offset))
        entries = cur.fetchall()
        
    import datetime
    today = datetime.date.today().isoformat()
    return render_template('food_entry.html', entries=entries, edit_data=edit_data, today=today, page=page, total_pages=total_pages)

@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    hotel_id = session.get('hotel_id')
    with get_db() as conn:
        conn.execute("DELETE FROM food_entries WHERE id = ? AND hotel_id = ?", (entry_id, hotel_id))
        conn.commit()
    flash("Entry deleted successfully.", "success")
    return redirect(url_for('food_entry'))

@app.route('/prediction')
@login_required
def prediction():
    hotel_id = session.get('hotel_id')
    import os
    db_path = os.path.join(app.root_path, DATABASE)
    from ml.predictor import predict_tomorrow_waste
    
    predicted_waste, insufficient_data = predict_tomorrow_waste(hotel_id, db_path)
    
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT threshold_kg FROM hotels WHERE id = ?", (hotel_id,))
        threshold = cur.fetchone()['threshold_kg']
        
        # Get NGOs
        cur.execute("SELECT * FROM ngos")
        ngos = cur.fetchall()
        
        import datetime
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
        is_high = predicted_waste > threshold
        
        cur.execute("INSERT INTO predictions (hotel_id, for_date, predicted_waste, threshold, exceeded_flag) VALUES (?, ?, ?, ?, ?)",
                     (hotel_id, tomorrow, predicted_waste, threshold, 1 if is_high else 0))
        conn.commit()
        prediction_id = cur.lastrowid
        
    return render_template('prediction.html', 
                           predicted_waste=predicted_waste, 
                           threshold=threshold, 
                           is_high=is_high,
                           insufficient_data=insufficient_data,
                           prediction_id=prediction_id,
                           ngos=ngos,
                           tomorrow=tomorrow)

@app.route('/send_alert/<int:prediction_id>', methods=['POST'])
@login_required
def send_alert(prediction_id):
    hotel_id = session.get('hotel_id')
    reserved_kg = request.form.get('reserved_kg', type=float)
    ngo_id = request.form.get('ngo_id')
    
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM predictions WHERE id = ? AND hotel_id = ?", (prediction_id, hotel_id))
        pred = cur.fetchone()
        if pred:
            expected_date = pred['for_date']
            
            conn.execute("INSERT INTO alerts (hotel_id, ngo_id, prediction_id, expected_date, predicted_waste, reserved_kg, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (hotel_id, ngo_id if ngo_id != 'Broadcast' else None, prediction_id, expected_date, pred['predicted_waste'], reserved_kg, 'Pending'))
            conn.commit()
            
            # Send notification
            cur = conn.cursor()
            cur.execute("SELECT email, email_notifications FROM hotels WHERE id = ?", (hotel_id,))
            hotel_data = cur.fetchone()
            if hotel_data:
                mailer.create_notification(
                    conn, 
                    'hotel', 
                    hotel_id, 
                    f"Alert sent to {'broadcast' if ngo_id == 'Broadcast' else 'NGO'} for {reserved_kg}kg of food.",
                    hotel_data['email'] if hotel_data['email_notifications'] else None,
                    "Meal Connect: Alert Sent"
                )
            flash("NGO Alert sent successfully!", "success")
    return redirect(url_for('alerts'))

@app.route('/alerts')
@login_required
def alerts():
    hotel_id = session.get('hotel_id')
    with get_db() as conn:
        cur = conn.cursor()
        # Get all alerts for the hotel, joined with NGOs for names
        cur.execute('''
            SELECT a.*, n.name as ngo_name 
            FROM alerts a 
            LEFT JOIN ngos n ON a.ngo_id = CAST(n.id AS TEXT) 
            WHERE a.hotel_id = ? 
            ORDER BY a.expected_date DESC
        ''', (hotel_id,))
        alerts_list = cur.fetchall()
        
        cur.execute("SELECT * FROM ngos")
        ngos_list = cur.fetchall()
        
    return render_template('alerts.html', alerts=alerts_list, ngos=ngos_list)

@app.route('/mark_collected/<int:alert_id>', methods=['POST'])
@login_required
def mark_collected(alert_id):
    hotel_id = session.get('hotel_id')
    actual_collected = request.form.get('actual_collected', type=float)
    collected_by = request.form.get('collected_by')
    
    with get_db() as conn:
        import datetime
        collection_date = datetime.date.today().isoformat()
        
        # Mark alert as completed
        conn.execute("UPDATE alerts SET status = 'Completed' WHERE id = ? AND hotel_id = ?", (alert_id, hotel_id))
        
        # Get alert info to copy into collections
        cur = conn.cursor()
        cur.execute("SELECT expected_date, predicted_waste, reserved_kg FROM alerts WHERE id = ?", (alert_id,))
        alert_data = cur.fetchone()
        
        # Get actual waste from food_entries for that expected_date
        actual_waste = None
        if alert_data:
            cur.execute("SELECT waste_kg FROM food_entries WHERE hotel_id = ? AND entry_date = ?", (hotel_id, alert_data['expected_date']))
            fe_data = cur.fetchone()
            if fe_data:
                actual_waste = fe_data['waste_kg']
        
        # Log collection
        conn.execute('''
            INSERT INTO collections 
            (alert_id, hotel_id, ngo_id, collection_date, predicted_waste, actual_waste, reserved_kg, collected_kg, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert_id, hotel_id, collected_by, collection_date, 
            alert_data['predicted_waste'] if alert_data else 0, 
            actual_waste, 
            alert_data['reserved_kg'] if alert_data else 0, 
            actual_collected, 'Completed'
        ))
        conn.commit()
        flash("Collection recorded successfully.", "success")
        
    return redirect(url_for('alerts'))

@app.route('/ignore_alert', methods=['POST'])
@login_required
def ignore_alert():
    flash("Alert ignored. Prediction logged for analytics.", "success")
    return redirect(url_for('dashboard'))

@app.route('/analytics')
@login_required
def analytics():
    hotel_id = session.get('hotel_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    date_filter = ""
    params = [hotel_id]
    if start_date and end_date:
        date_filter = " AND entry_date BETWEEN ? AND ?"
        params.extend([start_date, end_date])
        
    with get_db() as conn:
        cur = conn.cursor()
        
        # 1. Total Food Entries
        cur.execute(f"SELECT COUNT(*) as cnt FROM food_entries WHERE hotel_id = ? {date_filter}", params)
        total_entries = cur.fetchone()['cnt']
        
        # 3. Total Actual Waste
        cur.execute(f"SELECT SUM(waste_kg) as total FROM food_entries WHERE hotel_id = ? {date_filter}", params)
        total_actual_waste = round(cur.fetchone()['total'] or 0, 2)
        
        # Date filter for predictions & alerts
        pred_date_filter = ""
        pred_params = [hotel_id]
        if start_date and end_date:
            pred_date_filter = " AND for_date BETWEEN ? AND ?"
            pred_params.extend([start_date, end_date])
            
        # 2. Total Predicted Waste
        cur.execute(f"SELECT SUM(predicted_waste) as total FROM predictions WHERE hotel_id = ? {pred_date_filter}", pred_params)
        total_predicted_waste = round(cur.fetchone()['total'] or 0, 2)
        
        alert_date_filter = ""
        alert_params = [hotel_id]
        if start_date and end_date:
            alert_date_filter = " AND expected_date BETWEEN ? AND ?"
            alert_params.extend([start_date, end_date])
            
        # 4, 6, 7. Alerts stats
        cur.execute(f"SELECT SUM(reserved_kg) as total, COUNT(*) as cnt FROM alerts WHERE hotel_id = ? {alert_date_filter}", alert_params)
        alert_stats = cur.fetchone()
        total_reserved = round(alert_stats['total'] or 0, 2)
        alerts_generated = alert_stats['cnt']
        
        cur.execute(f"SELECT COUNT(*) as cnt FROM alerts WHERE hotel_id = ? AND status = 'Pending' {alert_date_filter}", alert_params)
        pending_alerts = cur.fetchone()['cnt']
        
        # 5, 8. Collections stats
        col_date_filter = ""
        col_params = [hotel_id]
        if start_date and end_date:
            col_date_filter = " AND collection_date BETWEEN ? AND ?"
            col_params.extend([start_date, end_date])
            
        cur.execute(f"SELECT SUM(collected_kg) as total, COUNT(*) as cnt FROM collections WHERE hotel_id = ? {col_date_filter}", col_params)
        col_stats = cur.fetchone()
        total_collected = round(col_stats['total'] or 0, 2)
        completed_collections = col_stats['cnt']
        
        # Data for Chart 1 & 4 (Waste trend & Pred vs Actual)
        cur.execute(f'''
            SELECT f.entry_date, f.waste_kg, p.predicted_waste
            FROM food_entries f
            LEFT JOIN (SELECT for_date, predicted_waste FROM predictions WHERE hotel_id = ?) p 
            ON f.entry_date = p.for_date
            WHERE f.hotel_id = ? {date_filter}
            ORDER BY f.entry_date ASC
        ''', [hotel_id, hotel_id] + (params[1:] if len(params)>1 else []))
        waste_trend_data = cur.fetchall()
        
        dates = [row['entry_date'] for row in waste_trend_data]
        actual_waste_series = [row['waste_kg'] for row in waste_trend_data]
        predicted_waste_series = [(row['predicted_waste'] or 0) for row in waste_trend_data]
        
        # Data for Chart 2 (Reserved vs Collected)
        cur.execute(f'''
            SELECT a.expected_date, a.reserved_kg, c.collected_kg
            FROM alerts a
            LEFT JOIN collections c ON a.id = c.alert_id
            WHERE a.hotel_id = ? {alert_date_filter}
            ORDER BY a.expected_date ASC
        ''', alert_params)
        res_col_data = cur.fetchall()
        res_col_dates = [row['expected_date'] for row in res_col_data]
        reserved_series = [row['reserved_kg'] for row in res_col_data]
        collected_series = [(row['collected_kg'] or 0) for row in res_col_data]
        
        # Data for Chart 3 (NGO Distribution)
        cur.execute(f'''
            SELECT n.name, SUM(c.collected_kg) as total
            FROM collections c
            JOIN ngos n ON c.ngo_id = CAST(n.id AS TEXT)
            WHERE c.hotel_id = ? {col_date_filter}
            GROUP BY n.name
        ''', col_params)
        ngo_dist_data = cur.fetchall()
        ngo_labels = [row['name'] for row in ngo_dist_data]
        ngo_values = [row['total'] for row in ngo_dist_data]
        
        # Latest 5 entries
        cur.execute("SELECT * FROM food_entries WHERE hotel_id = ? ORDER BY entry_date DESC LIMIT 5", (hotel_id,))
        latest_entries = cur.fetchall()
        
    kpis = {
        'total_entries': total_entries,
        'total_predicted_waste': total_predicted_waste,
        'total_actual_waste': total_actual_waste,
        'total_reserved': total_reserved,
        'total_collected': total_collected,
        'alerts_generated': alerts_generated,
        'pending_alerts': pending_alerts,
        'completed_collections': completed_collections
    }
    
    chart_data = {
        'dates': dates,
        'actual_waste': actual_waste_series,
        'predicted_waste': predicted_waste_series,
        'res_col_dates': res_col_dates,
        'reserved': reserved_series,
        'collected': collected_series,
        'ngo_labels': ngo_labels,
        'ngo_values': ngo_values
    }

    return render_template('analytics.html', kpis=kpis, chart_data=chart_data, latest_entries=latest_entries, start_date=start_date, end_date=end_date)


@app.route('/badge')
@login_required
def badge():
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT hotel_name FROM hotels WHERE id = ?", (session['hotel_id'],))
            hotel = cur.fetchone()
            hotel_name = hotel['hotel_name'] if hotel else "Partner"
    except:
        hotel_name = "Partner"
    return render_template('badge.html', hotel_name=hotel_name)

@app.route('/history')
@login_required
def history():
    hotel_id = session.get('hotel_id')
    ngo_filter = request.args.get('ngo', '')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = '''
        SELECT 
            COALESCE(c.collection_date, a.expected_date) as date,
            h.hotel_name as hotel_name,
            n.name as ngo_name,
            a.predicted_waste,
            f.waste_kg as actual_waste,
            a.reserved_kg,
            c.collected_kg,
            a.status
        FROM alerts a
        JOIN hotels h ON a.hotel_id = h.id
        LEFT JOIN collections c ON a.id = c.alert_id
        LEFT JOIN ngos n ON (a.ngo_id = CAST(n.id AS TEXT) OR c.ngo_id = CAST(n.id AS TEXT))
        LEFT JOIN food_entries f ON a.hotel_id = f.hotel_id AND a.expected_date = f.entry_date
        WHERE a.hotel_id = ?
    '''
    params = [hotel_id]
    
    if ngo_filter:
        query += " AND n.id = ?"
        params.append(ngo_filter)
    if start_date and end_date:
        query += " AND a.expected_date BETWEEN ? AND ?"
        params.extend([start_date, end_date])
        
    query += " ORDER BY date DESC"
    
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        records = cur.fetchall()
        
        cur.execute("SELECT * FROM ngos")
        ngos = cur.fetchall()
        
        total_col = sum(1 for r in records if r['status'] == 'Completed')
        total_kg = sum((r['collected_kg'] or 0) for r in records if r['status'] == 'Completed')
        
        from collections import Counter
        ngo_counts = Counter(r['ngo_name'] for r in records if r['status'] == 'Completed' and r['ngo_name'])
        top_ngo = ngo_counts.most_common(1)[0][0] if ngo_counts else "N/A"
        
    return render_template('history.html', records=records, ngos=ngos, total_col=total_col, total_kg=total_kg, top_ngo=top_ngo, selected_ngo=ngo_filter, start_date=start_date, end_date=end_date)

@app.route('/export_history')
@login_required
def export_history():
    hotel_id = session.get('hotel_id')
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT 
                COALESCE(c.collection_date, a.expected_date) as date,
                h.hotel_name as hotel_name,
                n.name as ngo_name,
                a.predicted_waste,
                f.waste_kg as actual_waste,
                a.reserved_kg,
                c.collected_kg,
                a.status
            FROM alerts a
            JOIN hotels h ON a.hotel_id = h.id
            LEFT JOIN collections c ON a.id = c.alert_id
            LEFT JOIN ngos n ON (a.ngo_id = CAST(n.id AS TEXT) OR c.ngo_id = CAST(n.id AS TEXT))
            LEFT JOIN food_entries f ON a.hotel_id = f.hotel_id AND a.expected_date = f.entry_date
            WHERE a.hotel_id = ?
            ORDER BY date DESC
        ''', (hotel_id,))
        records = cur.fetchall()
        
    import io
    import csv
    from flask import Response
    
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Date', 'Hotel', 'NGO', 'Predicted Waste (kg)', 'Actual Waste (kg)', 'Reserved (kg)', 'Collected (kg)', 'Status'])
    for r in records:
        cw.writerow([
            r['date'], r['hotel_name'], r['ngo_name'] or 'Broadcast', 
            r['predicted_waste'], r['actual_waste'] or 'N/A', 
            r['reserved_kg'], r['collected_kg'] or 0, r['status']
        ])
        
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=collection_history.csv"}
    )

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/notifications', methods=['GET', 'POST'])
@login_required
def notifications():
    hotel_id = session['hotel_id']
    with get_db() as conn:
        cur = conn.cursor()
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'mark_all_read':
                cur.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (hotel_id,))
                conn.commit()
                flash("All notifications marked as read.", "success")
            elif action == 'mark_read':
                notif_id = request.form.get('notif_id')
                cur.execute("UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?", (notif_id, hotel_id))
                conn.commit()
            return redirect(url_for('notifications'))
            
        cur.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 50", (hotel_id,))
        notifs = cur.fetchall()
        
    return render_template('notifications.html', notifications=notifs, hotel_name=session.get('hotel_name'), hotel_id=hotel_id)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    hotel_id = session['hotel_id']
    with get_db() as conn:
        cur = conn.cursor()
        
        if request.method == 'POST':
            # Handle updates
            hotel_name = request.form['hotel_name'].strip()
            owner_name = request.form['owner_name'].strip()
            phone = request.form['phone'].strip()
            address = request.form['address'].strip()
            hotel_type = request.form['hotel_type']
            threshold_kg = request.form.get('threshold_kg', 20.0, type=float)
            email_notifs = 1 if request.form.get('email_notifications') else 0
            
            cur.execute("""
                UPDATE hotels 
                SET hotel_name = ?, owner_name = ?, phone = ?, address = ?, hotel_type = ?, threshold_kg = ?, email_notifications = ?
                WHERE id = ?
            """, (hotel_name, owner_name, phone, address, hotel_type, threshold_kg, email_notifs, hotel_id))
            conn.commit()
            session['hotel_name'] = hotel_name
            flash("Profile updated successfully.", "success")
            return redirect(url_for('profile'))
            
        cur.execute("SELECT * FROM hotels WHERE id = ?", (hotel_id,))
        hotel = cur.fetchone()
        
    return render_template('profile.html', hotel=hotel, hotel_name=session.get('hotel_name'), hotel_id=hotel_id)

@app.route('/export/<format>')
@login_required
def export_data(format):
    import csv
    import io
    from flask import Response
    
    hotel_id = session['hotel_id']
    export_type = request.args.get('type', 'entries')
    
    with get_db() as conn:
        cur = conn.cursor()
        if export_type == 'entries':
            cur.execute("SELECT entry_date, prepared_kg, consumed_kg, waste_kg, notes FROM food_entries WHERE hotel_id = ? ORDER BY entry_date DESC", (hotel_id,))
            headers = ['Date', 'Prepared (kg)', 'Consumed (kg)', 'Waste (kg)', 'Notes']
        elif export_type == 'predictions':
            cur.execute("SELECT for_date, predicted_waste, threshold, exceeded_flag FROM predictions WHERE hotel_id = ? ORDER BY for_date DESC", (hotel_id,))
            headers = ['Date', 'Predicted Waste (kg)', 'Threshold (kg)', 'Exceeded']
        elif export_type == 'collections':
            cur.execute("SELECT collection_date, ngo_id, predicted_waste, actual_waste, collected_kg, status FROM collections WHERE hotel_id = ? ORDER BY collection_date DESC", (hotel_id,))
            headers = ['Date', 'NGO ID', 'Predicted Waste (kg)', 'Actual Waste (kg)', 'Collected (kg)', 'Status']
        else:
            flash("Invalid export type.", "error")
            return redirect(url_for('dashboard'))
            
        rows = cur.fetchall()
        
    if format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)
        output.seek(0)
        return Response(output, mimetype="text/csv", headers={"Content-Disposition": f"attachment;filename={export_type}.csv"})
        
    elif format == 'pdf':
        # PDF fallback - if libraries are missing, return a simple text or html response acting as PDF
        # To avoid crashing when WeasyPrint or reportlab is missing, we use simple HTML print view
        html_content = f"<h1>Export: {export_type.capitalize()}</h1><table border='1'><tr>"
        for h in headers: html_content += f"<th>{h}</th>"
        html_content += "</tr>"
        for r in rows:
            html_content += "<tr>"
            for val in r: html_content += f"<td>{val}</td>"
            html_content += "</tr>"
        html_content += "</table><script>window.print();</script>"
        return html_content

    flash("Invalid format.", "error")
    return redirect(url_for('dashboard'))


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


import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on the earth."""
    if None in (lat1, lon1, lat2, lon2):
        return None
        
    R = 6371  # Radius of the earth in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    
    a = (math.sin(dLat/2) * math.sin(dLat/2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dLon/2) * math.sin(dLon/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return round(R * c, 2)


@app.route('/api/map_data')
@login_required
def map_data():
    hotel_id = session.get('hotel_id')
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get Hotel Data
        cur.execute("""
            SELECT h.id, h.hotel_name, h.lat, h.lon, h.hotel_type, h.address, 
                   (SELECT SUM(reserved_kg) FROM alerts WHERE hotel_id = h.id AND status = 'Completed') as total_donated,
                   (SELECT status FROM alerts WHERE hotel_id = h.id AND status IN ('Pending', 'Accepted') LIMIT 1) as active_alert
            FROM hotels h WHERE h.id = ?
        """, (hotel_id,))
        hotel_row = cur.fetchone()
        
        if not hotel_row or hotel_row['lat'] is None or hotel_row['lon'] is None:
            hotel_data = {'id': hotel_id, 'name': session.get('hotel_name', 'Unknown'), 'lat': None, 'lon': None}
        else:
            total = hotel_row['total_donated'] or 0
            badge = 'Gold' if total > 500 else 'Silver' if total > 100 else 'Bronze' if total > 0 else 'New'
            hotel_data = {
                'id': hotel_row['id'],
                'name': hotel_row['hotel_name'],
                'lat': hotel_row['lat'],
                'lon': hotel_row['lon'],
                'type': hotel_row['hotel_type'] or 'Hotel',
                'address': hotel_row['address'],
                'rating': 4.5,
                'total_donated': total,
                'badge': badge,
                'active_alert': hotel_row['active_alert']
            }
            
        # Get NGOs Data
        cur.execute("""
            SELECT n.id, n.name, n.contact_person, n.phone, n.email, n.location, n.lat, n.lon,
                   (SELECT SUM(reserved_kg) FROM alerts WHERE ngo_id = n.id AND status = 'Completed') as total_collected,
                   (SELECT status FROM alerts WHERE hotel_id = ? AND (ngo_id = n.id OR ngo_id IS NULL) AND status IN ('Pending', 'Accepted') LIMIT 1) as active_alert
            FROM ngos n WHERE n.status = 'Approved' AND n.lat IS NOT NULL AND n.lon IS NOT NULL
        """, (hotel_id,))
        ngos_rows = cur.fetchall()
        
        # Get Other Hotels Data
        cur.execute("""
            SELECT h.id, h.hotel_name as name, h.hotel_type as type, h.address as location, h.lat, h.lon,
                   (SELECT SUM(reserved_kg) FROM alerts WHERE hotel_id = h.id AND status = 'Completed') as total_donated
            FROM hotels h WHERE h.lat IS NOT NULL AND h.lon IS NOT NULL AND h.id != ?
        """, (hotel_id,))
        other_hotels_rows = cur.fetchall()
        
    ngo_list = []
    for ngo in ngos_rows:
        dist = None
        eta = None
        if hotel_data['lat'] is not None and hotel_data['lon'] is not None:
            dist = calculate_distance(hotel_data['lat'], hotel_data['lon'], ngo['lat'], ngo['lon'])
            if dist is not None:
                eta = round(dist * 2) # Roughly 2 mins per km in city traffic
                
        ngo_list.append({
            'id': ngo['id'],
            'name': ngo['name'],
            'contact_person': ngo['contact_person'],
            'phone': ngo['phone'],
            'email': ngo['email'],
            'location': ngo['location'],
            'lat': ngo['lat'],
            'lon': ngo['lon'],
            'rating': 4.8,
            'total_collected': ngo['total_collected'] or 0,
            'distance_km': dist,
            'eta_mins': eta,
            'active_alert': ngo['active_alert']
        })
        
    other_hotels_list = []
    for h in other_hotels_rows:
        dist = None
        if hotel_data['lat'] is not None and hotel_data['lon'] is not None:
            dist = calculate_distance(hotel_data['lat'], hotel_data['lon'], h['lat'], h['lon'])
            
        other_hotels_list.append({
            'id': h['id'],
            'name': h['name'],
            'type': h['type'] or 'Hotel',
            'location': h['location'],
            'lat': h['lat'],
            'lon': h['lon'],
            'total_donated': h['total_donated'] or 0,
            'distance_km': dist
        })
        
    return jsonify({
        'hotel': hotel_data,
        'ngos': sorted(ngo_list, key=lambda x: x['distance_km'] if x['distance_km'] is not None else 999999),
        'other_hotels': other_hotels_list
    })

@app.route('/api/ngo_map_data')
@ngo_login_required
def ngo_map_data():
    ngo_id = session.get('ngo_id')
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get NGO Data
        cur.execute("SELECT id, name, lat, lon FROM ngos WHERE id = ?", (ngo_id,))
        ngo_row = cur.fetchone()
        
        ngo_data = {'name': 'Unknown', 'lat': None, 'lon': None}
        if ngo_row and ngo_row['lat'] is not None and ngo_row['lon'] is not None:
            ngo_data = {
                'id': ngo_row['id'],
                'name': ngo_row['name'],
                'lat': ngo_row['lat'],
                'lon': ngo_row['lon']
            }
        
        # Get Active Hotels
        cur.execute("""
            SELECT h.id, h.hotel_name, h.hotel_type, h.address, h.lat, h.lon, h.phone, 
                   a.id as alert_id, a.reserved_kg, a.status, a.created_at
            FROM alerts a
            JOIN hotels h ON a.hotel_id = h.id
            WHERE (a.ngo_id = ? OR a.ngo_id IS NULL) AND a.status = 'Pending' AND h.lat IS NOT NULL AND h.lon IS NOT NULL
        """, (ngo_id,))
        active_hotels = cur.fetchall()
        
    hotel_list = []
    for h in active_hotels:
        dist = None
        eta = None
        if ngo_data['lat'] is not None and ngo_data['lon'] is not None:
            dist = calculate_distance(ngo_data['lat'], ngo_data['lon'], h['lat'], h['lon'])
            if dist is not None:
                eta = round(dist * 2)
                
        hotel_list.append({
            'id': h['id'],
            'name': h['hotel_name'],
            'type': h['hotel_type'] or 'Hotel',
            'address': h['address'],
            'contact': h['phone'],
            'lat': h['lat'],
            'lon': h['lon'],
            'alert_id': h['alert_id'],
            'reserved_kg': h['reserved_kg'],
            'status': h['status'],
            'created_at': h['created_at'],
            'distance_km': dist,
            'eta_mins': eta
        })
        
    return jsonify({
        'ngo': ngo_data,
        'hotels': hotel_list
    })

@app.route('/map')
@login_required
def live_map():
    return render_template('map.html', hotel_name=session.get('hotel_name'), hotel_id=session['hotel_id'])

@app.route('/api/public_directory')
def public_directory():
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get up to 20 Approved Hotels
        cur.execute('SELECT hotel_name as name, address as location, hotel_type as type FROM hotels LIMIT 20')
        hotels = [dict(row) for row in cur.fetchall()]
        
        # Get up to 20 Approved NGOs
        cur.execute('SELECT name, location FROM ngos WHERE status = "Approved" LIMIT 20')
        ngos = [dict(row) for row in cur.fetchall()]
        
        # Add a mock 'focus' field for NGOs if needed by the frontend, or just use location
        for n in ngos:
            n['focus'] = 'Food Rescue & Redistribution'
            
        from flask import jsonify
        return jsonify({'hotels': hotels, 'ngos': ngos})

if __name__ == '__main__':
    app.run(debug=True, port=5000)




