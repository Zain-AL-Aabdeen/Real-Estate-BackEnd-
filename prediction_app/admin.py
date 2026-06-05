from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import History, validate_history_data

class HistoryForm(forms.ModelForm):
    Services_Choices = [
        ('bus_station', 'Near Bus Station'),
        ('hospital', 'Near Hospital'),
        ('main_street', 'Near Main Street'),
        ('school', 'Near School'),
        ('Shooping_center', 'Near Shooping Center'),
    ]
    Services = forms.MultipleChoiceField(choices=Services_Choices, widget=forms.CheckboxSelectMultiple, required=False)
    
    class Meta:
        model = History
        fields = '__all__'
        
    def clean(self):
        cleaned_data = super().clean()
        errors_dict = validate_history_data(
            floor=cleaned_data.get('Floor'),
            building_floor=cleaned_data.get('Building_Floor'),
            bathrooms=cleaned_data.get('Bathrooms'),
            rooms=cleaned_data.get('Rooms'),
            area_m2=cleaned_data.get('Area_m2'),
            age_years=cleaned_data.get('Age_Years')
        )
        if errors_dict:
            raise ValidationError(errors_dict)
    
@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    form = HistoryForm