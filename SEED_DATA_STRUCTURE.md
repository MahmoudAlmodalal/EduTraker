# Seed Data Structure Diagram

## Visual Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EDUTRACKER DATABASE                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
        ┌─────────────────────────────────────────────────────────┐
        │              5 WORKSTREAMS (Regions)                     │
        │  • North/South/East/West/Central Region Education District│
        │  • Capacity: 1000-5000 students                          │
        │  • Location: Random city                                 │
        └─────────────────────────────────────────────────────────┘
              │         │         │         │         │
              ▼         ▼         ▼         ▼         ▼
        ┌──────────────────────────────────────────────────┐
        │         5 WORKSTREAM MANAGERS (1 per WS)          │
        │  firstname.lastname.ws@edutracker.com             │
        └──────────────────────────────────────────────────┘
              │
              ▼
        ┌─────────────────────────────────────────────────┐
        │     8 SCHOOLS PER WORKSTREAM (40 total)          │
        │  • Riverside Middle School                       │
        │  • Oak Valley High School                        │
        │  • Sunrise Elementary School                     │
        │  • Mountain View Secondary School                │
        │  • Lakewood Academy School                       │
        │  • Cedar Park Preparatory School                 │
        │  • Greenfield International School               │
        │  • Westridge Comprehensive School                │
        └─────────────────────────────────────────────────┘
                    │
                    ▼
    ┌───────────────┴───────────────┬────────────────┐
    ▼                               ▼                ▼
┌──────────┐                  ┌──────────┐     ┌──────────┐
│ SCHOOL 1 │                  │ SCHOOL 2 │ ... │ SCHOOL 40│
└──────────┘                  └──────────┘     └──────────┘
    │                               │
    ├─ 1 School Manager             ├─ 1 School Manager
    ├─ 12 Teachers                  ├─ 12 Teachers
    ├─ 6 Secretaries                ├─ 6 Secretaries
    ├─ 50 Students                  ├─ 50 Students
    ├─ ~30 Guardians                ├─ ~30 Guardians
    ├─ 36 Courses                   ├─ 36 Courses
    ├─ 12 Classrooms                ├─ 12 Classrooms
    ├─ Assignments (7 per alloc.)   ├─ Assignments
    ├─ Marks (per student/assign.)  ├─ Marks
    ├─ Learning Materials           ├─ Learning Materials
    ├─ Lesson Plans                 ├─ Lesson Plans
    └─ Attendance (4 weeks)         └─ Attendance
```

## Detailed Entity Breakdown

### 1. Workstream Entity

```yaml
WorkStream:
  count: 5
  attributes:
    - workstream_name: "{Region} Region Education District"
    - description: "Realistic 3-sentence description"
    - capacity: 1000-5000 (random)
    - location: "Random city name"
    - manager: Link to Workstream Manager
  examples:
    - "North Region Education District"
    - "South Region Education District"
    - "Central Region Education District"
```

### 2. Workstream Manager Entity

```yaml
WorkstreamManager:
  count: 5 (1 per workstream)
  attributes:
    - email: "{firstname}.{lastname}.ws@edutracker.com"
    - password: "Password123!"
    - full_name: "{First} {Last}"
    - role: "manager_workstream"
    - work_stream: Link to Workstream
  relationships:
    - 1:1 with Workstream
    - Manages all schools in their workstream
```

### 3. School Entity

```yaml
School:
  count: 40 (8 per workstream)
  attributes:
    - school_name: "{City} {Type} School"
    - work_stream: Link to parent Workstream
    - manager: Link to School Manager
    - location: "Full street address"
    - capacity: 500-1500 (random)
    - contact_email: "info@{schoolname}.edu"
    - contact_phone: "Realistic phone number"
    - academic_year_start: "2025-09-01"
    - academic_year_end: "2026-06-30"
  types:
    - Elementary
    - Middle
    - High
    - Primary
    - Secondary
```

### 4. School Manager Entity

```yaml
SchoolManager:
  count: 40 (1 per school)
  attributes:
    - email: "{firstname}.{lastname}.sm@edutracker.com"
    - password: "Password123!"
    - full_name: "{First} {Last}"
    - role: "manager_school"
    - work_stream: Link to parent Workstream
    - school: Link to managed School
  relationships:
    - 1:1 with School
    - Reports to Workstream Manager
```

### 5. Teacher Entity

```yaml
Teacher:
  count: 480 (12 per school)
  user_attributes:
    - email: "{firstname}.{lastname}.t{N}@edutracker.com"
    - password: "Password123!"
    - full_name: "{First} {Last}"
    - role: "teacher"
    - work_stream: Link to School's Workstream
    - school: Link to School
  teacher_profile:
    - specialization: [Mathematics, Science, English, History, Geography,
                       Physics, Chemistry, Biology, PE, Arts, Music,
                       Computer Science, Economics, Literature]
    - hire_date: "Random date within last 5 years"
    - employment_status: [full_time, part_time, contract, substitute]
    - years_of_experience: 1-20 (random)
