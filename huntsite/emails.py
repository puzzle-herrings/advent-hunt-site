from io import StringIO

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from loguru import logger
import markdown
from markdown import Markdown


# https://stackoverflow.com/a/54923798
def unmark_element(element, stream=None):
    """Recursive function to convert markdown to plain text."""
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        unmark_element(sub, stream)
    if element.tag == "p":
        # Linebreaks after paragraphs
        stream.write("\n")
    if element.tag == "a":
        # Add the URL after the link text
        stream.write(f" ({element.get('href')})")
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()


# patching Markdown
markdown.Markdown.output_formats["plain"] = unmark_element
__md = Markdown(output_format="plain")
__md.stripTopLevelTags = False


def unmark(text):
    return __md.convert(text)


def send_email(subject, message, recipient_list):
    """Send email to a list of recipients as BCC, with a markdown message converted to both HTML
    and plaintext."""
    logger.info(f"Sending email with subject '{subject}' to {len(recipient_list)} recipients.")

    message_html = render_to_string("email.html", {"content": markdown.markdown(message)})
    message_plain = unmark(message)

    email = EmailMultiAlternatives(
        subject=subject,
        body=message_plain,
        to=(settings.EMAIL_REPLY_TO,),
        reply_to=(settings.EMAIL_REPLY_TO,),
        bcc=recipient_list,
    )
    email.attach_alternative(message_html, "text/html")
    email.send()
