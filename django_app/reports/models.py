import uuid

from django.db import models

from .state import get_state

# Note: Django auto-creates id fields for each model, so we don't need to define them manually
# Django naming conventions:
#       PascalCase - for class names
#       snake_case - for variable names

def generate_ticket():  # function to generate ticket numbers for pothole reports
    return ("YQR-" + str(uuid.uuid4())[:8].upper())  # generates unique number with prefix 'YQR-'
    # first 8 characters are capitalized
class Resident(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()  # validates proper email format
    phone_number = models.CharField(max_length=20)

class Staff(models.Model):
    username = models.CharField(max_length=50, unique=True)  # ensures all staff usernames are unique
    name = models.CharField(max_length=100)
    # Note: don't need password - the actual login/password stuff will be handled by Django's built-in auth system
class PotholeReport(models.Model):  # model for storing pothole report information
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE) 
    address = models.CharField(max_length=255)  # address of the pothole, to display to staff and for geocoding to get coordinates
        # TODO: add to class diagram
    latitude = models.DecimalField(max_digits=9, decimal_places=6)  # map coordinates for the pothole location (6 decimal places for precision)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    description = models.TextField(max_length=500)
    severity = models.CharField(
        max_length=20,
        choices=[
            ("n/a", "Not Assessed"),
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
        ],
        default="n/a",
    )
    ticket_number = models.CharField(max_length=20, unique=True, default=generate_ticket)  # auto-generate ticket number!
    created_date = models.DateTimeField(auto_now_add=True)  # automatically sets to current date/time when object is created (only once!)
    updated_date = models.DateTimeField(auto_now=True)  # updates every time report is saved
    staff_notes = models.TextField(blank=True)  
    public_notes = models.TextField(blank=True) 

    # TODO: add observers later when we implement the observer design pattern

    STATUS_CHOICES = [ # first value is what's stored in the database, second value is for UI
        ("new", "New"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("in_progress", "In Progress"),
        ("pending", "Pending"),
        ("closed", "Closed"),
    ]
    current_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="new"
    )  # TODO: changed the name to status instead of state

    @property
    def state(self):  # will return the current State object corresponding to current_status
        return get_state(self.current_status)

    @property
    def icon_color(self):
        return self.state.map_icon_color

    def set_state(self, new_status):
        self.current_status = new_status
        self.save()

        # transition methods that delegate to the current state object
    def approve(self, severity):
        self.state.approve(self, severity)

    def reject(self):
        self.state.reject(self)

    def start_work(self):
        self.state.start_work(self)

    def pend(self):
        self.state.pend(self)

    def close(self):
        self.state.close(self)

class Photo(models.Model):
    report = models.ForeignKey(PotholeReport, on_delete=models.CASCADE)  
    file_path = models.ImageField(upload_to="photos/") 
    timestamp = models.DateTimeField(auto_now_add=True)  # TODO: not sure why we had this lol

class Notification(models.Model):  # record of every email notif sent to resident
    report = models.ForeignKey(PotholeReport, on_delete=models.CASCADE) 
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE)
    message = models.TextField()
    sent_date = models.DateTimeField(auto_now_add=True)  # automatically sets to current date/time when object is created

class StatusHistory(models.Model):  # track status changes on reports
    report = models.ForeignKey(PotholeReport, on_delete=models.CASCADE)
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_at = models.DateTimeField(auto_now_add=True)  # records when the status change occurred
    changed_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)  # if staff deleted, then status history still remains
    staff_notes = models.TextField(blank=True)
    public_notes = models.TextField(blank=True)
