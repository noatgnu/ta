# Generated by Django 4.2.6 on 2023-11-04 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('turnover_atlas', '0005_modelparameters_k_pool_turnoverdata_tau_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='turnoverdata',
            name='Protein_Group',
            field=models.TextField(db_index=True, default=''),
            preserve_default=False,
        ),
    ]
