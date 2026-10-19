from django.db import migrations


def repair_missing_address_location_tables(apps, schema_editor):
    connection = schema_editor.connection
    existing_tables = set(connection.introspection.table_names())

    for model_name in ("DeliveryZone", "Region", "City"):
        model = apps.get_model("users", model_name)
        if model._meta.db_table not in existing_tables:
            schema_editor.create_model(model)
            existing_tables.add(model._meta.db_table)


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_merge_20261019_1621"),
    ]

    operations = [
        migrations.RunPython(
            repair_missing_address_location_tables,
            migrations.RunPython.noop,
        ),
    ]
