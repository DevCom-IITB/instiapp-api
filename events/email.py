"""Helpers for sending and tracking threaded group email."""

from email.utils import make_msgid, parseaddr
from html import escape

from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def _clean_message_id(message_id):
    """Return a Message-ID in the RFC format expected by mail headers."""
    if not message_id:
        return ""
    value = str(message_id).strip()
    return value if value.startswith("<") else f"<{value}>"


def _unique_addresses(addresses):
    """Preserve recipient order while removing duplicate addresses."""
    result = []
    values = [addresses] if isinstance(addresses, str) else (addresses or [])
    for value in values:
        for address in str(value).split(","):
            address = address.strip()
            if address and address not in result:
                result.append(address)
    return result


def add_quoted_parent_body(
    text_message,
    html_message,
    parent_text_message,
    parent_html_message,
    parent_created_at,
    parent_from_email,
):
    """Append the previous message in the conventional reply format."""
    if not parent_text_message and not parent_html_message:
        return text_message, html_message

    display_name, parent_address = parseaddr(parent_from_email)
    parent_address = parent_address or parent_from_email
    sender_label = display_name or parent_address
    text_sender = (
        f"{sender_label} <{parent_address}>"
        if display_name
        else f"<{parent_address}>"
    )
    html_sender = (
        f"{escape(display_name)} " if display_name else ""
    ) + (
        f'&lt;<a href="mailto:{escape(parent_address, quote=True)}">'
        f"{escape(parent_address)}</a>&gt;"
    )
    quoted_text = "\n".join(
        f"> {line}" if line else ">" for line in parent_text_message.splitlines()
    )
    text_message = (
        f"{text_message}\n\n"
        f"On {parent_created_at:%a, %d %b %Y at %H:%M} {text_sender} wrote:\n"
        f"{quoted_text}"
    )

    quoted_html = parent_html_message or f"<p>{escape(parent_text_message)}</p>"
    html_message = (
        f"{html_message}"
        f'<div class="gmail_quote" style="margin-top:1em;">'
        f'<div style="color:#5bc8ff;">On {parent_created_at:%a, %d %b %Y at %H:%M} '
        f"{html_sender} wrote:</div>"
        f'<blockquote type="cite" style="margin:0.8em 0 0 0.4em; padding-left:0.7em; '
        f'border-left:1px solid #d0d7de; color:#5bc8ff !important;">{quoted_html}</blockquote></div>'
    )
    return text_message, html_message


def send_group_threaded_email(
    *,
    subject,
    text_message,
    html_message,
    to_recipients,
    cc_recipients=None,
    parent_message_id=None,
    previous_message_ids=None,
):
    """Send one group message and return its threading metadata.

    The returned recipient lists are the exact lists used for the message, which
    lets callers persist the group and reuse it for a follow-up.
    """
    to_recipients = _unique_addresses(to_recipients)
    cc_recipients = _unique_addresses(cc_recipients)
    cc_recipients = [address for address in cc_recipients if address not in to_recipients]

    if not to_recipients and not cc_recipients:
        raise ValueError("At least one recipient is required")

    parent_message_id = _clean_message_id(parent_message_id)
    references = [
        _clean_message_id(message_id)
        for message_id in (previous_message_ids or [])
        if message_id
    ]
    if parent_message_id and parent_message_id not in references:
        references.append(parent_message_id)

    if parent_message_id and not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"

    message_id = make_msgid(domain=getattr(settings, "EMAIL_MESSAGE_ID_DOMAIN", None))
    headers = {
        "Message-ID": message_id,
    }
    if parent_message_id:
        headers["In-Reply-To"] = parent_message_id
        headers["References"] = " ".join(references)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=(
            settings.EMAIL_EVENT_HOST_USER or settings.EMAIL_HOST_USER
        ),
        to=to_recipients,
        cc=cc_recipients,
        headers=headers,
    )
    message.attach_alternative(html_message, "text/html")
    message.send(fail_silently=False)

    return {
        "message_id": message_id,
        "parent_message_id": parent_message_id or None,
        "references": references,
        "to_recipients": to_recipients,
        "cc_recipients": cc_recipients,
        "recipients": to_recipients + cc_recipients,
        "subject": subject,
        "body_text": text_message,
        "body_html": html_message,
    }
