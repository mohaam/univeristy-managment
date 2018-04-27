from flask import Flask ,request,render_template,redirect,url_for,flash,session,jsonify
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

engine = create_engine('mysql+mysqlconnector://root:test@localhost:3306/sis')
sessionDB = Session(engine)


app = Flask(__name__)
@app.route('/',methods =['POST','GET'])
def index():
    if request.method == 'POST':
        code = request.form['id']
        if code == "":
            return render_template('index.html', alret="* required information")
        try:
            job = request.form['job']
        except :
            return render_template('index.html', alret="* required information")


        if job == 'admin':
            result = sessionDB.execute("SELECT id FROM admin WHERE secretcode = :code",{"code":code}).fetchone()
            print(result.id)
            if result is None:
                return "wrong"
            else:
                session['id']=result.id
                return redirect(url_for('admin',id=result.id))

        if job == 'student':
            result =  sessionDB.execute("SELECT * FROM student WHERE secretcode = :code",{"code":code}).fetchone()
            if result is None:
                return "wrong"
            else:
                session['student_id'] = result.ID
                return redirect(url_for('student', id=result.ID))

        if job == 'teacher':
            result = sessionDB.execute("SELECT id , name ,department_name, program_graduated FROM teacher WHERE secretcode = :code",{"code":code}).fetchone()

            if result is None:
                return "wrong"
            else:
                session['te_id'] = result.id
                return redirect(url_for('teacher',id=result.id,name=result.name,prog_name= result.program_graduated,dep_name = result.department_name))

    else:
        return render_template('index.html',alret="")

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

                # test the input doesn`t empty

                if deparment == "" or program == "" or level == "":
                    return render_template('adminpage.html',alretst="* required information",id=id,notexist="")

                # testing that the inputs are already exists
                result = sessionDB.execute(
                    "SELECT * FROM program WHERE department_name = :deparment and name = :program and level = :level",
                    {"deparment": deparment, "program": program, "level": level}).fetchone()

                print(result)
                if result == None:
                    # that`s means not exists
                    return render_template('adminpage.html', notexist="* the program or the department not exist",
                                           id=id,alretst="")
                else:
                    return redirect(url_for('studentcontrol',id=id,dep_name=deparment,prog_name=program,level=level))

                ################################ teachers get ########################################
            if who =="teacher":
                deparment = request.form['deparment']

                if deparment == "":
                    return  render_template('adminpage.html',id=id,alrette="* required information")
                result = sessionDB.execute("SELECT * FROM department WHERE name = :deparment",
                                           {"deparment": deparment}).fetchone()
                if result == None:
                    # not exist
                    return render_template('adminpage.html', id=id, alrette="* department not exist")
                else:
                    return redirect(url_for('teachercontrol',id=id,dep_name=deparment))

                ################################# courses get #######################################
            if who == "courses":
                deparment = request.form['deparment']
                program = request.form['program']
                level = request.form['level']

                if deparment =="" or program =="" or level =="":
                    return render_template('adminpage.html',id=id,alretco = "* required information")

                result = sessionDB.execute(
                    "SELECT * FROM program WHERE department_name = :deparment and name = :program and level = :level",
                    {"deparment": deparment, "program": program, "level": level}).fetchone()

                print(result)
                if result == None:
                    # worng information
                    return render_template('adminpage.html', id=id, notexistco="* department or program may "
                                                                               "be not exist")
                else:
                    return redirect(url_for('coursescontrol', id=id, dep_name=deparment, prog_name=program, level=level))
            if who == "times":
                program = request.form ['program']
                level = request.form['level']
                if program == "" or level == "":
                    return  render_template('adminpage.html',id=id,alretti="* required information")

                result = sessionDB.execute("SELECT * FROM program WHERE name = :program and level = :level",
                                           {"program": program, "level": level}).fetchone()

                if result is None:
                    return render_template('adminpage.html', id=id, notexistti="*  program is not exist ")
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
            "SELECT * FROM student WHERE department_name = :dep_name and program_name = :prog_name and program_level = "
            ":level",
            {"dep_name": dep_name, "prog_name": prog_name, "level": level}).fetchall()

        states = sessionDB.execute("select * from states where program_level = :level and program_name = :prog_name ",
                                   {"prog_name":prog_name,"level":level}).fetchone()
        print(states)

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
                return render_template('student-control.html', result=result, alret=" * required field",
                                       dep_name=dep_name,id=id,prog_name=prog_name,level=level,states=states)
            else:
                try:
                    sessionDB.execute("INSERT INTO student(name,program_name,department_name,email,age,gpa,address,"
                                      "phonenumber,sex,secretcode,program_level) "
                                      "VALUES(:name,:prog_name,:dep_name,:email,:age,:gpa,:address,:phone,:gender,"
                                      ":secretcode,:level)",
                                      {"name":name,"prog_name":prog_name,"dep_name":dep_name,"email":email,"age":age,
                                       "gpa":gpa,"address":address,"phone":phone,"gender":gender,"secretcode":secretcode,
                                       "level":level})
                    sessionDB.commit()
                except:
                    return render_template('student-control.html', result=result, alretdb=" * enter valid data",
                                           dep_name=dep_name,prog_name=prog_name,level=level,id=id,states=states)

                return redirect(url_for('studentcontrol', id=id, dep_name=dep_name, prog_name=prog_name, level=level))
        else:

            print(result)
            return render_template('student-control.html', result=result ,alret = "",
                                   dep_name=dep_name,prog_name=prog_name,level=level,id=id,states=states)

