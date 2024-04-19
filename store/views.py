from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
# models
from store.models.product import Product
from store.models.category import Category
from .models.customer import Customer
from .models.cart import Cart
from .models.order import OrderDetail



# Create your views here.
def home(request):
    products = None
    total_item = 0
    if request.session.has_key('phone'):
        phone = request.session['phone']

        category = Category.get_all_caregories()
        customer = Customer.objects.filter(phone=phone)
        total_item = len(Cart.objects.filter(phone=phone))
        data = {}
        data['category'] = category
        data['total_item'] = total_item


        for cc in customer:
            name=cc.name
            
            categoryID = request.GET.get('category')
            if categoryID:
                products = Product.get_all_product_by_category_id(categoryID)
                data['products'] = products

                return render(request,'home.html', data)
                
            else:
                products = Product.objects.all()    
                
                data = {}
                data['name'] = name
                data['products'] = products
                data['category'] = category
                data['total_item'] = total_item
        return render(request,'home.html', data)
    else:
        return redirect('login')

# Signup 
    
class SignUp(View):
    def get(self, request):
        return render(request, 'signup.html')

    def post(self, request):
        postData = request.POST
        name = postData.get('name')
        phone = postData.get('phone')
        error_message = None
        value = {
            'phone': phone,
            'name': name
        }
        customer = Customer(name=name, phone=phone)
        if not name:
            error_message = "Name is Required"
        elif not phone:
            error_message = "Mobile Number is Required"
        elif len(phone) < 10:
            error_message = "Mobile Number Must set min 10 digits"
        elif len(phone) > 10:
            error_message = "Mobile Number must be set max 10 digits"
        elif customer.isExists():
            error_message = 'Mobile Number Already Exists'
            
        if not error_message:
            customer.register()
            messages.success(request, 'Congratulations! Registration Successful.')
            return redirect('signup')
        else:
            data = {
                'error': error_message,
                'value': value
            }
            return render(request, 'signup.html', data)

# Login
       
class Login(View):
    def get(self,request):
        return render(request, 'login.html')
    
    def post(self,request):
        phone = request.POST.get('phone')
        error_message = None
        value = {
            'phone' : phone
        }
        customer = Customer.objects.filter(phone=request.POST["phone"])
        if customer:
            request.session['phone']=phone
            return redirect('homepage')
        else:
            error_message = "Mobile Number is Invalid !"
            data = {
                'error' : error_message,
                'value' : value
                }
            
        return render(request, 'login.html', data)
    
    
# Product -Detail
   
def productdetail(request,pk):
    total_item = 0
    product = Product.objects.get(pk=pk)  
    item_already_in_cart = False
    if request.session.has_key('phone'):
        phone = request.session['phone']
        total_item = len(Cart.objects.filter(phone=phone))
        item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(phone=phone)).exists()
        customer = Customer.objects.filter(phone=request.session['phone'])
        name=customer.last().name
        data = {
            'product' :product,
            'item_already_in_cart' : item_already_in_cart,
            'name' : name,
            'total_item' : total_item
        }
        return render(request, 'productdetail.html',data)

# Loggout

def Logout(request):
    if request.session.has_key('phone'):
        del request.session['phone']
    return redirect('login')

#  Add to cart

def add_to_cart(request):
    phone = request.session['phone']
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    cart = Cart.objects.filter(product_id=product_id)
    if cart:
        cart.first().quantity += 1
        cart.first().save()
    else:
        Cart.objects.create(phone=phone,product_id=product.id)
    customer = Customer.objects.filter(phone=request.session['phone'])

    data = {
        'name': customer.first().name if customer else "User",
        'carts': Cart.objects.filter(phone=phone)
    }
    return render(request, 'show_cart.html', data)

