from django.db import migrations


def ensure_notifications_table(apps, schema_editor):
    Notification = apps.get_model("notifications", "Notification")
    table_name = Notification._meta.db_table

    existing_tables = schema_editor.connection.introspection.table_names()
    if table_name not in existing_tables:
        schema_editor.create_model(Notification)


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            ensure_notifications_table,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
