# Generated by Django 5.1.4 on 2025-05-01 11:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0005_alter_todo_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'verbose_name': 'Profile', 'verbose_name_plural': 'Profiles'},
        ),
        migrations.AlterModelOptions(
            name='todo',
            options={'ordering': ['-due_date', 'priority'], 'verbose_name': 'Todo Item', 'verbose_name_plural': 'Todo Items'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
        migrations.AddField(
            model_name='todo',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='creation date'),
        ),
        migrations.AddField(
            model_name='todo',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='last update'),
        ),
        migrations.AddField(
            model_name='todo',
            name='user',
            field=models.ForeignKey(blank=True, help_text='The user this todo item belongs to', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='todos', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='profile',
            name='full_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='default.jpg', upload_to='user_images/', verbose_name='profile image'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='todo',
            name='category',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='task category'),
        ),
        migrations.AlterField(
            model_name='todo',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='detailed description'),
        ),
        migrations.AlterField(
            model_name='todo',
            name='due_date',
            field=models.DateField(blank=True, null=True, verbose_name='due date'),
        ),
        migrations.AlterField(
            model_name='todo',
            name='priority',
            field=models.CharField(choices=[('L', 'Low'), ('M', 'Medium'), ('H', 'High')], default='M', max_length=1, verbose_name='task priority'),
        ),
        migrations.AlterField(
            model_name='todo',
            name='status',
            field=models.CharField(choices=[('O', 'Open'), ('P', 'In Progress'), ('D', 'Done'), ('C', 'Cancelled')], default='O', max_length=1, verbose_name='task status'),
        ),
        migrations.AlterField(
            model_name='todo',
            name='title',
            field=models.CharField(max_length=200, verbose_name='task title'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='email address'),
        ),
        migrations.AddIndex(
            model_name='todo',
            index=models.Index(fields=['due_date'], name='todo_todo_due_dat_4529b3_idx'),
        ),
        migrations.AddIndex(
            model_name='todo',
            index=models.Index(fields=['status'], name='todo_todo_status_90d961_idx'),
        ),
        migrations.AddIndex(
            model_name='todo',
            index=models.Index(fields=['priority'], name='todo_todo_priorit_2dbd60_idx'),
        ),
    ]
