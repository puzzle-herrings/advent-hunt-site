import random

from django.conf import settings
from django.db.models.signals import post_save
import factory
from faker import Faker

fake = Faker()


def team_name_text_factory(instance=None) -> str:
    nb = random.randint(1, 3)
    return " ".join(fake.words(nb=nb)).title()


def team_members_text_factory(instance=None) -> str:
    nb = random.randint(1, 3)
    return ", ".join(fake.first_name() for _ in range(nb))


@factory.django.mute_signals(post_save)
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL
        skip_postgeneration_save = True

    username = factory.Faker("user_name")
    email = factory.Faker("email")

    team_name = factory.lazy_attribute(team_name_text_factory)
    profile = factory.RelatedFactory("huntsite.teams.factories.TeamProfileFactory", "user")

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        if extracted:
            obj.set_password(extracted)
        else:
            obj.set_unusable_password()
        obj.save()


@factory.django.mute_signals(post_save)
class TeamProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "teams.TeamProfile"

    user = factory.SubFactory(UserFactory, profile=None)
    members = factory.lazy_attribute(team_members_text_factory)
