Django management command to seed the database with realistic test data using Faker.

Usage:
    python manage.py seed_data
    python manage.py seed_data --clear  # Clear existing data before seeding

This script creates:
- 5 Workstreams
- 5 Workstream Managers (1 per workstream)
- 8 Schools per workstream (40 total)
- 12 Grades (1-12) with descriptive names (Primary, Elementary, Middle, High School)
- For each school:
    - 1 School Manager
    - 12 Teachers with specializations
    - 6 Secretaries with department assignments
    - 50 Students distributed across grades
    - Guardians (~30 per school) linked to students as families
    - 6 Courses per grade (Math, Science, English, History, PE, Art)
    - 12 Classrooms (2 sections per grade across 6 grades)
    - Student enrollments
    - Course allocations (teacher-course-classroom assignments)
<<<<<<< HEAD
    - Assignments (homework, quizzes, exams per course)
    - Marks (student scores on assignments)
    - Learning materials per course
    - Lesson plans per course
    - Attendance records (past 4 weeks)
- Notifications (various types for all users)
- Messages between users
- Support tickets
- Staff evaluations
- User login history
- Activity logs
- System configuration entries
=======
    - Assignments and quizzes
    - Student marks/grades
    - Attendance records
    - Lesson plans
    - Learning materials/assets
    - Messages and notifications
>>>>>>> 12bb526 (work stram manager 66 bug solved)
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker
import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from workstream.models import WorkStream
from school.models import School, Grade, AcademicYear, Course, ClassRoom
from student.models import Student, StudentEnrollment
<<<<<<< HEAD
from teacher.models import Teacher, CourseAllocation, Attendance, Assignment, LearningMaterial, LessonPlan, Mark
from secretary.models import Secretary
from guardian.models import Guardian, GuardianStudentLink
from notifications.models import Notification
from user_messages.models import Message, MessageReceipt
from custom_admin.models import SupportTicket
from manager.models import StaffEvaluation
from reports.models import UserLoginHistory, ActivityLog
from accounts.models import SystemConfiguration
=======
from teacher.models import (
    Teacher,
    CourseAllocation,
    Attendance,
    Assignment,
    Mark,
    LessonPlan,
    LearningMaterial,
)
from secretary.models import Secretary
from guardian.models import Guardian, GuardianStudentLink
from user_messages.models import Message, MessageReceipt
from notifications.models import Notification
>>>>>>> 12bb526 (work stram manager 66 bug solved)

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = 'Seeds the database with realistic test data using Faker'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing seeded data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing seeded data...'))
            self.clear_seeded_data()

        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        try:
            with transaction.atomic():
                # Step 1: Create 5 Workstreams
                workstreams = self.create_workstreams(count=5)
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(workstreams)} workstreams'))

                # Step 2: Create 5 Workstream Managers (1 per workstream)
                workstream_managers = self.create_workstream_managers(workstreams)
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(workstream_managers)} workstream managers'))

                # Step 3: Create 8 schools per workstream
                all_schools = []
                for ws in workstreams:
                    schools = self.create_schools(ws, count=8)
                    all_schools.extend(schools)
                    self.stdout.write(self.style.SUCCESS(f'✓ Created {len(schools)} schools under workstream "{ws.workstream_name}"'))

                # Step 4: Create system configuration entries
                sys_configs = self.create_system_configurations(workstreams, all_schools)
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(sys_configs)} system configuration entries'))

                # Step 5: For each school, create comprehensive data
                total_school_managers = 0
                total_teachers = 0
                total_secretaries = 0
                total_students = 0
                total_guardians = 0
                total_guardian_links = 0
                total_courses = 0
                total_classrooms = 0
                total_enrollments = 0
                total_allocations = 0
                total_assignments = 0
                total_marks = 0
                total_attendance = 0
<<<<<<< HEAD
                total_assignments = 0
                total_marks = 0
                total_learning_materials = 0
                total_lesson_plans = 0
=======
                total_lesson_plans = 0
                total_learning_materials = 0
                total_messages = 0
                total_message_receipts = 0
                total_notifications = 0
>>>>>>> 12bb526 (work stram manager 66 bug solved)

                all_users = list(User.objects.all())
                all_teachers_list = []
                all_students_list = []
                all_school_manager_users = []

                for school in all_schools:
                    # Create grades for the school if they don't exist
                    grades = self.ensure_grades()

                    # Create academic year for the school
                    academic_year = self.create_academic_year(school)

                    # Create 1 School Manager
                    school_manager = self.create_school_manager(school)
                    total_school_managers += 1
                    all_users.append(school_manager)
                    all_school_manager_users.append(school_manager)

                    # Create 12 Teachers
                    teachers = self.create_teachers(school, count=12)
                    total_teachers += len(teachers)
                    all_teachers_list.extend(teachers)
                    all_users.extend([t.user for t in teachers])

                    # Create 6 Secretaries
                    secretaries = self.create_secretaries(school, count=6)
                    total_secretaries += len(secretaries)
                    all_users.extend([s.user for s in secretaries])

                    # Select 6 grades for this school (grades 4-9)
                    school_grades = grades[3:9]  # Grades 4, 5, 6, 7, 8, 9

                    # Create courses for this school (6 subjects per grade)
                    courses = self.create_courses(school, school_grades)
                    total_courses += len(courses)

                    # Create classrooms (2 sections per grade)
                    classrooms = self.create_classrooms(school, academic_year, school_grades, teachers)
                    total_classrooms += len(classrooms)

                    # Create 50 Students
                    students = self.create_students(school, school_grades, count=50)
                    total_students += len(students)
                    all_students_list.extend(students)
                    all_users.extend([s.user for s in students])

                    # Create guardians and link them to students
                    guardians, guardian_links = self.create_guardians_for_students(school, students)
                    total_guardians += len(guardians)
                    total_guardian_links += len(guardian_links)
                    all_users.extend([g.user for g in guardians])

                    # Create student enrollments
                    enrollments = self.create_enrollments(students, classrooms, academic_year)
                    total_enrollments += len(enrollments)
                    students_by_classroom = self.build_students_by_classroom(enrollments)

                    # Create course allocations (assign teachers to courses in classrooms)
                    allocations = self.create_course_allocations(courses, classrooms, teachers, academic_year)
                    total_allocations += len(allocations)

<<<<<<< HEAD
                    # Create assignments for each course allocation
                    assignments = self.create_assignments(allocations, teachers)
                    total_assignments += len(assignments)

                    # Create marks for students on assignments
                    marks = self.create_marks(assignments, students, teachers)
                    total_marks += len(marks)

                    # Create learning materials for courses
                    learning_materials = self.create_learning_materials(courses, classrooms, academic_year, teachers)
                    total_learning_materials += len(learning_materials)

                    # Create lesson plans for courses
                    lesson_plans = self.create_lesson_plans(courses, classrooms, academic_year, teachers)
                    total_lesson_plans += len(lesson_plans)

                    # Create attendance records for the past 4 weeks
                    attendance_records = self.create_attendance_records(students, allocations, teachers)
=======
                    # Create assignments/quizzes and marks
                    assignments = self.create_assignments(allocations)
                    total_assignments += len(assignments)
                    marks = self.create_marks(assignments, students_by_classroom)
                    total_marks += len(marks)

                    # Create attendance records for the past 2 weeks
                    attendance_records = self.create_attendance_records(students, allocations)
