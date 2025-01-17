import random

import factory
from faker import Faker

from huntsite.content import models

fake = Faker()


def content_factory():
    nb = random.randint(1, 3)
    return "\n\n".join(fake.paragraph(nb_sentences=random.randint(8, 12)) for _ in range(nb))


class AboutEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.AboutEntry

    title = factory.Faker("sentence")
    content = factory.LazyFunction(content_factory)
    order_by = factory.Sequence(lambda n: n)


class StoryEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.StoryEntry

    title = factory.Faker("sentence")
    content = factory.LazyFunction(content_factory)
    order_by = factory.Sequence(lambda n: n)


def attributions_entry_content_factory():
    return "\n".join("- " + fake.sentence() for _ in range(3))


class AttributionsEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.AttributionsEntry

    title = factory.Faker("sentence")
    content = factory.LazyFunction(attributions_entry_content_factory)
    order_by = factory.Sequence(lambda n: n)


def update_entry_content_factory():
    return fake.paragraph(nb_sentences=random.randint(2, 4))


class UpdateEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.UpdateEntry

    content = factory.LazyFunction(update_entry_content_factory)
