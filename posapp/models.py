from django.db import models
from datetime import date
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    role = models.CharField(max_length=50, default='member')
    points = models.IntegerField(default=0)

    
    # เพิ่ม related_name เพื่อหลีกเลี่ยงการชนกับ User ของ Django
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='custom_user_set',  # เพิ่ม related_name สำหรับฟิลด์ groups
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',  # เพิ่ม related_name สำหรับฟิลด์ user_permissions
        blank=True
    )

    
    # เพิ่ม related_name เพื่อหลีกเลี่ยงการชนกับ User ของ Django
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='custom_user_set',  # เพิ่ม related_name สำหรับฟิลด์ groups
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',  # เพิ่ม related_name สำหรับฟิลด์ user_permissions
        blank=True
    )

    def __str__(self):
        return self.username

class Menu(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField( null=True, blank=True)
    price = models.IntegerField()

    image = models.ImageField(upload_to='menu_images/', default='menu_images/default_menu.jpg')

    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# เราแก้ไขตรงนี้ ดดยการเปลี่ยน def save กับเพิ่ม status_choices
class Order(models.Model): 
    PENDING = 'pending'
    PREPARING = 'preparing'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (PENDING, 'รอดำเนินการ'),
        (PREPARING, 'กำลังเตรียมอาหาร'),
        (COMPLETED, 'สำเร็จ'),
        (CANCELLED, 'ยกเลิก')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.FloatField()
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    points_used = models.IntegerField(default=0)
    points_earned = models.IntegerField(default=0)

    status_order = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    complete = models.BooleanField(default=False)  

    points_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def save(self, *args, **kwargs):
        old_status = None 

        if self.pk:
            old_status = Order.objects.get(pk=self.pk).status_order

        is_becoming_completed = (
            self.status_order == self.COMPLETED and old_status != self.COMPLETED
        )
        if is_becoming_completed:   
            reward = Reward.objects.filter(
                is_active=True,
                # lte = less than or equal to "<=" , gte = greater than or equal to ">="
                start_date__lte=date.today(),
                end_date__gte=date.today()
            ).first()

            if reward and self.total_price >= reward.min_purchase:
                self.points_earned = reward.points_per_purchase
                self.user.points += self.points_earned
                self.user.save(update_fields=['points'])  # Update only the points field

        super().save(*args, **kwargs)

class History(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    # ้พิ่มเมนุมาเป็น FK
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    # เพอ่ม  unit_price มา
    unit_price = models.IntegerField(default=0)
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
        return self.is_active and self.start_date <= date.today() <= self.end_date
