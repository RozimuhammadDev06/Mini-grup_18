from django.db import migrations


def repair_missing_region_table(apps, schema_editor):
    Region = apps.get_model("users", "Region")
    table_name = Region._meta.db_table

    if table_name not in schema_editor.connection.introspection.table_names():
        schema_editor.create_model(Region)


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            repair_missing_region_table,
            migrations.RunPython.noop,
        ),
    ]
