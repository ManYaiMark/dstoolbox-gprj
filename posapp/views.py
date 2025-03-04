from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.utils import timezone
import matplotlib.pyplot as plt
from django.db.models import Sum, Count
from django.conf import settings
import os
import matplotlib
from django.contrib import messages
from django.http import HttpResponse

# matplotlib setting
plt.rcParams["font.family"] = "TH Sarabun New"
plt.rcParams.update({"font.size": 24})
matplotlib.use("Agg")

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


def dashboard(request):
    today = timezone.now().date()

    # 1. Bar Chart - เมนูที่ขายดีที่สุด
    top_menus_today = (
        History.objects.filter(order__created_at__date=today)
        .values("menu__name")
        .annotate(order_count=Count("id"))
        .order_by("-order_count")[:5]
    )

    has_top_menus_data = bool(top_menus_today)

    if has_top_menus_data:
        menu_data_today = [
            {"name": entry["menu__name"], "order_count": entry["order_count"]}
            for entry in top_menus_today
        ]

        # Create Bar Chart (แกน Y เป็นแนวนอน)
        menu_names_today = [entry["menu__name"] for entry in top_menus_today]
        menu_order_counts = [entry["order_count"] for entry in top_menus_today]
        fig, ax = plt.subplots(figsize=(20, 5))
        ax.set_xlabel("เมนู")
        ax.set_ylabel("จำนวนการสั่งซื้อ", rotation="horizontal", ha="right")

        colors = ["#FFD700", "#C0C0C0", "#CD7F32", "#1adbe4", "#a71ae4"]
        ax.bar(menu_names_today, menu_order_counts, color=colors)
        ax.tick_params(axis="y", rotation=0)  # ปรับการหมุนของ labels แกน Y

        ax.set_yticks(range(0, max(menu_order_counts) + 1))

        fig.tight_layout()

        save_plot(fig, "top_menus_today")  # Save the bar chart
    else:
        menu_data_today = []

    # 2. Pie Chart - เปรียบเทียบสถานะคำสั่งซื้อ
    order_status_data = (
        Order.objects.filter(created_at__date=today)
        .values("status_order")  
        .annotate(total_orders=Count("id"))
        .order_by("status_order")
    )

    has_order_status_data = bool(order_status_data)
    status_data = [
        {"status": entry["status_order"], "total_orders": entry["total_orders"]}
        for entry in order_status_data
    ]

    if has_order_status_data:
        statuses_translation = {
            "pending": "รอดำเนินการ",
            "preparing": "กำลังเตรียม",
            "completed": "สำเร็จ",
            "cancelled": "ยกเลิก"
        }

    statuses = [statuses_translation.get(entry["status"], entry["status"]) for entry in status_data]
    total_orders = [entry["total_orders"] for entry in status_data]
    
    fig3, ax3 = plt.subplots(figsize=(8, 7))
    ax3.pie(
        total_orders,
        labels=statuses,
        autopct="%1.1f%%",
        startangle=90,
        colors=["#FF6347", "#FFD700", "#32CD32", "#808080"],
    )
    ax3.axis('equal')  
    ax3.set_title("สถานะคำสั่งซื้อในวันนี้")

    save_plot(fig3, "order_status_today")  


    # 3. Line Chart - ยอดขายตามช่วงเวลา
    sales_by_hour = (
        Order.objects.filter(created_at__date=today)
        .values("created_at__hour")
        .annotate(total_sales=Sum("total_price"))
        .order_by("created_at__hour")
    )

    has_sales_data = bool(sales_by_hour)
    sales_data = [
        {"hour": entry["created_at__hour"], "total_sales": entry["total_sales"] or 0}
        for entry in sales_by_hour
    ]

    if has_sales_data:
        # Create Line Chart
        hours = [entry["created_at__hour"] for entry in sales_by_hour]
        sales = [entry["total_sales"] or 0 for entry in sales_by_hour]
        fig3, ax3 = plt.subplots(figsize=(12, 7))
        ax3.plot(hours, sales, marker="o", color="green")
        ax3.set_xlabel("ช่วงเวลา")
        ax3.set_ylabel("ยอดขาย (บาท)", rotation="horizontal", ha="right")

        # เพิ่มเส้นประ (grid lines)
        ax3.grid(True, linestyle="--", color="gray", alpha=0.7)

        # ปรับ tick ของแกน X ให้เป็นช่วงเวลา 24 ชั่วโมง
        ax3.set_xticks(
            range(0, 24, 6)
        )  # กำหนดให้ tick ของแกน X แสดงที่ 0, 4, 8, 12, 16, 20
        ax3.set_xticklabels([f"{i}:00" for i in range(0, 24, 6)])  # ตั้งค่าตัวอักษรให้เป็นเวลา
        fig3.tight_layout()
        save_plot(fig3, "sales_by_hour")  # Save the line chart

    return render(
        request,
        "admin_dashboard.html",
        {
            "has_top_menus_data": has_top_menus_data,
            "menu_data_today": menu_data_today,
            "has_order_status_data": has_order_status_data,
            "status_data": status_data,
            "has_sales_data": has_sales_data,
            "sales_data": sales_data,
            "sales_by_hour_img": "/static/images/sales_by_hour.png",
            "top_menus_today_img": "/static/images/top_menus_today.png",
            "order_status_today_img": "/static/images/order_status_today.png",
        },
    )


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
    if request.method == "POST":
        form = RewardForm(request.POST)
        if form.is_valid():
            reward = form.save(commit=False)
            if reward.start_date > timezone.now().date():
                reward.is_active = False
            else:
                reward.is_active = True
            reward.save()
            return redirect("reward")
    else:
        form = RewardForm()

    return render(request, "admin_rewards.html", {"form": form})


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
    return render(request, "admin_manage_menu.html", {"menus": menus})