@app.route('/student_control_ajax',methods=['POST'])
def student_control_ajax():
    do =request.form['do']
    id =request.form['id']
    table = request.form['table']
    if do == "delete":
        try:
            sessionDB.execute("DELETE FROM "+table+" WHERE ID = :id",{"id":id})
            sessionDB.commit()

        except:
            return jsonify({"del": 'failed'})
        return jsonify({"del": 'sucess'})
    elif do == "edit":
        try:
            what =request.form['what']
            newinfo = request.form['newinfo']
            sessionDB.execute("UPDATE "+table+" SET "+what+" = :newinfo WHERE ID = :id",{"newinfo":newinfo,"id":id})
            sessionDB.commit()
        except:
            return jsonify({"update": 'failed'})
        return jsonify({"update": 'sucess'})


@app.route('/admin/<int:id>/teachercontrol/<string:dep_name>/',methods=['POST','GET'])
def teachercontrol(id,dep_name):
    if session['id'] == id:
        result = sessionDB.execute("SELECT * FROM teacher WHERE department_name = :dep_name ",
                                   {"dep_name": dep_name}).fetchall()
        if request.method == 'POST':
            name = request.form['name']
            age = request.form['age']
            address = request.form['address']
            gender = request.form['gender']
            program = request.form['program']
            secretcode = request.form['secretcode']
            if name =="" or age == "" or address =="" or gender ==""or program =="" or secretcode =="":
                return render_template('teacher-control.html', result=result, alret=" * required field",
                                       id=id,dep_name=dep_name)
            else:
                try:
                    sessionDB.execute("INSERT INTO teacher(name,program_graduated,department_name,age,address,sex,"
                                      "secretcode) VALUES(:name,:program,:dep_name,:age,:address,:gender,:secretcode)",
                                      {"name":name,"program":program,"dep_name":dep_name,"age":age,"address":address,
                                       "gender":gender,"secretcode":secretcode})
                    sessionDB.commit()

                except:
                    return render_template('teacher-control.html', result=result, alretdb=" * enter valid data", id=id,
                                           dep_name=dep_name)

                return redirect(url_for('teachercontrol', id=id, dep_name=dep_name))

        else:

            print(result)
            return render_template('teacher-control.html', result=result , alret = "", id=id, dep_name=dep_name)


@app.route('/admin/<int:id>/coursescontrol/<string:dep_name>/<string:prog_name>/<int:level>',methods=['POST','GET'])
def coursescontrol(id,dep_name,prog_name,level):
    if session['id'] == id:
        result = sessionDB.execute("SELECT * FROM course WHERE program_department_name = :dep_name and program_name = "
                                   ":prog_name and program_level = :level",
                                   {"dep_name": dep_name,"prog_name":prog_name ,"level":level}).fetchall()



        if request.method == 'POST':

            name = request.form['name']
            code = request.form['code']
            fullmark = request.form['full']
            passmark = request.form['pass']
            optional = request.form['optional']
            hours = request.form['hours']
            term = request.form["term"]




            if name =="" or code == "" or fullmark =="" or passmark =="" or optional == "" or term == "":
                return render_template('courses-control.html', result=result, alret=" * required field",
                                       id=id,dep_name=dep_name,prog_name=prog_name,level=level)
            else:
                try:
                    sessionDB.execute("INSERT INTO course(id,name,full_mark,pass_mark,program_level,program_name,"
                                      "program_department_name,hours,optional,term) "
                                      "VALUES(:code,:name,:fullmark,:passmark,"
                                      ":level,:prog_name,:dep_name,:hours,:optional,:term)",{"code":code,"term":term,
                                                                                             "name":name
                                     ,"fullmark":fullmark,"passmark":passmark,"level":level,"prog_name":prog_name
                                    ,"dep_name":dep_name,"hours":hours,"optional":optional})

                    sessionDB.commit()
                except:
                    return render_template('courses-control.html', result=result, alretdb=" * enter valid data",
                                           id=id, dep_name=dep_name, prog_name=prog_name, level=level)

                return redirect(url_for('coursescontrol',id=id,dep_name=dep_name,prog_name=prog_name,level=level))
        else:

            print(result)
            return render_template('courses-control.html', result=result ,alret = "",
                                   id=id,dep_name=dep_name,prog_name=prog_name,level=level)


