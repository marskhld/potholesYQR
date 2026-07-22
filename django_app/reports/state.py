from abc import ABC

class PotholeReportState(ABC): # interface/abstract class for PotholeReportState
    """
    Defines all permissible actions/transitions
    """

    def approve(self, report, severity):
        raise ValueError("This report cannot be approved.")

    def reject(self, report):
        raise ValueError("This report cannot be rejected.")

    def start_work(self, report):
        raise ValueError("Work cannot be started.")

    def pend(self, report):
        raise ValueError("This report cannot be moved to Pending.")

    def close(self, report):
        raise ValueError("This report cannot be closed.")

    def prevent_transition_to_new(self, report):
        raise ValueError("A report cannot be moved back to New state.")
    
    @property
    def map_icon_color(self):
        return "gray"  # Default fallback

# concrete states - define allowed transitions for each state. if not there, then error
class NewState(PotholeReportState): # first state of a report, when it is first submitted
    def approve(self, report, severity): 
        if severity not in ['low', 'medium', 'high']:
            raise ValueError("A valid severity must be assigned upon approval.")
        report.severity = severity
        report.set_state("approved")

    def reject(self, report):
        report.set_state("rejected")

    @property
    def map_icon_color(self):
        return "blue"

class RejectedState(PotholeReportState):
    @property
    def map_icon_color(self):
        return "red"

class ApprovedState(PotholeReportState):
    def start_work(self, report):
        report.set_state("in_progress")

    def pend(self, report):
        report.set_state("pending")

    @property
    def map_icon_color(self):
        return "green"

class PendingState(PotholeReportState):
    def start_work(self, report):
        report.set_state("in_progress")

    @property
    def map_icon_color(self):
        return "yellow" 

class InProgressState(PotholeReportState):
    def close(self, report):
        report.set_state("closed")

    @property
    def map_icon_color(self):
        return "orange"  

class ClosedState(PotholeReportState):
    @property
    def map_icon_color(self):
        return "dark-grey" 

def get_state(status): # helper function
    states = {
        "new": NewState(),
        "approved": ApprovedState(),
        "rejected": RejectedState(),
        "pending": PendingState(),
        "in_progress": InProgressState(),
        "closed": ClosedState(),
    }
    return states.get(status, NewState())
