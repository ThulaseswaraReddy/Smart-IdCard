from flask import Flask,redirect,request,render_template,url_for,session,flash
from db import connection
from werkzeug.security import generate_password_hash, check_password_hash
import qrcode
import os
app=Flask(__name__)
app.secret_key='SmartIdCard@2026#FlaskProject'
cursor=connection.cursor(dictionary=True)
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=='POST':
        try:
            username = request.form["username"]
            password = request.form["password"]
            sql = "SELECT * FROM admin WHERE username=%s"
            cursor.execute(sql, (username,))
            admin = cursor.fetchone()
            if admin and check_password_hash(admin["password"], password):
                session["admin"] = username
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid Username or Password", "danger")
        except Exception as e:
            flash("Something went wrong!", "danger")
    return render_template('login.html')
     
@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))
    cursor.execute("SELECT COUNT(*) AS total FROM student")
    total_students = cursor.fetchone()['total']
    cursor.execute("SELECT qrcode FROM student")
    students = cursor.fetchall()
    qr_generated = 0
    qr_pending = 0
    for student in students:
        if student['qrcode']:
            path = os.path.join(app.root_path, "static", "qrcodes", student['qrcode'])
            if os.path.exists(path):
                qr_generated += 1
            else:
                qr_pending += 1
        else:
            qr_pending += 1
    return render_template(
        "dashboard.html",
        total_students=total_students,
        qr_generated=qr_generated,
        qr_pending=qr_pending
    )
    
@app.route('/add_student',methods=["GET","POST"])
def add_student():
    if 'admin' not in session:
        return redirect(url_for('login'))
    if request.method=='POST': 
        student_name =request.form['student_name']
        rollno  =request.form['rollno']
        department  =request.form['department']
        gender  =request.form['gender']
        phone =request.form['phone']
        address  =request.form['address']
        blood_group  =request.form['blood_group']
        parentnumber=request.form['parent']
        validate_rollno='select rollno from student where rollno=%s'
        cursor.execute(validate_rollno, (rollno,))
        fetchingstudent=cursor.fetchone()
        if not phone.isdigit() or len(phone)!=10:
            flash("Phone number must contain exactly 10 digits.", "danger")
            return redirect(url_for("add_student"))
        if not parentnumber.isdigit() or len(parentnumber)!=10:
            flash("Phone number must contain exactly 10 digits.", "danger")
            return redirect(url_for("add_student"))
        if fetchingstudent:
            flash("Roll Number Already Exists!", "danger")
            return redirect(url_for("add_student"))
        blood_groups=['A+','A-','B+','B-','AB+','AB-','O-','O+']
        if blood_group not in blood_groups:
            flash("Invalid Blood Group.", "danger")
            return redirect(url_for("add_student"))
        sql='''INSERT INTO student ( student_name,rollno,department,gender,phone,address,blood_group,parentnumber)VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'''
        values=(
            student_name,rollno,department,gender,phone,address,blood_group,parentnumber
        )
        try:
            cursor.execute(sql,values)
            connection.commit()
            flash("Student Added Successfully!", "success")
            return redirect(url_for("students"))
        except Exception as e:
            connection.rollback()
            flash("Something went wrong!", "danger")
            return redirect(url_for("add_student"))
    return render_template('add_student.html')

@app.route('/students',methods=["GET","POST"])
def students():
    if 'admin' not in session:
        return redirect(url_for('login'))
    try:
        sql = 'SELECT * FROM student'
        cursor.execute(sql)
        students = cursor.fetchall()
        for student in students:
            if student['qrcode']:
                path = os.path.join(app.root_path, "static", "qrcodes", student['qrcode'])
                student['qr_exists'] = os.path.exists(path)
            else:
                student['qr_exists'] = False
        return render_template('students.html', students=students)
    except Exception as e:
        flash("Something went wrong!", "danger")
        return redirect(url_for("dashboard"))
    
@app.route('/edit_student/<int:id>',methods=['GET','POST'])
def edit_student(id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    if request.method=="POST":
        student_name = request.form['student_name']
        rollno = request.form['rollno']
        department = request.form['department']
        gender = request.form['gender']
        phone = request.form['phone']
        address = request.form['address']
        blood_group = request.form['blood_group']
        parentnumber = request.form['parent']
        if not phone.isdigit() or len(phone)!=10:
            flash("Phone number must contain exactly 10 digits.", "danger")
            return redirect(url_for("edit_student", id=id))
        if not parentnumber.isdigit() or len(parentnumber)!=10:
            flash("Phone number must contain exactly 10 digits.", "danger")
            return redirect(url_for("edit_student", id=id))
        blood_groups=['A+','A-','B+','B-','AB+','AB-','O-','O+']
        if blood_group not in blood_groups:
            flash("Invalid Blood Group.", "danger")
            return redirect(url_for("edit_student", id=id))
        try:
            sql='''UPDATE student SET student_name=%s,rollno=%s,department=%s,gender=%s,phone=%s,address=%s,blood_group=%s,parentnumber=%s WHERE id=%s'''
            values=(student_name,rollno,department,gender,phone,address,blood_group,parentnumber,id)
            cursor.execute(sql,values)
            connection.commit()
            flash("Student Updated Successfully!", "success")
            return redirect(url_for('students'))
        except Exception as e:
            connection.rollback()
            flash("Something went wrong!", "danger")
            return redirect(url_for("edit_student", id=id))
    try:
        sql="SELECT * FROM student WHERE id=%s"
        cursor.execute(sql,(id,))
        student=cursor.fetchone()
        return render_template('edit_student.html',student=student)
    except Exception as e:
        flash("Something went wrong!", "danger")
        return redirect(url_for("students"))
    
@app.route('/delete_student/<int:id>',methods=['GET','POST'])
def delete_student(id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    try:
        cursor.execute("SELECT qrcode FROM student WHERE id=%s", (id,))
        student = cursor.fetchone()
        if student and student['qrcode']:
            path = os.path.join(app.root_path, "static", "qrcodes", student['qrcode'])
            if os.path.exists(path):
                os.remove(path)
        sql='DELETE FROM student WHERE id=%s'
        cursor.execute(sql,(id,))
        connection.commit()
        flash("Student Deleted Successfully!", "success")
    except Exception as e:
        connection.rollback()
        flash("Something went wrong!", "danger")
    return redirect(url_for('students'))

@app.route('/generate_qr/<rollno>',methods=["GET","POST"])
def generate_qr(rollno):
    if 'admin' not in session:
        return redirect(url_for('login'))
    link="http://127.0.0.1:5000/student/"+rollno
    img=qrcode.make(link)
    filename=rollno+".png"
    update='update student set qrcode=%s where rollno=%s'
    try:
        cursor.execute(update,(filename,rollno))
        connection.commit()
        save_dir = os.path.join(app.root_path, 'static', 'qrcodes')
        os.makedirs(save_dir, exist_ok=True)
        path = os.path.join(save_dir, filename)
        img.save(path)
        flash("QR Code Generated Successfully!", "success")
    except Exception as e:
        connection.rollback()
        flash("Something went wrong!", "danger")
    return redirect(url_for("students"))

@app.route('/student/<rollno>')
def student_details(rollno):
    try:
        sql='SELECT * FROM student WHERE rollno=%s'
        cursor.execute(sql,(rollno,))
        student=cursor.fetchone()
        if student:
            return render_template("student_details.html",student=student)
        else:
            return "Student not found."
    except Exception as e:
        return "Something went wrong!"
    
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

if __name__=='__main__':
    app.run()
    
