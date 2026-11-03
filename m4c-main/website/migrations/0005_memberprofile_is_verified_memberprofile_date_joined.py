from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0004_volunteerregistration_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="memberprofile",
            name="is_verified",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="memberprofile",
            name="date_joined",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]