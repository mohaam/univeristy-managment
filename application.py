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
            if result is None:
                return "wrong"
            else:
                session['id']=result.id
                return redirect(url_for('admin',id=result.id))

        if job == 'student':
            result =  sessionDB.execute("SELECT ID FROM student WHERE secretcode = :code",{"code":code}).fetchone()
            if result is None:
                return "wrong"
            else:
                pass

        if job == 'teacher':
            result = sessionDB.execute("SELECT id , name ,department_name, program_graduated FROM teacher WHERE secretcode = :code",{"code":code}).fetchone()

            if result is None:
                return "wrong"
            else:
                session['te_id'] = result.id
                return redirect(url_for('teacher',id=result.id,name=result.name,prog_name= result.program_graduated,dep_name = result.department_name))

    else:
        return render_template('index.html')

#admin workspace
@app.route('/admin/<int:id>/',methods=['POST','GET'])
#let admin choose the panel control he want testing debuging forget
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
            if who == "times":
                program = request.form ['program']
                level = request.form['level']

                result = sessionDB.execute("SELECT * FROM program WHERE name = :program and level = :level",{"program": program, "level": level}).fetchone()

                if result == []:
                    return "wrong"
                else:
                    return redirect(url_for('timescontrol', id=id, prog_name=program, level=level))
            if who == "department":
                return redirect(url_for('departmentcontrol',id=id))
        else:
            return render_template('adminpage.html', id=id)

@app.route('/admin/<int:id>/studentscontrol/<string:dep_name>/<string:prog_name>/<int:level>/',methods=['POST','GET'])

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
    table = request.form['table']
    if do == "delete":
        sessionDB.execute("DELETE FROM "+table+" WHERE ID = :id",{"id":id})
        sessionDB.commit()
        return jsonify({"del":'sucess'})
    elif do == "edit":
        what =request.form['what']
        newinfo = request.form['newinfo']
        sessionDB.execute("UPDATE "+table+" SET "+what+" = :newinfo WHERE ID = :id",{"newinfo":newinfo,"id":id})
        sessionDB.commit()

@app.route('/admin/<int:id>/teachercontrol/<string:dep_name>/',methods=['POST','GET'])
def teachercontrol(id,dep_name):
    if session['id'] == id:
        result = sessionDB.execute("SELECT * FROM teacher WHERE department_name = :dep_name ",{"dep_name": dep_name}).fetchall()
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


@app.route('/admin/<int:id>/coursescontrol/<string:dep_name>/<string:prog_name>/<int:level>',methods=['POST','GET'])
def coursescontrol(id,dep_name,prog_name,level):
    if session['id'] == id:
        result = sessionDB.execute("SELECT * FROM course WHERE program_department_name = :dep_name and program_name = :prog_name and program_level = :level",{"dep_name": dep_name,"prog_name":prog_name ,"level":level}).fetchall()
        if request.method == 'POST':

            name = request.form['name']
            code = request.form['code']
            fullmark = request.form['full']
            passmark = request.form['pass']
            optional = request.form['optional']
            hours = request.form['hours']

            if name =="" or code == "" or fullmark =="" or passmark =="" or optional == "":
                return render_template('courses-control.html', result=result, alret=" * required field")
            else:
                sessionDB.execute("INSERT INTO course(id,name,full_mark,pass_mark,program_level,program_name,program_department_name,hours,optional) VALUES(:code,:name,:fullmark,:passmark,:level,:prog_name,:dep_name,:hours,:optional)",{"code":code,"name":name,"fullmark":fullmark,"passmark":passmark,"level":level,"prog_name":prog_name,"dep_name":dep_name,"hours":hours,"optional":optional})
                sessionDB.commit()
                return redirect(url_for('coursescontrol',id=id,dep_name=dep_name,prog_name=prog_name,level=level))
        else:

            print(result)
            return render_template('courses-control.html', result=result ,alret = "")


