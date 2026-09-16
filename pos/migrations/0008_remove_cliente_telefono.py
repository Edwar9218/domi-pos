from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0007_copiar_telefonos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cliente',
            name='telefono',
        ),
    ]
