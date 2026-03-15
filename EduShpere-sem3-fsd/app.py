from flask import Flask,render_template,url_for,request,redirect,session,jsonify,make_response
import csv
from io import StringIO
from werkzeug.security import generate_password_hash,check_password_hash
from python_db_methods import MyDataMethods
from myEmail import SendEmail
app = Flask(__name__)

app.secret_key = 'secret123'

database = MyDataMethods()


# for home-Page:--------------------------------------------
@app.route('/')
def index_page():
    return render_template('index.html')


# for login-Page:---------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        data = request.form
        
        # if signup page is open---------------------
        if len(list(data))>=3:
            # to check user already there or not---
            if not database.getUserData(data['user_email']):
                # print('xxx')
                database.addUser(data['user_name'],data['user_email'],generate_password_hash(data['user_pass']))
                # to add user id and work in session storage---------------------

                session['user_id'] = database.getUserData(data['user_email'])[0]

                # to check wheather it is instituate or not---------
                isInstituate = True if 'roleCheck' in data else False
                if isInstituate:
                    database.addInstituate(session['user_id'])

                session['isInstituate'] = database.isInstituate(session['user_id'])
                session['user_email'] = data['user_email']
                # to launch the page instance or user_home_page---------
                if session['isInstituate']:
                    # return redirect(url_for('instituate_page'))
                    return render_template('login_page.html',error={'mode':'signin','msg':''})
                     
                return redirect(url_for('user_home_page'))
            
            else:
                return render_template('login_page.html',error={'mode':'signup','msg':'User Already Exits!!!'})
            
        # when signin page is open----------
        else:
            real_passwd = database.verifyUser(data['user_email'])
            if real_passwd and check_password_hash(real_passwd,data['user_pass']):
                # to add user id in session storage---------------------
                session['user_id'] = database.getUserData(data['user_email'])[0]
                session['isInstituate'] = database.isInstituate(session['user_id'])

                session['user_email'] = data['user_email']

                if session['isInstituate']:
                    user_name = database.getUserData2(session['user_id'])
                    ori_otp = SendEmail.admin_login_email(user_name)
                    session['otp'] = ori_otp
                    return redirect(url_for('otp_page'))
                
                
                return redirect(url_for('user_home_page'))
            
            else:
                return render_template('login_page.html',error={'mode':'signin','msg':'No Such User Data Founded!!!'})

    
    return render_template('login_page.html',error={'mode':'signin','msg':''})

# for otp verification-------------
@app.route('/otp', methods=['GET', 'POST'])
def otp_page():
    if request.method == 'POST':
        user_otp = request.form.get('otp')

        if int(user_otp) == session.get('otp'):
            # remove otp after success
            session.pop('otp', None)  
            return redirect(url_for('instituate_page'))
        else:
            return "<h1>Invalid OTP</h1>"

    return render_template('otp.html')

@app.route('/getLoginData')
def send_login_data():
    user_name = database.getUserData2(session['user_id'])

    return jsonify({
        "isInstituate": session.get('isInstituate', False),
        "user_name": user_name[0] if user_name else None
    })

# for user home page0--------------------------
@app.route('/home')
def user_home_page():
    if 'user_id' not in session:
        return ('<h1>No user Founded!</h1>')
    
    return render_template('home_page.html')

# for instituate home page-----------------------
@app.route('/Instituate')
def instituate_page():
    if 'user_id' not in session:
        return ('<h1>No user Founded!</h1>')
    user_id = session['user_id']

    instituate_data = {}
    instituate_name = database.getUserData2(user_id)
    courses_data = database.instituateCourse(user_id)
    # print(courses_data)
    total_course = len(courses_data[0])
    enrolled_course = len(courses_data[1])

    instituate_data['instituate_name'] = instituate_name[0]
    instituate_data['total_course'] = total_course
    instituate_data['enrolled_course'] = enrolled_course
    return render_template('instituate_page.html',instituate_data = instituate_data)

