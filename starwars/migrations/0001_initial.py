# Generated by Django 3.2.8 on 2021-10-13 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=256)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
