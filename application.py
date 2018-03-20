from flask import Flask ,request,render_template,redirect,url_for,flash,session
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

    else:
        return render_template('index.html')

#admin workspace
@app.route('/admin/<int:id>/',methods=['POST','GET'])
#let admin choose for links what he want
def admin(id):
    if session['id'] == id:
        if request.method == 'POST':
            pass
        else:
            return render_template('adminpage.html', id=id)

@app.route('/admin/<int:id>/studentscontrol/',methods=['POST','GET'])
#let admin to choose the what deparment and program to control
def studentcontrol(id):
    if session['id'] == id:
        if request.method == 'POST':
            deparment =request.form['deparment']
            program = request.form['program']
            level =request.form['level']
            result= sessionDB.execute("SELECT * FROM program WHERE department_name = :deparment and name = :program and level = :level",{"deparment":deparment,"program":program,"level":level}).fetchone()

            print(result)
            if result == None:
                #worng information
                return "wrong information"
            else:
                return redirect(url_for('studentedit',dep_name=deparment,prog_name=program,level=level,id=id))
        else:
            return render_template('student-control.html',id =id)

@app.route('/admin/<int:id>/studentscontrol/<string:dep_name>/<string:prog_name>/<int:level>/',methods=['POST','GET'])
def studentedit(id,dep_name,prog_name,level):
    if session['id'] == id:
        if request == 'POST':
            pass
        else:
            result = sessionDB.execute("SELECT * FROM student WHERE department_name = :dep_name and program_name = :prog_name and program_level = :level",{"dep_name":dep_name,"prog_name":prog_name,"level":level}).fetchall()

            print(result)
            return render_template('student-edit.html',result=result)


@app.route('/a')
def m():
    return "ashtaa"
if __name__ == '__main__':
    app.secret_key = 'super_'
    app.debug = True
    app.run(host = '0.0.0.0',port=5000)