# to send result data for instituate page purpose---------
@app.route('/getResultForInstituate')
def InstituateResultData():

    data = database.getResultForInstituate(session['user_id'])
    return jsonify(data)

# to get data from js and store it to server--------------------------
# to create new course data---------------------------

@app.route('/publishCourse', methods=['GET','POST'])
def publish_course():
    
    if request.method == 'POST':
        course_data = request.get_json()
        course_id = database.addCourses(course_data['module_title'],course_data['module_price'],session['user_id'])
        # print(course_data)
        chapters = course_data['module_chapters']
        for i in chapters:
            database.addChapters(i['title'],i['description'],i['yt_url'],i['notes_url'],course_id)

        questions = course_data['module_question']
        for i in questions:
            database.addQuestions(i['question'],i['option1'],i['option2'],i['option3'],i['option4'],i['answer'],course_id)
    
        return jsonify({'message':'course uploded'})
    
    return render_template('create_module.html')


# to makes api to fetch data from website----------------------------------
@app.route('/user/data')
def toSendUserData():
    if 'user_id' not in session:
        return jsonify({'error':'no  user found'}), 401
    udata = database.getUserData2(session['user_id'])
    user_data = {
        'name':udata[0]
    }

    return jsonify(user_data)


# to send data of courses in which user is enrolled-----------------
@app.route('/user_courses/data')
def toSendUserEnrolledCourse():
    recive_data = database.getEnrolledCourses(session['user_id'])
    course_data = []

    compelted_count = 0
    for i in recive_data:
        progress = database.getCourseProgress(session['user_id'],i['course_id'])
        quiz_attemp = database.getResultData2(session['user_id'])
        if progress==100 and len(quiz_attemp)>0:
            compelted_count += 1
        
        
        
        if len(quiz_attemp)<=0:
            if progress>0:
                progress -= 1

        course_data.append({
            'course_id':i['course_id'],
            'course_title':i['course_title'],
            'course_progress': progress
        })
    course_data.append({'completed':compelted_count})

    # to give certificate count of that users--------------
    certificate_count = getAllCertificates()
    course_data.append({'certificate_count':len(certificate_count.get_json())})

    return jsonify(course_data)


# to send data of all the avaiable courses------------------
@app.route('/courses/data')
def toSendAllCourses():
    recive_data = database.getAllCourseData(session['user_id'])
    course_data = []
    for i in recive_data:
        course_data.append({
            'course_id':i['course_id'],
            'course_title':i['course_title'],
            'course_price':i['course_price'],
            'course_owner':database.getUserData2(i['user_id'])
        })
    
    return jsonify(course_data)
    


# to add course when user Enroll it------------------------
@app.route('/enrollCourse',methods=['POST'])
def enrollCourses():
    if request.method == 'POST':
        data = request.get_json()
        course_id = data['courseId']
        course_details = database.getParticularCourseDetail(course_id)[0]
        course_price = course_details['course_price']
        user_balance = database.getBalance(session['user_id'])

        # to verify user and course price----------------
        if course_price>user_balance[0]:
            return jsonify({'message':'Not Enough Points!!!'})
        else:
            # to reduce points from buyer balance------------
            database.updateBalance(session['user_id'],course_price)
            database.addCourseToUser(session['user_id'],int(course_id))

            # and to add points to seller balance------------
            owner_id = course_details['user_id']
            database.updateBalance(owner_id,course_price,reduce=False)
            return jsonify({'message':'Course Enrolled Successfully'})
    
    return jsonify({'message':'Fails To Enroll Course!!!'})


# to visite module page----------------------------
@app.route('/myCourse/<int:course_id>',methods=['GET'])
def openModulePage(course_id):
    return render_template('module_page.html',course_id=course_id)


# to send chapters and it data to the module page------------------------
@app.route('/courseData/<int:course_id>')
def sendChaptersData(course_id):
    data = database.getChaptersData(course_id)
    if data:
        data.append(database.getCourseName(course_id))
        return jsonify(data)
    else:
        return jsonify({'data':'hello'})

