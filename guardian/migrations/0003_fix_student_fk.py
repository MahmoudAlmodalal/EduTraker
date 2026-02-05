from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('guardian', '0002_initial'),
        ('student', '0001_initial'),
    ]
    operations = [
        migrations.AlterField(
            model_name='guardianstudentlink',
            name='student',
            field=models.ForeignKey(
                db_column='student_id',
                help_text='Student in this relationship',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='guardian_links',
                to='student.student'
            ),
        ),
        migrations.AddIndex(
            model_name='guardianstudentlink',
            index=models.Index(fields=['student'], name='idx_link_student'),
        ),
        migrations.AddConstraint(
            model_name='guardianstudentlink',
            constraint=models.UniqueConstraint(fields=('guardian', 'student'), name='unique_guardian_student'),
        ),
    ]