@app.route('/admin/<int:id>/timescontrol/<string:prog_name>/<int:level>',methods=['POST','GET'])
def timescontrol(id,prog_name,level):
    if session['id'] == id:

        result = sessionDB.execute(
            "select sis.times.weekdays_day,sis.times.id,sis.times.course_id,sis.times.type,sis.course.name,"
            "sis.times.fromm,sis.times.too,sis.times.place from sis.times inner join "
            "sis.course on sis.course.id = sis.times.course_id where sis.times.course_program_name = :prog_name "
            "and sis.times.course_program_level = :level ORDER BY sis.times.weekdays_index ",
            {"prog_name": prog_name,"level": level}).fetchall()

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
                return render_template('times-control.html', result=result, alret=" * required field",
                                       prog_name=prog_name,level=level,id=id)
            else:
                try:

                    sessionDB.execute("INSERT INTO times (course_id,course_program_level,course_program_name,weekdays_day,weekdays_index,type,fromm,too,place) VALUES (:coursecode,:level,:prog_name,:day,:index,:type,:from1,:to,:place)",{"coursecode":coursecode,"level":level,"prog_name":prog_name,"day":day,"type":type,"from1":from1,"to":to,"index":index,"place":place})

                    sessionDB.commit()
                except:
                    return render_template('times-control.html', result=result, alretdb=" * enter valid data",
                                       prog_name=prog_name, level=level,id=id)

                return redirect(url_for('timescontrol',id=id,prog_name=prog_name, level=level))
        else:

            print(result)
            return render_template('times-control.html', result=result ,alret = "",prog_name=prog_name, level=level,id=id)

@app.route('/admin/<int:id>/departmentcontrol/',methods=['POST','GET'])
def departmentcontrol(id):
    if session['id'] == id:
        result = sessionDB.execute('select * from department').fetchall()
        result1 = sessionDB.execute('select * from teacher').fetchall()
        if request.method == 'POST':
            dep_name = request.form['depname']
            if dep_name == "":
                return render_template('department-control.html', result1=result1, result=result,
                                       alret = "* required field",id=id)
            sessionDB.execute('INSERT INTO department(name) VALUES(:dep_name)',{"dep_name":dep_name})
            sessionDB.commit()
            return redirect(url_for('departmentcontrol',id=id))
        else:
            return render_template('department-control.html',result1=result1,result=result,id=id)

@app.route('/department_ajax',methods=['POST'])
def department_ajax():
    dep_name = request.form['depname']
    what = request.form['what']
    newinfo = request.form['newinfo']
    print(dep_name)
    print(what)
    print(newinfo)
    try:
        sessionDB.execute("UPDATE department  SET " + what + " = :newinfo WHERE name = :dep_name",
                          {"newinfo": newinfo, "dep_name": dep_name})
        sessionDB.commit()
    except:
        return  jsonify({"update":"failed"})
    return jsonify({"update": "sucess"})

# this is the end of admin

#teacher start form here

@app.route('/teacher/<int:id>/<string:name>/<string:prog_name>/<string:dep_name>',methods = ['POST','GET'])
def teacher(id,name,prog_name,dep_name):
    if session['te_id'] == id:
        result = sessionDB.execute("select sis.times.weekdays_index ,sis.times.weekdays_day, sis.times.course_id , "
                                   "sis.course.name,sis.times.fromm,sis.times.too,sis.times.place from sis.times inner "
                                   "join sis.teachercourses on sis.times.course_id = sis.teachercourses.course_code "
                                   "inner join sis.course on sis.course.id = sis.teachercourses.course_code "
                                   "where sis.teachercourses.teacher_id= :id and sis.times.type = 'lecture' "
                                   "ORDER BY sis.times.weekdays_index ",{"id":id}).fetchall()
        print(result)

        dep_manage = sessionDB.execute("select teacher_id from department where teacher_id = :id",{"id":id}).fetchone()
        prog_manage = sessionDB.execute("select program_manage from teacher where id = :id",{"id":id}).fetchone()

        print(dep_manage)
        print(prog_manage)
        if request.method == 'POST':
            coursecode=request.form['coursecode']
            type = request.form['type']

            if coursecode == "" or type == "":
                return render_template('teacher-page.html', result=result, result1=None, result2=[],
                                       alret="* required field",prog_manage=prog_manage
                                       ,dep_manage=dep_manage,dep_name=dep_name,id=id,name=name,prog_name=prog_name)

            try:

                result1 =sessionDB.execute(" select * from exam where course_code = :coursecode and teacher_id = :id"
                                           " and type = :type"
                                           ,{"coursecode":coursecode,"id":id,"type":type}).fetchone()

                result2 =sessionDB.execute(" select  sis.studentexam.student_ID,sis.studentexam.student_mark, "
                                           "sis.student.name "
                                           "from sis.studentexam inner join sis.student on "
                                           "sis.student.id = sis.studentexam.student_ID  "
                                           "where exam_course_code = :coursecode and exam_id = :id",
                                           {"coursecode":coursecode,"id":result1.id}).fetchall()
            except:
                return render_template('teacher-page.html', result=result, result1=None, result2=[],
                                       alretdb="* enter valid data", prog_manage=prog_manage
                                       , dep_manage=dep_manage, dep_name=dep_name, id=id, name=name,
                                       prog_name=prog_name)

            print(result1)
            print(result2)

            return render_template('teacher-page.html',result = result,result1 =result1, result2 = result2
                                   ,prog_manage=prog_manage,dep_manage=dep_manage,dep_name=dep_name,id=id
                                   ,name=name,prog_name=prog_name)
        else:
            return render_template('teacher-page.html' , result=result ,result1=None,result2=[],alret=""
                                   ,prog_manage=prog_manage,dep_manage=dep_manage,
                                   dep_name=dep_name,id=id,name=name,prog_name=prog_name)

