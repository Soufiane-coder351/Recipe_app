# Generated by Django 5.1.3 on 2024-11-21 09:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_step'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='instructions',
        ),
    ]
