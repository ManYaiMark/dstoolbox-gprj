from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from posapp.models import Menu, Order, History
from .forms import CustomUserCreationForm

# เพิ่มลงตะกร้า
def login(request):
    return render(request, 'user/login.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # บันทึกผู้ใช้ใหม่
            return redirect('login')  # เปลี่ยนเส้นทางไปหน้าล็อกอินหลังจากสมัครสมาชิก
    else:
        form = CustomUserCreationForm()
    return render(request, 'user/register.html', {'form': form})

def add_to_cart(request, menu_id):
    user = request.user  # ใช้ user ที่ login
    menu_item = get_object_or_404(Menu, id=menu_id)

    # เช็คว่าผู้ใช้มีออเดอร์ที่ยังไม่เสร็จหรือไม่
    order, created = Order.objects.get_or_create(user=user, complete=False, defaults={'total_price': 0})

    # เพิ่มเมนูเข้าออเดอร์
    order_item, item_created = History.objects.get_or_create(order=order, menu=menu_item, defaults={'quantity': 1, 'unit_price': menu_item.price})

    if not item_created:
        order_item.quantity += 1  # ถ้ามีอยู่แล้วให้เพิ่มจำนวน
    order_item.save()

    # คำนวณราคาทั้งหมดใหม่
    order.total_price = sum(item.subtotal for item in order.order_items.all())
    order.save()

    return redirect('menu')

# หน้าสั่งอาหาร
def menu_view(request):
    menus = Menu.objects.filter(is_available=True)
    return render(request, 'user/menu.html', {'menus': menus})

# หน้ารายละเอียดออเดอร์
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = History.objects.filter(order=order)
    return render(request, 'user/order_detail.html', {'order': order, 'order_items': order_items})
