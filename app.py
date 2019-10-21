from flask import Flask, render_template, url_for, request, g , session, redirect
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
    
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def get_current_user():
    user_result = None

    if 'user' in session:
        user = session['user']

        db = get_db()
        user_cur = db.execute('select id, name, password from users where name = ?', [user])
        user_result = user_cur.fetchone()

    return user_result

@app.route('/index2')
def index():
    user = get_current_user()

    if  not user:
        return redirect(url_for('login'))

    db = get_db()

    log_cur = db.execute('select sent, delivered, Hard_Bounced, soft_Bounced, Pending, Opened, clicked_Email, Unsubscribed from email')
    log_results = log_cur.fetchall()

    totals = {}
    totals['sent'] = 0
    totals['delivered'] = 0
    totals['Opened'] = 0
    totals['clicked_Email'] = 0

    for email in log_results:
        totals['sent'] += email['sent']
        totals['delivered'] += email['delivered']
        totals['Opened'] += email['Opened']
        totals['clicked_Email'] += email['clicked_Email']

    db = get_db()

    log_chart = db.execute('select data1, data2, data3, data4, data5 from charts')
    chart_results = log_chart.fetchall()

    C_totals = {}
    C_totals['data1'] = 0
    C_totals['data2'] = 0
    C_totals['data3'] = 0
    C_totals['data4'] = 0
    C_totals['data5'] = 0

    for chart in chart_results:
        C_totals['data1'] += chart['data1']
        C_totals['data2'] += chart['data2']
        C_totals['data3'] += chart['data3']
        C_totals['data4'] += chart['data4']
        C_totals['data5'] += chart['data5']
        
    return render_template('html/index.html', user=user, totals=totals, chart=C_totals)

@app.route('/register', methods=['GET','POST'])
def register():
    user = get_current_user()

    if request.method == 'POST':
        db=get_db()
        existing_user_cur = db.execute('select id from users where name = ?', [request.form['name']])
        existing_user = existing_user_cur.fetchone()

        if existing_user:
            return render_template('html/page-register.html', user=user, error="User already exist")

        hashed_password = generate_password_hash(request.form['password'], method='sha256')
        db.execute('insert into users (name, password,admin) values(?,?,?)', [request.form['name'], hashed_password,'0'])
        db.commit()

        session['user'] = request.form['name']

        return redirect(url_for('index'))

    return render_template('html/page-register.html', user=user)


@app.route('/login', methods=["Get","POST"])
def login():
    user = get_current_user()

    if request.method == "POST":
        db=get_db()

        name = request.form['name']
        password = request.form['password']

        user_cur = db.execute('select id, name, password from users where name = ?',[name])
        user_result = user_cur.fetchone()

        if check_password_hash(user_result['password'], password):
            session['user'] = user_result['name']
            return redirect(url_for('index2'))
        else:
            return redirect(url_for('forgot'))
        
    return render_template('html/page-login2.html',user=user)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/email-dashboard')
def index2():
    user = get_current_user()

    if not user:
        return redirect(url_for('login'))

    db = get_db()

    log_cur = db.execute(
        'select Email_Name,sent, delivered, Hard_Bounced, soft_Bounced, Pending, Opened, clicked_Email, Unsubscribed from email')
    log_results = log_cur.fetchall()
    tab_cur = db.execute(
        'select Email_Name,sent, delivered, Opened, clicked_Email, First_Activity from email order by sent desc')
    
    log_table = tab_cur.fetchall()

    user_cur = db.execute('select name,FirstName,LastName from users')
    user_result = user_cur.fetchone()

    totals = {}
    totals['sent'] = 0
    totals['delivered'] = 0
    totals['Opened'] = 0
    totals['clicked_Email'] = 0

    for email in log_results:
        totals['sent'] += email['sent']
        totals['delivered'] += email['delivered']
        totals['Opened'] += email['Opened']
        totals['clicked_Email'] += email['clicked_Email']

    percent = {}
    percent['avr_sent'] = round(totals['sent'] / totals['sent'],2)
    percent['avr_del'] = round(totals['delivered'] / totals['sent'], 2)
    percent['avr_open'] = round(totals['Opened'] / totals['delivered'], 2)
    percent['avr_click'] = round(totals['clicked_Email'] / totals['delivered'], 2)

    return render_template('html/email-dashboard.html', user=user, user_result=user_result, totals=totals, percent=percent, log_results=log_results, log_table=log_table)


@app.route('/forgot')
def forgot():
  
    return render_template('html/page-forgot-password.html')


@app.route('/campaign-analytics')
def index3():

    user = get_current_user()

    if not user:
        return redirect(url_for('login'))

    db = get_db()

    user_cur = db.execute('select name,FirstName, LastName from users')
    user_result = user_cur.fetchone()

    return render_template('html/campaign-analytics.html', user=user, user_result=user_result)



if __name__ == '__main__':
    app.run(debug=True)

