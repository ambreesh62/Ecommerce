from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import F
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
            messages.success(request, 'Congratulations! Registration Successful')
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
    if 'phone' in request.session:
        phone = request.session['phone']
        product_id = request.GET.get('prod_id')
        product = Product.objects.get(id=product_id)
        
        # Check if the product is already in the cart
        cart = Cart.objects.filter(phone=phone, product=product).first()

        if cart:
            # If the product is in the cart, increment its quantity
            cart.quantity += 1
            cart.save()
        else:
            # If the product is not in the cart, add it
            Cart.objects.create(phone=phone, product=product, price=product.price, image=product.image, quantity=1)
        
        # Redirect to the 'show_cart' view
        return redirect('show_cart')
    else:
        return redirect('login')

# Show_Cart
def Show_cart(request):
    if 'phone' in request.session:
        phone = request.session['phone']
        customer = Customer.objects.filter(phone=phone).first()
        carts = Cart.objects.filter(phone=phone)

        if customer:
            name = customer.name
        else:
            name = "User"

        data = {
            'name': name,
            'carts': carts.annotate(total_price=F('quantity') * F('product__price'))  # Calculate total price for each cart item
        }
        
        if carts:
            return render(request, 'show_cart.html', data)
        else:
            return render(request, 'empty_cart.html', data)
    else:
        return redirect('login')

   
# Cart me plus krne ke liye
def plus_cart(request, pk):
    if 'phone' in request.session:
        try:
            # Get the cart item based on the product's primary key
            cart = Cart.objects.get(phone=request.session['phone'], product_id=pk)
            # Increment the quantity of the cart item
            cart.quantity += 1
            cart.save()
            
            # Reorder the cart items
            reorder_cart_items(request.session['phone'])
            
        except Cart.DoesNotExist:
            # Handle the case where the cart does not exist
            pass
        
        # Redirect to the 'show_cart' view
        return HttpResponseRedirect(reverse('show_cart'))
    else:
        return redirect('login')
    
    
    
# Cart se htaane ke liye
def minus_cart(request, pk):
    if 'phone' in request.session:
        try:
            cart = Cart.objects.get(phone=request.session['phone'], product_id=pk)
            if cart.quantity == 1:
                cart.delete()
            else:
                cart.quantity -= 1
                cart.save()
            
            # Reorder the cart items
            reorder_cart_items(request.session['phone'])
                
            return HttpResponseRedirect(reverse('show_cart'))
            
        except Cart.DoesNotExist:
            pass  # Cart doesn't exist, so no need to delete or decrement
    
    return redirect('login') 

def reorder_cart_items(phone):
    carts = Cart.objects.filter(phone=phone)
    for index, cart in enumerate(carts.order_by('id'), start=1):
        cart.sn = index
        cart.save()
    
    
# Remove Cart
def remove_cart(request, pk):
    if request.method == 'GET':
        if request.session.has_key('phone'):
            cart = Cart.objects.filter(product_id=pk)
            cart.delete()
            
    # Fetching all cart items
    carts = Cart.objects.filter(phone=request.session['phone'])
    
    # Fetching customer details
    customer = Customer.objects.filter(phone=request.session['phone']).first()

    data = {
        'name': customer.name if customer else "User",
        'carts': carts
    } 
    if carts: 
        return render(request, 'show_cart.html', data)
    else:
        return render(request, 'empty_cart.html', data)
                
                
 


# User Checkout
def checkout(request):
    total_item = 0
    if 'phone' in request.session:
        phone = request.session['phone']
        name = request.POST.get('name')
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')
        
        cart_products = Cart.objects.filter(phone=phone)
        
        order_details_to_save = []
        for cart in cart_products:
            qty = cart.quantity
            price = cart.product.price  
            product_name = cart.product.name
            image = cart.product.image
            
            order_details_to_save.append(OrderDetail(user=phone, product_name=product_name, image=image, qty=qty, price=price))
        
        OrderDetail.objects.bulk_create(order_details_to_save)
        cart_products.delete()
        
        total_item = Cart.objects.filter(phone=phone).count()
        customer = Customer.objects.filter(phone=phone).first()
        if customer:
            name = customer.name
        
        data = {
            'name': name,
            'total_item': total_item,
            'address': address,
            'mobile': mobile
        }
        
        return render(request, 'empty_cart.html', data)
    else:
        return redirect('login')



def order(request):
    total_item = 0
    if request.session.has_key('phone'):
        phone = request.session['phone']
        total_item = len(Cart.objects.filter(phone=phone))
        customers = Customer.objects.filter(phone=phone)
        for customer in customers:
            name = customer.name
            order = OrderDetail.objects.filter(user=phone)
            
            data ={
            'orders' : order,
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