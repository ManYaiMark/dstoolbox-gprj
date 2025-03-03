from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
import json
from .models import Order

# Create your views here.


## ส่วน Admin ##
# Dashboard สำหรับแอดมิน ยังไม่ทำ ต้องใช้เครื่องมือที่สุ่มได้คาบก่อน
def dashboard(request):
    return render(request, "admin_base.html")


# ตรวจสอบแต้มลูกค้าก่อนคอนเฟิร์มออเดอร์
def check_discount_eligibility(customer):
    reward_setting = Reward.objects.filter(is_active=True).first()
    if reward_setting and reward_setting.is_within_promo():
        if customer.points >= reward_setting.points_to_redeem:
            return {
                "can_redeem": True,
                "discount_amount": reward_setting.discount_amount,
            }
    return {"can_redeem": False}


# ลูกค้าเลือกใช้/ไม่ใช้แต้ม
def apply_discount(order, use_points=False):
    reward_setting = Reward.objects.filter(is_active=True).first()
    if use_points and reward_setting and reward_setting.is_within_promo():
        if order.customer.points >= reward_setting.points_to_redeem:
            order.total_price -= reward_setting.discount_amount
            order.customer.points -= reward_setting.points_to_redeem
            order.customer.save()
            order.save()


# แต้มหมดอายุ cron job will be added later desu
def reset_expired_points():
    reward_setting = Reward.objects.filter(is_active=True).first()
    if reward_setting and not reward_setting.is_within_promo():
        User.objects.update(points=0)


# แสดง Reward ทั้งหมด
def reward_dashboard(request):
    rewards = Reward.objects.filter(end_date__gte=timezone.now())
    return render(request, "admin_rewards.html", {"rewards": rewards})


# สร้างเงื่อนไขสะสมแต้มใหม่
def create_reward(request):
    if request.method == 'POST':
        form = RewardForm(request.POST)
        if form.is_valid():
            reward = form.save(commit=False)  
            if reward.start_date > timezone.now().date():
                reward.is_active = False  
            else:
                reward.is_active = True  
            reward.save()  
            return redirect('reward')  
    else:
        form = RewardForm()

    return render(request, 'admin_rewards.html', {'form': form})

# เปิด/ปิดการใช้งาน Reward
def toggle_reward(request, reward_id):
    reward = Reward.objects.get(id=reward_id)
    reward.is_active = not reward.is_active  # สลับสถานะ
    reward.save()
    return redirect("reward")


# ลบ Reward ที่หมดอายุหรือไม่ต้องการ
def delete_reward(request, reward_id):
    reward = Reward.objects.get(id=reward_id)
    reward.delete()

    return redirect("reward")

def manage_menu(request):
    menus = Menu.objects.all()
    return render(request, 'admin_manage_menu.html', {'menus': menus})


def add_menu(request):
    # ถ้าเป็นการส่งข้อมูลจากฟอร์ม (POST)
    if request.method == 'POST':
        form = MenuForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # หลังจากบันทึกเสร็จแล้วเปลี่ยนเส้นทางไปที่หน้า manage_menu
            return redirect('manage_menu')
    else:
        form = MenuForm()

    return render(request, 'manage_menu/add_menu.html', {'form': form})


def delete_menu(request, id):
    menu = get_object_or_404(Menu, id=id)

    menu.delete()

    return redirect('manage_menu')


def edit_menu(request, id):
    menu = get_object_or_404(Menu, id=id)
    if request.method == "POST":
        form = MenuForm(request.POST, request.FILES, instance=menu)
        if form.is_valid():
            form.save()
            return redirect('manage_menu')
    else:
        form = MenuForm(instance=menu)

    return render(request, 'manage_menu/edit_menu.html', {'form': form, 'menu': menu})

#จัดการออร์เดอร์
def admin_order_list(request):
    # เรียงลำดับออร์เดอร์โดยให้ Pending & Preparing อยู่ด้านบนสุด
    orders = Order.objects.all().order_by(
        '-status_order',  # Priority: Pending > Preparing > Completed
        'created_at'  # เรียงจากออร์เดอร์เก่าก่อนไปใหม่
    )
    return render(request, 'order/admin_order_list.html', {'orders': orders})


def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        data = json.loads(request.body)
        new_status = data.get("status")
        if new_status in dict(Order.STATUS_CHOICES):
            order.status_order = new_status
            order.save()
            return JsonResponse({"message": "อัปเดตสถานะสำเร็จ!", "status": order.status_order})

    return JsonResponse({"error": "Invalid status"}, status=400)


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order/order_detail.html', {'order': order})

def admin_order_list(request):
    orders = Order.objects.all().order_by('-status_order', 'created_at')
    return render(request, 'admin_order_list.html', {'orders': orders})


from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login')  # เปลี่ยน 'login' เป็นชื่อ URL ที่ต้องการให้เปลี่ยนหน้าไปหลัง logout
