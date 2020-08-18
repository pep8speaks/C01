# Generated by Django 3.0.9 on 2020-08-18 22:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0034_auto_20200703_1452'),
    ]

    operations = [
        migrations.RenameField(
            model_name='crawlrequest',
            old_name='link_extractor_max_depht',
            new_name='link_extractor_max_depth',
        ),
        migrations.RemoveField(
            model_name='crawlrequest',
            name='running',
        ),
        migrations.AlterField(
            model_name='crawlerinstance',
            name='crawler_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instances', to='main.CrawlRequest'),
        ),
    ]