@app.route('/chapterStatus',methods=["POST"])
def sendChapterStatus():
    if request.method == 'POST':
        data = request.get_json()
        data = database.getCompleteChapterData(session['user_id'],data['courseId'])
        return jsonify(data)
    
# to mark chapter as completed--------------------
@app.route('/chapterComplete',methods=["POST"])
def markAsComplete():
    if request.method == "POST":
        data = request.get_json()
        database.makeChapterComplete(session['user_id'],data['courseId'],data['chapterId'])
        return jsonify({'message':'Chapter Completed'})
    

# to send quiz data ---------------------------------
@app.route('/moduleQuiz',methods=['POST'])
def sendQuizData():
    if request.method == 'POST':
        data = request.get_json()

        quiz = database.getQuestionsData(data['courseId'])
        isAttempt = database.getResultData(session['user_id'],data['courseId'])
        if isAttempt:
            quiz.append({'isAttempt':True})
        else:
            quiz.append({'isAttempt':False})

        return jsonify(quiz)
    
    return jsonify({'message':'some thing wents wrong!'})


# to save quiz result data--------------------------------
@app.route('/quizFinished',methods=['POST'])
def saveQuizData():
    if request.method == 'POST':
        data = request.get_json()
        database.addResultData(session['user_id'],data['courseId'],data['score'])
        user_name = database.getUserData2(session['user_id'])
        user_email = session['user_email']
        course_name = database.getParticularCourseDetail(data['courseId'])[0]['course_title']
        SendEmail.result_email(user_email,user_name,course_name,data['score'])
        return jsonify({'message':'sucessfull'})
    

# to get result data ------------------
@app.route('/showResult',methods=['POST'])
def getResultData():
    if request.method == 'POST':
        course_id = request.get_json()['courseId']
        data = database.getResultData(session['user_id'],course_id)

        return jsonify(data)
    return jsonify({'message':'No Data Found!!!'})


# to open certificate page for that user by the help of course_id----------
@app.route('/certificate/<int:course_id>')
def openCertificatePage(course_id):
    user_name = database.getUserData2(session['user_id'])[0]
    user_course = database.getCourseName(course_id)
    user_score = database.getResultData(session['user_id'],course_id)['score']
    date = database.getResultData(session['user_id'],course_id)['completion_date']
    
    # to get owner name of that course-------------------------
    owner_id = database.getParticularCourseDetail(course_id)[0]['user_id']
    owner_name = database.getUserData2(owner_id)[0]

    return render_template('certificate.html',data = [user_name,user_course,user_score,owner_name,date])


# to open certificate list page--------------------------
@app.route('/myCertificates')
def openCertificatels():
    return render_template('certificate_list.html')



# to show the list of all the certicate of that user-------------------
@app.route('/getAllCertificate')
def getAllCertificates():
    result = database.getResultData2(session['user_id'])
    send_data = []
    for i in result:
        if i['score']>=50:
            send_data.append({'course_title':database.getCourseName(i['course_id']),'course_id':i['course_id']})
    return jsonify(send_data)


# for user profile---------------------------------
@app.route('/userprofile')
def show_profile():
    user_id = session['user_id']
    user_name = database.getUserData2(user_id)
    balance = database.getBalance(user_id)
    
    course_details = toSendUserEnrolledCourse().get_json()
    course_completed = course_details[len(course_details)-2]['completed']
    active_course = len(toSendUserEnrolledCourse().get_json()[0:-2])
    # print(toSendUserEnrolledCourse().get_json())
    return render_template('profile.html',data = [user_name[0],balance[0],course_completed,active_course])

# when user log out---------------------------------
@app.route('/logout')
def logout():
    # removes all session data----
    session.clear()
    return render_template('login_page.html',error={'mode':'signin','msg':''})