```

### 6. Secretary Entity

```yaml
Secretary:
  count: 240 (6 per school)
  attributes:
    - email: "{firstname}.{lastname}.sec@edutracker.com"
    - password: "Password123!"
    - full_name: "{First} {Last}"
    - role: "secretary"
    - work_stream: Link to School's Workstream
    - school: Link to School
  responsibilities:
    - Administrative support
    - Student records management
```

### 7. Student Entity

```yaml
Student:
  count: 2000 (50 per school)
  user_attributes:
    - email: "{firstname}.{lastname}.st{XXXX}@edutracker.com"
    - password: "Password123!"
    - full_name: "{First} {Last}"
    - role: "student"
    - work_stream: Link to School's Workstream
    - school: Link to School
  student_profile:
    - student_id: "STU{10000-99999}"
    - date_of_birth: "Age 5-18"
    - gender: [male, female, other]
    - grade: "Grade 1-12 (random)"
    - admission_date: "Within last 3 years"
    - enrollment_status: [active, enrolled, graduated, transferred, withdrawn]
    - current_gpa: 2.0-4.0 (random, 2 decimals)
    - total_absences: 0-20 (random)
```

## Relationship Diagram

```
┌──────────────┐
│  WorkStream  │
│   (Level 1)  │
└──────┬───────┘
       │ 1:1
       ▼
┌──────────────────┐
│ Workstream Mgr   │
│   (Level 2)      │
└──────────────────┘
       │
       │ 1:N
       ▼
┌──────────────┐
│    School    │
│   (Level 3)  │
└──────┬───────┘
       │ 1:1
       ▼
┌──────────────────┐         ┌──────────────────┐
│  School Manager  │         │    Teachers      │
│   (Level 4a)     │         │   (Level 4b)     │
└──────────────────┘         └──────┬───────────┘
                                    │
                      ┌─────────────┼─────────────┐
                      ▼             ▼             ▼
              ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
              │ Secretaries  │ │   Students   │ │   Courses    │
              │ (Level 4c)   │ │  (Level 4d)  │ │ (Level 4e)   │
              └──────────────┘ └──────┬───────┘ └──────┬───────┘
                                      │                │
                               ┌──────┤          ┌─────┤
                               ▼      ▼          ▼     ▼
                        ┌──────────┐ ┌──────┐ ┌──────────────┐
                        │Guardians │ │Marks │ │ Assignments  │
                        │(Level 5) │ │      │ │LessonPlans   │
                        └──────────┘ └──────┘ │Materials     │
                                              └──────────────┘

Cross-cutting entities:
  ├─ Notifications    (sender → recipient)
  ├─ Messages         (sender → recipients via receipts)
  ├─ Support Tickets  (created_by → assigned_to)
  ├─ Staff Evaluations(reviewer → reviewee)
  ├─ Login History    (user → login records)
  ├─ Activity Logs    (actor → actions)
  └─ System Config    (global / workstream / school level)
```

## Data Flow

```
1. CREATE WORKSTREAMS (5)
   └─> Generate regions, capacities, locations

2. CREATE WORKSTREAM MANAGERS (5)
   └─> Link 1 manager to each workstream
   └─> Update workstream.manager field

3. CREATE SYSTEM CONFIGURATIONS
   └─> Global, per-workstream, per-school settings

4. FOR EACH WORKSTREAM (5):
   └─> Create 8 schools under this workstream

5. FOR EACH SCHOOL (40):
   ├─> CREATE SCHOOL MANAGER (1)
   │   └─> Link to school
   │   └─> Update school.manager field
   │
   ├─> CREATE TEACHERS (12)
   │   └─> Create CustomUser with role='teacher'
   │   └─> Create Teacher profile (specialization, hire date, etc.)
   │
   ├─> CREATE SECRETARIES (6)
   │   └─> Create CustomUser with role='secretary'
   │   └─> Create Secretary profile (department, office, etc.)
   │
   ├─> CREATE COURSES (36: 6 subjects × 6 grades)
   │   └─> Math, Science, English, History, PE, Art
   │
   ├─> CREATE CLASSROOMS (12: 2 sections × 6 grades)
   │   └─> Assign homeroom teachers
   │
   ├─> CREATE STUDENTS (50)
   │   └─> Create CustomUser with role='student'
   │   └─> Create Student profile (student_id, GPA, grade, etc.)
   │
   ├─> CREATE GUARDIANS (~30)
   │   └─> Link to students as families (1-3 students per family)
   │
   ├─> CREATE ENROLLMENTS
   │   └─> Enroll students in matching classrooms
   │
   ├─> CREATE COURSE ALLOCATIONS
   │   └─> Assign teachers to courses in classrooms
   │
   ├─> CREATE ASSIGNMENTS (7 types per allocation)
   │   └─> Homework, Quiz, Midterm, Final, Project, etc.
   │
   ├─> CREATE MARKS
   │   └─> Student scores on assignments with grades
   │
   ├─> CREATE LEARNING MATERIALS (2-4 per course)
   │   └─> PDF, PPT, DOCX, video resources
   │
   ├─> CREATE LESSON PLANS (3-5 per course)
   │   └─> Weekly lesson plans with objectives
   │
   └─> CREATE ATTENDANCE (past 4 weeks)
       └─> Daily records for 20 weekdays

