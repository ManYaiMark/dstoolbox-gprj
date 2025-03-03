from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.utils import timezone
import matplotlib.pyplot as plt
from django.db.models import Sum, Count
from datetime import timedelta
from django.conf import settings
import os
import matplotlib
import matplotlib.font_manager as fm
from django.views.decorators.cache import cache_page

# matplotlib setting
matplotlib.use('Agg')

# Create your views here.

## ส่วน Admin ##
# Dashboard สำหรับแอดมิน ยังไม่ทำ ต้องใช้เครื่องมือที่สุ่มได้คาบก่อน


def save_plot(fig, filename):
    static_dir = os.path.join(settings.BASE_DIR, "static/images")
    os.makedirs(static_dir, exist_ok=True)

    filepath = os.path.join(static_dir, f"{filename}.png")
    fig.savefig(filepath)
    plt.close(fig)

    return f"/static/images/{filename}.png"


@cache_page(60 * 15)
def dashboard(request):
    today = timezone.now().date()

    # 1. Bar Chart - เมนูที่ขายดีที่สุด
    top_menus_today = History.objects.filter(order__created_at__date=today) \
                                     .values('menu__name') \
                                     .annotate(order_count=Count('id')) \
                                     .order_by('-order_count')[:5]

    menu_names_today = [entry['menu__name'] for entry in top_menus_today]
    menu_order_counts = [entry['order_count'] for entry in top_menus_today]

    top_menus_data = list(zip(menu_names_today, menu_order_counts))

    # Bar Chart with color variation
    colors = ['#FFD700', '#C0C0C0', '#CD7F32', '#FF5733', '#4CAF50']

    fig1, ax1 = plt.subplots(figsize=(15, 3))
    ax1.bar(menu_names_today, menu_order_counts, color=colors)
    ax1.tick_params(axis='x', rotation=45)

    save_plot(fig1, 'top_menus_today')

    # 2. Pie Chart - เปรียบเทียบลูกค้าทั่วไป/สมาชิก
    user_data = Order.objects.filter(created_at__date=today) \
                             .values('user__role') \
                             .annotate(order_count=Count('id'))

    roles = ['member' if entry['user__role'] == 'member' else 'guest' for entry in user_data]
    role_counts = [entry['order_count'] for entry in user_data]

    roles_data = list(zip(roles, role_counts))

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.pie(role_counts, labels=roles, autopct='%1.1f%%', startangle=90, colors=['#4CAF50', '#FF5733'])

    save_plot(fig2, 'roles_pie_chart')

    # 3. Line Chart - ยอดขายตามช่วงเวลา
    sales_by_hour = Order.objects.filter(created_at__date=today) \
                                  .values('created_at__hour') \
                                  .annotate(total_sales=Sum('total_price')) \
                                  .order_by('created_at__hour')

    hours = [entry['created_at__hour'] for entry in sales_by_hour]
    sales = [entry['total_sales'] or 0 for entry in sales_by_hour]

    sales_data = list(zip(hours, sales))  # Combine hours and sales into a list of tuples

    fig3, ax3 = plt.subplots(figsize=(10, 5))
    ax3.plot(hours, sales, marker='o', color='#007BFF')
    ax3.tick_params(axis='x', rotation=45)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)

    save_plot(fig3, 'sales_by_hour')

    # Passing image paths and data to the template
    return render(request, 'admin_dashboard.html', {
        'top_menus_data': top_menus_data,
        'roles_data': roles_data,
        'sales_data': sales_data,  # Added this line
        'sales_by_hour_img': '/static/images/sales_by_hour.png',
        'top_menus_today_img': '/static/images/top_menus_today.png',
        'roles_pie_chart_img': '/static/images/roles_pie_chart.png',
        'menu_names_today': menu_names_today,
        'menu_order_counts': menu_order_counts,
        'role_counts': role_counts,
        'roles': roles,
        'hours': hours,
        'sales': sales
    })


# ส่วนระบบสะสมแต้ม
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
        form = MenuForm(request.POST)
        if form.is_valid():
            # บันทึกข้อมูลที่ได้จากฟอร์ม
            form.save()
            # หลังจากบันทึกเสร็จแล้วเปลี่ยนเส้นทางไปที่หน้า manage_menu
            return redirect('manage_menu')
    else:
        # ถ้าไม่ใช่ POST จะส่งฟอร์มเปล่าให้กรอกข้อมูล
        form = MenuForm()

    return render(request, 'manage_menu/add_menu.html', {'form': form})


def delete_menu(request, id):
    # ดึงข้อมูลเมนูที่มี id ตรงกับที่ส่งมา
    menu = get_object_or_404(Menu, id=id)

    # ลบเมนูนั้นออกจากฐานข้อมูล
    menu.delete()

    # หลังจากลบเสร็จแล้วเปลี่ยนเส้นทางกลับไปที่หน้า manage_menu
    return redirect('manage_menu')


def edit_menu(request, id):
    # ดึงเมนูที่ต้องการแก้ไขจากฐานข้อมูล
    menu = get_object_or_404(Menu, id=id)

    # ถ้าเป็นการส่งข้อมูล (POST) จากฟอร์ม
    if request.method == 'POST':
        form = MenuForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()  # บันทึกการแก้ไข
            return redirect('manage_menu')  # เปลี่ยนเส้นทางไปยังหน้า manage_menu
    else:
        form = MenuForm(instance=menu)  # ถ้าเป็นการเรียกหน้าแรกให้โหลดข้อมูลเดิมของเมนู

    return render(request, 'manage_menu/edit_menu.html', {'form': form, 'menu': menu})
