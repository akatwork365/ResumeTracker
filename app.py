from uu import encode

from flask import Flask,render_template,request,redirect,url_for,flash,session
#from flask_mysqldb import MySQL
import pymysql
import bcrypt

app = Flask(__name__)

app.secret_key='Aashutosh'

def get_connection():
    return pymysql.connect(
        host='localhost',
        user='flaskuser',
        password='flask123',
        database='resume_tracker_db',
        port=3307
    )




@app.route('/')
def home():
    if 'user' not in session:
    # put application's code here
        return render_template('home.html')
    else:
        return render_template('dashboard.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup_save', methods=['post'])
def signup_save():
    n=request.form['Name']
    m=request.form['Mobile']
    e=request.form['Email']
    g=request.form['Gender']
    p=request.form['Password']
    hashed_password=bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt(10))

    try:

        con = get_connection()

        cur=con.cursor()

        cur.execute('insert into signup(name,mobile,email,gender,password) values(%s,%s,%s,%s,%s)' ,(n,m,e,g,hashed_password))
        con.commit()
        flash("Account Created Successfully ")

    except Exception as err:
        flash("User Mobile number already exists try again with other details")

    finally:
        cur.close()
        con.close()



    return redirect(url_for('signup'))

@app.route('/login')
def login():
    if 'user' not in session:
        return render_template('login.html')
    else:
        return redirect(url_for('dashboard'))

@app.route('/login_check', methods=['POST'])
def login_check():
    m=request.form['Mobile']
    p=request.form['Password']
    con = get_connection()
    cur = con.cursor()
    cur.execute('SELECT password FROM signup WHERE mobile=%s', (m,))
    user = cur.fetchone()
    cur.close()
    con.close()
    if user:
        stored_hash=user[0].encode('utf-8')
        if bcrypt.checkpw(p.encode('utf-8'),stored_hash):
            session['user']=m

            return redirect(url_for('dashboard'))
        else:
            flash("Login Unsuccessful. Please check username and password")
            return redirect(url_for('login'))
    else:
        flash("Login Unsuccessful. Please check username and password")
        return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:

        return redirect(url_for('home'))
    else:
        con=get_connection()
        cur=con.cursor()
        cur.execute('select name from signup where mobile=%s',(session['user'],))
        result=cur.fetchone()
        name=result[0]
        cur.execute('select id,company,role,date,status,interview,notes from applicants where mobile=%s',(session['user'],))
        data=cur.fetchall()
        cur.execute(""" SELECT COUNT(*) ,SUM(status='Interview'),SUM(status='Selected'),SUM(status='Rejected')FROM applicants WHERE mobile=%s""", (session['user'],))
        stats=cur.fetchall()
        cur.close()
        con.close()
        return render_template('dashboard.html',username=name,data=data,stats=stats)


@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect(url_for('home'))

@app.route('/add_application')
def add_application():
    if 'user' in session:
        return render_template('add_application.html')
    else:
        return redirect(url_for('home'))

@app.route('/save_application',methods=['post'])
def save_application():

    c=request.form['Company']
    r=request.form['Role']
    da=request.form['DateApplied']
    s=request.form['Status']
    id=request.form.get('InterviewDate')
    n=request.form.get('Notes')
    con=get_connection()
    cur=con.cursor()
    cur.execute('insert into applicants(mobile,company,role,date,status,interview,notes) values (%s,%s,%s,%s,%s,%s,%s)',(session['user'],c,r,da,s,id,n))
    con.commit()
    cur.close()
    con.close()
    flash("Application Saved Successfully ")
    return redirect(url_for('dashboard'))


@app.route('/edit/<int:id>')
def edit(id):
    if 'user' in session:
        con=get_connection()
        cur=con.cursor()
        cur.execute('select id,company,role,date,status,interview,notes from applicants where id=%s',(id,))
        data=cur.fetchone()
        cur.close()
        con.close()
        return render_template('edit.html',data=data)
    else:
        return redirect(url_for('home'))

@app.route('/edit_save',methods=['post'])
def edit_save():
    i=request.form['Id']
    c = request.form['Company']
    r = request.form['Role']
    da = request.form['DateApplied']
    s = request.form['Status']
    id = request.form.get('InterviewDate')
    n = request.form.get('Notes')
    con = get_connection()
    cur = con.cursor()
    cur.execute("""UPDATE applicants SET company=%s,role=%s,date=%s,status=%s,interview=%s,notes=%s WHERE id = %s""", (c, r, da, s, id, n, i))
    con.commit()
    cur.close()
    con.close()
    flash("Application Edited Successfully ")
    return redirect(url_for('dashboard'))


@app.route('/delete/<int:id>')
def delete(id):
    con=get_connection()
    cur = con.cursor()
    cur.execute('delete from applicants where id=%s',(id,))
    con.commit()
    cur.close()
    con.close()
    return redirect(url_for('dashboard'))











if __name__ == '__main__':
    app.run(debug=True)
