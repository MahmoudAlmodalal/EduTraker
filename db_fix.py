import os
import django
from django.db import connection, transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduTrack.settings')
django.setup()

from accounts.models import CustomUser

def column_exists(cursor, table_name, column_name):
    cursor.execute(f"SHOW COLUMNS FROM `{table_name}` LIKE %s", (column_name,))
    return cursor.fetchone() is not None

def add_column_if_missing(cursor, table_name, column_name, column_definition):
    if not column_exists(cursor, table_name, column_name):
        try:
            print(f"Adding column '{column_name}' to table '{table_name}'...")
            cursor.execute(f"ALTER TABLE `{table_name}` ADD COLUMN {column_name} {column_definition}")
            print(f"Successfully added '{column_name}' to '{table_name}'.")
        except Exception as e:
            print(f"Error adding column '{column_name}' to '{table_name}': {e}")
    else:
        print(f"Column '{column_name}' already exists in table '{table_name}'.")

def run():
    print("--- Starting Database Reconciliation ---")
    with connection.cursor() as cursor:
        # 1. Check 'users' table (managed in accounts)
        add_column_if_missing(cursor, "users", "work_stream_id", "INT NULL")
        add_column_if_missing(cursor, "users", "school_id", "INT NULL")

        # 2. Check 'work_streams' table (managed in workstream)
        add_column_if_missing(cursor, "work_streams", "slug", "VARCHAR(255) UNIQUE NULL")

        # 3. Check 'students' table (managed in student)
        add_column_if_missing(cursor, "students", "student_id", "VARCHAR(50) UNIQUE NULL")

        # 4. Reconcile 'token_blacklist_blacklistedtoken' column names
        # SimpleJWT might expect 'token_id' instead of 'blacklistedtoken_id' or similar
        print("Checking token_blacklist_blacklistedtoken columns...")
        try:
            if not column_exists(cursor, "token_blacklist_blacklistedtoken", "token_id") and \
               column_exists(cursor, "token_blacklist_blacklistedtoken", "blacklistedtoken_id"):
                print("Renaming blacklistedtoken_id to token_id in token_blacklist_blacklistedtoken...")
                cursor.execute("ALTER TABLE `token_blacklist_blacklistedtoken` CHANGE `blacklistedtoken_id` `token_id` bigint(20) NOT NULL")
        except Exception as e:
            print(f"Non-critical error reconciling token_blacklist: {e}")

    # Create admin user
    try:
        user, created = CustomUser.objects.get_or_create(
            email='admin@edutraker.com',
            defaults={
                'full_name': 'Admin User',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")
    except Exception as e:
        print(f"Error handling admin user: {e}")
    
    print("--- Database Reconciliation Complete ---")

if __name__ == "__main__":
    run()
