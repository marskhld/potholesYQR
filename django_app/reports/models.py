from django.db import models # Django's toolkit for defining database tables
import uuid # generates unique identifiers for ticket numbers

# Create your models here.
# Note: Django auto-creates id fields for each model, so we don't need to define them manually 
# Django naming conventions: 
#       PascalCase for class names
#       snake_case for variable names

def generate_ticket(): # function to generate ticket numbers for pothole reports
    return 'YQR-' + str(uuid.uuid4())[:8].upper() # generates unique number with prefix 'YQR-'  
            # first 8 characters are capitalized

class Resident(models.Model): # Resident model to store information about residents reporting potholes
    name = models.CharField(max_length=100)
    email = models.EmailField() # validates proper email format
    phone = models.CharField(max_length=20)

class Staff(models.Model): # stores staff profile info
    username = models.CharField(max_length=50, unique=True) # ensures all staff usernames are unique
    name = models.CharField(max_length=100)
        # Note: don't need password - the actual login/password stuff will be handled by Django's built-in auth system

class PotholeReport(models.Model): # model for storing pothole report information
    STATUS_CHOICES = [
        ('new', 'New'), # first value is what's stored in the database, second value is for UI
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending'),
        ('closed', 'Closed'),
    ]
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE) # links each report to a specific resident, via foreign key relationship
                                            # on_delete=models.CASCADE means if resident is deleted, then their reports are deleted
    latitude = models.DecimalField(max_digits=9, decimal_places=6) # map coordinates for the pothole location, with 6 decimal places for precision
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium') # severity of pothole, with default value
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new') # TODO: changed the name to status instead of state
    ticket_number = models.CharField(max_length=20, unique=True, default=generate_ticket) # auto-generate ticket number!
    created_date = models.DateTimeField(auto_now_add=True) # automatically sets to current date/time when object is created (only once!)
    updated_date = models.DateTimeField(auto_now=True) # updates every time report is saved
    staff_notes = models.TextField(blank=True) # notes for staff only, optional to fill
    public_notes = models.TextField(blank=True) # notes for public viewing, optional to fill
        # TODO: add observers later when we implement the observer design pattern

class Photo(models.Model):
    report = models.ForeignKey(PotholeReport, on_delete=models.CASCADE) # linked to report, so if report is deleted, photo is deleted too
    file_path = models.ImageField(upload_to='photos/') # will handle photo uploads and store in the 'photos/' directory
    timestamp = models.DateTimeField(auto_now_add=True) # TODO: not sure why we had this lol

class Notification(models.Model): # record of every email notif sent to resident
    report = models.ForeignKey(PotholeReport, on_delete=models.CASCADE) # linked to report
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE) # linked to resident
    message = models.TextField() 
    sent_date = models.DateTimeField(auto_now_add=True) # automatically sets to current date/time when object is created 

class StatusHistory(models.Model): # track status changes on reports
    report = models.ForeignKey(PotholeReport, on_delete=models.CASCADE) # linked to report
    old_status = models.CharField(max_length=20) 
    new_status = models.CharField(max_length=20)
    changed_at = models.DateTimeField(auto_now_add=True) # records when the status change occurred
    changed_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True) # links to staff, but not dependent on staff existing
        # if staff deleted, then status history still remains
    staff_notes = models.TextField(blank=True) # will store snapshot of notes at the moment the status changed
    public_notes = models.TextField(blank=True) 