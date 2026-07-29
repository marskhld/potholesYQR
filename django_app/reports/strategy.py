# Course:      CS 476
# Project:     PotholesYQR
# File:        reports/strategy.py
# Description: Implementation of strategy design pattern
# 
# Authors:
#     Opinder Kaur
#     Christopher Taylor
from abc import ABC, abstractmethod
 
class SearchCriteria:  
    def __init__(self, ticket=None, status=None, severity=None, start_date=None, end_date=None):
        self.ticket = ticket
        self.status = status
        self.severity = severity
        self.start_date = start_date
        self.end_date = end_date
        
class FilterStrategy(ABC):
    # Abstract Strategy defining the search() interface.
    @abstractmethod
    def search(self, reports, criteria: SearchCriteria):
        pass

class TicketFilterStrategy(FilterStrategy):
    # Filter pothole reports based on ticket number.
    def search(self, reports, criteria):
        if criteria.ticket:
            return reports.filter(ticket_number__icontains=criteria.ticket)
        return reports
 
class StatusFilterStrategy(FilterStrategy):
    # Filter reports based on status.
    def search(self, reports, criteria):
        if criteria.status:
            return reports.filter(current_status=criteria.status)
        return reports

class SeverityFilterStrategy(FilterStrategy):
    # Filter reports based on severity
    def search(self, reports, criteria):
        if criteria.severity:
            return reports.filter(severity=criteria.severity)
        return reports

class DateRangeFilterStrategy(FilterStrategy):   
    # Filter reports based on selected date range  
    def search(self, reports, criteria):
        if criteria.start_date and criteria.end_date:
            return reports.filter(created_date__date__range=(criteria.start_date, criteria.end_date))
        return reports

class StatusSeverityTimeStrategy(FilterStrategy):
    # Filter reports based on status, severity and selected date range
    def search(self, reports, criteria):
        qs = reports
        if criteria.status:
            qs = qs.filter(current_status=criteria.status)
        if criteria.severity:
            qs = qs.filter(severity=criteria.severity)
        if criteria.start_date and criteria.end_date:
            qs = qs.filter(created_date__date__range=(criteria.start_date, criteria.end_date))
        return qs

class StrategyContext:
    # Context class that executes the selected search strategy
    def __init__(self, strategy):
        self.strategy = strategy
    def execute(self, reports, criteria: SearchCriteria):
        return self.strategy.search(reports, criteria)