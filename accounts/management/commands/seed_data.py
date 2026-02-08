"""
Django management command to seed the database with realistic test data using Faker.

Usage:
    python manage.py seed_data
    python manage.py seed_data --clear  # Clear existing data before seeding

This script creates:
- 2 Workstreams
- 2 Workstream Managers (1 per workstream)
- 4 Schools (under one selected workstream)
- 12 Grades (1-12) with descriptive names (Primary, Elementary, Middle, High School)
- For each school:
    - 1 School Manager
    - 6 Teachers with specializations
    - 3 Secretaries with department assignments (Administration, Student Records, etc.)
    - 15 Students distributed across grades
    - 6 Courses per grade (Math, Science, English, History, PE, Art)
    - 6 Classrooms (2 sections per grade)
    - Student enrollments
    - Course allocations (teacher-course-classroom assignments)
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from faker import Faker
import random
from datetime import datetime, timedelta

from workstream.models import WorkStream
from school.models import School, Grade, AcademicYear, Course, ClassRoom
from student.models import Student, StudentEnrollment
from teacher.models import Teacher, CourseAllocation
from secretary.models import Secretary

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
                # Step 1: Create 2 Workstreams
                workstreams = self.create_workstreams(count=2)
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(workstreams)} workstreams'))

                # Step 2: Create 2 Workstream Managers (1 per workstream)
                workstream_managers = self.create_workstream_managers(workstreams)
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(workstream_managers)} workstream managers'))

                # Step 3: Select one workstream manager and create 4 schools
                selected_manager = workstream_managers[0]
                selected_workstream = selected_manager.work_stream
                schools = self.create_schools(selected_workstream, count=4)
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(schools)} schools under workstream "{selected_workstream.workstream_name}"'))

                # Step 4: For each school, create comprehensive data
                total_school_managers = 0
                total_teachers = 0
                total_secretaries = 0
                total_students = 0
                total_courses = 0
                total_classrooms = 0
                total_enrollments = 0
                total_allocations = 0

                for school in schools:
                    # Create grades for the school if they don't exist
                    grades = self.ensure_grades()

                    # Create academic year for the school
                    academic_year = self.create_academic_year(school)

                    # Create 1 School Manager
                    school_manager = self.create_school_manager(school)
                    total_school_managers += 1

                    # Create 6 Teachers (more than before)
                    teachers = self.create_teachers(school, count=6)
                    total_teachers += len(teachers)

                    # Create 3 Secretaries
                    secretaries = self.create_secretaries(school, count=3)
                    total_secretaries += len(secretaries)

                    # Select 3 grades for this school (e.g., grades 7-9 for middle school)
                    school_grades = grades[6:9]  # Grade 7, 8, 9

                    # Create courses for this school (6 subjects per grade)
                    courses = self.create_courses(school, school_grades)
                    total_courses += len(courses)

                    # Create classrooms (1 classroom per grade)
                    classrooms = self.create_classrooms(school, academic_year, school_grades, teachers)
                    total_classrooms += len(classrooms)

                    # Create 15 Students (more realistic)
                    students = self.create_students(school, school_grades, count=15)
                    total_students += len(students)

                    # Create student enrollments
                    enrollments = self.create_enrollments(students, classrooms, academic_year)
                    total_enrollments += len(enrollments)

                    # Create course allocations (assign teachers to courses in classrooms)
                    allocations = self.create_course_allocations(courses, classrooms, teachers, academic_year)
                    total_allocations += len(allocations)

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ School "{school.school_name}": '
                            f'1 manager, {len(teachers)} teachers, {len(secretaries)} secretaries, '
                            f'{len(students)} students, {len(courses)} courses, {len(classrooms)} classrooms'
                        )
                    )

                # Final summary
                self.stdout.write(self.style.SUCCESS('\n' + '='*70))
                self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
                self.stdout.write(self.style.SUCCESS('='*70))
                self.stdout.write(self.style.SUCCESS(f'Total created:'))
                self.stdout.write(self.style.SUCCESS(f'  - Workstreams: {len(workstreams)}'))
                self.stdout.write(self.style.SUCCESS(f'  - Workstream Managers: {len(workstream_managers)}'))
                self.stdout.write(self.style.SUCCESS(f'  - Schools: {len(schools)}'))
                self.stdout.write(self.style.SUCCESS(f'  - School Managers: {total_school_managers}'))
                self.stdout.write(self.style.SUCCESS(f'  - Teachers: {total_teachers}'))
                self.stdout.write(self.style.SUCCESS(f'  - Secretaries: {total_secretaries}'))
                self.stdout.write(self.style.SUCCESS(f'  - Students: {total_students}'))
                self.stdout.write(self.style.SUCCESS(f'  - Courses: {total_courses}'))
                self.stdout.write(self.style.SUCCESS(f'  - Classrooms: {total_classrooms}'))
                self.stdout.write(self.style.SUCCESS(f'  - Student Enrollments: {total_enrollments}'))
                self.stdout.write(self.style.SUCCESS(f'  - Course Allocations: {total_allocations}'))
                self.stdout.write(self.style.SUCCESS('\nDefault password for all users: Password123!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during seeding: {str(e)}'))
            raise

    def clear_seeded_data(self):
        """Clear seeded data (optional, use with --clear flag)"""
        # Clear in order to respect foreign key constraints
        StudentEnrollment.objects.all().delete()
        CourseAllocation.objects.all().delete()
        Student.objects.all().delete()
        Teacher.objects.all().delete()
        Secretary.objects.all().delete()  # Clear secretary profiles
        ClassRoom.objects.all().delete()
        Course.objects.all().delete()
        AcademicYear.objects.all().delete()

        # Use all_objects to include soft-deleted records
        User.all_objects.filter(role__in=[
            'manager_workstream', 'manager_school', 'teacher', 'secretary', 'student'
        ]).delete()
        School.all_objects.all().delete()
        WorkStream.all_objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ Cleared existing seeded data'))

    def create_workstreams(self, count=2):
        """Create workstreams with realistic data"""
        workstreams = []
        regions = ['North', 'South', 'East', 'West', 'Central']

        for i in range(count):
            region = regions[i % len(regions)]
            workstream = WorkStream.objects.create(
                workstream_name=f"{region} Region Education District",
                description=fake.paragraph(nb_sentences=3),
                capacity=random.randint(500, 2000),
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

    def create_schools(self, workstream, count=4):
        """Create schools under a workstream"""
        schools = []
        school_names = [
            ('Riverside', 'Middle'),
            ('Oak Valley', 'High'),
            ('Sunrise', 'Elementary'),
            ('Mountain View', 'Secondary')
        ]

        for i in range(count):
            name_prefix, school_type = school_names[i % len(school_names)]
            school_name = f"{name_prefix} {school_type} School"

            school = School.objects.create(
                school_name=school_name,
                work_stream=workstream,
                location=fake.address(),
                capacity=random.randint(300, 800),
                contact_email=f"info@{name_prefix.lower()}{school_type.lower()}.edu",
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

    def create_teachers(self, school, count=6):
        """Create teachers for the school"""
        teachers = []
        specializations = [
            'Mathematics', 'Science', 'English', 'History',
            'Physics', 'Art & Music'
        ]
        employment_statuses = ['full_time', 'full_time', 'full_time', 'part_time']

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

    def create_secretaries(self, school, count=3):
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

    def create_students(self, school, grades, count=15):
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
            name, description = grade_descriptions.get(level, (f'Grade {level}', ''))

            grade, created = Grade.objects.get_or_create(
                numeric_level=level,
                defaults={
                    'name': name,
                    'min_age': min_age,
                    'max_age': max_age
                }
            )

            # Update existing grades with better names if they were basic
            if not created and grade.name == f'Grade {level}':
                grade.name = name
                grade.save()

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
