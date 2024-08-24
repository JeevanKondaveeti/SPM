from flask import Flask,redirect,render_template,request,url_for,flash,session
from flask_session import Session
from colorama import Fore, Back, Style
from otp import genotp
from spmmail import semdmail
import mysql.connector
from stoken  import token,dtoken
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
app.secret_key = "E11CD7B8D64CAA25611DD4EE22393"

mydb = mysql.connector.connect(user='root',password='admin',db='SPM',host='localhost')
#print(mydb)
if mydb.is_connected():
    print("Connected")
else:
    print("Database not connected")
@app.route('/')
def home():
    return render_template("welcome.html")

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        data=dict(request.form)
        s_mail = data['email']
        cursor = mydb.cursor(buffered=True)
        """ cursor.execute(f'select * from student where email = {s_mail}') """
        cursor.execute('select count(email) from student where email = %s',[s_mail])
        dbdata = cursor.fetchone()[0]
        print(dbdata)
        if dbdata == 0:
            otp = genotp()
            data['otp'] = otp
            subject= 'Verification OTP for SPM application'
            body = f'Registration OTP for SPM application {otp}'
            to = data['email']
            semdmail(to,body,subject)
            print(Fore.RED+"data received from registration form")
            return redirect(url_for('otp_verification',data1=token(data=data)))
        else:
            flash('Email already existed')
            return redirect(url_for('register'))

            """
            return 'mail  already exist'
         cursor = mydb.cursor(buffered=True)
        data=cursor.execute('insert into student (email,student_fname,student_lname,password) 
        values (%s,%s,%s,%s)',[s_mail,s_fname,s_lname,s_pass])
        print(data)
        mydb.commit()
        cursor.close() """
    return render_template("register.html")

@app.route('/otp/<data1>',methods = ['GET','POST'])
def otp_verification(data1):
    try:
        data = dtoken(data=data1)
        print(type(data))
        print(data) 
        if request.method == 'POST':
            s_mail = data['email']
            s_fname = data['First name']
            s_lname = data['Last name']
            s_pass = data['password']
            uotp = request.form['otp'] 
            if uotp == data['otp'] :
                cursor = mydb.cursor(buffered=True)
                data=cursor.execute(
                    'insert into student (email,student_fname,student_lname,password) values (%s,%s,%s,%s)',
                    [s_mail,s_fname,s_lname,s_pass]
                    )
                print(data)
                mydb.commit()
                cursor.close()
                flash('USER ADDED TO SERVER')
                return redirect(url_for('register'))
            #return 'Registered successfully'
            else:
                flash('INVALID OTP')
                return redirect(url_for('otp_verification',data1=token(data=data)))
            #return f'otp invalid pls check your mail'
    except Exception as e:
        print(e)
        return "time out of otp"
    finally:
        print("ok form otp")
            
    return render_template('otp_verification.html')

@app.route('/Login',methods=['GET','POST'])
def Login():
    if session.get('email'):
        return redirect(url_for('panel'))
    else:
        if request.method == 'POST':
            login_info = dict(request.form)
            email = login_info['email']
            passwrd = login_info['password']
            print([email,passwrd])
            try:
                cursor = mydb.cursor(buffered=True)
                cursor.execute('select email,password from student where email = %s',[email])
                data = cursor.fetchone()
                passkey = data[1].decode('utf-8')
                print(type(passkey))
            except Exception as e:
                print(e)
                flash("Please check email")
                return redirect(url_for('Login'))
            else:
                if passkey == passwrd:
                    session['email'] = email
                    if not session.get(email):
                        session[email]={}
                        return render_template('panel.html')
                else:
                    flash("Invalid Password")            
    return render_template("Login.html")
@app.route('/addNote',methods = ['GET','POST'])
def addNotes():
    if not session.get('email'):
        return redirect(url_for('Login'))
    else:
        if request.method == 'POST':
            notes = dict(request.form)
            tittle = notes['Notes_Title']
            content = notes['content']
            addedby = session.get('email')
            cursor = mydb.cursor(buffered=True)
            cursor.execute(
                'insert into notes(title,note_content,added_by) values (%s,%s,%s)',[tittle,content,addedby]
            )
            mydb.commit()
            cursor.close()
            flash(f'Notes with {tittle} added successfully')
            return render_template('add_notes.html')
    return render_template('add_notes.html')

@app.route('/panel')
def panel():
    if not session.get('email'):
        return render_template('Login.html')
    return render_template('panel.html')

@app.route('/updatenotes',methods=['GET','POST'])
def updatenotes():
    if not session.get('email'):
        return render_template('Login.html')
    return render_template('updatenotes.html')

@app.route('/allnotes')
def allnotes():
    if not session.get('email'):
        return render_template('Login.html')
    added_by = session.get('email')
    cursor = mydb.cursor(buffered=True)
    cursor.execute("select created_at,nid,title from notes where added_by=%s",[added_by])
    data = cursor.fetchall()
    #print(data)
    return render_template('table.html',data=data)

@app.route('/viewnotes/<nid>')
def viewnotes(nid):
    id=int(nid)
    if not session.get('email'):
        return render_template('Login.html')
    else:
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select title,note_content from notes where nid = %s ',[id])
        notes_data = cursor.fetchone()
        #print(notes_data)
        return render_template('viewnotes.html',notes_data=notes_data)

@app.route('/update/<nid>',methods = ['GET','POST'])
def update_notes(nid):
    id=int(nid)
    if not session.get('email'):
        return render_template('Login.html')
    else:   
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select title,note_content from notes where nid = %s ',[id])
        notes_data = cursor.fetchone()
        if request.method == 'POST':
            notes = dict(request.form)
            tittle = notes['Notes_Title']
            content = notes['content']
            cursor.execute('UPDATE notes SET title = %s, note_content = %s WHERE nid = %s; ',[tittle,content,id])
            mydb.commit()
            cursor.close()
            return redirect(url_for('allnotes'))
        return render_template('updatenotes.html',notes_data=notes_data)

@app.route('/delete_notes/<nid>')
def delete_notes(nid):
    id=int(nid)
    if not session.get('email'):
        return render_template('Login.html')
    else:
        cursor = mydb.cursor(buffered=True)
        cursor.execute('delete from notes where nid=%s',[id])
        mydb.commit()
        cursor.close()
        flash(f'Notes with {id} deleted successfully')
        return redirect(url_for('allnotes'))


@app.route('/Logout')
def logout():
    if session.get('email'):
        session.pop('email')
        return redirect(url_for('Login'))
    else:
        return redirect(url_for('Login'))

app.run(debug=True,host='localhost',port=1601,use_reloader=True)