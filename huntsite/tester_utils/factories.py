import factory

from huntsite.teams.factories import UserFactory


class OrganizerDashboardPermissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "tester_utils.OrganizerDashboardPermission"

    user = factory.SubFactory(UserFactory)
