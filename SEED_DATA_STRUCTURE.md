# Seed Data Structure Diagram

## Visual Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EDUTRACKER DATABASE                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
        ┌─────────────────────────────────────────────────────────┐
        │              2 WORKSTREAMS (Regions)                     │
        │  • North/South/East/West/Central Region Education District│
        │  • Capacity: 500-2000 students                           │
        │  • Location: Random city                                 │
        └─────────────────────────────────────────────────────────┘
                    │                           │
                    ▼                           ▼
        ┌──────────────────────┐    ┌──────────────────────┐
        │ WORKSTREAM MANAGER 1 │    │ WORKSTREAM MANAGER 2 │
        │ firstname.lastname   │    │ firstname.lastname   │
        │    .ws@edutracker    │    │    .ws@edutracker    │
        └──────────────────────┘    └──────────────────────┘
                    │
                    ▼
        ┌─────────────────────────────────────────────────┐
        │        4 SCHOOLS (Selected Workstream)          │
        │  • Springfield Elementary School                │
        │  • Riverside Middle School                      │
        │  • Lakeview High School                         │
        │  • Oakwood Primary School                       │
        └─────────────────────────────────────────────────┘
                    │
                    ▼
    ┌───────────────┴───────────────┬───────────────┬───────────────┐
    ▼                               ▼               ▼               ▼
┌─────────┐                   ┌─────────┐     ┌─────────┐     ┌─────────┐
│ SCHOOL 1│                   │ SCHOOL 2│     │ SCHOOL 3│     │ SCHOOL 4│
└─────────┘                   └─────────┘     └─────────┘     └─────────┘
    │                               │               │               │
    ├─ 1 School Manager              ├─ 1 School Manager
    ├─ 3 Teachers                    ├─ 3 Teachers
    ├─ 3 Secretaries                 ├─ 3 Secretaries
    └─ 5 Students                    └─ 5 Students
```

## Detailed Entity Breakdown

### 1. Workstream Entity

```yaml
WorkStream:
  count: 2
  attributes:
    - workstream_name: "{Region} Region Education District"
    - description: "Realistic 3-sentence description"
    - capacity: 500-2000 (random)
    - location: "Random city name"
    - manager: Link to Workstream Manager
  examples:
    - "North Region Education District"
    - "Central Region Education District"
```

### 2. Workstream Manager Entity

```yaml
WorkstreamManager:
  count: 2 (1 per workstream)
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
  count: 4 (under selected workstream)
  attributes:
    - school_name: "{City} {Type} School"
    - work_stream: Link to parent Workstream
    - manager: Link to School Manager
    - location: "Full street address"
    - capacity: 200-1000 (random)
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
  count: 4 (1 per school)
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
  count: 12 (3 per school)
  user_attributes:
    - email: "{firstname}.{lastname}.t@edutracker.com"
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
  count: 12 (3 per school)
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
  count: 20 (5 per school)
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
└──────────────────┘         └──────────────────┘
                                     │
                             ┌───────┴────────┐
                             ▼                ▼
                     ┌──────────────┐  ┌──────────────┐
                     │ Secretaries  │  │   Students   │
                     │ (Level 4c)   │  │  (Level 4d)  │
                     └──────────────┘  └──────────────┘
```

## Data Flow

```
1. CREATE WORKSTREAMS (2)
   └─> Generate regions, capacities, locations

2. CREATE WORKSTREAM MANAGERS (2)
   └─> Link 1 manager to each workstream
   └─> Update workstream.manager field

3. SELECT ONE WORKSTREAM
   └─> Create 4 schools under this workstream

4. FOR EACH SCHOOL (4):
   ├─> CREATE SCHOOL MANAGER (1)
   │   └─> Link to school
   │   └─> Update school.manager field
   │
   ├─> CREATE TEACHERS (3)
   │   └─> Create CustomUser with role='teacher'
   │   └─> Create Teacher profile (specialization, hire date, etc.)
   │
   ├─> CREATE SECRETARIES (3)
   │   └─> Create CustomUser with role='secretary'
   │
   └─> CREATE STUDENTS (5)
       └─> Create CustomUser with role='student'
       └─> Create Student profile (student_id, GPA, grade, etc.)

5. CREATE SUPPORTING DATA
   ├─> Grades 1-12 (global, shared)
   └─> Academic Year 2025-2026 per school
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

AcademicYear
  └─> school (FK → School, required)
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
- Workstream capacity: 500-2000
- School capacity: 200-1000
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
**Last Updated:** 2026-02-08
**Django Version:** 5.2.8
**Faker Version:** 33.1.0
