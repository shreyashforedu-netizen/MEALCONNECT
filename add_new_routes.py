import os

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_routes = '''
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

'''

if 'def notifications():' not in content:
    content += '\n' + new_routes
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