@app.route('/teacher_ajax',methods = ['POST'])
def teahcer_ajax():
    mark = request.form['mark']
    id = request.form['id']
    examid = request.form['examid']
    type = request.form['type']
    print(id)
    print(mark)
    try:
        sessionDB.execute("update studentexam set student_mark = :mark where student_ID = :id and exam_type = :type and"
                          " exam_id = :examid",{"id":id,"mark":mark,"examid":examid,"type":type})
        sessionDB.commit()
    except:
        return jsonify({"insert": "failed"})

    return jsonify({"insert":"sucsess"})

#end of teacher

# department manager start form here
@app.route('/deparment_manager/<int:id>/<string:teachername>/<string:dep_name>/<string:prog_name>/',methods=['POST','GET'])
def dep_manager(id,dep_name,teachername,prog_name):
    if session['te_id'] == id:
        teachers = sessionDB.execute('select name , id from teacher where department_name = :dep_name',
                                     {"dep_name":dep_name}).fetchall()
        programs = sessionDB.execute('select name from program where department_name = :dep_name and level = 1',
                                     {"dep_name":dep_name}).fetchall()
        print(teachers)
        print(programs)
        if request.method == 'POST':
            who = request.form['btn']
            if who == 'program':
                name = request.form['program']

                if type(name) != str :
                    return render_template('dep-manager.html', teachers=teachers, programs=programs,
                                           alret="* enter valid data",teachername=teachername,id=id,prog_name=prog_name,
                                           dep_name=dep_name)
                if name == "" :
                    return render_template('dep-manager.html', teachers=teachers, programs=programs,
                                           alret="* required field",teachername=teachername,id=id,prog_name=prog_name,
                                           dep_name=dep_name)
                for level in range(1,5):

                    sessionDB.execute('INSERT INTO program(name,department_name,level) VALUES(:name,:dep_name,:level)',
                                        {"name":name,"dep_name":dep_name,"level":level})

                    sessionDB.execute('INSERT INTO states (program_level,program_name) VALUES(:level,:name)',
                                        {"name":name,"level":level})


                sessionDB.commit()
                return redirect(url_for('dep_manager', id=id, dep_name=dep_name,teachername=teachername,
                                        prog_name=prog_name))
            if who == 'hour':
                program = request.form.get('program')
                hours = request.form['hours']
                level = request.form.get('level')

                if hours == "":
                    return render_template('dep-manager.html', teachers=teachers, programs=programs,
                                           alrethour="* required field", teachername=teachername, id=id,
                                           prog_name=prog_name,
                                           dep_name=dep_name)

                try:
                    sessionDB.execute("update program set hours = :hours where name = :program and level = :level " ,
                                      {"hours":hours,"level":level,"program":program})
                    sessionDB.commit()
                except:
                    return render_template('dep-manager.html', teachers=teachers, programs=programs,
                                           alrethour="* enter valid data", teachername=teachername, id=id,
                                           prog_name=prog_name,
                                           dep_name=dep_name)

                return redirect(url_for('dep_manager', id=id, dep_name=dep_name, teachername=teachername,
                                        prog_name=prog_name))
            if who == 'manager':
                program = request.form.get('program')
                teacher = request.form.get('teacher')
                print(teacher)
                print(program)
                #check the last manager
                lastmanger= sessionDB.execute("select id from teacher where program_manage = :program",
                                              {"program":program}).fetchone()
                print(lastmanger)
                if lastmanger is not None:
                    # remove the lastmanger
                    sessionDB.execute("update teacher set program_manage = '-'  where id = :lastmanger ",
                                      {"lastmanger": lastmanger[0]})
                    sessionDB.commit()

                    # add the new one

                    sessionDB.execute("update teacher set program_manage = :program where id = :teacher " ,
                                      {"teacher":teacher,"program":program})
                    sessionDB.commit()
                    return redirect(url_for('dep_manager', id=id, dep_name=dep_name, teachername=teachername,
                                            prog_name=prog_name))
                else:
                    sessionDB.execute("update teacher set program_manage = :program where id = :teacher " ,
                                      {"teacher":teacher,"program":program})
                    sessionDB.commit()
                    return redirect(url_for('dep_manager', id=id, dep_name=dep_name, teachername=teachername,
                                            prog_name=prog_name))

        else:
            return render_template('dep-manager.html',teachers=teachers,programs=programs,
                                   alret="",teachername=teachername,id=id,prog_name=prog_name,dep_name=dep_name)

#end of dep manager

#program manager startes from here

