import factory

from huntsite.content import models


class AboutEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.AboutEntry

    title = factory.Faker("sentence")
    content = factory.Faker("paragraph", nb_sentences=8)
    order_by = factory.Sequence(lambda n: n)


class StoryEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.StoryEntry

    title = factory.Faker("sentence")
    content = factory.Faker("paragraph", nb_sentences=8)
    order_by = factory.Sequence(lambda n: n)
