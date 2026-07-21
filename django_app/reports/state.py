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
    
    @property
    def map_icon_color(self):
        return "gray"  # Default fallback