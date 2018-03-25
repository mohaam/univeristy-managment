from flask import Flask ,request,render_template,redirect,url_for,flash,session,jsonify
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
engine = create_engine('mysql+mysqlconnector://root:@localhost:3306/sis')
sessionDB = Session(engine)

app = Flask(__name__)
@app.route('/',methods =['POST','GET'])
def index():
    if request.method == 'POST':
        code = request.form['id']
        job = request.form['job']
        #work for admin only
        #forget to check the cases
        if job == 'admin':
            result = sessionDB.execute("SELECT id FROM admin WHERE secretcode = :code",{"code":code}).fetchone()
            print(result.id)
            if result ==None:
                return "wrong"
            else:
                session['id']=result.id
                return redirect(url_for('admin',id=result.id))

        if job == 'student':
            result =  sessionDB.execute("SELECT ID FROM student WHERE secretcode = :code",{"code":code}).fetchone()
            return "test"

    else:
        return render_template('index.html')

#admin workspace
@app.route('/admin/<int:id>/',methods=['POST','GET'])
#let admin choose for links what he want
def admin(id):
    if session['id'] == id:
        if request.method == 'POST':
            who = request.form['btn']
            if who == "student":
                deparment = request.form['deparment']
                program = request.form['program']
                level = request.form['level']
                result = sessionDB.execute(
                    "SELECT * FROM program WHERE department_name = :deparment and name = :program and level = :level",
                    {"deparment": deparment, "program": program, "level": level}).fetchone()

                print(result)
                if result == None:
                    # worng information
                    return "wrong information"
                else:
                    return redirect(url_for('studentcontrol',id=id,dep_name=deparment,prog_name=program,level=level))
            if who =="teacher":
                deparment = request.form['deparment']
                result = sessionDB.execute("SELECT * FROM department WHERE name = :deparment",{"deparment": deparment}).fetchone()
                if result == None:
                    # worng information
                    return "wrong information"
                else:
                    return redirect(url_for('teachercontrol',id=id,dep_name=deparment))

            if who == "courses":
                deparment = request.form['deparment']
                program = request.form['program']
                level = request.form['level']
                result = sessionDB.execute(
                    "SELECT * FROM program WHERE department_name = :deparment and name = :program and level = :level",
                    {"deparment": deparment, "program": program, "level": level}).fetchone()

                print(result)
                if result == None:
                    # worng information
                    return "wrong information"
                else:
                    return redirect(url_for('coursescontrol', id=id, dep_name=deparment, prog_name=program, level=level))


        else:
            return render_template('adminpage.html', id=id)

@app.route('/admin/<int:id>/studentscontrol/<string:dep_name>/<string:prog_name>/<int:level>/',methods=['POST','GET'])
#let admin to choose the what deparment and program to control
def studentcontrol(id,dep_name,prog_name,level):
    if session['id'] == id:
        result = sessionDB.execute(
            "SELECT * FROM student WHERE department_name = :dep_name and program_name = :prog_name and program_level = :level",
            {"dep_name": dep_name, "prog_name": prog_name, "level": level}).fetchall()


        if request.method == 'POST':
            name = request.form['name']
            gpa = request.form['gpa']
            age = request.form['age']
            address = request.form['address']
            email = request.form['email']
            gender = request.form['gender']
            phone = request.form['phone']
            secretcode = request.form['secretcode']
            if name =="" or age == "" or address =="" or gender ==""or phone =="" or secretcode =="":
                return render_template('student-control.html', result=result, alret=" * required field")
            else:

                sessionDB.execute("INSERT INTO student(name,program_name,department_name,email,age,gpa,address,phonenumber,sex,secretcode,program_level) VALUES(:name,:prog_name,:dep_name,:email,:age,:gpa,:address,:phone,:gender,:secretcode,:level)",{"name":name,"prog_name":prog_name,"dep_name":dep_name,"email":email,"age":age,"gpa":gpa,"address":address,"phone":phone,"gender":gender,"secretcode":secretcode,"level":level})
                sessionDB.commit()
                return redirect(url_for('studentcontrol',id=id,dep_name=dep_name,prog_name=prog_name,level=level))
        else:

            print(result)
            return render_template('student-control.html', result=result ,alret = "")

