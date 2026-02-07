import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduTrack.settings')
django.setup()

sql_statements = [
    # Constraint names shortened to <64 chars
    "ALTER TABLE `learning_materials` ADD CONSTRAINT `lm_academic_year_fk` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`);",
    "ALTER TABLE `learning_materials` ADD CONSTRAINT `lm_classroom_fk` FOREIGN KEY (`classroom_id`) REFERENCES `class_rooms` (`id`);",
    "ALTER TABLE `learning_materials` ADD CONSTRAINT `lm_course_fk` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`);",
    "ALTER TABLE `learning_materials` ADD CONSTRAINT `lm_deactivated_by_fk` FOREIGN KEY (`deactivated_by_id`) REFERENCES `users` (`id`);",
    "ALTER TABLE `learning_materials` ADD CONSTRAINT `lm_uploaded_by_fk` FOREIGN KEY (`uploaded_by_id`) REFERENCES `users` (`id`);",
    "CREATE INDEX IF NOT EXISTS `lm_is_active_idx` ON `learning_materials` (`is_active`);",
    "CREATE INDEX IF NOT EXISTS `idx_materials_course_year` ON `learning_materials` (`course_id`, `academic_year_id`);",
]

with connection.cursor() as cursor:
    for sql in sql_statements:
        try:
            print(f"Executing: {sql[:50]}...")
            cursor.execute(sql)
        except Exception as e:
            # Table/index might already exist, but that's okay
            print(f"Error: {e}")

print("Done.")
