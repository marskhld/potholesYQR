import uuid

from django.db import models

from .state import get_state


# ==========================================================
# TICKET NUMBER GENERATION
# ==========================================================

def generate_ticket():
    """
    Generate a unique ticket number such as:

    YQR-A1B2C3D4
    """

    return f"YQR-{str(uuid.uuid4())[:8].upper()}"


# ==========================================================
# RESIDENT
# ==========================================================

class Resident(models.Model):
    """
    Stores information about a resident who submits
    one or more pothole reports.
    """

    name = models.CharField(
        max_length=100,
    )

    email = models.EmailField(
        db_index=True,
    )

    phone_number = models.CharField(
        max_length=20,
    )

    def __str__(self):
        return f"{self.name} ({self.email})"


# ==========================================================
# STAFF
# ==========================================================

class Staff(models.Model):
    """
    Stores staff-profile information used by the
    report activity-history system.

    Authentication is handled by Django's built-in User model.
    """

    username = models.CharField(
        max_length=50,
        unique=True,
    )

    name = models.CharField(
        max_length=100,
    )

    def __str__(self):
        return self.name or self.username


# ==========================================================
# POTHOLE REPORT
# ==========================================================

class PotholeReport(models.Model):
    """
    Stores a pothole report submitted by a resident.
    """

    STATUS_CHOICES = [
        ("new", "New"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("in_progress", "In Progress"),
        ("pending", "Pending"),
        ("closed", "Closed"),
    ]

    SEVERITY_CHOICES = [
        ("n/a", "Not Assessed"),
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    
    
    ALLOWED_TRANSITIONS = {
        "new": [
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        "approved": [
            ("in_progress", "In Progress"),
            ("pending", "Pending"),
        ],
        "rejected": [],
        "in_progress": [
            ("pending", "Pending"),
            ("closed", "Closed"),
        ],
        "pending": [
            ("in_progress", "In Progress"),
        ],
        "closed": [],
    }

    resident = models.ForeignKey(
        Resident,
        on_delete=models.CASCADE,
    )

    address = models.CharField(
        max_length=255,
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
    )

    description = models.TextField(
        max_length=500,
    )

    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default="n/a",
    )

    current_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
    )

    ticket_number = models.CharField(
        max_length=20,
        unique=True,
        default=generate_ticket,
        editable=False,
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
    )

    updated_date = models.DateTimeField(
        auto_now=True,
    )

    staff_notes = models.TextField(
        blank=True,
        default="",
    )

    public_notes = models.TextField(
        blank=True,
        default="",
    )

    # ======================================================
    # STATUS TRANSITION HELPERS
    # ======================================================

    def get_allowed_status_choices(self):
        """
        Return the valid next statuses based on the
        report's current status.

        Examples:

        New:
            Approved, Rejected

        Approved:
            In Progress, Pending

        Closed:
            No further transitions
        """

        return self.ALLOWED_TRANSITIONS.get(
            self.current_status,
            [],
        )

    def can_transition_to(self, new_status):
        """
        Return True when the requested transition is allowed.
        """

        allowed_statuses = {
            value
            for value, _ in self.get_allowed_status_choices()
        }

        return new_status in allowed_statuses

    # ======================================================
    # STATE DESIGN PATTERN
    # ======================================================

    @property
    def state(self):
        """
        Return the concrete State object corresponding to
        the report's current status.
        """

        return get_state(self.current_status)

    def _set_state(self, new_status):
        """
        Internal helper used by concrete State classes.

        Views should call transition_to() instead of calling
        this method directly.
        """

        valid_statuses = {
            value
            for value, _ in self.STATUS_CHOICES
        }

        if new_status not in valid_statuses:
            raise ValueError(
                f"Unknown report status: {new_status}"
            )

        self.current_status = new_status
        self.save()

    def approve(self, severity=None):
        """
        Delegate approval to the current State object.
        """

        self.state.approve(
            self,
            severity,
        )

    def reject(self):
        """
        Delegate rejection to the current State object.
        """

        self.state.reject(self)

    def start_work(self):
        """
        Delegate the In Progress transition to the
        current State object.
        """

        self.state.start_work(self)

    def pend(self):
        """
        Delegate the Pending transition to the
        current State object.
        """

        self.state.pend(self)

    def close(self):
        """
        Delegate the Closed transition to the
        current State object.
        """

        self.state.close(self)

    def transition_to(self, new_status, severity=None):
        """
        Request a valid status transition.

        The transition is first checked against the required
        transition diagram. The operation is then delegated
        to the current concrete State object.
        """

        # Saving without changing status is allowed.
        if new_status == self.current_status:
            return

        if not self.can_transition_to(new_status):
            current_label = self.get_current_status_display()

            new_label = dict(
                self.STATUS_CHOICES
            ).get(
                new_status,
                new_status,
            )

            raise ValueError(
                f"Cannot change report from "
                f"{current_label} to {new_label}."
            )

        if new_status == "approved":
            self.approve(
                severity=severity,
            )

        elif new_status == "rejected":
            self.reject()

        elif new_status == "in_progress":
            self.start_work()

        elif new_status == "pending":
            self.pend()

        elif new_status == "closed":
            self.close()

        else:
            raise ValueError(
                f"Unsupported report status: {new_status}"
            )

    def __str__(self):
        return f"{self.ticket_number} - {self.address}"


# ==========================================================
# PHOTO
# ==========================================================

class Photo(models.Model):
    """
    Stores a photo uploaded for a pothole report.
    """

    report = models.ForeignKey(
        PotholeReport,
        on_delete=models.CASCADE,
    )

    file_path = models.ImageField(
        upload_to="photos/",
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"Photo for {self.report.ticket_number}"


# ==========================================================
# NOTIFICATION
# ==========================================================

class Notification(models.Model):
    """
    Stores a record of an email notification sent
    to a resident.
    """

    report = models.ForeignKey(
        PotholeReport,
        on_delete=models.CASCADE,
    )

    resident = models.ForeignKey(
        Resident,
        on_delete=models.CASCADE,
    )

    message = models.TextField()

    sent_date = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"Notification for {self.report.ticket_number}"


# ==========================================================
# STATUS AND ACTIVITY HISTORY
# ==========================================================

class StatusHistory(models.Model):
    """
    Stores staff activity involving report status,
    severity, location, details, or notes.
    """

    ACTIVITY_CHOICES = [
        ("status_updated", "Status Updated"),
        ("details_updated", "Report Details Updated"),
        ("location_updated", "Location Updated"),
        ("severity_updated", "Severity Updated"),
        ("notes_updated", "Notes Updated"),
        ("multiple_updates", "Multiple Updates"),
    ]

    report = models.ForeignKey(
        PotholeReport,
        on_delete=models.CASCADE,
    )

    activity_type = models.CharField(
        max_length=30,
        choices=ACTIVITY_CHOICES,
        default="status_updated",
    )

    old_status = models.CharField(
        max_length=20,
        choices=PotholeReport.STATUS_CHOICES,
        blank=True,
        default="",
    )

    new_status = models.CharField(
        max_length=20,
        choices=PotholeReport.STATUS_CHOICES,
        blank=True,
        default="",
    )

    change_details = models.TextField(
        blank=True,
        default="",
    )

    changed_at = models.DateTimeField(
        auto_now_add=True,
    )

    changed_by = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    staff_notes = models.TextField(
        blank=True,
        default="",
    )

    public_notes = models.TextField(
        blank=True,
        default="",
    )

    class Meta:
        ordering = [
            "-changed_at",
        ]

        verbose_name = (
            "Status and Activity History"
        )

        verbose_name_plural = (
            "Status and Activity Histories"
        )

    def __str__(self):
        return (
            f"{self.report.ticket_number} - "
            f"{self.get_activity_type_display()}"
        )