def add_menu(request):
    # ถ้าเป็นการส่งข้อมูลจากฟอร์ม (POST)
    if request.method == "POST":
        form = MenuForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # หลังจากบันทึกเสร็จแล้วเปลี่ยนเส้นทางไปที่หน้า manage_menu
            return redirect("manage_menu")
    else:
        form = MenuForm()

    return render(request, "manage_menu/add_menu.html", {"form": form})


def delete_menu(request, id):
    menu = get_object_or_404(Menu, id=id)

    menu.delete()

    return redirect("manage_menu")


def edit_menu(request, id):
    menu = get_object_or_404(Menu, id=id)
    if request.method == "POST":
        form = MenuForm(request.POST, request.FILES, instance=menu)
        if form.is_valid():
            form.save()
            return redirect("manage_menu")
    else:
        form = MenuForm(instance=menu)

    return render(request, "manage_menu/edit_menu.html", {"form": form, "menu": menu})


# จัดการออร์เดอร์


def manage_orders(request):
    status_filter = request.GET.get("status")
    if status_filter:
        orders = Order.objects.filter(status_order=status_filter).order_by(
            "-created_at"
        )
    else:
        orders = Order.objects.all().order_by("-created_at")

    user_filter = request.GET.get("user")
    if user_filter:
        orders = orders.filter(user__username__icontains=user_filter)

    return render(request, "orders/manage_orders.html", {"orders": orders})


def update_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        order.total_price = float(request.POST.get("total_price"))
        order.status_order = request.POST.get("status")
        order.save()
        messages.success(request, f"Order {order.id} updated successfully.")
        return redirect("orders")

    return render(request, "orders/update_order.html", {"order": order})


def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    messages.success(request, "Order deleted successfully!")
    return redirect("orders")


# ✅ แสดงหน้าดูออร์เดอร์
def detail_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # ดึงรายการ History ที่เกี่ยวข้องกับ Order นี้
    order_items = History.objects.filter(order=order)

    return render(
        request, "orders/details.html", {"order": order, "order_items": order_items}
    )


# ✅ อัปเดตสถานะออร์เดอร์
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        new_status = request.POST.get("status_order")
        if new_status in dict(Order.STATUS_CHOICES):
            order.status_order = new_status
            order.save()
            
            # ตรวจสอบว่าสถานะถูกอัปเดต
            if order.status_order == new_status:
                return redirect("orders")
            else:
                return HttpResponse("ไม่สามารถอัปเดตสถานะได้", status=500)
        else:
            return HttpResponse("สถานะไม่ถูกต้อง", status=400)

    return redirect("orders")