@app.route('/admin/<int:id>/timescontrol/<string:prog_name>/<int:level>',methods=['POST','GET'])
def timescontrol(id,prog_name,level):
    if session['id'] == id:

        result = sessionDB.execute(
            "select sis.times.weekdays_day,sis.times.id,sis.times.course_id,sis.times.type,sis.course.name,sis.times.fromm,sis.times.too,sis.times.place from sis.times inner join sis.course on sis.course.id = sis.times.course_id where sis.times.course_program_name = :prog_name and sis.times.course_program_level = :level ORDER BY sis.times.weekdays_index ",{"prog_name": prog_name,"level": level}).fetchall()
        if request.method == 'POST':
            weekday = request.form.get('weekday')
            print(weekday)
            day =weekday[1:]
            index=weekday[0]
            coursecode = request.form['coursecode']
            print(coursecode)
            type = request.form['type']
            from1 = request.form['from']
            to = request.form['to']
            place =request.form['place']

            if weekday =="" or coursecode == "" or type =="" or from1 =="" or to =="" or place == "":
                return render_template('times-control.html', result=result, alret=" * required field")
            else:
                sessionDB.execute(
                    "INSERT INTO times (course_id,course_program_level,course_program_name,weekdays_day,weekdays_index,type,fromm,too,place) VALUES(:coursecode,:level,:prog_name,:day,:index,:type,:from1,:to,:place)",{"coursecode":coursecode,"level":level,"prog_name":prog_name,"day":day,"type":type,"from1":from1,"to":to,"index":index,"place":place})
                sessionDB.commit()
                return redirect(url_for('timescontrol',id=id,prog_name=prog_name, level=level))
        else:

            print(result)
            return render_template('times-control.html', result=result ,alret = "")

@app.route('/admin<int:id>/departmentcontrol/',methods=['POST','GET'])
def departmentcontrol(id):
    if session['id'] == id:
        result = sessionDB.execute('select * from department').fetchall()
        result1 = sessionDB.execute('select name , id from teacher').fetchall()
        if request.method == 'POST':
            dep_name = request.form['depname']
            sessionDB.execute('INSERT INTO department(name) VALUES(:dep_name)',{"dep_name":dep_name})
            sessionDB.commit()
            return redirect(url_for('departmentcontrol',id=id))
        else:
            return render_template('department-control.html',result1=result1,result=result)

@app.route('/department_ajax',methods=['POST'])
def department_ajax():
    dep_name=request.form['depname']
    what = request.form['what']
    newinfo = request.form['newinfo']
    print(dep_name)
    print(what)
    print(newinfo)
    sessionDB.execute("UPDATE department  SET " + what + " = :newinfo WHERE name = :dep_name", {"newinfo": newinfo, "dep_name": dep_name})
    sessionDB.commit()
# this is the end of admin

#teacher start form here

@app.route('/teacher/<int:id>/<string:name>/<string:prog_name>/<string:dep_name>',methods = ['POST','GET'])
def teacher(id,name,prog_name,dep_name):
    if session['te_id'] == id:
        result = sessionDB.execute("select sis.times.weekdays_index ,sis.times.weekdays_day, sis.times.course_id , sis.course.name,sis.times.fromm,sis.times.too,sis.times.place from sis.times inner join sis.teachercourses on sis.times.course_id = sis.teachercourses.course_code inner join sis.course on sis.course.id = sis.teachercourses.course_code where sis.teachercourses.teacher_id= :id and sis.times.type = 'lecture' ORDER BY sis.times.weekdays_index ",{"id":id}).fetchall()
        print(result)

        dep_manage = sessionDB.execute("select teacher_id from department where teacher_id = :id",{"id":id}).fetchone()
        prog_manage = sessionDB.execute("select program_manage from teacher where id = :id",{"id":id}).fetchone()

        print(dep_manage)
        print(prog_manage)
        if request.method == 'POST':
            coursecode=request.form['coursecode']
            type = request.form['type']

            if coursecode == "":
                return render_template('teacher-page.html', result=result, result1=None, result2=[],alret="* required field",prog_manage=prog_manage,dep_manage=dep_manage,dep_name=dep_name,id=id)

            result1 =sessionDB.execute(" select * from exam where course_code = :coursecode and teacher_id = :id and type = :type",{"coursecode":coursecode,"id":id,"type":type}).fetchone()
            result2 =sessionDB.execute(" select  sis.studentexam.student_ID,sis.studentexam.student_mark, sis.student.name from sis.studentexam inner join sis.student on sis.student.id = sis.studentexam.student_ID  where exam_course_code = :coursecode and exam_id = :id",{"coursecode":coursecode,"id":result1.id}).fetchall()
            print(result1)
            print(result2)

            return render_template('teacher-page.html',result = result,result1 =result1, result2 = result2,prog_manage=prog_manage,dep_manage=dep_manage,dep_name=dep_name,id=id)
        else:
            return render_template('teacher-page.html' , result=result ,result1=None,result2=[],alret="",prog_manage=prog_manage,dep_manage=dep_manage,dep_name=dep_name,id=id)

