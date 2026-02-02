from flask import Flask,render_template,url_for,request,redirect,session,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from python_db_methods import MyDataMethods

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
        if len(list(data))==3:
            # to check user already there or not---
            if not database.getUserData(data['user_email']):

                database.addUser(data['user_name'],data['user_email'],generate_password_hash(data['user_pass']))
                # to add user id in session storage---------------------
                session['user_id'] = database.getUserData(data['user_email'])[0]
                return redirect(url_for('user_home_page'))
            else:
                return render_template('login_page.html',error={'mode':'signup','msg':'User Already Exits!!!'})
        # when signin page is open----------
        else:
            real_passwd = database.verifyUser(data['user_email'])
            if check_password_hash(real_passwd,data['user_pass']):
                # to add user id in session storage---------------------
                session['user_id'] = database.getUserData(data['user_email'])[0]

                return redirect(url_for('user_home_page'))
            else:
                return render_template('login_page.html',error={'mode':'signin','msg':'No Such User Data Founded!!!'})

    
    return render_template('login_page.html',error={'mode':'signin','msg':''})


@app.route('/home')
def user_home_page():
    if 'user_id' not in session:
        return ('<h1>No user Founded!</h1>')
    
    return render_template('home_page.html')


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
        if progress==100:
            compelted_count += 1

        course_data.append({
            'course_id':i['course_id'],
            'course_title':i['course_title'],
            'course_progress': progress
        })
    course_data.append({'completed':compelted_count})
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
        database.addCourseToUser(session['user_id'],int(course_id))
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
    
if __name__ == '__main__':
    app.run(debug=True)