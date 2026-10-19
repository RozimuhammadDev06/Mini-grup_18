from importlib import import_module

from django.apps import apps
from django.db import connection
from django.test import TransactionTestCase


class MissingRegionTableMigrationTests(TransactionTestCase):
    def test_recreates_missing_region_table(self):
        if connection.vendor != "sqlite":
            self.skipTest("The reported missing-table error is from SQLite.")

        migration = import_module(
            "apps.users.migrations.0002_repair_missing_region_table",
        )
        region_model = apps.get_model("users", "Region")
        table_name = region_model._meta.db_table

        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(region_model)

        try:
            self.assertNotIn(
                table_name,
                connection.introspection.table_names(),
            )

            with connection.schema_editor() as schema_editor:
                migration.repair_missing_region_table(
                    apps,
                    schema_editor,
                )

            self.assertIn(
                table_name,
                connection.introspection.table_names(),
            )
        finally:
            if table_name not in connection.introspection.table_names():
                with connection.schema_editor() as schema_editor:
                    schema_editor.create_model(region_model)


class MissingAddressLocationTablesMigrationTests(TransactionTestCase):
    def test_recreates_missing_city_table(self):
        if connection.vendor != "sqlite":
            self.skipTest("The reported missing-table error is from SQLite.")

        migration = import_module(
            "apps.users.migrations.0004_repair_missing_address_location_tables",
        )
        city_model = apps.get_model("users", "City")
        table_name = city_model._meta.db_table

        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(city_model)

        try:
            self.assertNotIn(
                table_name,
                connection.introspection.table_names(),
            )

            with connection.schema_editor() as schema_editor:
                migration.repair_missing_address_location_tables(
                    apps,
                    schema_editor,
                )

            self.assertIn(
                table_name,
                connection.introspection.table_names(),
            )
        finally:
            if table_name not in connection.introspection.table_names():
                with connection.schema_editor() as schema_editor:
                    schema_editor.create_model(city_model)