@app.route('/teacher_ajax',methods = ['POST'])
def teahcer_ajax():
    mark = request.form['mark']
    id = request.form['id']
    examid = request.form['examid']
    type = request.form['type']
    print(id)
    print(mark)
    sessionDB.execute("update studentexam set student_mark = :mark where student_ID = :id and exam_type = :type and exam_id = :examid",{"id":id,"mark":mark,"examid":examid,"type":type})
    sessionDB.commit()

    return jsonify({"insert":"sucsess"})

#end of teacher

# department manager start form here
@app.route('/deparment_manager/<int:id>/<string:dep_name>/',methods=['POST','GET'])
def dep_manager(id,dep_name):
    if session['te_id'] == id:
        teachers = sessionDB.execute('select name , id from teacher where department_name = :dep_name',{"dep_name":dep_name}).fetchall()
        programs = sessionDB.execute('select name from program where department_name = :dep_name and level = 1',{"dep_name":dep_name}).fetchall()
        print(teachers)
        print(programs)
        if request.method == 'POST':
            who = request.form['btn']
            if who == 'program':
                name= request.form['program']

                if name =="" :
                    return render_template('dep-manager.html', teachers=teachers, programs=programs,alret="* required field")
                for level in range(1,5):
                    sessionDB.execute('INSERT INTO program(name,department_name,level) VALUES(:name,:dep_name,:level)',{"name":name,"dep_name":dep_name,"level":level})
                sessionDB.commit()
                return redirect(url_for('dep_manager', id=id, dep_name=dep_name))
            if who == 'hour':
                program = request.form.get('program')
                hours = request.form['hours']
                level = request.form.get('level')
                sessionDB.execute("update program set hours = :hours where name = :program and level = :level " ,{"hours":hours,"level":level,"program":program})
                sessionDB.commit()
                return redirect(url_for('dep_manager',id=id,dep_name=dep_name))
            if who == 'manager':
                program = request.form.get('program')
                teacher = request.form.get('teacher')
                print(teacher)
                print(program)
                #check the last manager
                lastmanger= sessionDB.execute("select id from teacher where program_manage = :program",{"program":program}).fetchone()[0]
                print(lastmanger)
                if lastmanger is not None:
                    # remove the lastmanger
                    sessionDB.execute("update teacher set program_manage = ''  where id = :lastmanger ",{"lastmanger": lastmanger})
                    sessionDB.commit()

                    # add the new one

                    sessionDB.execute("update teacher set program_manage = :program where id = :teacher " ,{"teacher":teacher,"program":program})
                    sessionDB.commit()
                    return redirect(url_for('dep_manager',id=id,dep_name=dep_name))
                else:
                    sessionDB.execute("update teacher set program_manage = :program where id = :teacher " ,{"teacher":teacher,"program":program})
                    sessionDB.commit()
                    return redirect(url_for('dep_manager',id=id,dep_name=dep_name))

        else:
            return render_template('dep-manager.html',teachers=teachers,programs=programs,alret="")







if __name__ == '__main__':
    app.secret_key = 'super_'
    app.debug = True
    app.run(host = '0.0.0.0',port=5000)