@app.route('/program_manager/<int:id>/<string:teachername>/<string:dep_name>/<string:prog_name>/',methods=['POST','GET'])
def prog_manager(id,prog_name,dep_name,teachername):
    if session['te_id'] == id:
        exams_table = sessionDB.execute('select sis.teacher.name,sis.course.name,sis.exam.id , sis.exam.type ,'
                                        'sis.exam.full_mark ,sis.exam.passing_mark, '
                                        'sis.exam.course_code,sis.exam.teacher_id  '
                                        'from sis.exam inner join sis.course on sis.course.id = sis.exam.course_code '
                                        'inner join sis.teacher on sis.teacher.id =sis.exam.teacher_id  '
                                        'where sis.course.program_name = :prog_name order by sis.exam.id',
                                        {'prog_name':prog_name}).fetchall()
        print(exams_table)
        courses = sessionDB.execute('select id , name from course where program_name = :prog_name',
                                    {"prog_name":prog_name}).fetchall()

        teachers = sessionDB.execute('select name , id from teacher').fetchall()

        teacherscourses = sessionDB.execute('select sis.teachercourses.id, sis.teacher.name ,sis.course.name, '
                                            'sis.teachercourses.teacher_id , sis.teachercourses.course_code from '
                                            'sis.teachercourses inner join sis.course on sis.course.id = '
                                            'sis.teachercourses.course_code inner join sis.teacher on '
                                            'sis.teachercourses.teacher_id=sis.teacher.id '
                                            'where sis.course.program_name= :prog_name',
                                            {"prog_name":prog_name}).fetchall()

        print(teacherscourses)

        if request.method == 'POST':
            who = request.form['btn']
            if who == "teacher":
                course = request.form.get('courses')
                teacher = request.form.get('teacher')

                # check if already exist
                flag = sessionDB.execute('select teacher_id  from teachercourses '
                                         'where course_code = :course and teacher_id = :teacher',
                                         {"course": course, "teacher": teacher}).fetchone()

                if flag == None:
                    sessionDB.execute('INSERT INTO teachercourses(course_code,teacher_id) VALUES(:course,:teacher)',
                                      {"course":course,"teacher":teacher})
                    sessionDB.commit()
                    return redirect(url_for('prog_manager', id=id, prog_name=prog_name, dep_name=dep_name,
                                            teachername=teachername))
                else:
                    return render_template('prog-manager.html', exams_table=exams_table, courses=courses,
                                           teachers=teachers, teacherscourses=teacherscourses, dep_name=dep_name,
                                           prog_name=prog_name, id=id, teachername=teachername ,
                                           alret="* is already exist")
            if who=="exam":
                type=request.form['type']
                course = request.form.get('course')
                teacher = request.form.get('teacher')
                full = request.form['full']
                pas =request.form['pass']
                examcode = request.form['examcode']

                #check if exam already exist
                flag= sessionDB.execute("select teacher_id from exam where course_code = :course and "
                                        "teacher_id = :teacher",{"course":course,"teacher":teacher}).fetchone()

                if flag is not None:
                    return render_template('prog-manager.html', exams_table=exams_table, courses=courses,
                                           teachers=teachers, teacherscourses=teacherscourses, dep_name=dep_name,
                                           prog_name=prog_name, id=id, teachername=teachername,
                                           alretexam="* is already exist")


                #putting the exam
                studentenrol = sessionDB.execute("SELECT sis.studentcourses.student_ID FROM sis.studentcourses "
                                                 "where course_code = :course", {"course": course}).fetchall()
                if studentenrol == []:
                    return render_template('prog-manager.html', exams_table=exams_table, courses=courses,
                                           teachers=teachers, teacherscourses=teacherscourses, dep_name=dep_name,
                                           prog_name=prog_name, id=id, teachername=teachername,
                                           alretstudent="* no students enrol in that course")

                try:
                    sessionDB.execute("INSERT INTO exam(id,type,full_mark,passing_mark,course_code,teacher_id) "
                                      "VALUES(:examcode,:type,:full,:pas,:course,:teacher)",
                                      {"examcode":examcode,"type":type,"full":full,"pas":pas,"course":course,
                                       "teacher":teacher})
                except:
                    return render_template('prog-manager.html', exams_table=exams_table, courses=courses,
                                           teachers=teachers, teacherscourses=teacherscourses, dep_name=dep_name,
                                           prog_name=prog_name, id=id, teachername=teachername ,
                                           dbalret="enter valid data")


                #putting the examlist



                print(studentenrol)
                for student in studentenrol:
                    sessionDB.execute('INSERT INTO studentexam(student_ID,exam_id,exam_type,exam_course_code) '
                                      'VALUES(:student,:examcode,:type,:course)',
                                  {"student": student.student_ID,"examcode":examcode,"type":type,"course": course})
                sessionDB.commit()
                return redirect(url_for('prog_manager', id=id, prog_name=prog_name,dep_name=dep_name,
                                        teachername=teachername))
        else:
           return render_template('prog-manager.html',exams_table=exams_table,courses=courses,
                                  teachers=teachers,teacherscourses=teacherscourses,dep_name=dep_name,
                                  prog_name=prog_name,id=id,teachername=teachername)


@app.route('/program_manager_ajax',methods=['POST'])
def program_manager_ajax():

    table = request.form['table']
    do = request.form['do']
    id = request.form['id']

    if do == 'edit':
        col = request.form['col']
        newinfo = request.form['newinfo']
        try:
            sessionDB.execute("UPDATE "+table+" SET "+col+" = :newinfo WHERE id = :id",{"newinfo":newinfo,"id":id})
            sessionDB.commit()
        except:

            return jsonify({"edit": 0})

        return jsonify({"edit": 1})
    else:
        try:
            sessionDB.execute("DELETE FROM "+table+" WHERE ID = :id", {"id":id})
            sessionDB.commit()
        except:
            return jsonify({"delete": 0})

        return jsonify({"delete": 1})



