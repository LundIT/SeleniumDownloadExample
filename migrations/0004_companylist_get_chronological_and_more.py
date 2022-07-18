# Generated by Django 4.0.5 on 2022-07-07 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generic_app', '0003_remove_handelsregisterauszug_calculate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='companylist',
            name='get_chronological',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='companylist',
            name='get_structured',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='handelsregisterauszug',
            name='structured_handelsregister_auszug',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
    ]