>>>>>>> 12bb526 (work stram manager 66 bug solved)
                    total_attendance += len(attendance_records)

                    # Create lesson plans and learning materials
                    lesson_plans = self.create_lesson_plans(allocations, academic_year)
                    total_lesson_plans += len(lesson_plans)
                    learning_materials = self.create_learning_materials(allocations, academic_year)
                    total_learning_materials += len(learning_materials)

                    # Create communication data (messages + notifications)
                    messages, message_receipt_count = self.create_messages(
                        workstream_manager=selected_manager,
                        school_manager=school_manager,
                        teachers=teachers,
                        secretaries=secretaries,
                        students=students,
                        guardians=guardians,
                    )
                    total_messages += len(messages)
                    total_message_receipts += message_receipt_count

                    notifications = self.create_notifications(
                        workstream_manager=selected_manager,
                        school_manager=school_manager,
                        teachers=teachers,
                        secretaries=secretaries,
                        students=students,
                        guardian_links=guardian_links,
                        assignments=assignments,
                        marks=marks,
                        attendance_records=attendance_records,
                        messages=messages,
                    )
                    total_notifications += len(notifications)

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ School "{school.school_name}": '
                            f'1 manager, {len(teachers)} teachers, {len(secretaries)} secretaries, '
                            f'{len(students)} students, {len(guardians)} guardians, '
                            f'{len(assignments)} assignments, {len(marks)} marks, '
<<<<<<< HEAD
                            f'{len(attendance_records)} attendance records'
=======
                            f'{len(attendance_records)} attendance, {len(lesson_plans)} lesson plans, '
                            f'{len(learning_materials)} materials, {len(messages)} messages, '
                            f'{len(notifications)} notifications'
>>>>>>> 12bb526 (work stram manager 66 bug solved)
                        )
                    )

                # Step 6: Create cross-school data
                self.stdout.write(self.style.SUCCESS('\nCreating cross-school data...'))

                # Notifications
                notifications = self.create_notifications(all_users)
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(notifications)} notifications'))

                # Messages
                messages, receipts = self.create_messages(all_users)
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(messages)} messages with {len(receipts)} receipts'))

                # Support tickets
                tickets = self.create_support_tickets(all_users)
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(tickets)} support tickets'))

                # Staff evaluations
                evaluations = self.create_staff_evaluations(all_school_manager_users, all_teachers_list)
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(evaluations)} staff evaluations'))

                # Login history
                login_records = self.create_login_history(all_users)
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(login_records)} login history records'))

                # Activity logs
                activity_logs = self.create_activity_logs(all_users)
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(activity_logs)} activity logs'))

                # Final summary
                self.stdout.write(self.style.SUCCESS('\n' + '='*70))
                self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
                self.stdout.write(self.style.SUCCESS('='*70))
                self.stdout.write(self.style.SUCCESS(f'Total created:'))
                self.stdout.write(self.style.SUCCESS(f'  - Workstreams: {len(workstreams)}'))
                self.stdout.write(self.style.SUCCESS(f'  - Workstream Managers: {len(workstream_managers)}'))
                self.stdout.write(self.style.SUCCESS(f'  - Schools: {len(all_schools)}'))
                self.stdout.write(self.style.SUCCESS(f'  - School Managers: {total_school_managers}'))
                self.stdout.write(self.style.SUCCESS(f'  - Teachers: {total_teachers}'))
                self.stdout.write(self.style.SUCCESS(f'  - Secretaries: {total_secretaries}'))
                self.stdout.write(self.style.SUCCESS(f'  - Students: {total_students}'))
                self.stdout.write(self.style.SUCCESS(f'  - Guardians: {total_guardians}'))
                self.stdout.write(self.style.SUCCESS(f'  - Guardian-Student Links: {total_guardian_links}'))
                self.stdout.write(self.style.SUCCESS(f'  - Courses: {total_courses}'))
                self.stdout.write(self.style.SUCCESS(f'  - Classrooms: {total_classrooms}'))
                self.stdout.write(self.style.SUCCESS(f'  - Student Enrollments: {total_enrollments}'))
                self.stdout.write(self.style.SUCCESS(f'  - Course Allocations: {total_allocations}'))
<<<<<<< HEAD
                self.stdout.write(self.style.SUCCESS(f'  - Assignments: {total_assignments}'))
                self.stdout.write(self.style.SUCCESS(f'  - Marks: {total_marks}'))
                self.stdout.write(self.style.SUCCESS(f'  - Learning Materials: {total_learning_materials}'))
                self.stdout.write(self.style.SUCCESS(f'  - Lesson Plans: {total_lesson_plans}'))
                self.stdout.write(self.style.SUCCESS(f'  - Attendance Records: {total_attendance}'))
                self.stdout.write(self.style.SUCCESS(f'  - Notifications: {len(notifications)}'))
                self.stdout.write(self.style.SUCCESS(f'  - Messages: {len(messages)}'))
                self.stdout.write(self.style.SUCCESS(f'  - Message Receipts: {len(receipts)}'))
                self.stdout.write(self.style.SUCCESS(f'  - Support Tickets: {len(tickets)}'))
                self.stdout.write(self.style.SUCCESS(f'  - Staff Evaluations: {len(evaluations)}'))
                self.stdout.write(self.style.SUCCESS(f'  - Login History: {len(login_records)}'))
                self.stdout.write(self.style.SUCCESS(f'  - Activity Logs: {len(activity_logs)}'))
                self.stdout.write(self.style.SUCCESS(f'  - System Configurations: {len(sys_configs)}'))
=======
                self.stdout.write(self.style.SUCCESS(f'  - Assignments/Quizzes: {total_assignments}'))
                self.stdout.write(self.style.SUCCESS(f'  - Marks: {total_marks}'))
                self.stdout.write(self.style.SUCCESS(f'  - Attendance Records: {total_attendance}'))
                self.stdout.write(self.style.SUCCESS(f'  - Lesson Plans: {total_lesson_plans}'))
                self.stdout.write(self.style.SUCCESS(f'  - Learning Materials: {total_learning_materials}'))
                self.stdout.write(self.style.SUCCESS(f'  - Messages: {total_messages}'))
                self.stdout.write(self.style.SUCCESS(f'  - Message Receipts: {total_message_receipts}'))
                self.stdout.write(self.style.SUCCESS(f'  - Notifications: {total_notifications}'))
>>>>>>> 12bb526 (work stram manager 66 bug solved)
                self.stdout.write(self.style.SUCCESS('\nDefault password for all users: Password123!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during seeding: {str(e)}'))
            raise

    def clear_seeded_data(self):
        """Clear seeded data (optional, use with --clear flag)"""
        # Clear in order to respect foreign key constraints
<<<<<<< HEAD
        ActivityLog.objects.all().delete()
        UserLoginHistory.objects.all().delete()
        StaffEvaluation.objects.all().delete()
        SupportTicket.objects.all().delete()
        MessageReceipt.objects.all().delete()
        Message.objects.all().delete()
        Notification.objects.all().delete()
        Mark.objects.all().delete()
        LessonPlan.objects.all().delete()
        LearningMaterial.objects.all().delete()
        Assignment.objects.all().delete()
        Attendance.objects.all().delete()  # Clear attendance records
        GuardianStudentLink.objects.all().delete()  # Clear guardian-student links first
        Guardian.objects.all().delete()  # Clear guardian profiles
        StudentEnrollment.objects.all().delete()
        CourseAllocation.objects.all().delete()
        Student.objects.all().delete()
        Teacher.objects.all().delete()
        Secretary.objects.all().delete()  # Clear secretary profiles
        ClassRoom.objects.all().delete()
        Course.objects.all().delete()
        AcademicYear.objects.all().delete()
        SystemConfiguration.objects.all().delete()