# to purhcase point-------------------------------------
@app.route('/buyPackage',methods=['POST'])
def buyPoints():
    if request.method == 'POST':
        points = request.get_json()['points']
        user_id = session['user_id']
        # check that user had any balance or not---------------

        user_balance = database.getBalance(user_id)
        if user_balance[0]>0: #if user already had balance
            database.updateBalance(user_id,points,reduce=False)

        else: #there is no data of user balance
            database.addBalance(user_id,points)
        return jsonify({'message':'Successfully Buy'})
    return jsonify({'message':'Fails To Buy'})


# to launch instituate_user_page--------------
@app.route('/instituate_user')
def openInstituateUser():
    return render_template('instituate_user.html')

# to send particular instituate_page courses data--------
@app.route('/instituatesCourses')
def getInstituatesCourses():
    data = database.instituateCourse(session['user_id'])[0]
    return jsonify(data)

@app.route('/instituateStudentData')
def getInstituateStudent():
    data = database.getInstituateStudent(session['user_id'])
    return jsonify(data)

@app.route('/GeneralData')
def getGeneralData():
    data = database.getGeneralUserData()
    return jsonify(data)

@app.route('/instituateProfile')
def showInstituateprofile():
    return render_template('instituateProfile.html')

@app.route('/instituateReveneu')
def getInstituateRevenu():
    data = database.getInstituateStudent(session['user_id'])
    return jsonify(data)

#===================================================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_page():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email == 'admin@gmail.com' and password == 'Admin_1':
            session.clear()
            session['user_id'] = 'admin'
            session['is_admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            return render_template('admin_login.html', error='Invalid Credentials')
    return render_template('admin_login.html')

# for admin panel page---------------------
@app.route('/adminpanel')
def admin_panel():
    if session.get('is_admin'):
        admin_data = {
            'admin_name': 'Admin',
            'total_users': database.getTotalUsers() or 0,
            'total_institutes': database.getTotalInstitutes() or 0,
            'total_courses': database.getTotalCourses() or 0
        }
        return render_template('admin_panel.html', admin_data=admin_data)
    return redirect(url_for('admin_login_page'))

# to send admin dashboard data---------------------
@app.route('/admin/data')
def admin_dashboard_data():
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403

    # Fetch data for tables
    top_institutes = database.getTopInstitutes()

    return jsonify({"top_institutes": top_institutes})

# to get all users for admin---------------------
@app.route('/admin/users')
def admin_users():
    if session.get('is_admin'):
        return jsonify(database.getAllUsers())
    return jsonify({'error': 'Unauthorized'}), 403

# to get all courses for admin---------------------
@app.route('/admin/courses')
def admin_courses():
    if session.get('is_admin'):
        return jsonify(database.getAllCoursesAdmin())
    return jsonify({'error': 'Unauthorized'}), 403

# to delete a user---------------------
@app.route('/admin/delete_user', methods=['POST'])
def delete_user():
    if session.get('is_admin'):
        user_id = request.get_json()['user_id']
        success = database.deleteUser(user_id)
        if success:
            return jsonify({'message':'Deleted'})
        else:
            return jsonify({'error':'Failed'}),500
    return jsonify({'error':'Unauthorized'}),403

# to get courses of a specific institute for admin---------------------
@app.route('/admin/institute_courses/<int:user_id>')
def admin_institute_courses(user_id):
    if session.get('is_admin'):
        return jsonify(database.instituateCourse(user_id)[0])
    return jsonify({'error': 'Unauthorized'}), 403

# to download reports (daily/monthly)---------------------
@app.route('/admin/download_report/<report_type>')
def download_report(report_type):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login_page'))
    
    si = StringIO()
    cw = csv.writer(si)
    filename = "report.csv"
    
    if report_type == 'top_institutes':
        data = database.getTopInstitutes()
        cw.writerow(['Institute Name', 'Courses', 'Total Enrollments'])
        for row in data:
            cw.writerow([row['name'], row['course_count'], row['enrollments']])
        filename = 'top_institutes_report.csv'
    else:
        return "Invalid report type", 400
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename={filename}"
    output.headers["Content-type"] = "text/csv"
    return output

if __name__ == '__main__':
    app.run(debug=True)