import logging
import os 
from contextlib import contextmanager

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()


class MyDataMethods:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _db_config(self):
        config = {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'dbname': os.getenv('DB_NAME'),
            'port': os.getenv('DB_PORT'),
        }
        missing = [key.upper() for key, value in config.items() if not value]
        if missing:
            raise RuntimeError(f'Missing required database environment variables: {", ".join(missing)}')
        return config

    def dataBase(self):
        return psycopg2.connect(**self._db_config())

    @contextmanager
    def _cursor(self, *, dict_cursor=False):
        db = self.dataBase()
        cursor = db.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor if dict_cursor else None
        )
        try:
            yield db, cursor
        except Exception:
            db.rollback()
            self.logger.exception('Database operation failed')
            raise
        finally:
            cursor.close()
            db.close()

    def _fetchone(self, query, params=(), *, dict_cursor=False):
        with self._cursor(dict_cursor=dict_cursor) as (_, cursor):
            cursor.execute(query, params)
            return cursor.fetchone()

    def _fetchall(self, query, params=(), *, dict_cursor=False):
        with self._cursor(dict_cursor=dict_cursor) as (_, cursor):
            cursor.execute(query, params)
            return cursor.fetchall()

    def _execute(self, query, params=(), *, returning=False):
        with self._cursor() as (db, cursor):
            cursor.execute(query, params)
            returned_value = cursor.fetchone() if returning else None
            db.commit()
            return returned_value

    def addUser(self, user_name, user_email, user_password):
        self._execute(
            'INSERT INTO USERS (name,email,password,join_date) VALUES (%s,%s,%s,CURRENT_DATE)',
            (user_name, user_email, user_password),
        )

    def verifyUser(self, user_email):
        data = self._fetchone('SELECT password FROM USERS WHERE email=%s', (user_email,))
        return data[0] if data else False

    def getUserData(self, user_email):
        return self._fetchone('SELECT * FROM USERS WHERE email=%s', (user_email,))

    def getUserData2(self, user_id):
        return self._fetchone('SELECT name FROM USERS WHERE user_id=%s', (user_id,))

    def addInstituate(self, user_id):
        self._execute('INSERT INTO Instituate (user_id) VALUES (%s)', (user_id,))

    def isInstituate(self, user_id):
        return bool(self._fetchone('SELECT 1 FROM Instituate WHERE user_id=%s', (user_id,)))

    def addCourses(self, title, price, user_id):
        course_id = self._execute(
            '''
            INSERT INTO COURSES (COURSE_TITLE,COURSE_PRICE,USER_ID)
            VALUES (%s,%s,%s)
            RETURNING COURSE_ID
            ''',
            (title, price, user_id),
            returning=True,
        )
        return course_id[0]

    def addChapters(self, title, description, video, notes, course_id):
        self._execute(
            'INSERT INTO chapters (chapter_title,CHAPTER_DESCRIPTION,CHAPTER_VIDEO,CHAPTER_NOTES,COURSE_ID) VALUES (%s,%s,%s,%s,%s)',
            (title, description, video, notes, course_id),
        )

    def addQuestions(self, title, opta, optb, optc, optd, answer, course_id):
        self._execute(
            'INSERT INTO QUESTIONS (QUESTION_TEXT,OPTIONA,OPTIONB,OPTIONC,OPTIOND,ANSWER,COURSE_ID) VALUES (%s,%s,%s,%s,%s,%s,%s)',
            (title, opta, optb, optc, optd, answer, course_id),
        )

    def getAllCourseData(self, user_id):
        return self._fetchall(
            '''
            SELECT *
            FROM COURSES
            WHERE COURSE_ID NOT IN (
                SELECT COURSE_ID FROM ENROLLMENT WHERE USER_ID=%s
            )
            ''',
            (user_id,),
            dict_cursor=True,
        )

    def getEnrolledCourses(self, user_id):
        return self._fetchall(
            '''
            SELECT *
            FROM COURSES
            INNER JOIN ENROLLMENT ON COURSES.COURSE_ID=ENROLLMENT.COURSE_ID
            WHERE ENROLLMENT.USER_ID=%s
            ''',
            (user_id,),
            dict_cursor=True,
        )

    def getParticularCourseDetail(self, course_id):
        return self._fetchall(
            'SELECT * FROM COURSES WHERE COURSE_ID=%s',
            (course_id,),
            dict_cursor=True,
        )

    def getCourseProgress(self, user_id, course_id):
        completed_chapters = self._fetchall(
            'SELECT CHAPTER_ID FROM COURSE_PROGRESS WHERE USER_ID=%s AND COURSE_ID=%s AND IS_COMPLETED=%s',
            (user_id, course_id, True),
        )
        total_chapters = self._fetchall('SELECT CHAPTER_ID FROM CHAPTERS WHERE COURSE_ID=%s', (course_id,))

        if not total_chapters:
            return 0

        return (len(completed_chapters) / len(total_chapters)) * 100

    def addCourseToUser(self, user_id, course_id):
        existing = self._fetchone(
            'SELECT 1 FROM ENROLLMENT WHERE USER_ID=%s AND COURSE_ID=%s',
            (user_id, course_id),
        )
        if not existing:
            self._execute(
                'INSERT INTO ENROLLMENT (user_id,course_id) VALUES (%s,%s)',
                (user_id, course_id),
            )

    def getChaptersData(self, course_id):
        return self._fetchall(
            'SELECT * FROM CHAPTERS WHERE COURSE_ID=%s',
            (course_id,),
            dict_cursor=True,
        )

    def getCourseName(self, course_id):
        data = self._fetchone('SELECT course_title FROM courses WHERE COURSE_ID=%s', (course_id,))
        return data[0] if data else None

    def makeChapterComplete(self, user_id, course_id, chapter_id):
        existing = self._fetchone(
            'SELECT 1 FROM course_progress WHERE USER_ID=%s AND COURSE_ID=%s AND CHAPTER_ID=%s',
            (user_id, course_id, int(chapter_id)),
        )
        if not existing:
            self._execute(
                'INSERT INTO COURSE_PROGRESS (USER_ID,COURSE_ID,CHAPTER_ID,IS_COMPLETED) VALUES (%s,%s,%s,%s)',
                (user_id, course_id, int(chapter_id), True),
            )

    def getCompleteChapterData(self, user_id, course_id):
        return self._fetchall(
            'SELECT * FROM course_progress WHERE user_id=%s AND COURSE_ID=%s AND is_completed=%s',
            (user_id, course_id, True),
            dict_cursor=True,
        )

    def getQuestionsData(self, course_id):
        return self._fetchall(
            'SELECT * FROM questions WHERE COURSE_ID=%s',
            (course_id,),
            dict_cursor=True,
        )

    def getResultData(self, user_id, course_id):
        return self._fetchone(
            'SELECT * FROM result WHERE USER_ID=%s AND COURSE_ID=%s',
            (user_id, course_id),
            dict_cursor=True,
        )

    def getResultData2(self, user_id):
        return self._fetchall(
            'SELECT * FROM result WHERE USER_ID=%s',
            (user_id,),
            dict_cursor=True,
        )

    def addResultData(self, user_id, course_id, score):
        if not self.getResultData(user_id, course_id):
            self._execute(
                'INSERT INTO RESULT (USER_ID,COURSE_ID,SCORE) VALUES (%s,%s,%s)',
                (user_id, course_id, score),
            )

    def addBalance(self, user_id, amount):
        self._execute('INSERT INTO BALANCE (USER_ID,AMOUNT) VALUES (%s,%s)', (user_id, amount))

    def getBalance(self, user_id):
        data = self._fetchone('SELECT AMOUNT FROM BALANCE WHERE USER_ID=%s', (user_id,))
        return data if data else [0]

    def updateBalance(self, user_id, amount, reduce=True):
        current_balance = self._fetchone('SELECT amount FROM BALANCE WHERE user_id=%s', (user_id,))
        if current_balance is None:
            starting_amount = -amount if reduce else amount
            self._execute(
                'INSERT INTO BALANCE (user_id, amount) VALUES (%s, %s)',
                (user_id, starting_amount),
            )
            return

        operation = '-' if reduce else '+'
        self._execute(
            f'UPDATE BALANCE SET amount = amount {operation} %s WHERE user_id = %s',
            (amount, user_id),
        )

    def instituateCourse(self, user_id):
        course_data = self._fetchall(
            'SELECT * FROM COURSES WHERE USER_ID=%s',
            (user_id,),
            dict_cursor=True,
        )
        enrolled_data = self._fetchall(
            '''
            SELECT ENROLLMENT.user_id
            FROM ENROLLMENT
            INNER JOIN COURSES ON ENROLLMENT.course_id = COURSES.course_id
            WHERE COURSES.USER_ID=%s
            ''',
            (user_id,),
            dict_cursor=True,
        )
        return [course_data, enrolled_data]

    def getResultForInstituate(self, user_id):
        return self._fetchall(
            '''
            SELECT USERS.NAME, COURSES.COURSE_TITLE, RESULT.SCORE
            FROM COURSES
            LEFT JOIN RESULT ON RESULT.COURSE_ID = COURSES.COURSE_ID
            LEFT JOIN USERS ON RESULT.USER_ID = USERS.USER_ID
            WHERE COURSES.USER_ID = %s
            ''',
            (user_id,),
            dict_cursor=True,
        )

    def getInstituateStudent(self, owner_id):
        return self._fetchall(
            '''
            SELECT USERS.NAME, USERS.EMAIL, COURSES.COURSE_TITLE, COURSES.JOIN_DATE, COURSES.COURSE_PRICE
            FROM USERS
            INNER JOIN ENROLLMENT ON ENROLLMENT.USER_ID=USERS.USER_ID
            INNER JOIN COURSES ON ENROLLMENT.COURSE_ID = COURSES.COURSE_ID
            WHERE COURSES.USER_ID=%s
            ''',
            (owner_id,),
            dict_cursor=True,
        )

    def getGeneralUserData(self):
        return self._fetchall('SELECT * FROM USERS', dict_cursor=True)

    def getTotalUsers(self):
        return self._fetchone('SELECT COUNT(*) FROM USERS')[0]

    def getTotalCourses(self):
        return self._fetchone('SELECT COUNT(*) FROM COURSES')[0]

    def getTopInstitutes(self):
        try:
            return self._fetchall(
                '''
                SELECT u.name, COUNT(DISTINCT c.course_id) AS course_count, COUNT(e.user_id) AS enrollments
                FROM USERS u
                JOIN Instituate i ON u.user_id = i.user_id
                LEFT JOIN COURSES c ON u.user_id = c.user_id
                LEFT JOIN ENROLLMENT e ON c.course_id = e.course_id
                GROUP BY u.user_id, u.name
                ORDER BY enrollments DESC
                LIMIT 5
                ''',
                dict_cursor=True,
            )
        except Exception:
            self.logger.exception('Error fetching top institutes')
            return []

    def getTotalInstitutes(self):
        return self._fetchone('SELECT COUNT(*) FROM Instituate')[0]

    def getAllUsers(self):
        return self._fetchall(
            '''
            SELECT u.*, CASE WHEN i.user_id IS NOT NULL THEN 'Institute' ELSE 'Student' END AS role
            FROM USERS u
            LEFT JOIN Instituate i ON u.user_id = i.user_id
            ''',
            dict_cursor=True,
        )

    def getAllCoursesAdmin(self):
        return self._fetchall(
            'SELECT c.*, u.name AS owner_name FROM COURSES c LEFT JOIN USERS u ON c.USER_ID = u.USER_ID',
            dict_cursor=True,
        )

    def deleteUser(self, user_id):
        try:
            with self._cursor() as (db, cursor):
                cursor.execute('DELETE FROM balance WHERE user_id=%s', (user_id,))
                cursor.execute('DELETE FROM enrollment WHERE user_id=%s', (user_id,))
                cursor.execute('DELETE FROM result WHERE user_id=%s', (user_id,))
                cursor.execute('DELETE FROM course_progress WHERE user_id=%s', (user_id,))
                cursor.execute('DELETE FROM instituate WHERE user_id=%s', (user_id,))

                cursor.execute('SELECT course_id FROM courses WHERE user_id=%s', (user_id,))
                courses = cursor.fetchall()

                for (course_id,) in courses:
                    cursor.execute('DELETE FROM chapters WHERE course_id=%s', (course_id,))
                    cursor.execute('DELETE FROM questions WHERE course_id=%s', (course_id,))
                    cursor.execute('DELETE FROM enrollment WHERE course_id=%s', (course_id,))
                    cursor.execute('DELETE FROM result WHERE course_id=%s', (course_id,))
                    cursor.execute('DELETE FROM course_progress WHERE course_id=%s', (course_id,))
                    cursor.execute('DELETE FROM courses WHERE course_id=%s', (course_id,))

                cursor.execute('DELETE FROM users WHERE user_id=%s', (user_id,))
                db.commit()
                return True
        except Exception:
            self.logger.exception('DELETE USER ERROR')
            return False