@app.route('/logout')
def logout():
    if 'id' in session:
        session.pop('id', None)
        return redirect(url_for('index'))
    if 'te_id' in session:
        session.pop('id', None)
        return redirect(url_for('index'))


#end of program manager

@app.route('/states', methods=['POST'])
def states():

    state = int(request.form['state'])
    what = request.form['what']
    prog = request.form['prog']
    level = request.form['level']

    print(state)
    print(what)
    print(prog)
    print(level)
    sessionDB.execute("UPDATE states SET " + what + " =:state WHERE program_level = :level and program_name = :prog ",
                          {"state": state, "level": level,"prog":prog})
    sessionDB.commit()

##### begin of student ######

@app.route('/student/<int:id>/', methods=['POST', 'GET'])
def student(id):
    if session['student_id'] == id:
        get_term = sessionDB.execute("select term from states where program_level = 1").fetchone()
        term = int(get_term.term)


        result_score = sessionDB.execute("select exam_course_code, exam_type, sum(student_mark) as total from "
                                         "studentexam where student_ID = :id group by exam_course_code, exam_type",
                                         {"id": id}).fetchall()
        # TODO: add the grade
        result_final = sessionDB.execute("select studentexam.exam_course_code, sum(studentexam.student_mark) as total, "
                                         "studentcourses.grade from studentexam inner join studentcourses on "
                                         "studentexam.exam_course_code = studentcourses.course_code and "
                                         "studentcourses.student_ID=:id group by studentcourses.course_code",
                                        {"id": id}).fetchall()

        result_summer = sessionDB.execute("select course.name, course.hours, studentcourses.course_code from course "
                                          "inner join studentcourses on course.id = studentcourses.course_code and "
                                          "studentcourses.pass = 0 and studentcourses.student_ID = :id",
                                          {"id": id}).fetchall()

        result_subject = sessionDB.execute("select distinct course.id, course.name, course.hours,"
                                           " course.optional, student.program_level from course inner "
                                           "join student on student.program_level = course.program_level "
                                           "and student.ID = :id and course.term =:term",
                                           {"id": id, "term": term}).fetchall()

        student_level = sessionDB.execute("select program_level from student where ID = :id", {"id": id}).fetchone()
        student_level = int(student_level[0])
        # TODO GET the hours variable
        result_subject_test = subject_calc(result_subject, term, student_level, id)
        hours = hours_calc(result_final=result_final, id=id)
        gpa = GPA(id)
        gpa_acc = sessionDB.execute("select hours, qp from student where ID=:id", {"id": id}).fetchone()
        temp = float(gpa_acc.qp)/float(gpa_acc.hours)
        sessionDB.execute("update student set gpa=:gpa, cumulative_gpa=:temp where ID=:id",
                          {"gpa": gpa, "temp": temp, "id": id})
        sessionDB.commit()
        # TODO : The result info
        result_info = sessionDB.execute("select * from student where id = :id",{"id":id}).fetchall()

        studentcourses = sessionDB.execute("select * from studentcourses where student_ID = :id",{"id":id}).fetchall()

        program = sessionDB.execute("select program_name from student where ID = :id ",{"id":id}).fetchone()
        result = sessionDB.execute(
            "select sis.times.weekdays_day,sis.times.id,sis.times.course_id,sis.times.type,sis.course.name,"
            "sis.times.fromm,sis.times.too,sis.times.place from sis.times inner join "
            "sis.course on sis.course.id = sis.times.course_id where sis.times.course_program_name = :prog_name "
            "and sis.times.course_program_level = :level ORDER BY sis.times.weekdays_index ",
            {"prog_name": program[0], "level": student_level}).fetchall()
        # TODO: make the buttons go voom
        states = sessionDB.execute("select * from states where program_level = :student_level and "
                                   "program_name = :program",{"student_level":student_level,"program":program[0]}).fetchone()

        if request.method == 'POST':
            who = request.form['btn']
            if who == 'register':
                value = request.form.getlist('check')
                if value:
                    sessionDB.execute("delete from studentcourses where student_ID=:id", {"id": id})
                    for element in value:
                        # default value for pass equal zero to facilitate giving_f() funtion
                        sessionDB.execute("insert into studentcourses (student_ID, course_code, pass) "
                                          "values (:id, :code, NULL)", {"id": id, "code": element})
                    sessionDB.commit()
                    return render_template('thanks.html')
                else:
                    return render_template(url_for('student', id=id))
            if who == 'summer':
                value = request.form.getlist('check2')
                if value:
                    test = 0
                    for element in value:
                        temp = sessionDB.execute("select hours from course where id=:code",
                                                 {"code": element}).fetchone()
                        test += int(temp.hours)
                    if test <= 6:
                        for element in value:
                            sessionDB.execute("update studentcourses set summer = 1 where student_ID = :id and "
                                              "course_code = :code", {"id": id, "code": element})

                        sessionDB.commit()
                        return render_template('thanks.html')
                    else:
                        return render_template('studentpage.html', subjects=result_subject_test, summer=result_summer,
                                               final=result_final, score=result_score, id=id, alret="* 6 hours only",
                                               states=states)
                else:
                    return render_template('studentpage.html', subjects=result_subject_test, summer=result_summer,
                                           final=result_final, score=result_score, id=id, alret="* Choose subjects",
                                           states=states)
            if who == 'drop':
                value = request.form['code']
                if value:
                    exist = sessionDB.execute("select course_code from studentcourses where student_ID=:id and "
                                              "course_code=:value", {"id": id, "value": value}).fetchone()
                    if exist:
                        sessionDB.execute("delete from studentcourses where student_ID=:id and course_code=:value",
                                          {"id": id, "value": value})
                        sessionDB.commit()
                        return render_template('Drop.html')
                    else:
                        return render_template('fail.html')
                else:
                    return redirect(url_for('student', id=id))
        else:
            # add result info to the code
            return render_template('studentpage.html', subjects=result_subject_test, summer=result_summer,
                                   final=result_final, score=result_score, id=id, result_info=result_info,
                                   studentcourses=studentcourses, result=result, states=states)


