from django.db import models
from datetime import datetime
from django.conf import settings
from django.core.exceptions import ValidationError

def validate_history_data(floor=None, building_floor=None, bathrooms=None, rooms=None, 
                        area_m2=None, age_years=None):
    """Validate history data and return errors"""
    errors = {}
    
    if floor is not None and building_floor is not None:
        if floor > building_floor:
            errors['Floor'] = "Floor Number لا يمكن أن يكون أكبر من Building Floor Number"
    
    if bathrooms is not None and rooms is not None:
        if bathrooms > rooms:
            errors['Bathrooms'] = "Bathrooms Number لا يمكن أن يكون أكبر من Rooms Number"
    
    if area_m2 is not None and area_m2 <= 0:
        errors['Area_m2'] = "Area لا يمكن أن تكون سالبة"
    
    if bathrooms is not None and bathrooms < 0:
        errors['Bathrooms'] = "Bathrooms Number لا يمكن أن يكون سالباً"
    
    if building_floor is not None and building_floor < 0:
        errors['Building_Floor'] = "Building Floor Number لا يمكن أن يكون سالباً"
    
    if rooms is not None and rooms < 0:
        errors['Rooms'] = "Rooms Number لا يمكن أن يكون سالباً"
    
    if age_years is not None and age_years < 0:
        errors['Age_Years'] = "Building Age لا يمكن أن يكون سالباً"
    
    if floor is not None and floor < 0:
        errors['Floor'] = "Floor Number لا يمكن أن يكون سالباً"
    
    return errors

class History(models.Model):
    LOCATION_CHOICES = [
        ('akrama', 'Akrama'),
        ('al-nuzha', 'Al-Nuzha'),
        ('muhajreen', 'Muhajreen'),
    ]
    CONDITION_CHOICES = [
        ('normal', 'Normal'),
        ('delux', 'Delux'),
        ('super-delux', 'Super-Delux'),
    ]
    ORIENTATION_CHOICES = [
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
        ('east-west', 'East-West'),
        ('north-east', 'North-East'),
        ('north-west', 'North-West'),
        ('south-east', 'South-East'),
        ('south-west', 'South-West'),
        ('south-north', 'South-North'),
    ]
    FURNISHED_CHOICES = [
        ('furnished', 'Furnished'),
        ('unfurnished', 'Unfurnished'),
    ]
    Services_Choices = [
        ('bus_station', 'Near Bus Station'),
        ('hospital', 'Near Hospital'),
        ('main_street', 'Near Main Street'),
        ('school', 'Near School'),
        ('Shooping_center', 'Near Shooping Center'),
    ]
    
    Location = models.CharField(max_length=50, choices=LOCATION_CHOICES, null=False, verbose_name="Location")
    Area_m2 = models.FloatField(null=False, help_text="Enter Area in square meters", verbose_name="Area (m²)")
    Bathrooms = models.IntegerField(null=False, help_text="Enter A number", verbose_name="Bathrooms")
    Condition = models.CharField(max_length=50, choices=CONDITION_CHOICES, null=False, verbose_name="Condition")
    Building_Floor = models.IntegerField(null=False, help_text="Enter A number", verbose_name="Building Floor")
    Rooms = models.IntegerField(null=False, help_text="Enter A number", verbose_name="Number of Rooms")
    Age_Years = models.IntegerField(null=False, help_text="Enter A number", verbose_name="Building Age (Years)")
    Furnished = models.CharField(max_length=50, choices=FURNISHED_CHOICES, null=False, verbose_name="Furnished Status")
    Floor = models.IntegerField(null=False, help_text="Enter A number", verbose_name="Floor Number")
    Orientation = models.CharField(max_length=50, choices=ORIENTATION_CHOICES, null=False, verbose_name="Orientation")
    Services = models.JSONField(default=list, verbose_name="Services",blank=True)
    price = models.IntegerField(null=False, help_text="Enter A number", verbose_name="Price")
    Date = models.DateTimeField(default=datetime.now, verbose_name="Listing Date")  

    # ربط السجل بالمستخدم الحالي من تطبيق الحسابات
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="User", related_name='history')

    def __str__(self):
        return f"{self.Location}-{self.price}"
    
    def clean(self):
        errors_dict = validate_history_data(
            floor=self.Floor,
            building_floor=self.Building_Floor,
            bathrooms=self.Bathrooms,
            rooms=self.Rooms,
            area_m2=self.Area_m2,
            age_years=self.Age_Years
        )
        if errors_dict:
            raise ValidationError(errors_dict)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    class Meta:
        ordering = ['-Date']