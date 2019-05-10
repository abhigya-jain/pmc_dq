from flask import Flask
from flask import Markup
from flask import Flask
from flask import render_template
from flask import session, redirect, url_for, escape, request, render_template
from hashlib import md5

import os
import pymysql

#db = pymysql.connect("localhost", "username", "password", "database")

application = Flask(__name__,static_folder='templates/assets')
application.secret_key = os.urandom(24)


if __name__ == '__main__':
    #db = pymysql.connect("aaz892gshlopnn.cgzb88d6tyf7.us-east-2.rds.amazonaws.com", "root", "mysql-123", "pmc_dq_main")
    #db = MySQLdb.connect(host="localhost", user="root", passwd="mysql@123", db="pmc_dq_main",auth_plugin="mysql_native_password")
    #cur = db.cursor()
    application.secret_key = os.urandom(24)

class ServerError(Exception):pass

@application.route("/")
def index():
    if 'username' not in session:
        print("in index - session doesnt exists")
        return redirect(url_for('login'))
    print("in index - session exists")
    username_session = escape(session['username']).capitalize()
    db = pymysql.connect("aaz892gshlopnn.cgzb88d6tyf7.us-east-2.rds.amazonaws.com", "root", "mysql-123", "pmc_dq_main")
    cur = db.cursor()
    trend_labels=[]
    trend_values = []

    cat_legend = 'Monthly Data Files'
    cat_labels = ["Sales", "Brand", "HR", "Legal", "Finance"]
    cat_values = [50,20,10,20,44]

    cur.execute("SELECT * FROM pmc_monthly_data_input_trend")
    records=cur.fetchall()

    trend_legend = 'Monthly Data Files'
    for row in records:
        trend_labels.append(row[1])
        trend_values.append(row[2])

    return render_template('index.html', session_user_name=username_session, trend_values=trend_values, trend_labels=trend_labels, trend_legend=trend_legend,cat_values=cat_values, cat_labels=cat_labels, cat_legend=cat_legend)


@application.route('/dqm/login', methods=['GET', 'POST'])
def login():
    print("*****in login**")
    if 'username' in session:
        return redirect(url_for('index'))

    error = None
    try:
        if request.method == 'POST':
            db = pymysql.connect("aaz892gshlopnn.cgzb88d6tyf7.us-east-2.rds.amazonaws.com", "root", "mysql-123", "pmc_dq_main")
            cur = db.cursor()
            username_form  = request.form['username']
            print("Username - " + request.form['username'])
            #cur.execute("SELECT COUNT(1) FROM pmc_dq_user_details WHERE username = {};"
            #            .format(username_form))
            cur.execute("SELECT COUNT(1) FROM pmc_dq_user_details WHERE username = '" + format(username_form) +"'")

            if not cur.fetchone()[0]:
                raise ServerError('Invalid username')

            password_form  = request.form['password']
            cur.execute("SELECT password FROM pmc_dq_user_details WHERE username = '" + format(username_form) +"'")

            for row in cur.fetchall():
                if password_form == row[0]:
                    session['username'] = request.form['username']
                    return redirect(url_for('index'))

            raise ServerError('Invalid password')
    except ServerError as e:
        error = str(e)
        print(error)

    return render_template('/ipsen-dq/login.html', error=error)


@application.route("/dqm/file_view")
def file_view():
    if 'username' not in session:
        print("in index - session doesnt exists")
        return redirect(url_for('login'))
    print("in index - session exists")
    username_session = escape(session['username']).capitalize()
    db = pymysql.connect("aaz892gshlopnn.cgzb88d6tyf7.us-east-2.rds.amazonaws.com", "root", "mysql-123", "pmc_dq_main")
    cur = db.cursor()
    trend_labels=[]
    trend_values = []

    cat_legend = 'Monthly Data Files'
    cat_labels = ["Sales", "Brand", "HR", "Legal", "Finance"]
    cat_values = [50,20,10,20,44]

    cur.execute("SELECT * FROM pmc_monthly_data_input_trend")
    records=cur.fetchall()

    trend_legend = 'Monthly Data Files'
    for row in records:
        trend_labels.append(row[1])
        trend_values.append(row[2])

    return render_template('/ipsen-dq/file_view.html', session_user_name=username_session, trend_values=trend_values, trend_labels=trend_labels, trend_legend=trend_legend,cat_values=cat_values, cat_labels=cat_labels, cat_legend=cat_legend)


@application.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5001)
