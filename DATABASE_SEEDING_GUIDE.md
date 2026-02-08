# Database Seeding Guide for EduTracker

## Overview

This guide explains how to use the database seeding script to populate your EduTracker database with realistic test data using the Faker library.

## Seeding Script Location

```
/accounts/management/commands/seed_data.py
```

This is a Django management command that follows Django best practices.

## What Gets Created

The seeding script creates the following hierarchical structure:

```
EduTracker Database
│
├── 2 Workstreams
│   ├── North/South/East/West/Central Region Education District
│   └── Each with: name, description, capacity, location
│
├── 2 Workstream Managers (1 per workstream)
│   └── Each linked to their respective workstream
│
└── 4 Schools (under one selected workstream)
    └── For each school:
        ├── 1 School Manager
        ├── 3 Teachers (with specializations, hire dates, experience)
        ├── 3 Secretaries
        └── 5 Students (with student IDs, GPAs, grades, etc.)
```

### Total Entities Created

- **Workstreams:** 2
- **Workstream Managers:** 2
- **Schools:** 4
- **School Managers:** 4
- **Teachers:** 12 (3 per school)
- **Secretaries:** 12 (3 per school)
- **Students:** 20 (5 per school)
- **Total Users:** 50

## Usage

### Basic Usage

To seed the database with test data:

```bash
cd /home/mahmoud/Desktop/my\ projects/eduTraker/EduTraker
python manage.py seed_data
```

### Clear and Reseed

To clear existing seeded data before creating new data:

```bash
python manage.py seed_data --clear
```

**⚠️ Warning:** The `--clear` flag will delete ALL users with roles: `manager_workstream`, `manager_school`, `teacher`, `secretary`, and `student`. Use with caution!

## Default Credentials

All seeded users have the default password:

```
Password123!
```

### Email Patterns

Emails follow consistent patterns for easy identification:

| Role | Email Pattern | Example |
|------|---------------|---------|
| Workstream Manager | `firstname.lastname.ws@edutracker.com` | `john.doe.ws@edutracker.com` |
| School Manager | `firstname.lastname.sm@edutracker.com` | `jane.smith.sm@edutracker.com` |
| Teacher | `firstname.lastname.t@edutracker.com` | `alice.johnson.t@edutracker.com` |
| Secretary | `firstname.lastname.sec@edutracker.com` | `bob.wilson.sec@edutracker.com` |
| Student | `firstname.lastname.stXXXX@edutracker.com` | `charlie.brown.st1234@edutracker.com` |

## Data Realism

All data is generated using the **Faker library** for realistic values:

### Workstreams
- Names based on geographic regions (North, South, East, West, Central)
- Realistic descriptions
- Capacity: 500-2000 students
- Random city locations

### Schools
- Names combine city + school type (Elementary, Middle, High, Primary, Secondary)
- Full addresses
- Capacity: 200-1000 students
- Contact emails and phone numbers
- Academic year: 2025-2026

### Teachers
- Specializations: Mathematics, Science, English, History, Geography, Physics, Chemistry, Biology, Physical Education, Arts, Music, Computer Science, Economics, Literature
- Employment status: full_time, part_time, contract, substitute
- Years of experience: 1-20 years
- Hire dates: Within last 5 years

### Students
- Unique student IDs (STU10000-STU99999)
- Ages: 5-18 years old
- Grades: 1-12
- GPA: 2.0-4.0
- Enrollment status: active, enrolled, graduated, transferred, withdrawn
- Total absences: 0-20

## Idempotency

### Safe to Run Multiple Times

The script is **partially idempotent**:

✅ **Safe operations:**
- Creating grades (uses `get_or_create`)
- Creating academic years (uses `get_or_create`)

⚠️ **Creates new records:**
- Users, Schools, Workstreams will be created fresh on each run

### Recommended Workflow

1. **First run:** Create initial seed data
   ```bash
   python manage.py seed_data
   ```

2. **Subsequent runs:** Clear and reseed if needed
   ```bash
   python manage.py seed_data --clear
   ```

3. **Production:** Never use `--clear` in production!

## Database Requirements

### Prerequisites

1. **Database must be migrated:**
   ```bash
   python manage.py migrate
   ```

2. **Required models:**
   - CustomUser (accounts app)
   - WorkStream (workstream app)
   - School (school app)
   - Teacher (teacher app)
   - Student (student app)
   - Grade (school app)
   - AcademicYear (school app)

3. **Faker library:**
   Already included in `requirements.txt` (Faker==33.1.0)

## Integration with Docker

### In Docker Environment

If using Docker, you can add seeding to the entrypoint:

```bash
# In entrypoint.sh, after migrations:
python manage.py migrate --noinput
python manage.py seed_data  # Add this line
python manage.py collectstatic --noinput
```

## Troubleshooting

### Common Issues

1. **"Table doesn't exist" error:**
   - Run migrations first: `python manage.py migrate`

2. **"Email already exists" error:**
   - Use `--clear` flag to remove existing data first

3. **Foreign key constraint errors:**
   - Ensure all migrations are up to date
   - Check that WorkStream and School models are properly migrated

4. **Permission denied:**
   - Ensure you have write access to the database

### Verification

After seeding, verify the data:

```bash
# Check user counts
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.filter(role='teacher').count()
12
>>> User.objects.filter(role='student').count()
20

# Check schools
>>> from school.models import School
>>> School.objects.count()
4

# Check workstreams
>>> from workstream.models import WorkStream
>>> WorkStream.objects.count()
2
```

## Customization

### Modify Seed Quantities

Edit `/accounts/management/commands/seed_data.py`:

```python
# Line 51: Change number of workstreams
workstreams = self.create_workstreams(count=2)  # Change count

# Line 57: Change number of schools
schools = self.create_schools(selected_workstream, count=4)  # Change count

# Lines 77-81: Change staff/student counts per school
teachers = self.create_teachers(school, count=3)  # Change count
secretaries = self.create_secretaries(school, count=3)  # Change count
students = self.create_students(school, grades, count=5)  # Change count
```

### Modify Data Patterns

Edit the respective methods in `seed_data.py`:

- `create_workstreams()` - Modify workstream data
- `create_teachers()` - Change specializations, employment types
- `create_students()` - Adjust GPA ranges, grade levels
- `create_schools()` - Customize school types, capacities

## Testing the Seeding Script

### Run in Test Mode

```bash
# Test without committing to database
python manage.py seed_data --dry-run  # Note: implement if needed
```

### Manual Testing Steps

1. Seed the database
2. Log in as different user types
3. Verify relationships (schools → workstreams, students → schools)
4. Check that all fields are populated
5. Test data integrity across related models

## Best Practices

1. **Always backup before seeding in production-like environments**
2. **Use `--clear` only in development**
3. **Never commit seeded data to version control**
4. **Document any custom modifications to the script**
5. **Test seeding script after model changes**

## Support

For issues or questions:
1. Check Django logs: `tail -f /path/to/django.log`
2. Review migration status: `python manage.py showmigrations`
3. Inspect database directly if needed

---

**Created:** 2026-02-08
**Script Location:** `/accounts/management/commands/seed_data.py`
**Django Version:** 5.2.8
**Faker Version:** 33.1.0
