import psycopg2
import psycopg2.extras
from werkzeug.security import check_password_hash

class MyDataMethods:

    def dataBase(self):
        return psycopg2.connect(
            host='localhost',
            user='postgres',
            password='@1157Dipikass',
            dbname='eduSphere',
            port='5432'
        )

    def addUser(self, user_name, user_email, user_password):
        db = self.dataBase()
        cursor = db.cursor()

        query = 'INSERT INTO USERS (name,email,password) values (%s,%s,%s)'
        cursor.execute(query, (user_name, user_email, user_password))

        # to save changes which are done--------------------
        db.commit()
        cursor.close()
        db.close()


    # use to verify user data from signin page------
    def verifyUser(self, user_email):
        db = self.dataBase()
        cursor = db.cursor()

        query = 'SELECT password FROM USERS WHERE email=(%s)'
        cursor.execute(query, (user_email,))

        data = cursor.fetchone()
        cursor.close()
        db.close()

        if not data:
            return False

        real_pass = data[0]
        return real_pass
        

    # and to verify that user is already exit or not for signup page to prevent to create duplicate users-------
    # if it return data that mean user is already exit-
    # if user not exit it return None-------
    def getUserData(self, user_email):
        db = self.dataBase()
        cursor = db.cursor()

        query = 'SELECT * FROM USERS WHERE email=(%s)'
        cursor.execute(query, (user_email,))

        user_data = cursor.fetchone()
        cursor.close()
        db.close()
        return user_data
    

    # to get user data from id user_id------------
    def getUserData2(self, user_id):
        db = self.dataBase()
        cursor = db.cursor()

        query = 'SELECT name FROM USERS WHERE user_id=(%s)'
        cursor.execute(query, (user_id,))

        user_data = cursor.fetchone()
        cursor.close()
        db.close()
        return user_data


    # to add course to database-----------------
    # and it return course id so we can add it in chapters-
    def addCourses(self, title, price, user_id):
        db = self.dataBase()
        cursor = db.cursor()

        query = '''
        INSERT INTO COURSES (COURSE_TITLE,COURSE_PRICE,USER_ID)
        values (%s,%s,%s)
        RETURNING COURSE_ID
        '''
        cursor.execute(query, (title, price, user_id))
        course_id = cursor.fetchone()[0]

        # to get course_id for last added data--------------
        db.commit()
        cursor.close()
        db.close()
        return course_id


    # to add chapter data of that course-----------------------------
    def addChapters(self, title, description, video, notes, course_id):
        db = self.dataBase()
        cursor = db.cursor()

        query = 'INSERT INTO chapters (chapter_title,CHAPTER_DESCRIPTION,CHAPTER_VIDEO,CHAPTER_NOTES,COURSE_ID) values (%s,%s,%s,%s,%s)'
        cursor.execute(query, (title, description, video, notes, course_id))
        db.commit()

        cursor.close()
        db.close()


    # to add questions(mcq) in question table----------------------
    def addQuestions(self, title, opta, optb, optc, optd, answer, course_id):
        db = self.dataBase()
        cursor = db.cursor()

        query = 'INSERT INTO QUESTIONS (QUESTION_TEXT,OPTIONA,OPTIONB,OPTIONC,OPTIOND,ANSWER,COURSE_ID) values (%s,%s,%s,%s,%s,%s,%s)'
        cursor.execute(query, (title, opta, optb, optc, optd, answer, course_id))
        db.commit()

        cursor.close()
        db.close()


    # to courses data-------------------------------------
    def getAllCourseData(self,user_id):
        # dictionary=True returns data in from of python dic
        db = self.dataBase()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = "SELECT * FROM courses"
        cursor.execute(query)

        data = cursor.fetchall()
         
        user_enroll_data = self.getEnrolledCourses(user_id)
        user_enroll_course_id = []

        # to send only the course in which user is not enrolled----------
        for i in user_enroll_data:
            user_enroll_course_id.append(i['course_id'])
        final_data = []
        for i in data:
            if i['course_id'] not in user_enroll_course_id:
                final_data.append(i)

        cursor.close()
        db.close()
        return final_data
    

    # to get list of the courses in which user is enrolls------
    def getEnrolledCourses(self,user_id):
        db = self.dataBase()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = 'SELECT * FROM COURSES INNER JOIN ENROLLMENT ON COURSES.COURSE_ID=ENROLLMENT.COURSE_ID WHERE ENROLLMENT.USER_ID=%s'
        cursor.execute(query,(user_id,))

        data = cursor.fetchall()
        cursor.close()
        db.close()

        return data
    
    # to send particular course details--------------------------------
    # use to get owner name in certificate-------------------------
    def getParticularCourseDetail(self,course_id):
        db = self.dataBase()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = 'SELECT * FROM COURSES WHERE COURSE_ID=%s'
        cursor.execute(query,(course_id,))

        data = cursor.fetchall()
        cursor.close()
        db.close()

        return data
    

    # to get course progress0----------------------------------
    def getCourseProgress(self,user_id,course_id):
        db = self.dataBase()
        cursor = db.cursor()

        query = 'SELECT IS_COMPLETED FROM course_progress WHERE USER_ID=%s AND COURSE_ID=%s'
        cursor.execute(query,(user_id,course_id))
        data = cursor.fetchall()

        # to get total chapters in that course-----------
        query = 'SELECT chapter_id FROM chapters WHERE COURSE_ID=%s'
        cursor.execute(query,(course_id,))

        total_chapters = cursor.fetchall()

        cursor.close()
        db.close()

        if len(data)>0:
            progress = (len(data)/len(total_chapters))*100
        else:
            progress = 0
        return progress
    

    # to add course to user enrolled course data---------------------
    def addCourseToUser(self,user_id,course_id):
        db = self.dataBase()
        cursor = db.cursor()

        query = 'SELECT * FROM ENROLLMENT WHERE USER_ID=%s AND COURSE_ID=%s'
        cursor.execute(query, (user_id,course_id))
        get_data = cursor.fetchall()

        if not get_data:
            query = 'INSERT INTO ENROLLMENT (user_id,course_id) values (%s,%s)'
            cursor.execute(query, (user_id,course_id))

            db.commit()
            
        cursor.close()
        db.close()
        

    # to get chapters data of that course----------------------------
    def getChaptersData(self,course_id):
        db = self.dataBase()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = 'SELECT * FROM CHAPTERS WHERE COURSE_ID=%s'
        cursor.execute(query,(course_id,))

        data = cursor.fetchall()
        cursor.close()
        db.close()

        return data
    

    def getCourseName(self,course_id):
        db = self.dataBase()
        cursor = db.cursor()

        query = 'SELECT course_title FROM courses WHERE COURSE_ID=%s'
        cursor.execute(query,(course_id,))

        data = cursor.fetchone()
        cursor.close()
        db.close()

        return data[0]
    

    # to add complete tag to that chapter for that user---------------------
    def makeChapterComplete(self,user_id,course_id,chapter_id):
        db = self.dataBase()
        cursor = db.cursor()

        query = 'SELECT IS_COMPLETED FROM course_progress WHERE USER_ID=%s AND COURSE_ID=%s AND CHAPTER_ID=%s'
        cursor.execute(query,(user_id,course_id,chapter_id))
        data = cursor.fetchone()

        if not data:
            query = 'INSERT INTO COURSE_PROGRESS (USER_ID,COURSE_ID,CHAPTER_ID,IS_COMPLETED) VALUES (%s,%s,%s,%s)'
            cursor.execute(query,(user_id,course_id,chapter_id,True))
            db.commit()

        cursor.close()
        db.close()

    
    # to get questions data for that course-------------------
    def getQuestionsData(self,course_id):
        db = self.dataBase()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = 'SELECT * FROM questions WHERE COURSE_ID=%s'
        cursor.execute(query,(course_id,))
        data = cursor.fetchall()
        cursor.close()
        db.close()

        return data
    

    def getResultData(self,user_id,course_id):
        db = self.dataBase()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = 'SELECT * FROM result WHERE USER_ID=%s AND COURSE_ID=%s'
        cursor.execute(query,(user_id,course_id))
        data = cursor.fetchone()
        cursor.close()
        db.close()

        return data
    
    # to get result from userid only----------------
    def getResultData2(self,user_id):
        db = self.dataBase()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = 'SELECT * FROM result WHERE USER_ID=%s'
        cursor.execute(query,(user_id,))
        data = cursor.fetchall()
        cursor.close()
        db.close()

        return data
    

    def addResultData(self,user_id,course_id,score):
        if not self.getResultData(user_id,course_id):
            db = self.dataBase()
            cursor = db.cursor()

            query = 'INSERT INTO RESULT (USER_ID,COURSE_ID,SCORE) VALUES (%s,%s,%s)'
            cursor.execute(query,(user_id,course_id,score))
            db.commit()
            cursor.close()
            db.close()
        else:
            return


if __name__ == '__main__':
    xx = MyDataMethods()
    print(xx.getParticularCourseDetail(3))