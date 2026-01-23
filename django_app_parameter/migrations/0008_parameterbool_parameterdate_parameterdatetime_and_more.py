from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("django_app_parameter", "0007_parameter_enable_history_parameterhistory"),
    ]

    operations = [
        migrations.CreateModel(
            name="ParameterBool",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("django_app_parameter.parameter",),
        ),
        migrations.CreateModel(
            name="ParameterDate",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("django_app_parameter.parameter",),
        ),
        migrations.CreateModel(
            name="ParameterDatetime",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("django_app_parameter.parameter",),
        ),
        migrations.CreateModel(
            name="ParameterDecimal",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("django_app_parameter.parameter",),
        ),
        migrations.CreateModel(
            name="ParameterDict",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("django_app_parameter.parameter",),
        ),
        migrations.CreateModel(
            name="ParameterDuration",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("django_app_parameter.parameter",),
        ),
        migrations.CreateModel(
            name="ParameterEmail",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("django_app_parameter.parameter",),
        ),
        migrations.CreateModel(
            name="ParameterFloat",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("django_app_parameter.parameter",),
        ),
        migrations.CreateModel(
            name="ParameterInt",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("django_app_parameter.parameter",),
        ),
        migrations.CreateModel(
            name="ParameterJson",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("django_app_parameter.parameter",),
        ),
        migrations.CreateModel(
            name="ParameterList",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("django_app_parameter.parameter",),
        ),
        migrations.CreateModel(
            name="ParameterPath",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("django_app_parameter.parameter",),
        ),
        migrations.CreateModel(
            name="ParameterPercentage",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("django_app_parameter.parameter",),
        ),
        migrations.CreateModel(
            name="ParameterStr",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("django_app_parameter.parameter",),
        ),
        migrations.CreateModel(
            name="ParameterTime",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("django_app_parameter.parameter",),
        ),
        migrations.CreateModel(
            name="ParameterUrl",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("django_app_parameter.parameter",),
        ),
    ]
