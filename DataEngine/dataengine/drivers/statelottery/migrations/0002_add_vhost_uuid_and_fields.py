# Generated manually - consolidates migrations for cross-database support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statelottery', '0001_initial'),
    ]

    operations = [
        # Add vhost_id as UUIDField (not FK) for cross-database support
        migrations.AddField(
            model_name='lotterygame',
            name='vhost_id',
            field=models.UUIDField(blank=True, null=True, db_index=True, help_text='VHost UUID reference (cross-database)'),
        ),
        migrations.AddField(
            model_name='lotterydraw',
            name='vhost_id',
            field=models.UUIDField(blank=True, null=True, db_index=True, help_text='VHost UUID reference (cross-database)'),
        ),
        migrations.AddField(
            model_name='lotteryscrapelog',
            name='vhost_id',
            field=models.UUIDField(blank=True, null=True, db_index=True, help_text='VHost UUID reference (cross-database)'),
        ),
        # Increase state field max_length
        migrations.AlterField(
            model_name='lotterygame',
            name='state',
            field=models.CharField(help_text='State code (e.g., NY, CA, MULTI)', max_length=10),
        ),
        # Add manual_override field
        migrations.AddField(
            model_name='lotterydraw',
            name='manual_override',
            field=models.BooleanField(default=False, help_text='Whether this draw was manually entered/corrected'),
        ),
    ]