=======
        MessageReceipt.all_objects.all().delete()
        Message.all_objects.all().delete()
        Notification.all_objects.all().delete()
        LearningMaterial.all_objects.all().delete()
        LessonPlan.all_objects.all().delete()
        Mark.all_objects.all().delete()
        Attendance.all_objects.all().delete()
        Assignment.all_objects.all().delete()
        GuardianStudentLink.all_objects.all().delete()
        Guardian.all_objects.all().delete()
        StudentEnrollment.all_objects.all().delete()
        CourseAllocation.all_objects.all().delete()
        Student.all_objects.all().delete()
        Teacher.all_objects.all().delete()
        Secretary.all_objects.all().delete()
        ClassRoom.all_objects.all().delete()
        Course.all_objects.all().delete()
        AcademicYear.all_objects.all().delete()
>>>>>>> 12bb526 (work stram manager 66 bug solved)

        # Use all_objects to include soft-deleted records
        User.all_objects.filter(role__in=[
            'manager_workstream', 'manager_school', 'teacher', 'secretary', 'student', 'guardian'
        ]).delete()
        School.all_objects.all().delete()
        WorkStream.all_objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ Cleared existing seeded data'))

    def create_workstreams(self, count=5):
        """Create workstreams with realistic data"""
        workstreams = []
        regions = [
            'North', 'South', 'East', 'West', 'Central',
            'Northeast', 'Southeast', 'Northwest', 'Southwest', 'Coastal'
        ]

        for i in range(count):
            region = regions[i % len(regions)]
            workstream = WorkStream.objects.create(
                workstream_name=f"{region} Region Education District",
                description=fake.paragraph(nb_sentences=3),
                capacity=random.randint(1000, 5000),
                location=fake.city()
            )
            workstreams.append(workstream)

        return workstreams

    def create_workstream_managers(self, workstreams):
        """Create one workstream manager per workstream"""
        managers = []

        for workstream in workstreams:
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}.ws@edutracker.com"

            manager = User.objects.create_user(
                email=email,
                password='Password123!',
                full_name=f"{first_name} {last_name}",
                role='manager_workstream',
                work_stream=workstream,
                is_staff=False,
                is_superuser=False
            )

            # Link manager to workstream
            workstream.manager = manager
            workstream.save()

            managers.append(manager)

        return managers

    def create_schools(self, workstream, count=8):
        """Create schools under a workstream"""
        schools = []
        school_names = [
            ('Riverside', 'Middle'),
            ('Oak Valley', 'High'),
            ('Sunrise', 'Elementary'),
            ('Mountain View', 'Secondary'),
            ('Lakewood', 'Academy'),
            ('Cedar Park', 'Preparatory'),
            ('Greenfield', 'International'),
            ('Westridge', 'Comprehensive'),
            ('Hillcrest', 'Grammar'),
            ('Brookside', 'Primary'),
        ]

        for i in range(count):
            name_prefix, school_type = school_names[i % len(school_names)]
            school_name = f"{name_prefix} {school_type} School"

            school = School.objects.create(
                school_name=school_name,
                work_stream=workstream,
                location=fake.address(),
                capacity=random.randint(500, 1500),
                contact_email=f"info@{name_prefix.lower().replace(' ', '')}-{school_type.lower()}.edu",
                contact_phone=fake.phone_number()[:15],
                academic_year_start=datetime(2025, 9, 1).date(),
                academic_year_end=datetime(2026, 6, 30).date()
            )
            schools.append(school)

        return schools

    def create_school_manager(self, school):
        """Create a school manager for the school"""
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}.sm@edutracker.com"

        manager = User.objects.create_user(
            email=email,
            password='Password123!',
            full_name=f"{first_name} {last_name}",
            role='manager_school',
            work_stream=school.work_stream,
            school=school,
            is_staff=False,
            is_superuser=False
        )

        # Link manager to school
        school.manager = manager
        school.save()

        return manager

    def create_teachers(self, school, count=12):
        """Create teachers for the school"""
        teachers = []
        specializations = [
            'Mathematics', 'Science', 'English', 'History',
            'Physics', 'Art & Music', 'Chemistry', 'Biology',
            'Geography', 'Computer Science', 'Physical Education', 'Foreign Languages'
        ]
        employment_statuses = ['full_time', 'full_time', 'full_time', 'part_time', 'contract']

        for i in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}.t{i}@edutracker.com"

            # Create CustomUser with teacher role
            user = User.objects.create_user(
                email=email,
                password='Password123!',
                full_name=f"{first_name} {last_name}",
                role='teacher',
                work_stream=school.work_stream,
                school=school,
                is_staff=False,
                is_superuser=False
            )

            # Create Teacher profile
            teacher = Teacher.objects.create(
                user=user,
                specialization=specializations[i % len(specializations)],
                hire_date=fake.date_between(start_date='-5y', end_date='today'),
                employment_status=random.choice(employment_statuses),
                years_of_experience=random.randint(2, 15)
            )

            teachers.append(teacher)

        return teachers

    def create_secretaries(self, school, count=6):
        """Create secretaries for the school with department assignments"""
        secretaries = []

        # Realistic school department names
        departments = [
            'Administration',
            'Student Records',
            'Finance & Accounting',
            'Admissions',
            'Academic Affairs',
            'Human Resources'
        ]

        # Office number formats
        office_prefixes = ['A', 'B', 'C', 'Main']

        for i in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}.sec@edutracker.com"

            # Create CustomUser with secretary role
            user = User.objects.create_user(
                email=email,
                password='Password123!',
                full_name=f"{first_name} {last_name}",
                role='secretary',
                work_stream=school.work_stream,
                school=school,
                is_staff=False,
                is_superuser=False
            )

            # Create Secretary profile with department
            secretary = Secretary.objects.create(
                user=user,
                department=departments[i % len(departments)],
                office_number=f"{random.choice(office_prefixes)}-{random.randint(100, 299)}",
                hire_date=fake.date_between(start_date='-5y', end_date='today')
            )

            secretaries.append(secretary)

        return secretaries

    def create_courses(self, school, grades):
        """Create courses for the school"""
        courses = []
        subjects = [
            ('MATH', 'Mathematics', 'Core mathematics curriculum'),
            ('SCI', 'Science', 'General science and experiments'),
            ('ENG', 'English Language', 'Reading, writing, and literature'),
            ('HIST', 'History', 'World and national history'),
            ('PHY', 'Physical Education', 'Sports and fitness'),
            ('ART', 'Art & Music', 'Creative arts and music appreciation'),
        ]

        for grade in grades:
            for code, name, desc in subjects:
                course_code = f"{code}-G{grade.numeric_level}"
                course = Course.objects.create(
                    course_code=course_code,
                    school=school,
                    grade=grade,
                    name=f"{name} - Grade {grade.numeric_level}",
                    description=desc
                )
                courses.append(course)

        return courses

    def create_classrooms(self, school, academic_year, grades, teachers):
        """Create classrooms for the school"""
        classrooms = []
        sections = ['A', 'B']

        teacher_index = 0
        for grade in grades:
            for section in sections:
                classroom_name = f"{grade.numeric_level}{section}"

                # Assign a homeroom teacher
                homeroom_teacher = teachers[teacher_index % len(teachers)]
                teacher_index += 1

                classroom = ClassRoom.objects.create(
                    classroom_name=classroom_name,
                    school=school,
                    academic_year=academic_year,
                    grade=grade,
                    homeroom_teacher=homeroom_teacher,
                    capacity=30
                )
                classrooms.append(classroom)

        return classrooms

    def create_students(self, school, grades, count=50):
        """Create students for the school"""
        students = []
        genders = ['male', 'female']

        for i in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}.st{random.randint(1000, 9999)}@edutracker.com"

            # Select a grade for this student
            selected_grade = grades[i % len(grades)]

            # Create CustomUser with student role
            user = User.objects.create_user(
                email=email,
                password='Password123!',
                full_name=f"{first_name} {last_name}",
                role='student',
                work_stream=school.work_stream,
                school=school,
                is_staff=False,
                is_superuser=False
            )

            # Create Student profile
            student = Student.objects.create(
                user=user,
                student_id=f"STU{random.randint(10000, 99999)}",
                date_of_birth=fake.date_of_birth(minimum_age=11, maximum_age=16),
                gender=random.choice(genders),
                grade=selected_grade,
                admission_date=fake.date_between(start_date='-2y', end_date='today'),
                enrollment_status='active',
                current_gpa=round(random.uniform(2.5, 4.0), 2),
                total_absences=random.randint(0, 10)
            )

            students.append(student)

        return students

    def create_enrollments(self, students, classrooms, academic_year):
        """Enroll students in classrooms"""
        enrollments = []

        for student in students:
            # Find a classroom matching the student's grade
            matching_classrooms = [c for c in classrooms if c.grade_id == student.grade_id]

            if matching_classrooms:
                # Randomly pick one of the matching classrooms
                classroom = random.choice(matching_classrooms)

                enrollment = StudentEnrollment.objects.create(
                    student=student,
                    class_room=classroom,
                    academic_year=academic_year,
                    status='active',
                    enrollment_date=student.admission_date
                )
                enrollments.append(enrollment)

        return enrollments

    def create_course_allocations(self, courses, classrooms, teachers, academic_year):
        """Assign teachers to courses in classrooms"""
        allocations = []

        # Group courses by grade
        courses_by_grade = {}
        for course in courses:
            grade_id = course.grade_id
            if grade_id not in courses_by_grade:
                courses_by_grade[grade_id] = []
            courses_by_grade[grade_id].append(course)

        teacher_index = 0
        for classroom in classrooms:
            grade_courses = courses_by_grade.get(classroom.grade_id, [])

            for course in grade_courses:
                # Assign a teacher to this course-classroom combination
                teacher = teachers[teacher_index % len(teachers)]
                teacher_index += 1

                allocation = CourseAllocation.objects.create(
                    course=course,
                    class_room=classroom,
                    teacher=teacher,
                    academic_year=academic_year
                )
                allocations.append(allocation)

        return allocations

    def ensure_grades(self):
        """Ensure grades 1-12 exist in the database with descriptive names"""
        grades = []

        # Grade level descriptions for educational context
        grade_descriptions = {
            1: ('Grade 1 - Primary', 'First year of elementary education'),
            2: ('Grade 2 - Primary', 'Second year of elementary education'),
            3: ('Grade 3 - Primary', 'Third year of elementary education'),
            4: ('Grade 4 - Elementary', 'Fourth year of elementary education'),
            5: ('Grade 5 - Elementary', 'Fifth year of elementary education'),
            6: ('Grade 6 - Elementary', 'Final year of elementary education'),
            7: ('Grade 7 - Middle School', 'First year of middle school'),
            8: ('Grade 8 - Middle School', 'Second year of middle school'),
            9: ('Grade 9 - Middle School', 'Final year of middle school'),
            10: ('Grade 10 - High School', 'First year of high school (Sophomore)'),
            11: ('Grade 11 - High School', 'Second year of high school (Junior)'),
            12: ('Grade 12 - High School', 'Final year of high school (Senior)')
        }

        for level in range(1, 13):
            min_age = level + 5
            max_age = level + 6
            name, _ = grade_descriptions.get(level, (f'Grade {level}', ''))

            # Use all_objects so soft-deleted grades are re-used instead of causing
            # unique constraint conflicts on numeric_level.
            grade, _ = Grade.all_objects.update_or_create(
                numeric_level=level,
                defaults={
                    'name': name,
                    'min_age': min_age,
                    'max_age': max_age,
                    'is_active': True,
                    'deactivated_at': None,
                    'deactivated_by': None,
                }
            )

            grades.append(grade)

        return grades

    def create_academic_year(self, school):
        """Create an academic year for the school"""
        academic_year, created = AcademicYear.objects.get_or_create(
            school=school,
            academic_year_code="2025/2026",
            defaults={
                'start_date': datetime(2025, 9, 1).date(),
                'end_date': datetime(2026, 6, 30).date()
            }
        )
        return academic_year

    def create_guardians_for_students(self, school, students):
        """
        Create guardians and link them to students.
        Simulates realistic family structures:
        - Some students share guardians (siblings)
        - Most students have 1-2 guardians
        - Relationship types: parent, legal_guardian, foster_parent
        """
        guardians = []
        guardian_links = []

        # Group students into "families" of 1-3 students each
        families = []
        remaining_students = list(students)
        random.shuffle(remaining_students)

        while remaining_students:
            # Family size: 1-3 students (weighted towards 1-2)
            family_size = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
            family_size = min(family_size, len(remaining_students))

            family = remaining_students[:family_size]
            remaining_students = remaining_students[family_size:]
            families.append(family)

        # Create guardians for each family
        guardian_index = 0
        for family in families:
            # Each family has 1-2 guardians (weighted towards 2)
            num_guardians = random.choices([1, 2], weights=[30, 70])[0]

            family_guardians = []
            family_last_name = family[0].user.full_name.split()[-1]  # Use first student's last name

            for i in range(num_guardians):
                first_name = fake.first_name()
                # Use same last name as students for realism
                email = f"{first_name.lower()}.{family_last_name.lower()}.g{guardian_index}@edutracker.com"

                # Create CustomUser with guardian role
                user = User.objects.create_user(
                    email=email,
                    password='Password123!',
                    full_name=f"{first_name} {family_last_name}",
                    role='guardian',
                    work_stream=school.work_stream,
                    school=school,
                    is_staff=False,
                    is_superuser=False
                )

                # Create Guardian profile
                guardian = Guardian.objects.create(
                    user=user,
                    phone_number=fake.phone_number()[:15]
                )

                guardians.append(guardian)
                family_guardians.append((guardian, i == 0))  # First guardian is primary
                guardian_index += 1

            # Link all guardians to all students in this family
            for student in family:
                for guardian, is_first in family_guardians:
                    # Determine relationship type
                    relationship_type = random.choices(
                        ['parent', 'legal_guardian', 'foster_parent'],
                        weights=[85, 10, 5]
                    )[0]

                    link = GuardianStudentLink.objects.create(
                        guardian=guardian,
                        student=student,
                        relationship_type=relationship_type,
                        is_primary=is_first,  # First guardian is primary
                        can_pickup=True
                    )
                    guardian_links.append(link)

        return guardians, guardian_links

    def build_students_by_classroom(self, enrollments):
        """Build a fast lookup of students keyed by classroom id."""
        students_by_classroom = {}
        for enrollment in enrollments:
            students_by_classroom.setdefault(enrollment.class_room_id, []).append(enrollment.student)
        return students_by_classroom

    def create_assignments(self, allocations):
        """Create assignment/quiz records for each course allocation."""
        assignments = []
        assignment_templates = [
            "Unit Review",
            "Chapter Practice",
            "Progress Quiz",
            "Weekly Homework",
            "Project Milestone",
            "Concept Check",
        ]
        assignment_types = ["assignment", "quiz", "homework", "project", "midterm", "participation"]
        full_marks = [10, 20, 25, 50, 100]

        for allocation in allocations:
            assignment_count = random.randint(2, 4)

            for idx in range(assignment_count):
                assignment_type = random.choice(assignment_types)
                due_date = timezone.now() + timedelta(days=random.randint(-14, 28), hours=random.randint(1, 18))
                assigned_date = (due_date - timedelta(days=random.randint(3, 12))).date()
                full_mark = Decimal(str(random.choice(full_marks)))

                assignment = Assignment.objects.create(
                    assignment_code=f"ASG-{allocation.id}-{idx + 1:02d}",
                    course_allocation=allocation,
                    created_by=allocation.teacher,
                    title=f"{random.choice(assignment_templates)} - {allocation.course.name}",
                    description=fake.paragraph(nb_sentences=3),
                    assignment_type=assignment_type,
                    exam_type=assignment_type,
                    full_mark=full_mark,
                    weight=Decimal("1.00"),
                    assigned_date=assigned_date,
                    due_date=due_date,
                    instructions_url=fake.url() if random.random() < 0.35 else "",
                    is_published=random.random() < 0.9,
                )
                assignments.append(assignment)

        return assignments

    def grade_from_percentage(self, percentage):
        """Convert percentage to letter grade."""
        value = float(percentage)
        if value >= 90:
            return "A"
        if value >= 80:
            return "B"
        if value >= 70:
            return "C"
        if value >= 60:
            return "D"
        return "F"

    def create_marks(self, assignments, students_by_classroom):
        """Create marks for assignments per classroom enrollment."""
        marks = []
        now = timezone.now()
        feedback_options = [
            "Excellent progress.",
            "Good effort, keep practicing.",
            "Needs revision on key concepts.",
            "Great participation and understanding.",
            "Satisfactory work, improve presentation.",
            "",
        ]

        for assignment in assignments:
            if not assignment.course_allocation_id:
                continue

            class_students = students_by_classroom.get(assignment.course_allocation.class_room_id, [])
            if not class_students:
                continue

            for student in class_students:
                # Keep some assignments pending grading for realism.
                if assignment.due_date and assignment.due_date > now and random.random() < 0.65:
                    continue
                if random.random() < 0.12:
                    continue

                max_score = assignment.full_mark
                percentage = Decimal(str(round(random.uniform(45, 100), 2)))
                score = (max_score * percentage / Decimal("100")).quantize(Decimal("0.01"))
                is_final = bool(assignment.due_date and assignment.due_date <= now)

                mark = Mark.objects.create(
                    student=student,
                    assignment=assignment,
                    score=score,
                    max_score=max_score,
                    percentage=percentage,
                    letter_grade=self.grade_from_percentage(percentage),
                    feedback=random.choice(feedback_options),
                    graded_by=assignment.created_by,
                    graded_at=now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23)),
                    is_final=is_final,
                )
                marks.append(mark)

        return marks

    def create_lesson_plans(self, allocations, academic_year):
        """Create lesson plans for course allocations."""
        plans = []
        for allocation in allocations:
            plan_count = random.randint(1, 2)

            for idx in range(plan_count):
                plan_date = timezone.now().date() + timedelta(days=random.randint(-10, 21))
                plan = LessonPlan.objects.create(
                    course=allocation.course,
                    classroom=allocation.class_room,
                    academic_year=academic_year,
                    teacher=allocation.teacher,
                    title=f"Lesson {idx + 1}: {allocation.course.name}",
                    content=fake.paragraph(nb_sentences=6),
                    objectives=fake.paragraph(nb_sentences=2),
                    resources_needed=fake.sentence(nb_words=12),
                    date_planned=plan_date,
                    is_published=random.random() < 0.8,
                )
                plans.append(plan)

        return plans

    def create_learning_materials(self, allocations, academic_year):
        """Create downloadable learning materials (assets)."""
        materials = []
        file_types = ["pdf", "pptx", "docx", "xlsx", "mp4"]

        for allocation in allocations:
            material_count = random.randint(1, 2)
            for idx in range(material_count):
                file_ext = random.choice(file_types)
                material_code = f"MAT-{allocation.id}-{idx + 1:02d}"
                material = LearningMaterial.objects.create(
                    material_code=material_code,
                    course=allocation.course,
                    classroom=allocation.class_room,
                    academic_year=academic_year,
                    uploaded_by=allocation.teacher.user,
                    title=f"{allocation.course.name} Resource {idx + 1}",
                    description=fake.sentence(nb_words=16),
                    file_url=f"/media/materials/{material_code.lower()}.{file_ext}",
                    file_type=file_ext,
                    file_size=random.randint(120_000, 6_500_000),
                )
                materials.append(material)

        return materials

    def create_messages(self, workstream_manager, school_manager, teachers, secretaries, students, guardians):
        """Create realistic threaded communication between roles."""
        teacher_users = [teacher.user for teacher in teachers]
        secretary_users = [secretary.user for secretary in secretaries]
        student_users = [student.user for student in students]
        guardian_users = [guardian.user for guardian in guardians]

        staff_users = [workstream_manager, school_manager, *teacher_users, *secretary_users]
        all_users = staff_users + student_users + guardian_users

        # Deduplicate users while preserving order.
        unique_users = []
        seen_user_ids = set()
        for user in all_users:
            if user and user.id not in seen_user_ids:
                seen_user_ids.add(user.id)
                unique_users.append(user)

        messages = []
        message_receipt_count = 0
        subjects = [
            "Attendance Follow-up",
            "Assignment Clarification",
            "Progress Update",
            "Class Schedule Notice",
            "Parent Meeting Request",
            "Support Needed",
            "Weekly Academic Review",
        ]

        if len(unique_users) < 2:
            return messages, message_receipt_count

        thread_count = max(12, len(students) // 2)
        for _ in range(thread_count):
            sender = random.choice(unique_users)
            recipient_pool = [user for user in unique_users if user.id != sender.id]
            if not recipient_pool:
                continue

            recipient_count = 1 if random.random() < 0.85 else min(2, len(recipient_pool))
            recipients = random.sample(recipient_pool, k=recipient_count)

            message = Message.objects.create(
                sender=sender,
                subject=random.choice(subjects),
                body=fake.paragraph(nb_sentences=3),
            )
            message.recipients.add(*recipients)
            messages.append(message)
            message_receipt_count += len(recipients)

            for receipt in message.receipts.all():
                if random.random() < 0.65:
                    receipt.is_read = True
                    receipt.read_at = timezone.now() - timedelta(hours=random.randint(1, 96))
                    receipt.save(update_fields=["is_read", "read_at"])

            # Add reply in the same thread for realism.
            if random.random() < 0.65:
                replier = random.choice(recipients)
                reply = Message.objects.create(
                    sender=replier,
                    subject=f"Re: {message.subject}",
                    body=fake.paragraph(nb_sentences=2),
                    parent_message=message,
                    thread_id=message.thread_id,
                )
                reply.recipients.add(sender)
                messages.append(reply)
                message_receipt_count += 1

                for receipt in reply.receipts.all():
                    if random.random() < 0.7:
                        receipt.is_read = True
                        receipt.read_at = timezone.now() - timedelta(hours=random.randint(1, 48))
                        receipt.save(update_fields=["is_read", "read_at"])

        return messages, message_receipt_count

    def maybe_mark_notification_read(self, notification, read_probability=0.35):
        """Randomly mark seeded notifications as read to mimic real usage."""
        if random.random() < read_probability:
            notification.is_read = True
            notification.read_at = timezone.now() - timedelta(hours=random.randint(1, 96))
            notification.save(update_fields=["is_read", "read_at"])

    def create_notifications(
        self,
        workstream_manager,
        school_manager,
        teachers,
        secretaries,
        students,
        guardian_links,
        assignments,
        marks,
        attendance_records,
        messages,
    ):
        """Create notifications for assignments, marks, attendance, announcements, and messages."""
        notifications = []
        teacher_users = [teacher.user for teacher in teachers]
        secretary_users = [secretary.user for secretary in secretaries]

        # Workstream announcement for school staff.
        for recipient in [school_manager, *teacher_users, *secretary_users]:
            notification = Notification.objects.create(
                sender=workstream_manager,
                recipient=recipient,
                title="Workstream Academic Update",
                message="Please review this week's teaching and attendance targets.",
                notification_type="announcement",
                action_url="/dashboard",
            )
            self.maybe_mark_notification_read(notification, read_probability=0.55)
            notifications.append(notification)

        # Assignment reminders for students.
        for student in students:
            student_assignments = [
                assignment for assignment in assignments
                if assignment.course_allocation.class_room.grade_id == student.grade_id
            ]
            if not student_assignments:
                continue

            assignment = random.choice(student_assignments)
            notification = Notification.objects.create(
                sender=assignment.created_by.user,
                recipient=student.user,
                title=f"Upcoming: {assignment.title}",
                message="You have an assignment/quiz due soon. Review the instructions and submit on time.",
                notification_type="assignment_due",
                action_url="/student/assessments",
                related_object_type="assignment",
                related_object_id=assignment.id,
            )
            self.maybe_mark_notification_read(notification, read_probability=0.25)
            notifications.append(notification)

        # Grade posted notifications for students.
        marks_by_student = {}
        for mark in marks:
            marks_by_student.setdefault(mark.student_id, []).append(mark)

        for student in students:
            if student.user_id not in marks_by_student:
                continue
            mark = random.choice(marks_by_student[student.user_id])
            notification = Notification.objects.create(
                sender=mark.graded_by.user if mark.graded_by else school_manager,
                recipient=student.user,
                title=f"Grade Posted: {mark.assignment.title}",
                message=f"Score: {mark.score}/{mark.max_score} ({mark.percentage}%).",
                notification_type="grade_posted",
                action_url="/student/grades",
                related_object_type="mark",
                related_object_id=mark.id,
            )
            self.maybe_mark_notification_read(notification, read_probability=0.2)
            notifications.append(notification)

        # Attendance notifications for guardians.
        attendance_by_student = {}
        for record in attendance_records:
            attendance_by_student.setdefault(record.student_id, []).append(record)

        sent_guardian_ids = set()
        for link in guardian_links:
            if link.guardian_id in sent_guardian_ids:
                continue
            student_attendance = attendance_by_student.get(link.student_id, [])
            if not student_attendance:
                continue
            latest = max(student_attendance, key=lambda item: item.date)

            notification = Notification.objects.create(
                sender=latest.recorded_by.user if latest.recorded_by else school_manager,
                recipient=link.guardian.user,
                title=f"Attendance Update for {link.student.user.full_name}",
                message=f"Status on {latest.date}: {latest.status}.",
                notification_type="attendance_marked",
                action_url="/guardian/attendance",
                related_object_type="attendance",
                related_object_id=latest.id,
            )
            self.maybe_mark_notification_read(notification, read_probability=0.3)
            notifications.append(notification)
            sent_guardian_ids.add(link.guardian_id)

        # Message notifications for recipients.
        for message in messages:
            for receipt in message.receipts.all():
                notification = Notification.objects.create(
                    sender=message.sender,
                    recipient=receipt.recipient,
                    title=f"New Message: {message.subject or 'No Subject'}",
                    message="You received a new message in your communication inbox.",
                    notification_type="message_received",
                    action_url="/communication",
                    related_object_type="message",
                    related_object_id=message.id,
                )
                self.maybe_mark_notification_read(notification, read_probability=0.4)
                notifications.append(notification)

        return notifications

    def create_attendance_records(self, students, allocations):
        """
        Create realistic attendance records for the past 4 weeks.
        Most students are present (85%), some are absent (8%), late (5%), or excused (2%).
        """
        records = []
        today = datetime.now().date()

        # Generate records for the past 20 weekdays (4 weeks)
        dates = []
        current = today
        while len(dates) < 20:
            if current.weekday() < 5:  # Monday to Friday
                dates.append(current)
            current -= timedelta(days=1)

        # Get allocations for creating attendance
        if not allocations:
            return records

        for student in students:
            # Find a course allocation for this student (by grade)
            student_allocations = [
                a for a in allocations
                if a.class_room.grade_id == student.grade_id
            ]

            if not student_allocations:
                continue

            # Pick one allocation for this student
            allocation = random.choice(student_allocations)
            teacher = allocation.teacher

            for date in dates:
                # Skip randomly (not every student has record every day)
                if random.random() < 0.1:  # 10% chance to skip
                    continue

                # Determine status with weighted randomness
                status = random.choices(
                    ['present', 'absent', 'late', 'excused'],
                    weights=[85, 8, 5, 2]
                )[0]

                # Add notes for non-present statuses
                note = None
                if status == 'absent':
                    note = random.choice([
                        'Medical leave',
                        'Family emergency',
                        'Not feeling well',
                        None
                    ])
                elif status == 'late':
                    note = random.choice([
                        'Traffic delay',
                        'Bus was late',
                        '10 minutes late',
                        None
                    ])
                elif status == 'excused':
                    note = random.choice([
                        'Doctor appointment',
                        'School event',
                        'Prior approval',
                        None
                    ])

                try:
                    record = Attendance.objects.create(
                        student=student,
                        course_allocation=allocation,
                        date=date,
                        status=status,
                        note=note,
                        recorded_by=teacher
                    )
                    records.append(record)
                except Exception:
                    # Skip if unique constraint violation (already exists)
                    pass

        return records

    def create_assignments(self, allocations, teachers):
        """Create assignments for each course allocation (homework, quizzes, exams)"""
        assignments = []
        assignment_templates = [
            ('homework', 'Homework', 20.0, 0.10),
            ('quiz', 'Quiz', 30.0, 0.15),
            ('assignment', 'Assignment', 50.0, 0.15),
            ('midterm', 'Midterm Exam', 100.0, 0.25),
            ('project', 'Project', 80.0, 0.20),
            ('final', 'Final Exam', 100.0, 0.30),
            ('participation', 'Class Participation', 10.0, 0.05),
        ]

        counter = Assignment.objects.count()
        today = datetime.now().date()

        for allocation in allocations:
            course_name = allocation.course.name
            teacher = allocation.teacher

            for atype, label, full_mark, weight in assignment_templates:
                counter += 1
                assignment_code = f"ASGN-{counter:05d}"

                assigned_date = fake.date_between(start_date='-60d', end_date='today')
                due_date = datetime.combine(
                    assigned_date + timedelta(days=random.randint(3, 21)),
                    datetime.min.time()
                )

                try:
                    assignment = Assignment.objects.create(
                        assignment_code=assignment_code,
                        course_allocation=allocation,
                        created_by=teacher,
                        title=f"{label} - {course_name}",
                        description=fake.paragraph(nb_sentences=2),
                        assignment_type=atype,
                        full_mark=full_mark,
                        weight=weight,
                        assigned_date=assigned_date,
                        due_date=due_date,
                        is_published=random.choice([True, True, True, False]),
                    )
                    assignments.append(assignment)
                except Exception:
                    pass

        return assignments

    def create_marks(self, assignments, students, teachers):
        """Create marks for students on assignments"""
        marks = []

        for assignment in assignments:
            # Find students in the same grade as the assignment's classroom
            grade_id = assignment.course_allocation.class_room.grade_id
            grade_students = [s for s in students if s.grade_id == grade_id]

            if not grade_students:
                continue

            teacher = assignment.created_by
            full_mark = float(assignment.full_mark)

            for student in grade_students:
                # 80% chance of having a mark (some haven't submitted)
                if random.random() < 0.2:
                    continue

                score = round(random.uniform(full_mark * 0.3, full_mark), 2)
                percentage = round((score / full_mark) * 100, 2) if full_mark > 0 else 0

                # Determine letter grade
                if percentage >= 90:
                    letter = 'A'
                elif percentage >= 80:
                    letter = 'B'
                elif percentage >= 70:
                    letter = 'C'
                elif percentage >= 60:
                    letter = 'D'
                else:
                    letter = 'F'

                feedback_options = [
                    'Good work!', 'Excellent effort.', 'Needs improvement.',
                    'Well done.', 'Keep it up!', 'Please review the material.',
                    'Great understanding shown.', 'Satisfactory.',
                    None, None, None,
                ]

                try:
                    mark = Mark.objects.create(
                        student=student,
                        assignment=assignment,
                        score=score,
                        max_score=full_mark,
                        percentage=percentage,
                        letter_grade=letter,
                        feedback=random.choice(feedback_options),
                        graded_by=teacher,
                        graded_at=timezone.now() - timedelta(days=random.randint(0, 14)),
                        is_final=random.choice([True, False]),
                    )
                    marks.append(mark)
                except Exception:
                    pass

        return marks

    def create_learning_materials(self, courses, classrooms, academic_year, teachers):
        """Create learning materials for courses"""
        materials = []
        material_types = [
            ('pdf', 'PDF Document'),
            ('pptx', 'PowerPoint Presentation'),
            ('docx', 'Word Document'),
            ('mp4', 'Video Lecture'),
            ('xlsx', 'Spreadsheet'),
        ]

        counter = LearningMaterial.objects.count()

        for course in courses:
            matching_classrooms = [c for c in classrooms if c.grade_id == course.grade_id]
            if not matching_classrooms:
                continue

            classroom = matching_classrooms[0]
            teacher = random.choice(teachers)

            # 2-4 materials per course
            num_materials = random.randint(2, 4)
            for j in range(num_materials):
                counter += 1
                file_type, type_desc = random.choice(material_types)

                try:
                    material = LearningMaterial.objects.create(
                        material_code=f"MAT-{counter:05d}",
                        course=course,
                        classroom=classroom,
                        academic_year=academic_year,
                        uploaded_by=teacher.user,
                        title=f"{course.name} - {type_desc} {j + 1}",
                        description=fake.sentence(),
                        file_url=f"https://storage.edutracker.com/materials/{counter}.{file_type}",
                        file_type=file_type,
                        file_size=random.randint(50000, 50000000),
                    )
                    materials.append(material)
                except Exception:
                    pass

        return materials

    def create_lesson_plans(self, courses, classrooms, academic_year, teachers):
        """Create lesson plans for courses"""
        plans = []
        today = datetime.now().date()

        for course in courses:
            matching_classrooms = [c for c in classrooms if c.grade_id == course.grade_id]
            if not matching_classrooms:
                continue

            classroom = matching_classrooms[0]
            teacher = random.choice(teachers)

            # 3-5 lesson plans per course
            num_plans = random.randint(3, 5)
            for j in range(num_plans):
                plan_date = today + timedelta(days=random.randint(-30, 30))

                try:
                    plan = LessonPlan.objects.create(
                        course=course,
                        classroom=classroom,
                        academic_year=academic_year,
                        teacher=teacher,
                        title=f"Week {j + 1} - {course.name}",
                        content=fake.paragraph(nb_sentences=5),
                        objectives=fake.paragraph(nb_sentences=3),
                        resources_needed=', '.join(fake.words(nb=4)),
                        date_planned=plan_date,
                        is_published=random.choice([True, True, False]),
                    )
                    plans.append(plan)
                except Exception:
                    pass

        return plans

    def create_notifications(self, all_users):
        """Create notifications for users"""
        notifications = []
        notification_types = [
            'grade_posted', 'assignment_due', 'attendance_marked',
            'announcement', 'message_received', 'account_change', 'system'
        ]

        notification_templates = {
            'grade_posted': ('New Grade Posted', 'Your grade for {subject} has been posted.'),
            'assignment_due': ('Assignment Due Soon', 'Reminder: {subject} assignment is due tomorrow.'),
            'attendance_marked': ('Attendance Recorded', 'Your attendance for today has been marked as {status}.'),
            'announcement': ('School Announcement', '{announcement}'),
            'message_received': ('New Message', 'You have received a new message from {sender}.'),
            'account_change': ('Account Updated', 'Your account settings have been updated.'),
            'system': ('System Notification', 'System maintenance scheduled for this weekend.'),
        }

        # Create 500 notifications across users
        sample_users = random.choices(all_users, k=min(500, len(all_users) * 3))

        for recipient in sample_users:
            ntype = random.choice(notification_types)
            title, message_template = notification_templates[ntype]

            message = message_template.format(
                subject=random.choice(['Mathematics', 'Science', 'English', 'History']),
                status=random.choice(['present', 'absent', 'late']),
                announcement=fake.sentence(),
                sender=fake.name(),
            )

            sender = random.choice(all_users) if random.random() > 0.2 else None

            try:
                notification = Notification.objects.create(
                    sender=sender,
                    recipient=recipient,
                    title=title,
                    message=message,
                    notification_type=ntype,
                    is_read=random.choice([True, False, False]),
                    read_at=timezone.now() - timedelta(hours=random.randint(0, 168)) if random.random() > 0.5 else None,
                )
                notifications.append(notification)
            except Exception:
                pass

        return notifications

    def create_messages(self, all_users):
        """Create messages between users"""
        messages = []
        receipts = []

        # Create 200 message threads
        for _ in range(200):
            sender = random.choice(all_users)
            num_recipients = random.randint(1, 5)
            recipient_list = random.sample(
                [u for u in all_users if u != sender],
                min(num_recipients, len(all_users) - 1)
            )

            if not recipient_list:
                continue

            thread_id = uuid.uuid4()
            subject = random.choice([
                'Meeting Tomorrow',
                'Grade Report Update',
                'Upcoming Event',
                'Question about Assignment',
                'Parent-Teacher Conference',
                'Schedule Change',
                'Field Trip Permission',
                'Academic Progress',
                'Attendance Notice',
                'Important Announcement',
            ])

            try:
                message = Message.objects.create(
                    sender=sender,
                    subject=subject,
                    body=fake.paragraph(nb_sentences=random.randint(2, 6)),
                    thread_id=thread_id,
                    is_draft=False,
                )
                messages.append(message)

                for recipient in recipient_list:
                    receipt = MessageReceipt.objects.create(
                        message=message,
                        recipient=recipient,
                        is_read=random.choice([True, False]),
                        read_at=timezone.now() - timedelta(hours=random.randint(0, 72)) if random.random() > 0.4 else None,
                    )
                    receipts.append(receipt)

                # 40% chance of a reply in the thread
                if random.random() < 0.4 and recipient_list:
                    reply_sender = random.choice(recipient_list)
                    reply = Message.objects.create(
                        sender=reply_sender,
                        subject=f"Re: {subject}",
                        body=fake.paragraph(nb_sentences=random.randint(1, 4)),
                        parent_message=message,
                        thread_id=thread_id,
                        is_draft=False,
                    )
                    messages.append(reply)

                    reply_receipt = MessageReceipt.objects.create(
                        message=reply,
                        recipient=sender,
                        is_read=random.choice([True, False]),
                    )
                    receipts.append(reply_receipt)

            except Exception:
                pass

        return messages, receipts

    def create_support_tickets(self, all_users):
        """Create support tickets from various users"""
        tickets = []
        ticket_subjects = [
            'Cannot access my account',
            'Grade not showing correctly',
            'Need password reset',
            'Attendance record is wrong',
            'Cannot download materials',
            'System is slow',
            'Profile information needs update',
            'Missing course enrollment',
            'Schedule conflict',
            'Technical issue with dashboard',
            'Request for new feature',
            'Data export not working',
            'Permission access issue',
            'Report generation error',
            'Mobile app not syncing',
        ]

        # Create 100 support tickets
        for i in range(100):
            user = random.choice(all_users)
            subject = random.choice(ticket_subjects)

            try:
                ticket = SupportTicket.objects.create(
                    subject=subject,
                    description=fake.paragraph(nb_sentences=3),
                    priority=random.choices(
                        ['low', 'medium', 'high'],
                        weights=[30, 50, 20]
                    )[0],
                    status=random.choices(
                        ['open', 'in_progress', 'closed'],
                        weights=[40, 30, 30]
                    )[0],
                    created_by=user,
                    assigned_to=random.choice(all_users) if random.random() > 0.3 else None,
                )
                tickets.append(ticket)
            except Exception:
                pass

        return tickets

    def create_staff_evaluations(self, manager_users, teachers):
        """Create staff evaluations by managers for teachers"""
        evaluations = []

        if not manager_users or not teachers:
            return evaluations

        # Each manager evaluates several teachers
        for manager in manager_users:
            # Evaluate 3-6 random teachers
            num_evaluations = min(random.randint(3, 6), len(teachers))
            evaluated_teachers = random.sample(teachers, num_evaluations)

            for teacher in evaluated_teachers:
                try:
                    evaluation = StaffEvaluation.objects.create(
                        reviewer=manager,
                        reviewee=teacher.user,
                        evaluation_date=fake.date_between(start_date='-6m', end_date='today'),
                        rating_score=random.randint(1, 10),
                        comments=random.choice([
                            'Excellent teaching methods and classroom management.',
                            'Good performance overall. Shows dedication to students.',
                            'Meets expectations. Could improve in student engagement.',
                            'Outstanding contribution to the school community.',
                            'Satisfactory performance. Recommended for professional development.',
                            'Very effective in curriculum delivery.',
                            'Strong communication skills with parents and staff.',
                            None,
                        ]),
                    )
                    evaluations.append(evaluation)
                except Exception:
                    pass

        return evaluations

    def create_login_history(self, all_users):
        """Create login history records for users"""
        records = []

        # Create 1000 login records across users
        for _ in range(1000):
            user = random.choice(all_users)

            try:
                record = UserLoginHistory.objects.create(
                    user=user,
                    ip_address=fake.ipv4(),
                    user_agent=random.choice([
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)',
                        'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X)',
                        'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36',
                    ]),
                )
                records.append(record)
            except Exception:
                pass

        return records

    def create_activity_logs(self, all_users):
        """Create activity log entries"""
        logs = []
        action_types = ['CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'EXPORT']
        entity_types = [
            'Student', 'Teacher', 'Course', 'ClassRoom', 'Assignment',
            'Mark', 'Attendance', 'Enrollment', 'School', 'User'
        ]

        descriptions = {
            'CREATE': 'Created a new {entity}',
            'UPDATE': 'Updated {entity} record',
            'DELETE': 'Deleted {entity} record',
            'LOGIN': 'User logged in to the system',
            'LOGOUT': 'User logged out of the system',
            'EXPORT': 'Exported {entity} data to CSV',
        }

        # Create 1500 activity logs
        for _ in range(1500):
            user = random.choice(all_users)
            action = random.choice(action_types)
            entity = random.choice(entity_types)

            try:
                log = ActivityLog.objects.create(
                    actor=user,
                    action_type=action,
                    entity_type=entity,
                    entity_id=str(random.randint(1, 5000)),
                    description=descriptions.get(action, 'Performed action on {entity}').format(entity=entity),
                    ip_address=fake.ipv4(),
                )
                logs.append(log)
            except Exception:
                pass

        return logs

    def create_system_configurations(self, workstreams, schools):
        """Create system configuration entries"""
        configs = []

        # Global configurations
        global_configs = {
            'max_students_per_class': '35',
            'grading_scale': 'A,B,C,D,F',
            'academic_year_format': 'YYYY/YYYY',
            'default_language': 'en',
            'attendance_threshold': '75',
            'max_absence_before_alert': '5',
            'enable_sms_notifications': 'true',
            'report_generation_format': 'pdf',
            'session_timeout_minutes': '30',
            'password_min_length': '8',
        }

        for key, value in global_configs.items():
            try:
                config = SystemConfiguration.objects.create(
                    config_key=key,
                    config_value=value,
                )
                configs.append(config)
            except Exception:
                pass

        # Per-workstream configurations
        for ws in workstreams:
            ws_configs = {
                'timezone': random.choice(['UTC', 'US/Eastern', 'US/Central', 'US/Pacific', 'Europe/London']),
                'currency': random.choice(['USD', 'EUR', 'GBP']),
                'school_week_days': '5',
            }
            for key, value in ws_configs.items():
                try:
                    config = SystemConfiguration.objects.create(
                        work_stream=ws,
                        config_key=key,
                        config_value=value,
                    )
                    configs.append(config)
                except Exception:
                    pass

        # Per-school configurations
        for school in schools:
            school_configs = {
                'bell_schedule': '08:00,09:00,10:00,11:00,12:00,13:00,14:00,15:00',
                'max_class_size': str(random.randint(25, 40)),
            }
            for key, value in school_configs.items():
                try:
                    config = SystemConfiguration.objects.create(
                        school=school,
                        config_key=key,
                        config_value=value,
                    )
                    configs.append(config)
                except Exception:
                    pass

        return configs