def subject_calc(result_subjects, term, student_level, id):
    main_subject = []
    added_subject = []
    result_subjects_rtn = []
    hours = 0
    if student_level == 1 and term == 1:
        return result_subjects
    else:
        dependent_subjects = []

        test_subjects = sessionDB.execute("select * from course_has_course where course_program_level = :level",
                                          {"level": student_level}).fetchall()

        check_passage = sessionDB.execute("select course_code from studentcourses where pass = 0 and student_ID = :id",
                                          {"id": id}).fetchall()
        # We got a list of available subjects
        for subject in test_subjects:
            temp = subject.course_id1
            main_subject.append(subject.course_id)
            dependent_subjects.append(temp)
            if check_passage:
                for subject1 in check_passage:
                    if subject1.course_code in dependent_subjects:
                        main_subject.remove(subject.course_id)

        for subject in result_subjects:
            if subject.id in main_subject:
                continue
                hours += subject.hours
            else:
                result_subjects_rtn.append(subject)

        if hours >= 12:
            return result_subjects_rtn
        if hours < 12:
            temp = sessionDB.execute("select course_has_course.course_id, course.hours from course_has_course inner join "
                                     "course where course_has_course.course_id = course.id and "
                                     "course_has_course.course_program_level=:level and course_id1 is NULL",
                                     {"level": student_level + 1}).fetchall()

            for subject in temp:
                added_subject.append(subject.course_id)
                hours += int(subject.hours)
                if hours >= 12:
                    break
                else:
                    continue
        if added_subject:
            for course in added_subject:
                result = sessionDB.execute("select id, name, hours, optional from course where program_level=:level and"
                                           " term=:term and id=:id", {"level": student_level + 1, "term": term, "id":
                                                                      course}).fetchone()
                result_subjects_rtn.append(result)
            return result_subjects_rtn
        else:
            return result_subjects_rtn


# This function calculates student hours, decides if he passes a subject and change a level
def hours_calc(result_final, id):
    # calculating number of hours in the new subjects
    hours_added = 0
    new_hours = 0
    for subject in result_final:
        try:
            temp = sessionDB.execute("select pass_mark, hours from course where id=:id",
                                 {"id": subject.exam_course_code}).fetchone()
        except:
            pass
        if subject.total >= int(temp.pass_mark):
            grade_calc(int(subject.total), int(temp.hours), subject.exam_course_code, id)  # This function calculates grade Type
            sessionDB.execute("update studentcourses set pass = 1 where student_ID=:id and course_code=:code",
                              {"id": id, "code": subject.exam_course_code})
            hours_added += int(temp.hours)
        else:
            sessionDB.execute("update studentcourses set pass = 0 where student_ID=:id and course_code=:code",
                              {"id": id, "code": subject.exam_course_code})
    sessionDB.commit()
    cur_hours = sessionDB.execute("select hours from student where ID=:id", {"id": id}).fetchone()
    if cur_hours:
        new_hours = int(cur_hours.hours) + hours_added
    else:
        new_hours = hours_added
    sessionDB.execute("update student set hours=:hours where ID=:id",
                      {"hours": new_hours, "id": id})
    sessionDB.commit()
    if new_hours < 33:
        sessionDB.execute("update student set program_level = 1 where ID=:id", {"id": id})
    elif 33 <= new_hours < 67:
        sessionDB.execute("update student set program_level = 2 where ID=:id", {"id": id})
    elif 67 <= new_hours < 100:
        sessionDB.execute("update student set program_level = 3 where ID=:id", {"id": id})
    elif new_hours >= 100:
        sessionDB.execute("update student set program_level = 4 where ID=:id", {"id": id})

    sessionDB.commit()
    giving_f(id) # This function gives the grade F to the failed subjects
    return new_hours