# Show_Cart
def Show_cart(request):
    total_item = 0
    if request.session.has_key('phone'):
        phone = request.session['phone']
        
        carts = Cart.objects.filter(phone=phone)

        customer = Customer.objects.filter(phone=request.session['phone'])

        data = {
            'name': customer.first().name if customer else "User",
            'carts': Cart.objects.filter(phone=phone)
        }
                
        if carts:
            return render(request, 'show_cart.html', data)
        else:
            return render(request, 'empty_cart.html', data)
            
    return render(request, 'login.html')
        
     

    
    
# Cart me plus krne ke liye
def plus_cart(request, pk):
    if request.session.has_key('phone'):
        cart = Cart.objects.get(product_id=pk)
        cart.quantity+=1
        cart.save()
        
    carts = Cart.objects.filter(phone=request.session['phone'])
    customer = Customer.objects.filter(phone=request.session['phone'])

    data = {
        'name': customer.first().name if customer else "User",
        'carts': carts
    }
    return render(request, 'show_cart.html', data)
    
    
    
# Cart se htaane ke liye

def minus_cart(request, pk):
    if request.session.has_key('phone'):
        cart = Cart.objects.get(product_id=pk)
        if cart.quantity == 1:
            cart.delete()
        else:
            cart.quantity-=1
            cart.save()
        
    carts = Cart.objects.filter(phone=request.session['phone'])
    customer = Customer.objects.filter(phone=request.session['phone'])

    data = {
        'name': customer.first().name if customer else "User",
        'carts': carts
    } 
    if carts:      
        return render(request, 'show_cart.html', data)
    else:
        return render(request, 'empty_cart.html',data)
    
    
# Remove Cart

def remove_cart(request, pk):
    
    if request.method == 'GET':
        if request.session.has_key('phone'):
            cart = Cart.objects.filter(product_id=pk)
            cart.delete()
    carts = Cart.objects.filter(phone=request.session['phone'])
    customer = Customer.objects.filter(phone=request.session['phone'])

    data = {
        'name': customer.first().name if customer else "User",
        'carts': carts
    } 
    if carts: 
        return render(request, 'show_cart.html', data)
    else:
        return render(request, 'empty_cart.html', data)
                
                
 


# User Checkout
def checkout(request):
    total_item = 0
    if request.session.has_key('phone'):
        phone = request.session['phone']
        name = request.POST.get('name')
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')
        
        cart_product = Cart.objects.filter(phone=phone)
        for c in cart_product:
            qty = c.quantity
            price = c.price
            product_name = c.product
            image = c.image
            
            OrderDetail(user=phone, product_name=product_name, image=image, qty=qty, price=price).save()
            cart_product.delete()
            
            total_item = len(Cart.objects.filter(phone=phone))
            customer = Customer.objects.filter(phone=phone)
            
            for c in customer:
                name = c.name
            
            data = {
                'name' : name,
                'total_item' : total_item,
                'address' : address,
                'mobile' : mobile
            }    
                
                
            return render(request, 'empty_cart.html',data)
    else:
        return redirect('login')    


def order(request):
    total_item = 0
    if request.session.has_key('phone'):
        phone = request.session['phone']
        total_item = len(Cart.objects.filter(phone=phone))
        customer = Customer.objects.filter(phone=phone)
        for c in customer:
            name = c.name
            order = OrderDetail.objects.filter(user=phone)
            
            data ={
            'order' : order,
            'name' : name,
            'total_item' : total_item
        }
            if order :
                return render(request, 'order.html',data)
            else: 
                return render(request, 'emptyorder.html', data)    
    else:
        return redirect('login')    

def search(request):
    total_item = 0
    if request.session.has_key('phone'):
        phone = request.session['phone']
        query = request.GET.get('query')
        search = Product.objects.filter(name__icontains=query)
        category = Category.get_all_caregories()
        total_item = len(Cart.objects.filter(phone=phone))
        customer = Customer.objects.filter(phone=phone)
        for c in customer:
            name = c.name
            
        data = {
            'name' : name,
            'total_item' : total_item,
            'search' : search,
            'category' : category,
            'query ' : query 
        }    
        return render(request, 'search.html',data)  
    else:
        return redirect('login')