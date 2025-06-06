from django.db import models
from Контор.models import Resident, ApartmentBlock
from django.utils import timezone
from django.contrib.auth.models import User
    
class HOA_members(models.Model):
    members = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hoa_members')
    memberName = models.TextField(max_length=25, null=False)
    category = models.CharField(
        max_length=50,
        choices=[
            ('directors', 'Directors'),
            ('executive', 'Executive'),
            ('supervisory', 'Supervisory'),
        ],
        default='other'
    )
    password = models.CharField(null=False, max_length = 20)
    description = models.CharField(blank=True, null=True, max_length=255)
    since = models.DateTimeField()

    def __str__(self):
        return f"HOA Member: {self.memberName}, Category: {self.category}, Since: {self.since.strftime('%Y-%m-%d')}"

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fname = models.CharField(max_length = 20)
    lname = models.CharField(max_length = 20) 
    RD = models.CharField(max_length = 20) 
    phone_number = models.CharField(max_length = 20)  
    role = models.CharField(
        max_length=50,
        choices=[
            ('Cleaner', 'Cleaner'),
            ('Utility', 'Utility'),
            ('Garbage_Man', 'Garbage_Man'),
            ('Other', 'Other')
        ],
        default='other'
    )
    staff_salary = models.IntegerField(null=True)
    description = models.CharField(max_length = 20) 
    since = models.DateTimeField(default=timezone.now)
    password = models.CharField(max_length = 20) 

    def __str__(self):
        return f"ID: {self.id}, Name: {self.fname}, RD: {self.RD}, role: {self.role}"
    
class PayDay(models.Model):
    date = models.DateTimeField(default=timezone.now)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    staff_salary = models.DecimalField(max_digits=10, decimal_places=2) 
    description = models.CharField(max_length = 100) 
    pretext = models.CharField(max_length = 50)
    def __str__(self):
        return f"ID: {self.id}, Name: {self.fname}, RD: {self.RD}, role: {self.role}"
    
class BudgetOfApartmentBlock(models.Model):
    budget_month = models.DateTimeField(default=timezone.now) 
    total_budget_amount = models.DecimalField(max_digits=10, decimal_places=2)  
    staff_salaries_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    resident_utility_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    common_property_expenses_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.TextField(blank=True, null=True)  
    additional_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pretext = models.CharField(max_length=100) 
    created_at = models.DateTimeField(default=timezone.now)  
    apartment_block = models.ForeignKey(
        ApartmentBlock, 
        on_delete=models.CASCADE, 
        related_name='budgetofapartmentblock'
    ) 

    def __str__(self):
        return f"Budget for {self.budget_month} - Total: {self.total_budget_amount}"

    def calculate_total_expenses(self):
        """Helper method to calculate the total expenses."""
        return self.staff_salaries_total + self.common_property_expenses_total + self.additional_expenses

class TimeTable(models.Model):
    date = models.DateField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    job_type = models.CharField(
        max_length=50,
        choices=[
            ('General', 'General'),
            ('Utility', 'Utility'),
            ('Garbage_Collection', 'Garbage_Collection'),
            ('Scheduled_Maintenance', 'Scheduled_Maintenance'),
            ('Other', 'Other'),
        ],
        default='General'
    )
    job_site = models.ForeignKey(ApartmentBlock, on_delete=models.CASCADE, related_name='timetables')
    job_description = models.CharField(max_length=150)
    attendance = models.CharField(
        max_length=50,
        choices=[
            ('Did Not Come To Work', 'Did Not Come To Work'),
            ('Came To Work', 'Came To Work'),
            ('Pending / Shift Clock', 'Pending / Shift Clock'),
            ('Other', 'Other'),
        ],
        default='Pending / Shift Clock'
    )

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"ID: {self.date}, Name: {self.user}"

