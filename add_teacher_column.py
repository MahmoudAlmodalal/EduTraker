#!/usr/bin/env python
"""
Script to add missing teacher_id column to course_allocations table.
This handles the case where the migration exists but the column wasn't created.
"""
from django.db import connection

def add_teacher_column():
    cursor = connection.cursor()
    
    # Try to add the column
    try:
        cursor.execute('ALTER TABLE course_allocations ADD COLUMN teacher_id BIGINT NULL')
        print('✅ Column teacher_id added successfully')
    except Exception as e:
        if 'Duplicate column name' in str(e) or 'already exists' in str(e):
            print('ℹ️  Column teacher_id already exists')
        else:
            print(f'❌ Error adding column: {e}')
            return False
    
    # Try to add the foreign key constraint
    try:
        cursor.execute('''
            ALTER TABLE course_allocations 
            ADD CONSTRAINT fk_course_allocations_teacher 
            FOREIGN KEY (teacher_id) REFERENCES teachers(user_id) ON DELETE CASCADE
        ''')
        print('✅ Foreign key constraint added successfully')
    except Exception as e:
        if 'Duplicate' in str(e) or 'already exists' in str(e):
            print('ℹ️  Foreign key constraint already exists')
        else:
            print(f'❌ Error adding foreign key: {e}')
    
    # Try to add the index
    try:
        cursor.execute('CREATE INDEX idx_allocation_teacher ON course_allocations(teacher_id)')
        print('✅ Index added successfully')
    except Exception as e:
        if 'Duplicate' in str(e) or 'already exists' in str(e):
            print('ℹ️  Index already exists')
        else:
            print(f'❌ Error adding index: {e}')
    
    # Verify the column exists
    cursor.execute('DESCRIBE course_allocations')
    columns = cursor.fetchall()
    has_teacher_id = any(col[0] == 'teacher_id' for col in columns)
    
    if has_teacher_id:
        print('\\n✅ Verification: teacher_id column exists in course_allocations table')
        return True
    else:
        print('\\n❌ Verification failed: teacher_id column still missing')
        return False

if __name__ == '__main__':
    add_teacher_column()
