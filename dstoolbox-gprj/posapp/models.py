from django.db import models
from django.utils.timezone import now


# ตรงนี้ต้องแก้ไขเพิ่มเติม ถ้าจพทำระบบล็อคอิน
class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.username
    
    def is_member(self):
        return self.role == "member"

class Menu(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField()
    image_url = models.URLField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# เราแก้ไขตรงนี้ ดดยการเปลี่ยน def save กับเพิ่ม status_choices
class Order(models.Model): 
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.FloatField()
    status_order = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    complete = models.BooleanField(default=False)  
    points_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def save(self, *args, **kwargs):
        """ ให้แต้มเฉพาะออเดอร์ที่เสร็จสมบูรณ์ """
        if self.status_order == 'completed':  
            reward_setting = Reward.objects.filter(is_active=True).first()
            if reward_setting and reward_setting.is_within_promo():
                if self.total_price >= reward_setting.min_purchase:
                    self.points_earned = reward_setting.points_per_purchase
                    self.user.points += self.points_earned
                    self.user.save()
        super().save(*args, **kwargs)

class History(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    # ้พิ่มเมนุมาเป็น FK
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    # เพอ่ม  unit_price มา
    unit_price = models.IntegerField()
    price = models.IntegerField()

    # เพิ่ม save มาเพื่อยันทึก price ใหม่
    def save(self, *args, **kwargs):
        self.price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"History {self.id} - Order {self.order.id}"

class Reward(models.Model):
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    points_per_purchase = models.IntegerField(default=1)
    points_to_redeem = models.IntegerField(default=10)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def is_within_promo(self):
        return self.is_active and self.start_date <= now() <= self.end_date
