

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=100)),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('image', models.ImageField(default='default.jpg', upload_to='user_images/', verbose_name='profile image')),
                ('verified', models.BooleanField(default=False)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
            },
        ),
        migrations.CreateModel(
            name='Todo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Open', 'Open'), ('In Progress', 'In Progress'), ('Done', 'Done')], default='Open', max_length=20)),
                ('priority', models.CharField(choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], default='Medium', max_length=10)),
                ('category', models.CharField(blank=True, max_length=20, null=True)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, help_text='The user this todo item belongs to', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='todos', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Todo Item',
                'verbose_name_plural': 'Todo Items',
                'ordering': ['-due_date', 'priority'],
                'indexes': [models.Index(fields=['due_date'], name='todo_todo_due_dat_4529b3_idx'), models.Index(fields=['status'], name='todo_todo_status_90d961_idx'), models.Index(fields=['priority'], name='todo_todo_priorit_2dbd60_idx'), models.Index(fields=['user'], name='todo_todo_user_id_873df0_idx')],
            },
        ),
    ]