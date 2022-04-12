# Generated by Django 4.0.3 on 2022-04-12 10:34

from django.db import migrations

from server_app_api.house_importer import import_house_items


class Migration(migrations.Migration):
    dependencies = [
        ('server_app_api', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(
            lambda apps, schema_editor: import_house_items(apps=apps, schema_editor=schema_editor,
                                                           bulk_commit_size=1000, import_limit=50000,
                                                           file_url="http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-complete.csv")),
    ]
