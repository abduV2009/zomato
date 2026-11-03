from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("customers", "0002_deliveryaddress"),
    ]

    operations = [
        migrations.CreateModel(
            name="RestaurantInquiry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=20)),
                (
                    "inquiry_type",
                    models.CharField(
                        choices=[
                            ("missing", "Missing restaurant"),
                            ("unlisted", "Unlisted restaurant"),
                            ("new", "New restaurant"),
                        ],
                        max_length=20,
                    ),
                ),
                ("restaurant_name", models.CharField(max_length=150)),
                ("city", models.CharField(blank=True, max_length=100)),
                ("details", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="PartnerApplication",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("owner_name", models.CharField(max_length=150)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=20)),
                (
                    "place_type",
                    models.CharField(
                        choices=[
                            ("restaurant", "Restaurant"),
                            ("kitchen", "Cloud kitchen"),
                        ],
                        max_length=20,
                    ),
                ),
                ("place_name", models.CharField(max_length=150)),
                ("city", models.CharField(max_length=100)),
                ("address", models.TextField()),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
