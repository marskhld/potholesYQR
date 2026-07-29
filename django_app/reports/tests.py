from django.core import mail
from django.test import TestCase

from .models import (
    Notification,
    PotholeReport,
    Resident,
)
from .observers import (
    EmailNotificationObserver,
    NotificationRecordObserver,
    ReportNotificationSubject,
    ReportObserver,
    notify_report_observers,
)


class TestObserver(ReportObserver):
    """
    Simple test observer used to verify Subject behaviour.
    """

    def __init__(self):
        self.was_notified = False
        self.received_report = None
        self.received_data = None

    def update(
        self,
        report,
        notification_data,
    ):
        self.was_notified = True
        self.received_report = report
        self.received_data = notification_data


class ObserverPatternTests(TestCase):

    def setUp(self):
        self.resident = Resident.objects.create(
            name="Test Resident",
            email="resident@example.com",
            phone_number="3065551234",
        )

        self.report = PotholeReport.objects.create(
            resident=self.resident,
            address="123 Albert Street, Regina",
            latitude="50.445200",
            longitude="-104.618900",
            description="Large pothole near the road.",
        )

        self.notification_data = {
            "subject": "Test Notification",
            "message": "This is a test notification.",
        }

    def test_subject_attaches_and_notifies_observer(self):
        subject = ReportNotificationSubject()
        observer = TestObserver()

        subject.attach(observer)

        subject.notify(
            self.report,
            self.notification_data,
        )

        self.assertTrue(
            observer.was_notified
        )

        self.assertEqual(
            observer.received_report,
            self.report,
        )

        self.assertEqual(
            observer.received_data,
            self.notification_data,
        )

    def test_subject_detaches_observer(self):
        subject = ReportNotificationSubject()
        observer = TestObserver()

        subject.attach(observer)
        subject.detach(observer)

        subject.notify(
            self.report,
            self.notification_data,
        )

        self.assertFalse(
            observer.was_notified
        )

    def test_subject_prevents_duplicate_observer(self):
        subject = ReportNotificationSubject()
        observer = TestObserver()

        subject.attach(observer)
        subject.attach(observer)

        self.assertEqual(
            len(subject._observers),
            1,
        )

    def test_email_observer_sends_one_email(self):
        observer = EmailNotificationObserver()

        observer.update(
            self.report,
            self.notification_data,
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        self.assertEqual(
            mail.outbox[0].subject,
            "Test Notification",
        )

        self.assertEqual(
            mail.outbox[0].to,
            ["resident@example.com"],
        )

    def test_record_observer_creates_notification(self):
        observer = NotificationRecordObserver()

        observer.update(
            self.report,
            self.notification_data,
        )

        self.assertEqual(
            Notification.objects.count(),
            1,
        )

        notification = Notification.objects.first()

        self.assertEqual(
            notification.report,
            self.report,
        )

        self.assertEqual(
            notification.resident,
            self.resident,
        )

        self.assertEqual(
            notification.message,
            "This is a test notification.",
        )

    def test_helper_notifies_both_observers(self):
        notify_report_observers(
            report=self.report,
            subject="Combined Observer Test",
            message="Both observers should react.",
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        self.assertEqual(
            Notification.objects.count(),
            1,
        )