def grade_calc(grade, hours, course_code, id):
    if hours == 1:
        percentage = (grade * 100)/50
        if 60 <= percentage < 65:
            sessionDB.execute("update studentcourses set grade='D' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 65 <= percentage < 70:
            sessionDB.execute("update studentcourses set grade='C' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 70 <= percentage < 75:
            sessionDB.execute("update studentcourses set grade='C+' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 75 <= percentage < 80:
            sessionDB.execute("update studentcourses set grade='B' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 80 <= percentage < 85:
            sessionDB.execute("update studentcourses set grade='B+' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 85 <= percentage < 90:
            sessionDB.execute("update studentcourses set grade='A-' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif percentage >= 90:
            sessionDB.execute("update studentcourses set grade='A' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
    elif hours == 2:
        percentage = (grade * 100)/100
        if 60 <= percentage < 65:
            sessionDB.execute("update studentcourses set grade='D' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 65 <= percentage < 70:
            sessionDB.execute("update studentcourses set grade='C' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 70 <= percentage < 75:
            sessionDB.execute("update studentcourses set grade='C+' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 75 <= percentage < 80:
            sessionDB.execute("update studentcourses set grade='B' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 80 <= percentage < 85:
            sessionDB.execute("update studentcourses set grade='B+' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 85 <= percentage < 90:
            sessionDB.execute("update studentcourses set grade='A-' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif percentage >= 90:
            sessionDB.execute("update studentcourses set grade='A' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
    elif hours == 3:
        percentage = (grade * 100)/150
        if 60 <= percentage < 65:
            sessionDB.execute("update studentcourses set grade='D' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 65 <= percentage < 70:
            sessionDB.execute("update studentcourses set grade='C' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 70 <= percentage < 75:
            sessionDB.execute("update studentcourses set grade='C+' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 75 <= percentage < 80:
            sessionDB.execute("update studentcourses set grade='B' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 80 <= percentage < 85:
            sessionDB.execute("update studentcourses set grade='B+' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 85 <= percentage < 90:
            sessionDB.execute("update studentcourses set grade='A-' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif percentage >= 90:
            sessionDB.execute("update studentcourses set grade='A' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
    elif hours == 4: # Check if there is 4 credit hours subjects if not remove this portion of the code
        percentage = (grade * 100) / 200
        if 60 <= percentage < 65:
            sessionDB.execute("update studentcourses set grade='D' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 65 <= percentage < 70:
            sessionDB.execute("update studentcourses set grade='C' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 70 <= percentage < 75:
            sessionDB.execute("update studentcourses set grade='C+' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 75 <= percentage < 80:
            sessionDB.execute("update studentcourses set grade='B' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 80 <= percentage < 85:
            sessionDB.execute("update studentcourses set grade='B+' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif 85 <= percentage < 90:
            sessionDB.execute("update studentcourses set grade='A-' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
        elif percentage >= 90:
            sessionDB.execute("update studentcourses set grade='A' where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code})
    sessionDB.commit()


def giving_f(id):
    results = sessionDB.execute("select course_code from studentcourses where student_ID=:id and pass=0",
                               {"id": id}).fetchall()
    for result in results:
        sessionDB.execute("update studentcourses set grade='F' where student_ID=:id and course_code=:code",
                          {"id": id, "code": result.course_code})
    sessionDB.commit()


def GPA(id):
    """
    This function calculates semester gpa
    :param id: student ID
    :return: semester gpa
    """
    results = sessionDB.execute("select studentcourses.course_code, course.hours from studentcourses inner join course "
                                "on studentcourses.course_code = course.id and studentcourses.student_ID=:id",
                                 {"id": id})
    hours = 0
    qp = 0.0
    for result in results:
        hours += int(result.hours)
        qp += QP(result.course_code, id)
    # This code snippet add cumulative QP to the student
    cur_qp = sessionDB.execute("select qp from student where ID=:id", {"id": id}).fetchone()
    new_qp = 0
    if cur_qp:
        new_qp = qp + int(cur_qp.qp)
    else:
        new_qp = qp
    sessionDB.execute("update student set qp=:code where ID=:id", {"code": new_qp, "id": id})
    sessionDB.commit()
    return hours * qp

def QP(course_code, id):
    """This function calculates the quality point for a given subject
    :param course_code: the course code I guess it's obvious
    :param id: student id smart boy
    :return:return quality points for a given subject to a specified student
    """
    hour = sessionDB.execute("select hours from course where id=:code", {"code": course_code}).fetchone()
    hours = int(hour.hours)
    point = sessionDB.execute("select grade from studentcourses where student_ID=:id and course_code=:code",
                              {"id": id, "code": course_code}).fetchone()

    qp = 0.0
    if str(point.grade) == "A":
        qp = 4.0
    elif str(point.grade) == "A-":
        qp = 3.67
    elif str(point.grade) == "B+":
        qp = 3.33
    elif str(point.grade) == "B":
        qp = 3.0
    elif str(point.grade) == "C+":
        qp = 2.67
    elif str(point.grade) == "C":
        qp = 2.33
    elif str(point.grade) == "D":
        qp = 2.0
    elif str(point.grade) == "F":
        qp = 0.0
    return hours * qp


if __name__ == '__main__':
    app.secret_key = 'super_'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
