from allauth.account.models import EmailAddress
from django.db import transaction
from loguru import logger

from huntsite.teams.models import User


@transaction.atomic
def user_deactivate(user: User):
    logger.info("Deactivating user {user}", user=user)
    user.is_active = False
    old_username = user.username
    user.username = f"deactivated-{old_username}"
    user.team_name = f"{user.team_name} (Deactivated)"
    user.email = (
        user.email.replace("@", "__at__").replace(".", "__dot__") + "@deactivated.adventhunt.com"
    )
    user.set_unusable_password()
    user.save()
    # Remove allauth email addresses
    email_addresses = EmailAddress.objects.filter(user=user)
    email_addresses.delete()
    logger.success(
        "Deactivated user {old_username}, new username is {user}",
        old_username=old_username,
        user=user,
    )


def user_clear_password(user: User):
    """Clears a user password. This makes them unable to log in until they perform a password
    reset."""
    logger.info("Clearing password for user {user}", user=user)
    user.set_password("")
    user.save()
    logger.success("Cleared password for user {user}", user=user)
