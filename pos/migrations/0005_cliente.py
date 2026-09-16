from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0004_producto_impreso_producto_recogido_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150)),
                ('telefono', models.CharField(blank=True, max_length=30)),
                ('direccion', models.TextField()),
                ('plus_code', models.CharField(blank=True, help_text='Pega el Plus Code de Google Maps, ej: 7WCV+2Q Cali, Colombia', max_length=150)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['nombre'],
            },
        ),
    ]
