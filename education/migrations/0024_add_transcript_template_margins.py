# Generated migration for adding margin fields to TranscriptTemplate

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0023_collegetimetable_file_alter_collegetimetable_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='transcripttemplate',
            name='margin_top',
            field=models.FloatField(default=72.0, help_text='Top margin in points (default: 72pt = 1 inch)'),
        ),
        migrations.AddField(
            model_name='transcripttemplate',
            name='margin_bottom',
            field=models.FloatField(default=72.0, help_text='Bottom margin in points (default: 72pt = 1 inch)'),
        ),
        migrations.AddField(
            model_name='transcripttemplate',
            name='margin_left',
            field=models.FloatField(default=72.0, help_text='Left margin in points (default: 72pt = 1 inch)'),
        ),
        migrations.AddField(
            model_name='transcripttemplate',
            name='margin_right',
            field=models.FloatField(default=72.0, help_text='Right margin in points (default: 72pt = 1 inch)'),
        ),
    ]

