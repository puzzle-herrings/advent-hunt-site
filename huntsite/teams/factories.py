import factory
from huntsite.factories import UserFactory


class TeamProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "teams.Team"

    user = factory.SubFactory(UserFactory)
    team_name = factory.Faker("word")
