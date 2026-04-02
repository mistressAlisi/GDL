from django.db import migrations

class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.RunSQL(
            "CREATE EXTENSION IF NOT EXISTS unaccent;",
            reverse_sql="DROP EXTENSION IF EXISTS unaccent;"
        )
    ]