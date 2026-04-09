import os
from werkzeug.security import generate_password_hash
from python_db_methods import MyDataMethods

def seed_database():
    print("Connecting to the database...")
    db = MyDataMethods()

    # Create dummy password
    dummy_password = generate_password_hash('password123')

    print("Creating Student Accounts...")
    students = [
        ("Alice Student", "alice@student.com"),
        ("Bob Learner", "bob@student.com"),
        ("Charlie Scholar", "charlie@student.com")
    ]
    for name, email in students:
        if not db.verifyUser(email):
            db.addUser(name, email, dummy_password)

    print("Creating Institute Accounts...")
    institutes = [
        ("Tech University", "contact@tech.edu"),
        ("Design Academy", "info@design.edu")
    ]
    for name, email in institutes:
        if not db.verifyUser(email):
            db.addUser(name, email, dummy_password)
            user_data = db.getUserData(email)
            if user_data:
                db.addInstituate(user_data[0])

    print("Generating Courses & Chapters...")
    tech_inst = db.getUserData("contact@tech.edu")
    design_inst = db.getUserData("info@design.edu")

    if tech_inst and design_inst:
        tech_id = tech_inst[0]
        design_id = design_inst[0]

        # Tech Courses
        course1_id = db.addCourses("Advanced Python Programming", 50, tech_id)
        db.addChapters("Introduction to Python", "Learn basics.", "https://youtube.com/watch?v=123", "https://docs.py", course1_id)
        db.addChapters("Data Structures", "Lists, Dicts, Sets", "https://youtube.com/watch?v=456", "https://docs.py", course1_id)
        for i in range(5):
            db.addQuestions(f"Python Question {i+1}", "A", "B", "C", "D", "A", course1_id)

        course2_id = db.addCourses("Machine Learning Basics", 100, tech_id)
        db.addChapters("What is ML?", "Theory.", "https://youtube.com/watch?v=123", "https://docs.py", course2_id)
        for i in range(5):
            db.addQuestions(f"ML Question {i+1}", "A", "B", "C", "D", "B", course2_id)

        # Design Courses
        course3_id = db.addCourses("UI/UX Masterclass", 75, design_id)
        db.addChapters("Color Theory", "Choosing palettes.", "https://youtube.com/watch?v=123", "https://docs.py", course3_id)
        db.addChapters("Typography", "Fonts and structure.", "https://youtube.com/watch?v=456", "https://docs.py", course3_id)
        for i in range(5):
            db.addQuestions(f"Design Question {i+1}", "A", "B", "C", "D", "C", course3_id)

        print("Enrolling Students into Courses...")
        alice = db.getUserData("alice@student.com")
        bob = db.getUserData("bob@student.com")
        
        if alice and bob:
            alice_id = alice[0]
            bob_id = bob[0]

            db.addCourseToUser(alice_id, course1_id)
            db.addCourseToUser(alice_id, course3_id)
            db.addCourseToUser(bob_id, course2_id)

            # Completing a chapter for Alice
            # Get chapter id for course 1
            chapters = db.getChaptersData(course1_id)
            if chapters:
                first_chap = chapters[0]['chapter_id']
                db.makeChapterComplete(alice_id, course1_id, first_chap)

            # Add result for Bob
            db.addResultData(bob_id, course2_id, 80)
            
            # Balance
            db.updateBalance(tech_id, 150, reduce=False)
            db.updateBalance(design_id, 75, reduce=False)

    print("Success! Fake data generated successfully.")

if __name__ == "__main__":
    seed_database()
