import csv
import logging
import os
from datetime import datetime, timedelta, timezone
from functools import wraps
from io import StringIO

from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from myEmail import SendEmail
from python_db_methods import MyDataMethods

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, '.env')
ENV_EXAMPLE_FILE = os.path.join(BASE_DIR, '.env.example')

if os.path.exists(ENV_EXAMPLE_FILE):
    load_dotenv(ENV_EXAMPLE_FILE)

if os.path.exists(ENV_FILE):
    load_dotenv(ENV_FILE, override=True)
elif not os.path.exists(ENV_EXAMPLE_FILE):
    load_dotenv()

logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO').upper())
LOGGER = logging.getLogger(__name__)


def _require_env(name):
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(f'Missing required environment variable: {name}')


def _int_env(name, default):
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f'Environment variable {name} must be an integer') from exc


OTP_EXPIRY_MINUTES = _int_env('OTP_EXPIRY_MINUTES', 5)
SESSION_LIFETIME_HOURS = _int_env('SESSION_LIFETIME_HOURS', 8)
ADMIN_EMAIL = _require_env('ADMIN_EMAIL')
ADMIN_PASSWORD = _require_env('ADMIN_PASSWORD')

app = Flask(__name__)
app.config.update(
    SECRET_KEY=_require_env('FLASK_SECRET_KEY'),
    PERMANENT_SESSION_LIFETIME=timedelta(hours=SESSION_LIFETIME_HOURS),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true',
)

database = MyDataMethods()


def render_login(message='', mode='signin'):
    return render_template('login_page.html', error={'mode': mode, 'msg': message})


def json_error(message, status_code):
    return jsonify({'error': message}), status_code


def get_json_body():
    return request.get_json(silent=True) or {}


def parse_int(value, field_name, *, minimum=None):
    try:
        parsed_value = int(value)
    except (TypeError, ValueError):
        raise ValueError(f'{field_name} must be a valid integer')

    if minimum is not None and parsed_value < minimum:
        raise ValueError(f'{field_name} must be at least {minimum}')

    return parsed_value


def current_user_name():
    user_name = database.getUserData2(session['user_id'])
    return user_name[0] if user_name else None


def login_user(user_id, email, *, is_instituate=False, is_admin=False):
    session.clear()
    session.permanent = True
    session['user_id'] = user_id
    session['user_email'] = email
    session['isInstituate'] = is_instituate
    session['is_admin'] = is_admin


def clear_otp_state():
    session.pop('otp', None)
    session.pop('otp_expires_at', None)


def start_institute_otp_flow(user_name, user_email):
    otp = SendEmail.admin_login_email(user_name, user_email)
    if otp is None:
        return False
    session['otp'] = otp
    session['otp_expires_at'] = int(
        (datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)).timestamp()
    )
    return True


def build_user_course_summary(user_id):
    enrolled_courses = database.getEnrolledCourses(user_id)
    results = database.getResultData2(user_id)
    attempted_course_ids = {result['course_id'] for result in results}

    course_data = []
    completed_count = 0
    certificate_count = 0

    for result in results:
        if result['score'] >= 50:
            certificate_count += 1

    for course in enrolled_courses:
        progress = database.getCourseProgress(user_id, course['course_id'])
        attempted_quiz = course['course_id'] in attempted_course_ids

        if progress == 100 and attempted_quiz:
            completed_count += 1

        if not attempted_quiz and progress > 0:
            progress -= 1

        course_data.append(
            {
                'course_id': course['course_id'],
                'course_title': course['course_title'],
                'course_progress': progress,
            }
        )

    return course_data, completed_count, certificate_count