@app.route('/student_control_ajax',methods=['POST'])
def student_control_ajax():
    do =request.form['do']
    id =request.form['id']
    if do == "delete":
        sessionDB.execute("DELETE FROM student WHERE ID = :id",{"id":id})
        sessionDB.commit()
        return jsonify({"del":'sucess'})
    elif do == "edit":
        what =request.form['what']
        newinfo = request.form['newinfo']
        sessionDB.execute("UPDATE student SET "+what+" = :newinfo WHERE ID = :id",{"newinfo":newinfo,"id":id})
        sessionDB.commit()

@app.route('/admin/<int:id>/teachercontrol/<string:dep_name>/',methods=['POST','GET'])
def teachercontrol(id,dep_name):
    if session['id'] == id:
        result = sessionDB.execute(
            "SELECT * FROM teacher WHERE department_name = :dep_name ",{"dep_name": dep_name}).fetchall()
        if request.method == 'POST':
            name = request.form['name']
            age = request.form['age']
            address = request.form['address']
            gender = request.form['gender']
            program = request.form['program']
            secretcode = request.form['secretcode']
            if name =="" or age == "" or address =="" or gender ==""or program =="" or secretcode =="":
                return render_template('teacher-control.html', result=result, alret=" * required field")
            else:
                sessionDB.execute("INSERT INTO teacher(name,program_graduated,department_name,age,address,sex,secretcode) VALUES(:name,:program,:dep_name,:age,:address,:gender,:secretcode)",{"name":name,"program":program,"dep_name":dep_name,"age":age,"address":address,"gender":gender,"secretcode":secretcode})
                sessionDB.commit()
                return redirect(url_for('teachercontrol',id=id,dep_name=dep_name))
        else:

            print(result)
            return render_template('teacher-control.html', result=result ,alret = "")

@app.route('/teacher_control_ajax',methods=['POST'])
def teacher_control_ajax ():
    do =request.form['do']
    id =request.form['id']
    if do == "delete":
        sessionDB.execute("DELETE FROM teacher WHERE id = :id",{"id":id})
        sessionDB.commit()
        return jsonify({"del":'sucess'})
    elif do == "edit":
        what =request.form['what']
        newinfo = request.form['newinfo']
        sessionDB.execute("UPDATE teacher SET "+what+" = :newinfo WHERE id = :id",{"newinfo":newinfo,"id":id})
        sessionDB.commit()


@app.route('/admin/<int:id>/coursescontrol/<string:dep_name>/<string:prog_name>/<int:level>',methods=['POST','GET'])
def coursescontrol(id,dep_name,prog_name,level):
    if session['id'] == id:
        result = sessionDB.execute("SELECT * FROM course WHERE program_department_name = :dep_name and program_name = :prog_name and program_level = :level",{"dep_name": dep_name,"prog_name":prog_name ,"level":level}).fetchall()
        if request.method == 'POST':

            name = request.form['name']
            code = request.form['code']
            fullmark = request.form['full']
            passmark = request.form['pass']

            hours = request.form['hours']

            if name =="" or code == "" or fullmark =="" or passmark =="":
                return render_template('courses-control.html', result=result, alret=" * required field")
            else:
                sessionDB.execute("INSERT INTO course(code,name,full_mark,pass_mark,program_level,program_name,program_department_name,hours) VALUES(:code,:name,:fullmark,:passmark,:level,:prog_name,:dep_name,:hours)",{"code":code,"name":name,"fullmark":fullmark,"passmark":passmark,"level":level,"prog_name":prog_name,"dep_name":dep_name,"hours":hours})
                sessionDB.commit()
                return redirect(url_for('coursescontrol',id=id,dep_name=dep_name,prog_name=prog_name,level=level))
        else:

            print(result)
            return render_template('courses-control.html', result=result ,alret = "")

@app.route('/courses_control_ajax',methods=['POST'])
def courses_control_ajax ():
    do =request.form['do']
    code =request.form['id']
    if do == "delete":
        sessionDB.execute("DELETE FROM course WHERE code = :code",{"code":code})
        sessionDB.commit()
        return jsonify({"del":'sucess'})
    elif do == "edit":
        what =request.form['what']
        newinfo = request.form['newinfo']
        sessionDB.execute("UPDATE course SET "+what+" = :newinfo WHERE code = :code",{"newinfo":newinfo,"code":code})
        sessionDB.commit()


if __name__ == '__main__':
    app.secret_key = 'super_'
    app.debug = True
    app.run(host = '0.0.0.0',port=5000)
