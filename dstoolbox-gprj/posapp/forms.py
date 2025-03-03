from django import forms
from django.utils import timezone
from .models import *

class RewardForm(forms.ModelForm):
    class Meta:
        model = Reward
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        # ตรวจสอบวันที่
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError('วันที่เริ่มต้นต้องก่อนวันที่สิ้นสุด')

        if start_date and start_date < timezone.now().date():
            raise forms.ValidationError('วันที่เริ่มต้นไม่สามารถเป็นวันที่ผ่านมาแล้วได้')

        if end_date and end_date < timezone.now().date():
            raise forms.ValidationError('วันที่สิ้นสุดไม่สามารถเป็นวันที่ผ่านมาแล้วได้')

        # ตั้งค่าฟิลด์ is_active ตามวันที่เริ่มต้น
        if start_date and start_date > timezone.now().date():
            cleaned_data['is_active'] = False  # ปิดใช้งานถ้าวันเริ่มต้นในอนาคต
        else:
            cleaned_data['is_active'] = True  # เปิดใช้งานถ้าผ่านวันที่เริ่มต้นแล้ว

        return cleaned_data

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'description', 'price', 'image', 'is_available']

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status_order']
        widgets = {
            'status_order': forms.Select(choices=Order.STATUS_CHOICES),
        }