class BudgetRequest(models.Model):
    name = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    request_type = models.CharField(
        max_length=50,
        choices=[
            ('General', 'General'),
            ('Utility', 'Utility'),
            ('Garbage_Collection', 'Garbage_Collection'),
            ('Scheduled_Maintenance', 'Scheduled_Maintenance'),
            ('Other', 'Other'),
        ],
        default='General'
    )
    request_info = models.ImageField(upload_to='budget_requests/', null=True, blank=True)
    pretext = models.CharField(
        max_length=50,
        choices=[
            ('Low_on_Supply', 'Low_on_Supply'),
            ('Broken', 'Broken'),
            ('Out_of_Date', 'Out_of_Date'),
            ('Defective', 'Defective'),
            ('Other', 'Other'),
        ],
        default='Low_on_Supply'
    )
    comment = models.CharField(max_length=150)
    request_date = models.DateTimeField(default=timezone.now)
    desicion = models.CharField(
        max_length=50,
        choices=[
            ('Approved', 'Approved'),
            ('Denied', 'Denied'),
        ],
        default='Pending',
        null=True
    )
    desicion_comment = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"Name: {self.name}, Staff: {self.user}, Request_Type: {self.request_type}, role: {self.pretext}" 

class StaffSalary(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    salary_amount = models.DecimalField(max_digits=10, decimal_places=2)  
    month = models.DateTimeField(default=timezone.now) 
    paid_on = models.DateTimeField(default=timezone.now)
    bank_account= models.IntegerField(null=False)
    bank_type = models.CharField(
        max_length=50,
        choices=[
            ('Khan Bank', 'Khan Bank'),
            ('Golomt Bank', 'Golomt Bank'),
            ('TDB', 'TDB'),
            ('Khas Bank', 'Khas Bank'),
            ('Other', 'Other')
        ],
        default='Other'
    )
    def __str__(self):
        return f"Salary for {self.staff.lname} ({self.month.strftime('%B %Y')})"

class CommonProperty(models.Model):
    block = models.ForeignKey(ApartmentBlock, on_delete=models.CASCADE, related_name='common_properties')
    name = models.CharField(max_length=150, null=False)
    category = models.CharField(
        max_length=50,
        choices=[
            ('Structural', 'Structural'),
            ('Utility', 'Utility'),
            ('Amenity', 'Amenity'),
            ('Security', 'Security'),
            ('Other', 'Other')
        ],
        default='Other'
    )
    description = models.TextField(blank=True, null=True)
    maintenance_status = models.CharField(
        max_length=50,
        choices=[
            ('Good', 'Good'),
            ('Needs Repair', 'Needs Repair'),
            ('Under Maintenance', 'Under Maintenance')
        ],
        default='Good'
    )
    last_maintenance_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"({self.category})"
    
class StructuralElement(models.Model):
    property_category = models.CharField(
        max_length=50,
        choices=[
            ('Structural', 'Structural'),
            ('Utility', 'Utility'),
            ('Amenity', 'Amenity'),
            ('Security', 'Security'),
            ('Other', 'Other')
        ],
        default='Other'
    )
    apartmentblock = models.ForeignKey(ApartmentBlock, on_delete=models.CASCADE, related_name='structural_elements_location')
    unit = models.IntegerField(null=True)
    story = models.IntegerField(null=True)
    element_type = models.CharField(
        max_length=50,
        choices=[
            ('Exterior Wall', 'Exterior Wall'),
            ('Load-Bearing Wall', 'Load-Bearing Wall'),
            ('Roof', 'Roof'),
            ('Column', 'Column'),
            ('Basement', 'Basement'),
            ('Attic', 'Attic')
        ]
    )
    condition = models.CharField(
        max_length=50,
        choices=[
            ('Intact', 'Intact'),
            ('Damaged', 'Damaged'),
            ('Under Repair', 'Under Repair')
        ],
        default='Intact'
    )
    inspection_date = models.DateField(null=False, blank=True)

    def __str__(self):
        return f"{self.element_type} Condition: {self.condition} Last Inspection Date: {self.inspection_date}"

class UtilitySystem(models.Model):
    property_category = models.CharField(
        max_length=50,
        choices=[
            ('Structural', 'Structural'),
            ('Utility', 'Utility'),
            ('Amenity', 'Amenity'),
            ('Security', 'Security'),
            ('Other', 'Other')
        ],
        default='Other'
    )
    apartmentblock = models.ForeignKey(ApartmentBlock, on_delete=models.CASCADE, related_name='utility_systems_location')
    unit = models.CharField(null=True, max_length=10)
    story = models.CharField(null=True,  max_length=10)
    system_type = models.CharField(
        max_length=50,
        choices=[
            ('Heating System', 'Heating System'),
            ('Electricity Supply', 'Electricity Supply'),
            ('Water Supply', 'Water Supply'),
            ('Sewage System', 'Sewage System')
        ]
    )
    operational_status = models.CharField(
        max_length=50,
        choices=[
            ('Operational', 'Operational'),
            ('Faulty', 'Faulty'),
            ('Maintenance Needed', 'Maintenance Needed')
        ],
        default='Operational'
    )
    last_service_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.system_type}"

