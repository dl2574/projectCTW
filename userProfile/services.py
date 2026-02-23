from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

User = get_user_model()


def email_event_status_update(event):
    """
    Send a status-change notification email to all users who should hear about
    this event: anyone who upvoted it OR has an AttendanceCommitment for its
    plan, filtered to those who haven't opted out (email_status_updates=True).

    Called whenever an event transitions status (e.g. PROPOSAL → PLANNING,
    PLANNING → SCHEDULED). The caller is responsible for saving the new status
    before calling this function so the email reflects the current state.
    """
    # Collect upvoters who want status emails
    upvoters = event.upvotes.filter(email_status_updates=True)

    # Collect committed attendees — only possible if the event has a Plan.
    # hasattr guards against PROPOSAL-stage events that have no plan yet.
    committed = User.objects.none()
    if hasattr(event, 'plan'):
        committed = User.objects.filter(
            attendance_commitments__plan=event.plan,
            email_status_updates=True,
        )

    # Union and deduplicate so a user who both upvoted and committed only gets
    # one email.
    recipients = (upvoters | committed).distinct()

    if not recipients.exists():
        return

    subject = f"Project Update: {event.name}"
    message = (
        f"Hi,\n\n"
        f'The status of "{event.name}" has been updated to: '
        f"{event.get_status_display()}.\n\n"
        f"View the event:\n"
        f"https://www.projectctw.com{event.get_absolute_url()}\n\n"
        f"To stop receiving these emails, update your notification preferences "
        f"in your account settings.\n\n"
        f"— The ProjectCTW Team"
    )

    for user in recipients:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