def require_auth(*, api=False, institute=False, admin=False):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if admin:
                if not session.get('is_admin'):
                    if api:
                        return json_error('Unauthorized', 403)
                    return redirect(url_for('admin_login_page'))
                return view_func(*args, **kwargs)

            if not session.get('user_id') or session.get('is_admin'):
                if api:
                    return json_error('Unauthorized', 401)
                return redirect(url_for('login_page'))

            if institute and not session.get('isInstituate'):
                if api:
                    return json_error('Forbidden', 403)
                return redirect(url_for('user_home_page'))

            return view_func(*args, **kwargs)

        return wrapper

    return decorator


@app.route('/')
def index_page():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        data = request.form
        user_email = (data.get('user_email') or '').strip().lower()
        user_password = (data.get('user_pass') or '').strip()
        user_name = (data.get('user_name') or '').strip()
        is_signup = bool(user_name)

        if not user_email or not user_password:
            return render_login('Email and password are required.', 'signup' if is_signup else 'signin')

        if is_signup:
            if not user_name:
                return render_login('Name is required to create an account.', 'signup')

            if database.getUserData(user_email):
                return render_login('User already exists.', 'signup')

            database.addUser(user_name, user_email, generate_password_hash(user_password))
            user_record = database.getUserData(user_email)
            if not user_record:
                LOGGER.error('User signup completed but user could not be reloaded: %s', user_email)
                return render_login('Unable to create account right now.', 'signup')

            if 'roleCheck' in data:
                database.addInstituate(user_record[0])
                return render_login('Institute account created. Sign in to verify your OTP.', 'signin')

            login_user(user_record[0], user_email, is_instituate=False)
            return redirect(url_for('user_home_page'))

        real_password = database.verifyUser(user_email)
        if not real_password or not check_password_hash(real_password, user_password):
            return render_login('Invalid email or password.', 'signin')

        user_record = database.getUserData(user_email)
        if not user_record:
            return render_login('Unable to find the requested account.', 'signin')

        is_instituate = database.isInstituate(user_record[0])
        login_user(user_record[0], user_email, is_instituate=is_instituate)

        if is_instituate:
            user_name = current_user_name()
            if not start_institute_otp_flow(user_name, user_email):
                session.clear()
                return render_login('Unable to send OTP. Check email configuration and try again.', 'signin')
            return redirect(url_for('otp_page'))

        return redirect(url_for('user_home_page'))

    return render_login()


@app.route('/otp', methods=['GET', 'POST'])
@require_auth(institute=True)
def otp_page():
    if 'otp' not in session or 'otp_expires_at' not in session:
        return redirect(url_for('login_page'))

    if request.method == 'POST':
        user_otp = (request.form.get('otp') or '').strip()
        expires_at = session.get('otp_expires_at', 0)

        if datetime.now(timezone.utc).timestamp() > expires_at:
            session.clear()
            return render_template('otp.html', error='OTP expired. Please sign in again.')

        try:
            submitted_otp = parse_int(user_otp, 'OTP', minimum=100000)
        except ValueError as exc:
            return render_template('otp.html', error=str(exc))

        if submitted_otp == session.get('otp'):
            clear_otp_state()
            return redirect(url_for('instituate_page'))

        return render_template('otp.html', error='Invalid OTP.')

    return render_template('otp.html', error='')


@app.route('/getLoginData')
@require_auth(api=True)
def send_login_data():
    return jsonify(
        {
            'isInstituate': session.get('isInstituate', False),
            'user_name': current_user_name(),
        }
    )


@app.route('/home')
@require_auth()
def user_home_page():
    return render_template('home_page.html')


@app.route('/Instituate')
@require_auth(institute=True)
def instituate_page():
    user_id = session['user_id']
    instituate_name = database.getUserData2(user_id)
    courses_data = database.instituateCourse(user_id)

    instituate_data = {
        'instituate_name': instituate_name[0] if instituate_name else 'Institute',
        'total_course': len(courses_data[0]),
        'enrolled_course': len(courses_data[1]),
    }
    return render_template('instituate_page.html', instituate_data=instituate_data)


