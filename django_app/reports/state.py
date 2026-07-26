from abc import ABC


class PotholeReportState(ABC):
    """
    Base State class.

    Each method represents a possible status transition.
    Concrete State classes override only the transitions
    that are allowed from that state.
    """

    def approve(self, report, severity=None):
        raise ValueError(
            f"A report in '{report.current_status}' status "
            "cannot be approved."
        )

    def reject(self, report):
        raise ValueError(
            f"A report in '{report.current_status}' status "
            "cannot be rejected."
        )

    def start_work(self, report):
        raise ValueError(
            f"Work cannot be started while the report is "
            f"'{report.current_status}'."
        )

    def pend(self, report):
        raise ValueError(
            f"A report in '{report.current_status}' status "
            "cannot be moved to Pending."
        )

    def close(self, report):
        raise ValueError(
            f"A report in '{report.current_status}' status "
            "cannot be closed."
        )

# ==========================================================
# NEW STATE
#
# Allowed:
# New -> Approved
# New -> Rejected
# ==========================================================

class NewState(PotholeReportState):

    def approve(self, report, severity=None):
        valid_severities = {
            "low",
            "medium",
            "high",
        }

        if severity not in valid_severities:
            raise ValueError(
                "A valid severity must be assigned "
                "when approving a report."
            )

        report.severity = severity
        report._set_state("approved")

    def reject(self, report):
        report._set_state("rejected")

# ==========================================================
# APPROVED STATE
#
# Allowed:
# Approved -> In Progress
# Approved -> Pending
# ==========================================================

class ApprovedState(PotholeReportState):

    def start_work(self, report):
        report._set_state("in_progress")

    def pend(self, report):
        report._set_state("pending")

# ==========================================================
# REJECTED STATE
#
# Final state: no further transitions
# ==========================================================

class RejectedState(PotholeReportState):
    pass
# ==========================================================
# PENDING STATE
#
# Allowed:
# Pending -> In Progress
# ==========================================================

class PendingState(PotholeReportState):

    def start_work(self, report):
        report._set_state("in_progress")

# ==========================================================
# IN PROGRESS STATE
#
# Allowed:
# In Progress -> Pending
# In Progress -> Closed
# ==========================================================

class InProgressState(PotholeReportState):

    def pend(self, report):
        report._set_state("pending")

    def close(self, report):
        report._set_state("closed")

# ==========================================================
# CLOSED STATE
#
# Final state: no further transitions
# ==========================================================

class ClosedState(PotholeReportState):
    pass

# Create one reusable object for each concrete State.
STATE_MAP = {
    "new": NewState(),
    "approved": ApprovedState(),
    "rejected": RejectedState(),
    "pending": PendingState(),
    "in_progress": InProgressState(),
    "closed": ClosedState(),
}


def get_state(status):
    """
    Return the concrete State object matching the stored status.
    """

    try:
        return STATE_MAP[status]

    except KeyError as error:
        raise ValueError(
            f"Unknown pothole report status: {status}"
        ) from error