class SharedAmenity(models.Model):
    property_category = models.CharField(
        max_length=50,
        choices=[
            ('Structural', 'Structural'),
            ('Utility', 'Utility'),
            ('Amenity', 'Amenity'),
            ('Security', 'Security'),
            ('Other', 'Other')
        ],
        default='Other'
    )
    apartmentblock = models.ForeignKey(ApartmentBlock, on_delete=models.CASCADE, related_name='amenities_location')
    unit = models.CharField(null=True, max_length=10)
    story = models.CharField(null=True,  max_length=10)
    amenity_type = models.CharField(
        max_length=50,
        choices=[
            ('Public Pool', 'Public Pool'),
            ('Parking Lot', 'Parking Lot'),
            ('Stairwell', 'Stairwell'),
            ('Garbage Chute', 'Garbage Chute')
        ]
    )
    usage_status = models.CharField(
        max_length=50,
        choices=[
            ('Available', 'Available'),
            ('Under Maintenance', 'Under Maintenance'),
            ('Restricted', 'Restricted')
        ],
        default='Available'
    )
    last_cleaned_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.amenity_type}"

class Security(models.Model):
    property_category = models.CharField(
        max_length=50,
        choices=[
            ('Structural', 'Structural'),
            ('Utility', 'Utility'),
            ('Amenity', 'Amenity'),
            ('Security', 'Security'),
            ('Other', 'Other')
        ],
        default='Other'
    )
    apartmentblock = models.ForeignKey(ApartmentBlock, on_delete=models.CASCADE, related_name='securities_location')
    unit = models.CharField(null=True, max_length=10)
    story = models.CharField(null=True,  max_length=10)
    type = models.CharField(
        max_length=50,
        choices=[
            ('CCTV', 'CCTV Cameras'),
            ('Security Guard', 'Security Guard'),
            ('Access Control System', 'Access Control System'),
            ('Alarm System', 'Alarm System'),
            ('Other', 'Other')
        ],
        default='Other'
    )
    location = models.CharField(max_length=255, help_text="Location where the security feature is installed")
    installation_date = models.DateTimeField(null=True, blank=True, help_text="Date of installation")
    condition = models.CharField(
        max_length=50,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
        ],
        default='good',
        help_text="Condition of the security feature"
    )
    notes = models.TextField(blank=True, help_text="Additional notes or observations about the security feature")

    def __str__(self):
        return f"{self.type} at {self.location} ({self.condition})"

class Property_Maintenance(models.Model):
    apartmentblock = models.ForeignKey(ApartmentBlock, on_delete=models.CASCADE)
    property_category = models.CharField(max_length=100)
    property_id = models.IntegerField(null=True)
    maintenance_date = models.DateField()
    maintenance_cost = models.DecimalField(max_digits=10, decimal_places=2)
    property_image = models.ImageField(upload_to='maintenance_images/', null=True, blank=True)
    on_ground_location = models.CharField(max_length=100, blank=True)
    unit = models.IntegerField(blank=True, null=True)
    story = models.IntegerField(blank=True, null=True)
    next_maintenance_date = models.DateField()

    def __str__(self):
        return f"{self.apartmentblock} at {self.maintenance_date} ({self.property_category})"