@app.route('/getResultForInstituate')
@require_auth(api=True, institute=True)
def instituate_result_data():
    return jsonify(database.getResultForInstituate(session['user_id']))


@app.route('/publishCourse', methods=['GET', 'POST'])
@require_auth(institute=True)
def publish_course():
    if request.method == 'POST':
        course_data = get_json_body()
        try:
            module_title = (course_data.get('module_title') or '').strip()
            module_price = parse_int(course_data.get('module_price'), 'module price', minimum=0)
        except ValueError as exc:
            return json_error(str(exc), 400)

        if not module_title:
            return json_error('Module title is required.', 400)

        course_id = database.addCourses(module_title, module_price, session['user_id'])

        for chapter in course_data.get('module_chapters', []):
            database.addChapters(
                chapter.get('title', '').strip(),
                chapter.get('description', '').strip(),
                chapter.get('yt_url', '').strip(),
                chapter.get('notes_url', '').strip(),
                course_id,
            )

        for question in course_data.get('module_question', []):
            database.addQuestions(
                question.get('question', '').strip(),
                question.get('option1', '').strip(),
                question.get('option2', '').strip(),
                question.get('option3', '').strip(),
                question.get('option4', '').strip(),
                question.get('answer', '').strip(),
                course_id,
            )

        return jsonify({'message': 'Course uploaded successfully.'})

    return render_template('create_module.html')


@app.route('/user/data')
@require_auth(api=True)
def to_send_user_data():
    return jsonify({'name': current_user_name()})


@app.route('/user_courses/data')
@require_auth(api=True)
def to_send_user_enrolled_course():
    course_data, completed_count, certificate_count = build_user_course_summary(session['user_id'])
    course_data.append({'completed': completed_count})
    course_data.append({'certificate_count': certificate_count})
    return jsonify(course_data)


@app.route('/courses/data')
@require_auth(api=True)
def to_send_all_courses():
    received_data = database.getAllCourseData(session['user_id'])
    course_data = []
    for course in received_data:
        owner = database.getUserData2(course['user_id'])
        course_data.append(
            {
                'course_id': course['course_id'],
                'course_title': course['course_title'],
                'course_price': course['course_price'],
                'course_owner': owner[0] if owner else None,
            }
        )
    return jsonify(course_data)


@app.route('/enrollCourse', methods=['POST'])
@require_auth(api=True)
def enroll_courses():
    data = get_json_body()
    try:
        course_id = parse_int(data.get('courseId'), 'courseId', minimum=1)
    except ValueError as exc:
        return json_error(str(exc), 400)

    course_details = database.getParticularCourseDetail(course_id)
    if not course_details:
        return json_error('Course not found.', 404)

    course_detail = course_details[0]
    course_price = course_detail['course_price']
    user_balance = database.getBalance(session['user_id'])[0]

    if course_price > user_balance:
        return jsonify({'message': 'Not enough points.'}), 400

    database.updateBalance(session['user_id'], course_price)
    database.addCourseToUser(session['user_id'], course_id)
    database.updateBalance(course_detail['user_id'], course_price, reduce=False)
    return jsonify({'message': 'Course enrolled successfully.'})


@app.route('/myCourse/<int:course_id>', methods=['GET'])
@require_auth()
def open_module_page(course_id):
    return render_template('module_page.html', course_id=course_id)


@app.route('/courseData/<int:course_id>')
@require_auth(api=True)
def send_chapters_data(course_id):
    data = database.getChaptersData(course_id)
    if not data:
        return jsonify([])

    data.append(database.getCourseName(course_id))
    return jsonify(data)


@app.route('/chapterStatus', methods=['POST'])
@require_auth(api=True)
def send_chapter_status():
    data = get_json_body()
    try:
        course_id = parse_int(data.get('courseId'), 'courseId', minimum=1)
    except ValueError as exc:
        return json_error(str(exc), 400)

    return jsonify(database.getCompleteChapterData(session['user_id'], course_id))


