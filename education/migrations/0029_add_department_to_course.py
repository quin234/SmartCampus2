# Generated migration for adding department field to CollegeCourse

from django.db import migrations, models
import django.db.models.deletion


def assign_departments_to_existing_courses(apps, schema_editor):
    """Assign default departments to existing courses"""
    CollegeCourse = apps.get_model('education', 'CollegeCourse')
    Department = apps.get_model('accounts', 'Department')
    College = apps.get_model('education', 'College')
    
    # Get all colleges
    colleges = College.objects.all()
    
    for college in colleges:
        # Get or create a default "General" department for each college
        default_dept, created = Department.objects.get_or_create(
            college=college,
            department_name='General',
            defaults={}
        )
        
        # Assign default department to all courses without a department
        CollegeCourse.objects.filter(college=college, department__isnull=True).update(department=default_dept)


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0028_reporttemplatemapping'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Step 1: Add department field as nullable
        migrations.AddField(
            model_name='collegecourse',
            name='department',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='courses',
                to='accounts.department',
                help_text='Department is required'
            ),
        ),
        # Step 2: Assign departments to existing courses
        migrations.RunPython(assign_departments_to_existing_courses, migrations.RunPython.noop),
        # Step 3: Make department field non-nullable
        migrations.AlterField(
            model_name='collegecourse',
            name='department',
            field=models.ForeignKey(
                null=False,
                blank=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='courses',
                to='accounts.department',
                help_text='Department is required'
            ),
        ),
        # Step 4: Add index for performance
        migrations.AddIndex(
            model_name='collegecourse',
            index=models.Index(fields=['college', 'department'], name='college_cou_college_6768e5_idx'),
        ),
    ]

