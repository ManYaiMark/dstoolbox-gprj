from django.shortcuts import get_object_or_404, render
from django.contrib.auth import login, authenticate
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm
from posapp.models import Menu, Order, History
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import check_password
from posapp.models import User
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required


def login_and_convert_cart(request):

    cart = request.session.get('cart', {})
    error = None
    if request.method == "POST":
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
            error = "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"

        # ตรวจสอบรหัสผ่าน
        if user and check_password(password, user.password):  
            print("Login success")
            login(request, user)

            # บันทึกข้อมูลเป็น session
            request.session['username'] = user.username
            request.session['email'] = user.email
            request.session['role'] = user.role
            request.session['total_points'] = user.points

            # ถ้าเป็น Admin ให้ไปหน้า Dashboard
            if user.role == "admin":
                return redirect('dashboard')

            
            return redirect('menu')

        else:
            error = "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้องนะครับ"  
    request.session['cart'] = cart
    return render(request, 'user/login.html', {'error': error})

def register(request):

    cart = request.session.get('cart', {})
    error = None
    if request.method == "POST":
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password').strip()
        confirm_password = request.POST.get('confirm_password').strip()
        role = request.POST.get('role', 'member')  

        # ตรวจสอบว่าชื่อผู้ใช้หรืออีเมลซ้ำหรือไม่
        if User.objects.filter(username=username).exists():
            error = "ชื่อผู้ใช้นี้ถูกใช้งานแล้ว"
        elif User.objects.filter(email=email).exists():
            error = "อีเมลนี้ถูกใช้งานแล้ว"
        elif password != confirm_password:
            error = "รหัสผ่านไม่ตรงกัน"  
        else:
            
            hashed_password = make_password(password)

            # สร้างผู้ใช้ใหม่
            user = User.objects.create(
                username=username,
                email=email,
                password=hashed_password,
                role=role
            )
            
            request.session['username'] = user.username
            request.session['email'] = user.email
            request.session['role'] = user.role
            request.session['total_points'] = user.points

            return redirect('menu')  
    request.session['cart'] = cart
    return render(request, 'user/register.html', {'error': error})

# ออกจากระบบ
def logout_view(request):
    logout(request)
    request.session.flush()  
    return redirect('menu') 


def add_to_cart_guest(request, menu_id):
    menu_item = get_object_or_404(Menu, id=menu_id)

    # ดึงตะกร้าจาก session หรือสร้างใหม่
    cart = request.session.get('cart', {})

    if str(menu_id) in cart:
        cart[str(menu_id)]['quantity'] += 1
    else:
        cart[str(menu_id)] = {
            'name': menu_item.name,
            'price': menu_item.price,
            'quantity': 1,
            'image': menu_item.image.url,
        }

    # บันทึกตะกร้าไว้ใน session
    request.session['cart'] = cart
    return redirect('menu')

def add_to_cart(request, menu_id):
    menu_item = get_object_or_404(Menu, id=menu_id)

    cart = request.session.get('cart', {})

    if str(menu_id) in cart:
        cart[str(menu_id)]['quantity'] += 1
    else:
        cart[str(menu_id)] = {
            'name': menu_item.name,
            'price': menu_item.price,
            'quantity': 1,
            'image': menu_item.image.url,
        }

    request.session['cart'] = cart
    return redirect('cart')

def decrease_quantity(request, menu_id):
    menu_item = get_object_or_404(Menu, id=menu_id)

    cart = request.session.get('cart', {})
    if str(menu_id) in cart:
        cart[str(menu_id)]['quantity'] -= 1
        if cart[str(menu_id)]['quantity'] == 0:
            del cart[str(menu_id)]
    else:
        cart[str(menu_id)] = {
            'name': menu_item.name,
            'price': menu_item.price,
            'quantity': 1,
            'image': menu_item.image.url,
        }
    request.session['cart'] = cart
    return redirect('cart')

def cart_view(request):
    cart = request.session.get('cart', {})
    total_price = 0

    # คำนวณราคสินค้า
    for item in cart.values():
        item['total_price'] = item['quantity'] * item['price']
        total_price += item['total_price']

    return render(request, "user/cart.html", {"cart": cart, "total_price": total_price})

def remove_from_cart(request, menu_id):
    cart = request.session.get('cart', {})
    if str(menu_id) in cart:
        del cart[str(menu_id)]
        request.session['cart'] = cart  # อัปเดต session
    return redirect('cart') 

def clear_cart(request):
    request.session['cart'] = {}  # ล้างตะกร้า
    return redirect('cart')

# หน้าสั่งอาหาร
def menu_view(request):
    menus = Menu.objects.filter(is_available=True)
    return render(request, 'user/menu.html', {'menus': menus})

def order_status(request):
    username = request.session.get('username')
    
    if not username:
        return redirect('login') 

    user = get_object_or_404(User, username=username)

    cart = request.session.get('cart', {})
    print("Cart:", cart)
    if request.method == "POST":
        if cart:
            print("Cart")
          
            order = Order.objects.create(
                user=user,  
                total_price=0,  
                status_order='pending'  
            )
            total_price = 0

            for menu_id, item in cart.items():
                menu_item = get_object_or_404(Menu, id=int(menu_id))
                order_item = History.objects.create(
                    order=order,
                    menu=menu_item,
                    quantity=item['quantity'],
                    unit_price=item['price'],
                    price=item['quantity'] * item['price']
                )
                total_price += order_item.price

            # อัปเดตราคา
            order.total_price = total_price
            order.save()

            # ลบตะกร้า
            del request.session['cart']
            print("Order created successfully. Order ID:", order.id)

            
            return redirect('order_detail', order_id=order.id) 

        else:
            print("Cart is empty, no items to order.") 
            return redirect('cart') 

    return render(request, 'user/cart.html') 

def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = History.objects.filter(order=order)
    
    return render(request, 'user/order_detail.html', {
        'order': order,
        'order_items': order_items,
        'status_order': order.get_status_order_display(),  
    })

def check_points(request):
    
    user_id = request.session.get('user_id')

    if not user_id:
        return render(request, 'user/check_points.html', {'total_points': 0, 'error': 'กรุณาเข้าสู่ระบบก่อน'})
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return render(request, 'user/check_points.html', {'total_points': 0, 'error': 'ไม่พบข้อมูลผู้ใช้'})
    user_orders = Order.objects.filter(user=user)
    total_points = sum(item.price for item in History.objects.filter(order__in=user_orders))

    return render(request, 'user/check_points.html', {'total_points': total_points})