@app.route('/chapterComplete', methods=['POST'])
@require_auth(api=True)
def mark_as_complete():
    data = get_json_body()
    try:
        course_id = parse_int(data.get('courseId'), 'courseId', minimum=1)
        chapter_id = parse_int(data.get('chapterId'), 'chapterId', minimum=1)
    except ValueError as exc:
        return json_error(str(exc), 400)

    database.makeChapterComplete(session['user_id'], course_id, chapter_id)
    return jsonify({'message': 'Chapter completed.'})


@app.route('/moduleQuiz', methods=['POST'])
@require_auth(api=True)
def send_quiz_data():
    data = get_json_body()
    try:
        course_id = parse_int(data.get('courseId'), 'courseId', minimum=1)
    except ValueError as exc:
        return json_error(str(exc), 400)

    quiz = database.getQuestionsData(course_id)
    quiz.append({'isAttempt': bool(database.getResultData(session['user_id'], course_id))})
    return jsonify(quiz)


@app.route('/quizFinished', methods=['POST'])
@require_auth(api=True)
def save_quiz_data():
    data = get_json_body()
    try:
        course_id = parse_int(data.get('courseId'), 'courseId', minimum=1)
        score = parse_int(data.get('score'), 'score', minimum=0)
    except ValueError as exc:
        return json_error(str(exc), 400)

    course_details = database.getParticularCourseDetail(course_id)
    if not course_details:
        return json_error('Course not found.', 404)

    database.addResultData(session['user_id'], course_id, score)
    course_name = course_details[0]['course_title']
    SendEmail.result_email(session['user_email'], current_user_name(), course_name, score)
    return jsonify({'message': 'Result saved successfully.'})


@app.route('/showResult', methods=['POST'])
@require_auth(api=True)
def get_result_data():
    data = get_json_body()
    try:
        course_id = parse_int(data.get('courseId'), 'courseId', minimum=1)
    except ValueError as exc:
        return json_error(str(exc), 400)

    result = database.getResultData(session['user_id'], course_id)
    if not result:
        return json_error('Result not found.', 404)
    return jsonify(result)


@app.route('/certificate/<int:course_id>')
@require_auth()
def open_certificate_page(course_id):
    result = database.getResultData(session['user_id'], course_id)
    if not result:
        return redirect(url_for('open_certificatels'))

    course_details = database.getParticularCourseDetail(course_id)
    if not course_details:
        return redirect(url_for('open_certificatels'))

    owner_id = course_details[0]['user_id']
    owner_name = database.getUserData2(owner_id)
    return render_template(
        'certificate.html',
        data=[
            current_user_name(),
            database.getCourseName(course_id),
            result['score'],
            owner_name[0] if owner_name else '',
            result['completion_date'],
        ],
    )


@app.route('/myCertificates')
@require_auth()
def open_certificatels():
    return render_template('certificate_list.html')


@app.route('/getAllCertificate')
@require_auth(api=True)
def get_all_certificates():
    result = database.getResultData2(session['user_id'])
    send_data = []
    for item in result:
        if item['score'] >= 50:
            send_data.append(
                {
                    'course_title': database.getCourseName(item['course_id']),
                    'course_id': item['course_id'],
                }
            )
    return jsonify(send_data)


@app.route('/userprofile')
@require_auth()
def show_profile():
    user_id = session['user_id']
    user_name = database.getUserData2(user_id)
    balance = database.getBalance(user_id)
    course_details, course_completed, _ = build_user_course_summary(user_id)
    return render_template(
        'profile.html',
        data=[user_name[0] if user_name else '', balance[0], course_completed, len(course_details)],
    )


@app.route('/logout')
def logout():
    session.clear()
    return render_login('You have been logged out.', 'signin')


