import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduTrack.settings')
django.setup()

from accounts.models import CustomUser

def table_exists(cursor, table_name):
    cursor.execute("SHOW TABLES LIKE %s", (table_name,))
    return cursor.fetchone() is not None

def column_exists(cursor, table_name, column_name):
    if not table_exists(cursor, table_name):
        return False
    cursor.execute(f"SHOW COLUMNS FROM `{table_name}` LIKE %s", (column_name,))
    return cursor.fetchone() is not None

def add_column_if_missing(cursor, table_name, column_name, column_definition):
    if not table_exists(cursor, table_name):
        print(f"Table '{table_name}' not found, skipping column '{column_name}'.")
        return

    if not column_exists(cursor, table_name, column_name):
        try:
            print(f"Adding column '{column_name}' to table '{table_name}'...")
            cursor.execute(f"ALTER TABLE `{table_name}` ADD COLUMN {column_name} {column_definition}")
            print(f"Successfully added '{column_name}' to '{table_name}'.")
        except Exception as e:
            print(f"Error adding column '{column_name}' to '{table_name}': {e}")
    else:
        print(f"Column '{column_name}' already exists in table '{table_name}'.")


def index_exists(cursor, table_name, index_name):
    if not table_exists(cursor, table_name):
        return False
    cursor.execute(f"SHOW INDEX FROM `{table_name}` WHERE Key_name = %s", (index_name,))
    return cursor.fetchone() is not None


def add_index_if_missing(cursor, table_name, index_name, index_sql):
    if not table_exists(cursor, table_name):
        print(f"Table '{table_name}' not found, skipping index '{index_name}'.")
        return

    if not index_exists(cursor, table_name, index_name):
        try:
            print(f"Adding index '{index_name}' to table '{table_name}'...")
            cursor.execute(f"ALTER TABLE `{table_name}` ADD {index_sql}")
            print(f"Successfully added index '{index_name}' to '{table_name}'.")
        except Exception as e:
            print(f"Error adding index '{index_name}' to '{table_name}': {e}")
    else:
        print(f"Index '{index_name}' already exists in table '{table_name}'.")


def ensure_token_blacklist_schema(cursor):
    print("Checking token blacklist tables...")

    if not table_exists(cursor, "token_blacklist_outstandingtoken"):
        try:
            print("Creating table 'token_blacklist_outstandingtoken'...")
            cursor.execute(
                """
                CREATE TABLE `token_blacklist_outstandingtoken` (
                    `id` bigint(20) NOT NULL AUTO_INCREMENT,
                    `jti` varchar(255) NOT NULL,
                    `token` longtext NOT NULL,
                    `created_at` datetime(6) NULL,
                    `expires_at` datetime(6) NOT NULL,
                    `user_id` bigint(20) NULL,
                    PRIMARY KEY (`id`),
                    UNIQUE KEY `token_blacklist_outstandingtoken_jti_key` (`jti`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
                """
            )
            print("Created 'token_blacklist_outstandingtoken'.")
        except Exception as e:
            print(f"Error creating token_blacklist_outstandingtoken: {e}")
    else:
        add_column_if_missing(cursor, "token_blacklist_outstandingtoken", "jti", "varchar(255) NOT NULL")
        add_column_if_missing(cursor, "token_blacklist_outstandingtoken", "token", "longtext NOT NULL")
        add_column_if_missing(cursor, "token_blacklist_outstandingtoken", "created_at", "datetime(6) NULL")
        add_column_if_missing(cursor, "token_blacklist_outstandingtoken", "expires_at", "datetime(6) NOT NULL")
        add_column_if_missing(cursor, "token_blacklist_outstandingtoken", "user_id", "bigint(20) NULL")
        add_index_if_missing(
            cursor,
            "token_blacklist_outstandingtoken",
            "token_blacklist_outstandingtoken_jti_key",
            "UNIQUE INDEX `token_blacklist_outstandingtoken_jti_key` (`jti`)",
        )

    if not table_exists(cursor, "token_blacklist_blacklistedtoken"):
        try:
            print("Creating table 'token_blacklist_blacklistedtoken'...")
            cursor.execute(
                """
                CREATE TABLE `token_blacklist_blacklistedtoken` (
                    `id` bigint(20) NOT NULL AUTO_INCREMENT,
                    `blacklisted_at` datetime(6) NOT NULL,
                    `token_id` bigint(20) NOT NULL,
                    PRIMARY KEY (`id`),
                    UNIQUE KEY `token_blacklist_blacklistedtoken_token_id_uniq` (`token_id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
                """
            )
            print("Created 'token_blacklist_blacklistedtoken'.")
        except Exception as e:
            print(f"Error creating token_blacklist_blacklistedtoken: {e}")
    else:
        add_column_if_missing(cursor, "token_blacklist_blacklistedtoken", "blacklisted_at", "datetime(6) NOT NULL")
        if (
            not column_exists(cursor, "token_blacklist_blacklistedtoken", "token_id")
            and column_exists(cursor, "token_blacklist_blacklistedtoken", "blacklistedtoken_id")
        ):
            try:
                print("Renaming blacklistedtoken_id to token_id in token_blacklist_blacklistedtoken...")
                cursor.execute(
                    "ALTER TABLE `token_blacklist_blacklistedtoken` "
                    "CHANGE `blacklistedtoken_id` `token_id` bigint(20) NULL"
                )
            except Exception as e:
                print(f"Error renaming blacklistedtoken_id to token_id: {e}")
        else:
            add_column_if_missing(cursor, "token_blacklist_blacklistedtoken", "token_id", "bigint(20) NULL")

        add_index_if_missing(
            cursor,
            "token_blacklist_blacklistedtoken",
            "token_blacklist_blacklistedtoken_token_id_uniq",
            "UNIQUE INDEX `token_blacklist_blacklistedtoken_token_id_uniq` (`token_id`)",
        )

def run():
    print("--- Starting Database Reconciliation ---")
    with connection.cursor() as cursor:
        # 1. Check 'users' table (managed in accounts)
        add_column_if_missing(cursor, "users", "work_stream_id", "bigint(20) NULL")
        add_column_if_missing(cursor, "users", "school_id", "bigint(20) NULL")
        add_column_if_missing(cursor, "users", "created_by_id", "bigint(20) NULL")
        add_column_if_missing(cursor, "users", "deactivated_by_id", "bigint(20) NULL")
        # Settings/profile preference fields used by unified settings page.
        add_column_if_missing(cursor, "users", "timezone", "varchar(64) NOT NULL DEFAULT 'UTC'")
        add_column_if_missing(cursor, "users", "email_notifications", "tinyint(1) NOT NULL DEFAULT 1")
        add_column_if_missing(cursor, "users", "in_app_alerts", "tinyint(1) NOT NULL DEFAULT 1")
        add_column_if_missing(cursor, "users", "sms_notifications", "tinyint(1) NOT NULL DEFAULT 0")
        add_column_if_missing(cursor, "users", "enable_2fa", "tinyint(1) NOT NULL DEFAULT 0")

        # 2. Check 'work_streams' table (managed in workstream)
        add_column_if_missing(cursor, "work_streams", "slug", "VARCHAR(255) UNIQUE NULL")

        # 3. Check 'students' table (managed in student)
        add_column_if_missing(cursor, "students", "student_id", "VARCHAR(50) UNIQUE NULL")

        # 4. Ensure SimpleJWT token blacklist tables/columns exist.
        ensure_token_blacklist_schema(cursor)

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
