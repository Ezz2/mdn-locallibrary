# Generated by Django 4.2.1 on 2023-06-19 04:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0008_alter_language_choice_language'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='language',
            options={'ordering': ['choice_language']},
        ),
    ]