@app.route('/buyPackage', methods=['POST'])
@require_auth(api=True)
def buy_points():
    data = get_json_body()
    try:
        points = parse_int(data.get('points'), 'points', minimum=1)
    except ValueError as exc:
        return json_error(str(exc), 400)

    user_id = session['user_id']
    user_balance = database.getBalance(user_id)[0]
    if user_balance > 0:
        database.updateBalance(user_id, points, reduce=False)
    else:
        database.addBalance(user_id, points)
    return jsonify({'message': 'Successfully bought points.'})


@app.route('/instituate_user')
@require_auth(institute=True)
def open_instituate_user():
    return render_template('instituate_user.html')


@app.route('/instituatesCourses')
@require_auth(api=True, institute=True)
def get_instituates_courses():
    return jsonify(database.instituateCourse(session['user_id'])[0])


@app.route('/instituateStudentData')
@require_auth(api=True, institute=True)
def get_instituate_student():
    return jsonify(database.getInstituateStudent(session['user_id']))


@app.route('/GeneralData')
@require_auth(api=True, institute=True)
def get_general_data():
    return jsonify(database.getGeneralUserData())


@app.route('/instituateProfile')
@require_auth(institute=True)
def show_instituate_profile():
    return render_template('instituateprofile.html')


@app.route('/instituateReveneu')
@require_auth(api=True, institute=True)
def get_instituate_revenue():
    return jsonify(database.getInstituateStudent(session['user_id']))


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_page():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        password = (request.form.get('password') or '').strip()

        if email == ADMIN_EMAIL.lower() and password == ADMIN_PASSWORD:
            login_user('admin', email, is_admin=True)
            return redirect(url_for('admin_panel'))

        return render_template('admin_login.html', error='Invalid credentials.')

    return render_template('admin_login.html')


@app.route('/adminpanel')
@require_auth(admin=True)
def admin_panel():
    admin_data = {
        'admin_name': 'Admin',
        'total_users': database.getTotalUsers() or 0,
        'total_institutes': database.getTotalInstitutes() or 0,
        'total_courses': database.getTotalCourses() or 0,
    }
    return render_template('admin_panel.html', admin_data=admin_data)


@app.route('/admin/data')
@require_auth(api=True, admin=True)
def admin_dashboard_data():
    return jsonify({'top_institutes': database.getTopInstitutes()})


@app.route('/admin/users')
@require_auth(api=True, admin=True)
def admin_users():
    return jsonify(database.getAllUsers())


@app.route('/admin/courses')
@require_auth(api=True, admin=True)
def admin_courses():
    return jsonify(database.getAllCoursesAdmin())


@app.route('/admin/delete_user', methods=['POST'])
@require_auth(api=True, admin=True)
def delete_user():
    data = get_json_body()
    try:
        user_id = parse_int(data.get('user_id'), 'user_id', minimum=1)
    except ValueError as exc:
        return json_error(str(exc), 400)

    if database.deleteUser(user_id):
        return jsonify({'message': 'Deleted'})
    return json_error('Failed to delete user.', 500)


@app.route('/admin/institute_courses/<int:user_id>')
@require_auth(api=True, admin=True)
def admin_institute_courses(user_id):
    return jsonify(database.instituateCourse(user_id)[0])


@app.route('/admin/download_report/<report_type>')
@require_auth(admin=True)
def download_report(report_type):
    si = StringIO()
    csv_writer = csv.writer(si)
    filename = 'report.csv'

    if report_type == 'top_institutes':
        data = database.getTopInstitutes()
        csv_writer.writerow(['Institute Name', 'Courses', 'Total Enrollments'])
        for row in data:
            csv_writer.writerow([row['name'], row['course_count'], row['enrollments']])
        filename = 'top_institutes_report.csv'
    else:
        return 'Invalid report type', 400

    output = make_response(si.getvalue())
    output.headers['Content-Disposition'] = f'attachment; filename={filename}'
    output.headers['Content-type'] = 'text/csv'
    return output


if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true')
