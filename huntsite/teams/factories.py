from django.conf import settings
import factory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.Faker("password")

    team_name = factory.Faker("word")


class TeamProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "teams.Team"

    user = factory.SubFactory(UserFactory)