6. CREATE CROSS-SCHOOL DATA
   ├─> Notifications (500) - various types
   ├─> Messages (200+) - with threaded replies
   ├─> Support Tickets (100) - from various users
   ├─> Staff Evaluations - manager reviews of teachers
   ├─> Login History (1000) - login records
   └─> Activity Logs (1500) - audit trail
```

## Foreign Key Relationships

```
WorkStream
  └─> manager (FK → CustomUser, nullable)

School
  ├─> work_stream (FK → WorkStream, required)
  └─> manager (FK → CustomUser, nullable)

CustomUser
  ├─> work_stream (FK → WorkStream, nullable)
  └─> school (FK → School, nullable)

Teacher (OneToOne)
  └─> user (FK → CustomUser, required)

Student (OneToOne)
  ├─> user (FK → CustomUser, required)
  └─> grade (FK → Grade, required)

Guardian (OneToOne)
  └─> user (FK → CustomUser, required)

GuardianStudentLink
  ├─> guardian (FK → Guardian, required)
  └─> student (FK → Student, required)

AcademicYear
  └─> school (FK → School, required)

Course
  ├─> school (FK → School, required)
  └─> grade (FK → Grade, required)

ClassRoom
  ├─> school (FK → School, required)
  ├─> academic_year (FK → AcademicYear, required)
  ├─> grade (FK → Grade, required)
  └─> homeroom_teacher (FK → Teacher, nullable)

Assignment
  ├─> course_allocation (FK → CourseAllocation, nullable)
  └─> created_by (FK → Teacher, required)

Mark
  ├─> student (FK → Student, required)
  ├─> assignment (FK → Assignment, required)
  └─> graded_by (FK → Teacher, nullable)

LearningMaterial
  ├─> course (FK → Course, required)
  ├─> classroom (FK → ClassRoom, required)
  ├─> academic_year (FK → AcademicYear, required)
  └─> uploaded_by (FK → CustomUser, required)

LessonPlan
  ├─> course (FK → Course, required)
  ├─> classroom (FK → ClassRoom, required)
  ├─> academic_year (FK → AcademicYear, required)
  └─> teacher (FK → Teacher, required)

Notification
  ├─> sender (FK → CustomUser, nullable)
  └─> recipient (FK → CustomUser, nullable)

Message
  ├─> sender (FK → CustomUser, required)
  └─> parent_message (FK → self, nullable)

MessageReceipt
  ├─> message (FK → Message, required)
  └─> recipient (FK → CustomUser, required)

SupportTicket
  ├─> created_by (FK → CustomUser, required)
  └─> assigned_to (FK → CustomUser, nullable)

StaffEvaluation
  ├─> reviewer (FK → CustomUser, required)
  └─> reviewee (FK → CustomUser, required)

Attendance
  ├─> student (FK → Student, required)
  ├─> course_allocation (FK → CourseAllocation, nullable)
  └─> recorded_by (FK → Teacher, nullable)

SystemConfiguration
  ├─> work_stream (FK → WorkStream, nullable)
  └─> school (FK → School, nullable)
```

## Data Validation Rules

### User Emails
- **Must be unique** across all users
- Follow role-based patterns for easy identification
- Lowercase, no special characters except @ and .

### Passwords
- All seeded users: `Password123!`
- Meets typical requirements (length, special char, number)

### Capacities
- Workstream capacity: 1000-5000
- School capacity: 500-1500
- Must be >= 1 (validated at model level)

### Dates
- Academic year: 2025-09-01 to 2026-06-30
- Teacher hire dates: Within last 5 years
- Student admission dates: Within last 3 years
- Student DOB: Ages 5-18

### Grades
- Numeric levels: 1-12
- Shared globally across all schools
- Uses `get_or_create` (idempotent)

## Transaction Safety

The entire seeding process runs in a **database transaction**:

```python
with transaction.atomic():
    # All creation operations
    # If any step fails, entire operation rolls back
```

**Benefits:**
- ✅ All-or-nothing execution
- ✅ No partial data on errors
- ✅ Database consistency guaranteed
- ✅ Can safely retry on failure

## Idempotency Notes

### Idempotent Operations
- ✅ Grade creation (uses `get_or_create`)
- ✅ Academic year creation (uses `get_or_create`)

### Non-Idempotent Operations
- ❌ User creation (creates new on each run)
- ❌ School creation (creates new on each run)
- ❌ Workstream creation (creates new on each run)

**Solution:** Use `--clear` flag to remove existing data first

---

**Generated by:** seed_data.py management command
**Last Updated:** 2026-02-14
**Django Version:** 5.2.8
**Faker Version:** 33.1.0
