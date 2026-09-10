"""Modernizations shipped with 3.0.

Replaces ``Meta.unique_together`` with a named ``UniqueConstraint``, moves
the slug default to a callable so ``DEFAULT_TERMS_SLUG`` is read per row,
and widens both primary keys to ``BigAutoField``.

The primary key change rewrites the id column on both tables.  On a large
``usertermsandconditions`` table run this during a maintenance window, or
pin the old behaviour by setting ``default_auto_field`` back to
``django.db.models.AutoField`` on your own AppConfig subclass.
"""


import termsandconditions.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("termsandconditions", "0004_auto_20201107_0711"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="usertermsandconditions",
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name="termsandconditions",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="termsandconditions",
            name="slug",
            field=models.SlugField(
                default=termsandconditions.models.get_default_terms_slug
            ),
        ),
        migrations.AlterField(
            model_name="usertermsandconditions",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AddConstraint(
            model_name="usertermsandconditions",
            constraint=models.UniqueConstraint(
                fields=("user", "terms"), name="termsandconditions_unique_user_terms"
            ),
        ),
    ]
