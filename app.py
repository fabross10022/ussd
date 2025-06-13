from flask import Flask, render_template, request, redirect
import pymysql

app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='ussd_appeal_system',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def dashboard():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM appeals")
        appeals = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', appeals=appeals)

@app.route('/update_status/<int:appeal_id>', methods=['POST'])
def update_status(appeal_id):
    new_status = request.form['status']
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("UPDATE appeals SET status=%s WHERE id=%s", (new_status, appeal_id))
        conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(port=5500, debug=True)