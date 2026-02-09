"""
Django management command to load faker data from JSON files into the database.
Usage: python manage.py load_faker_data [--clear]
"""

import json
import os
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.hashers import make_password

from workstream.models import WorkStream
from school.models import School, AcademicYear, Grade, Course, ClassRoom
from accounts.models import CustomUser
from teacher.models import Teacher, CourseAllocation, Assignment, Mark, Attendance, LessonPlan, LearningMaterial
from student.models import Student, StudentEnrollment
from guardian.models import Guardian, GuardianStudentLink


class Command(BaseCommand):
    help = 'Load faker data from JSON files into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing',
        )
        parser.add_argument(
            '--data-dir',
            type=str,
            default='../faker_data',
            help='Directory containing JSON files (default: ../faker_data)',
        )

    def handle(self, *args, **options):
        data_dir = Path(options['data_dir'])
        
        if not data_dir.exists():
            self.stdout.write(self.style.ERROR(f'Data directory not found: {data_dir}'))
            return

        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('Loading Faker Data into Database'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write('')

        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()
            self.stdout.write(self.style.SUCCESS('✓ Data cleared'))
            self.stdout.write('')

        try:
            with transaction.atomic():
                # Load data in dependency order
                self.load_workstreams(data_dir)
                self.load_schools(data_dir)
                self.load_academic_years(data_dir)
                self.load_grades(data_dir)
                self.load_users(data_dir)
                self.update_school_managers(data_dir)
                self.load_teachers(data_dir)
                self.load_students(data_dir)
                self.load_guardians(data_dir)
                self.load_guardian_student_links(data_dir)
                self.load_courses(data_dir)
                self.load_classrooms(data_dir)
                self.load_student_enrollments(data_dir)
                self.load_course_allocations(data_dir)
                self.load_assignments(data_dir)
                self.load_marks(data_dir)
                self.load_attendance(data_dir)
                self.load_lesson_plans(data_dir)
                self.load_learning_materials(data_dir)

            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('='*60))
            self.stdout.write(self.style.SUCCESS('✓ All data loaded successfully!'))
            self.stdout.write(self.style.SUCCESS('='*60))
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('Default password for all users: "password123"'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading data: {str(e)}'))
            raise

    def clear_data(self):
        """Clear all existing data"""
        LearningMaterial.objects.all().delete()
        LessonPlan.objects.all().delete()
        Attendance.objects.all().delete()
        Mark.objects.all().delete()
        Assignment.objects.all().delete()
        CourseAllocation.objects.all().delete()
        StudentEnrollment.objects.all().delete()
        ClassRoom.objects.all().delete()
        Course.objects.all().delete()
        GuardianStudentLink.objects.all().delete()
        Guardian.objects.all().delete()
        Student.objects.all().delete()
        Teacher.objects.all().delete()
        CustomUser.objects.filter(role__in=['teacher', 'student', 'guardian', 'secretary', 'manager_school']).delete()
        AcademicYear.objects.all().delete()
        Grade.objects.all().delete()
        School.objects.all().delete()
        WorkStream.objects.all().delete()

    def load_json(self, data_dir, filename):
        """Load and parse JSON file"""
        filepath = data_dir / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def parse_date(self, date_str):
        """Parse date string to date object"""
        if not date_str:
            return None
        if isinstance(date_str, date):
            return date_str
        return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()

    def parse_datetime(self, datetime_str):
        """Parse datetime string to datetime object"""
        if not datetime_str:
            return None
        if isinstance(datetime_str, datetime):
            return datetime_str
        return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))

    def load_workstreams(self, data_dir):
        """Load workstream data"""
        self.stdout.write('Loading workstreams...')
        data = self.load_json(data_dir, 'workstreams.json')
        
        for item in data:
            WorkStream.objects.update_or_create(
                id=item['id'],
                defaults={
                    'workstream_name': item['workstream_name'],
                    'description': item.get('description', ''),
                    'is_active': item.get('is_active', True),
                    'created_at': self.parse_datetime(item.get('created_at')),
                    'updated_at': self.parse_datetime(item.get('updated_at')),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Loaded {len(data)} workstreams'))

    def load_schools(self, data_dir):
        """Load school data"""
        self.stdout.write('Loading schools...')
        data = self.load_json(data_dir, 'schools.json')
        
        for item in data:
            School.objects.update_or_create(
                id=item['id'],
                defaults={
                    'school_name': item['school_name'],
                    'work_stream_id': item['work_stream_id'],
                    'manager_id': None,  # Will be updated later
                    'location': item.get('location'),
                    'capacity': item.get('capacity'),
                    'contact_email': item.get('contact_email'),
                    'contact_phone': item.get('contact_phone'),
                    'academic_year_start': self.parse_date(item.get('academic_year_start')),
                    'academic_year_end': self.parse_date(item.get('academic_year_end')),
                    'is_active': item.get('is_active', True),
                    'created_at': self.parse_datetime(item.get('created_at')),
                    'updated_at': self.parse_datetime(item.get('updated_at')),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Loaded {len(data)} schools'))

    def load_academic_years(self, data_dir):
        """Load academic year data"""
        self.stdout.write('Loading academic years...')
        data = self.load_json(data_dir, 'academic_years.json')
        
        for item in data:
            AcademicYear.objects.update_or_create(
                id=item['id'],
                defaults={
                    'academic_year_code': item['academic_year_code'],
                    'school_id': item['school_id'],
                    'start_date': self.parse_date(item['start_date']),
                    'end_date': self.parse_date(item['end_date']),
                    'is_active': item.get('is_active', True),
                    'created_at': self.parse_datetime(item.get('created_at')),
                    'updated_at': self.parse_datetime(item.get('updated_at')),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Loaded {len(data)} academic years'))

    def load_grades(self, data_dir):
        """Load grade data"""
        self.stdout.write('Loading grades...')
        data = self.load_json(data_dir, 'grades.json')
        
        for item in data:
            Grade.objects.update_or_create(
                id=item['id'],
                defaults={
                    'name': item['name'],
                    'numeric_level': item['numeric_level'],
                    'min_age': item['min_age'],
                    'max_age': item['max_age'],
                    'is_active': item.get('is_active', True),
                    'created_at': self.parse_datetime(item.get('created_at')),
                    'updated_at': self.parse_datetime(item.get('updated_at')),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Loaded {len(data)} grades'))

    def load_users(self, data_dir):
        """Load user data"""
        self.stdout.write('Loading users...')
        data = self.load_json(data_dir, 'users.json')
        
        default_password = make_password('password123')
        
        for item in data:
            CustomUser.objects.update_or_create(
                id=item['id'],
                defaults={
                    'email': item['email'],
                    'full_name': item['full_name'],
                    'role': item['role'],
                    'work_stream_id': item.get('work_stream_id'),
                    'school_id': item.get('school_id'),
                    'is_staff': item.get('is_staff', False),
                    'is_active': item.get('is_active', True),
                    'password': default_password,
                    'date_joined': self.parse_datetime(item.get('date_joined')),
                    'created_at': self.parse_datetime(item.get('created_at')),
                    'updated_at': self.parse_datetime(item.get('updated_at')),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Loaded {len(data)} users'))

    def update_school_managers(self, data_dir):
        """Update school manager references"""
        self.stdout.write('Updating school managers...')
        data = self.load_json(data_dir, 'schools.json')
        
        for item in data:
            if item.get('manager_id'):
                school = School.objects.get(id=item['id'])
                school.manager_id = item['manager_id']
                school.save(update_fields=['manager'])
        self.stdout.write(self.style.SUCCESS('✓ Updated school managers'))

    def load_teachers(self, data_dir):
        """Load teacher profile data"""
        self.stdout.write('Loading teachers...')
        data = self.load_json(data_dir, 'teachers.json')
        
        for item in data:
            Teacher.objects.update_or_create(
                user_id=item['user_id'],
                defaults={
                    'specialization': item.get('specialization'),
                    'hire_date': self.parse_date(item['hire_date']),
                    'employment_status': item['employment_status'],
                    'highest_degree': item.get('highest_degree'),
                    'years_of_experience': item.get('years_of_experience'),
                    'office_location': item.get('office_location'),
                    'is_active': item.get('is_active', True),
                    'created_at': self.parse_datetime(item.get('created_at')),
                    'updated_at': self.parse_datetime(item.get('updated_at')),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Loaded {len(data)} teachers'))

    def load_students(self, data_dir):
        """Load student profile data"""
        self.stdout.write('Loading students...')
        data = self.load_json(data_dir, 'students.json')
        
        for item in data:
            Student.objects.update_or_create(
                user_id=item['user_id'],
                defaults={
                    'student_id': item.get('student_id'),
                    'date_of_birth': self.parse_date(item['date_of_birth']),
                    'gender': item.get('gender'),
                    'grade_id': item.get('grade_id'),
                    'grade_level': item.get('grade_level'),
                    'admission_date': self.parse_date(item['admission_date']),
                    'enrollment_status': item.get('enrollment_status', 'active'),
                    'current_status': item.get('current_status', 'active'),
                    'current_gpa': Decimal(str(item['current_gpa'])) if item.get('current_gpa') else None,
                    'total_absences': item.get('total_absences', 0),
                    'address': item.get('address'),
                    'national_id': item.get('national_id'),
                    'emergency_contact': item.get('emergency_contact'),
                    'medical_notes': item.get('medical_notes'),
                    'phone': item.get('phone'),
                    'is_active': item.get('is_active', True),
                    'created_at': self.parse_datetime(item.get('created_at')),
                    'updated_at': self.parse_datetime(item.get('updated_at')),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Loaded {len(data)} students'))

    def load_guardians(self, data_dir):
        """Load guardian profile data"""
        self.stdout.write('Loading guardians...')
        data = self.load_json(data_dir, 'guardians.json')
        
        for item in data:
            Guardian.objects.update_or_create(
                user_id=item['user_id'],
                defaults={
                    'phone_number': item.get('phone_number'),
                    'is_active': item.get('is_active', True),
                    'created_at': self.parse_datetime(item.get('created_at')),
                    'updated_at': self.parse_datetime(item.get('updated_at')),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Loaded {len(data)} guardians'))

    def load_guardian_student_links(self, data_dir):
        """Load guardian-student relationship data"""
        self.stdout.write('Loading guardian-student links...')
        data = self.load_json(data_dir, 'guardian_student_links.json')
        
        for item in data:
            GuardianStudentLink.objects.update_or_create(
                id=item['id'],
                defaults={
                    'guardian_id': item['guardian_id'],
                    'student_id': item['student_id'],
                    'relationship_type': item['relationship_type'],
                    'is_primary': item.get('is_primary', False),
                    'can_pickup': item.get('can_pickup', True),
                    'is_active': item.get('is_active', True),
                    'created_at': self.parse_datetime(item.get('created_at')),
                    'updated_at': self.parse_datetime(item.get('updated_at')),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Loaded {len(data)} guardian-student links'))

    def load_courses(self, data_dir):
        """Load course data"""
        self.stdout.write('Loading courses...')
        data = self.load_json(data_dir, 'courses.json')
        
        for item in data:
            Course.objects.update_or_create(
                id=item['id'],
                defaults={
                    'course_code': item['course_code'],
                    'school_id': item['school_id'],
                    'grade_id': item['grade_id'],
                    'name': item['name'],
                    'description': item.get('description'),
                    'is_active': item.get('is_active', True),
                    'created_at': self.parse_datetime(item.get('created_at')),
                    'updated_at': self.parse_datetime(item.get('updated_at')),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Loaded {len(data)} courses'))

    def load_classrooms(self, data_dir):
        """Load classroom data"""
        self.stdout.write('Loading classrooms...')
        data = self.load_json(data_dir, 'classrooms.json')
        
        for item in data:
            ClassRoom.objects.update_or_create(
                id=item['id'],
                defaults={
                    'classroom_name': item['classroom_name'],
                    'school_id': item['school_id'],
                    'academic_year_id': item['academic_year_id'],
                    'grade_id': item['grade_id'],
                    'homeroom_teacher_id': item.get('homeroom_teacher_id'),
                    'capacity': item.get('capacity'),
                    'is_active': item.get('is_active', True),
                    'created_at': self.parse_datetime(item.get('created_at')),
                    'updated_at': self.parse_datetime(item.get('updated_at')),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Loaded {len(data)} classrooms'))

    def load_student_enrollments(self, data_dir):
        """Load student enrollment data"""
        self.stdout.write('Loading student enrollments...')
        data = self.load_json(data_dir, 'student_enrollments.json')
        
        for item in data:
            StudentEnrollment.objects.update_or_create(
                id=item['id'],
                defaults={
                    'student_id': item['student_id'],
                    'class_room_id': item['class_room_id'],
                    'academic_year_id': item['academic_year_id'],
                    'status': item.get('status', 'active'),
                    'enrollment_date': self.parse_date(item.get('enrollment_date')),
                    'completion_date': self.parse_date(item.get('completion_date')),
                    'is_active': item.get('is_active', True),
                    'created_at': self.parse_datetime(item.get('created_at')),
                    'updated_at': self.parse_datetime(item.get('updated_at')),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Loaded {len(data)} student enrollments'))

    def load_course_allocations(self, data_dir):
        """Load course allocation data"""
        self.stdout.write('Loading course allocations...')
        data = self.load_json(data_dir, 'course_allocations.json')
        
        for item in data:
            CourseAllocation.objects.update_or_create(
                id=item['id'],
                defaults={
                    'course_id': item['course_id'],
                    'class_room_id': item['class_room_id'],
                    'teacher_id': item['teacher_id'],
                    'academic_year_id': item.get('academic_year_id'),
                    'is_active': item.get('is_active', True),
                    'created_at': self.parse_datetime(item.get('created_at')),
                    'updated_at': self.parse_datetime(item.get('updated_at')),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Loaded {len(data)} course allocations'))

    def load_assignments(self, data_dir):
        """Load assignment data"""
        self.stdout.write('Loading assignments...')
        data = self.load_json(data_dir, 'assignments.json')
        
        for item in data:
            Assignment.objects.update_or_create(
                id=item['id'],
                defaults={
                    'assignment_code': item['assignment_code'],
                    'course_allocation_id': item.get('course_allocation_id'),
                    'created_by_id': item['created_by_id'],
                    'title': item['title'],
                    'description': item.get('description'),
                    'assignment_type': item.get('assignment_type', 'assignment'),
                    'exam_type': item.get('exam_type'),
                    'full_mark': Decimal(str(item['full_mark'])),
                    'weight': Decimal(str(item.get('weight', 1.0))),
                    'assigned_date': self.parse_date(item.get('assigned_date')),
                    'due_date': self.parse_datetime(item.get('due_date')),
                    'instructions_url': item.get('instructions_url', ''),
                    'attachments': item.get('attachments', []),
                    'is_published': item.get('is_published', False),
                    'is_active': item.get('is_active', True),
                    'created_at': self.parse_datetime(item.get('created_at')),
                    'updated_at': self.parse_datetime(item.get('updated_at')),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Loaded {len(data)} assignments'))

    def load_marks(self, data_dir):
        """Load marks/grades data"""
        self.stdout.write('Loading marks...')
        data = self.load_json(data_dir, 'marks.json')
        
        for item in data:
            Mark.objects.update_or_create(
                id=item['id'],
                defaults={
                    'student_id': item['student_id'],
                    'assignment_id': item['assignment_id'],
                    'score': Decimal(str(item['score'])),
                    'max_score': Decimal(str(item.get('max_score'))) if item.get('max_score') else None,
                    'percentage': Decimal(str(item.get('percentage'))) if item.get('percentage') else None,
                    'letter_grade': item.get('letter_grade', ''),
                    'feedback': item.get('feedback'),
                    'graded_by_id': item.get('graded_by_id'),
                    'graded_at': self.parse_datetime(item.get('graded_at')),
                    'is_final': item.get('is_final', False),
                    'is_active': item.get('is_active', True),
                    'created_at': self.parse_datetime(item.get('created_at')),
                    'updated_at': self.parse_datetime(item.get('updated_at')),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Loaded {len(data)} marks'))

    def load_attendance(self, data_dir):
        """Load attendance data"""
        self.stdout.write('Loading attendance records...')
        data = self.load_json(data_dir, 'attendance.json')
        
        for item in data:
            Attendance.objects.update_or_create(
                id=item['id'],
                defaults={
                    'student_id': item['student_id'],
                    'course_allocation_id': item.get('course_allocation_id'),
                    'date': self.parse_date(item['date']),
                    'status': item['status'],
                    'note': item.get('note'),
                    'recorded_by_id': item.get('recorded_by_id'),
                    'is_active': item.get('is_active', True),
                    'created_at': self.parse_datetime(item.get('created_at')),
                    'updated_at': self.parse_datetime(item.get('updated_at')),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Loaded {len(data)} attendance records'))

    def load_lesson_plans(self, data_dir):
        """Load lesson plan data"""
        self.stdout.write('Loading lesson plans...')
        data = self.load_json(data_dir, 'lesson_plans.json')
        
        for item in data:
            LessonPlan.objects.update_or_create(
                id=item['id'],
                defaults={
                    'course_id': item['course_id'],
                    'classroom_id': item['classroom_id'],
                    'academic_year_id': item['academic_year_id'],
                    'teacher_id': item['teacher_id'],
                    'title': item['title'],
                    'content': item['content'],
                    'objectives': item.get('objectives'),
                    'resources_needed': item.get('resources_needed'),
                    'date_planned': self.parse_date(item['date_planned']),
                    'is_published': item.get('is_published', False),
                    'is_active': item.get('is_active', True),
                    'created_at': self.parse_datetime(item.get('created_at')),
                    'updated_at': self.parse_datetime(item.get('updated_at')),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Loaded {len(data)} lesson plans'))

    def load_learning_materials(self, data_dir):
        """Load learning material data"""
        self.stdout.write('Loading learning materials...')
        data = self.load_json(data_dir, 'learning_materials.json')
        
        for item in data:
            LearningMaterial.objects.update_or_create(
                id=item['id'],
                defaults={
                    'material_code': item['material_code'],
                    'course_id': item['course_id'],
                    'classroom_id': item['classroom_id'],
                    'academic_year_id': item['academic_year_id'],
                    'uploaded_by_id': item['uploaded_by_id'],
                    'title': item['title'],
                    'description': item.get('description'),
                    'file_url': item['file_url'],
                    'file_type': item.get('file_type'),
                    'file_size': item.get('file_size'),
                    'is_active': item.get('is_active', True),
                    'created_at': self.parse_datetime(item.get('created_at')),
                    'updated_at': self.parse_datetime(item.get('updated_at')),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ Loaded {len(data)} learning materials'))
