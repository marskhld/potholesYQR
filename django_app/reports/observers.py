"""
Observer Design Pattern for report notifications.

When a report notification event occurs, the Subject
notifies all registered observers.

Current observers:
1. EmailNotificationObserver
2. NotificationRecordObserver
"""

from abc import ABC, abstractmethod

from django.core.mail import send_mail

from .models import Notification


class ReportObserver(ABC):
    """
    Abstract Observer interface.

    Every concrete observer must implement update().
    """

    @abstractmethod
    def update(
        self,
        report,
        notification_data,
    ):
        """
        React to a report-notification event.
        """

        raise NotImplementedError


class ReportNotificationSubject:
    """
    Subject that stores and notifies ReportObserver objects.
    """

    def __init__(self):
        self._observers = []

    def attach(self, observer):
        """
        Register an observer.
        """

        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        """
        Remove a registered observer.
        """

        if observer in self._observers:
            self._observers.remove(observer)

    def notify(
        self,
        report,
        notification_data,
    ):
        """
        Notify every registered observer.
        """

        for observer in self._observers:
            observer.update(
                report,
                notification_data,
            )


class EmailNotificationObserver(ReportObserver):
    """
    Concrete Observer that sends an email to the resident.
    """

    def update(
        self,
        report,
        notification_data,
    ):
        send_mail(
            subject=notification_data["subject"],
            message=notification_data["message"],
            from_email="noreply@potholesyqr.com",
            recipient_list=[
                report.resident.email,
            ],
            fail_silently=False,
        )


class NotificationRecordObserver(ReportObserver):
    """
    Concrete Observer that stores the notification
    in the database.
    """

    def update(
        self,
        report,
        notification_data,
    ):
        Notification.objects.create(
            report=report,
            resident=report.resident,
            message=notification_data["message"],
        )


def notify_report_observers(
    report,
    subject,
    message,
):
    """
    Configure the Subject and notify all concrete observers.
    """

    notification_subject = ReportNotificationSubject()

    notification_subject.attach(
        EmailNotificationObserver()
    )

    notification_subject.attach(
        NotificationRecordObserver()
    )

    notification_data = {
        "subject": subject,
        "message": message,
    }

    notification_subject.notify(
        report,
        notification_data,
    )