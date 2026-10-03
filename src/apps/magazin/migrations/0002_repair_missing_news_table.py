from django.db import migrations


def create_missing_news_table(apps, schema_editor):
    News = apps.get_model("magazin", "News")
    table_name = News._meta.db_table

    existing_tables = (
        schema_editor.connection.introspection.table_names()
    )

    if table_name not in existing_tables:
        schema_editor.create_model(News)


def remove_news_table(apps, schema_editor):
    News = apps.get_model("magazin", "News")
    table_name = News._meta.db_table

    existing_tables = (
        schema_editor.connection.introspection.table_names()
    )

    if table_name in existing_tables:
        schema_editor.delete_model(News)


class Migration(migrations.Migration):

    # Keep the dependencies that Django generated automatically.
    dependencies = [
        ("magazin", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            create_missing_news_table,
            reverse_code=remove_news_table,
        ),
    ]
