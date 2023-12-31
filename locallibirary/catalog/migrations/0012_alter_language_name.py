# Generated by Django 4.2.1 on 2023-06-22 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0011_alter_language_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='name',
            field=models.CharField(choices=[('English', 'English'), ('France', 'France'), ('German', 'Germany')], default='English', help_text='Enter a book language', max_length=200),
        ),
    ]
