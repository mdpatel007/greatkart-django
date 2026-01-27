import requests
from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import Banner
from store.models import Product
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from carts.models import Cart, CartItem
from carts.views import _cart_id
from orders.models import Order, OrderProduct
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.conf import settings
from django.http import HttpResponse
from weasyprint import HTML

# Varification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# Create your views here.
def home(request):
    banners = Banner.objects.filter(is_active=True)
    products = Product.objects.all().filter(is_available=True)
    context = {
        'banners': banners,
        'products': products,
    }
    return render(request, 'home.html', context)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Data extract 
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            
            # User create
            user = Account.objects.create_user(
                first_name=first_name, 
                last_name=last_name, 
                email=email, 
                username=username, 
                password=password
            )
            user.phone_number = phone_number
            user.save()

            # User Activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verifaction_email.html',{
                'user':user,
                'domain':current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # messages.success(request, 'Thank you for Registerning with us. We have sent you a verification email to your email address. Please verify it.')
            url = reverse('login') + f'?command=verification&email={email}'
            return redirect(url)
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                # Find Session cart 
                cart = Cart.objects.get(cart_id=_cart_id(request))
                # Session cart all items (Guest Cart)
                session_cart_items = CartItem.objects.filter(cart=cart)
                
                # Login user existing items (User Cart)
                user_cart_items = CartItem.objects.filter(user=user)
                
                ex_var_list = []
                id_list = []
                for item in user_cart_items:
                    existing_variation = list(item.variations.all())
                    ex_var_list.append(existing_variation)
                    id_list.append(item.id)

                for item in session_cart_items:
                    current_variation = list(item.variations.all())
                    
                    if current_variation in ex_var_list:
                        # if variation match then add quantity 
                        index = ex_var_list.index(current_variation)
                        item_id = id_list[index]
                        cart_item = CartItem.objects.get(id=item_id)
                        cart_item.quantity += item.quantity # Add Session quantity 
                        cart_item.user = user
                        cart_item.save()
                        item.delete() # Delete Session item  
                    else:
                        # if variation Not match then new item to joined user 
                        item.user = user
                        item.save()
                        
            except Cart.DoesNotExist:
                pass

            auth.login(request, user)
            messages.success(request, 'You are now logged in.')

            url = request.META.get('HTTP_REFERER')
            try: 
                query = requests.utils.urlparse(url).query 
                # next=/cart/checkout/
                params = dict(x.split('=')for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')
    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are now logged out.')
    return redirect('login')

def activate(request, uidb64, token): 
    try:
        # uidb64 will be decode 
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('register')
    
@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    context = {
        'orders_count': orders_count,
    }
    return render(request,'accounts/dashboard.html',context)

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            mail_body = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            
            to_email = email
            send_email = EmailMessage(mail_subject, mail_body, to=[to_email])
            send_email.send()
            
            # FIX: Call success on the 'messages' module, not 'mail_body'
            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
            
    return render(request, 'accounts/forgotPassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        # uidb64 will be decode 
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Your password is successfully reset.')
        return redirect('resetpassword')
    else:
        messages.error(request, 'This link had been expired')
        return redirect('login')
    
def resetpassword(request):
    if request.method == "POST":
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset succesfully')
            return redirect('login')
        else:
            messages.error(request,'Passoword do not match')
            return redirect('resetpassword')
    else:
        return render(request,'accounts/resetpassword.html')
    
def my_orders(request):
    userprofile = UserProfile.objects.get(user=request.user)
    oders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders' : oders,
        'userprofile':userprofile,  
    }
    return render(request,'accounts/my_orders.html',context)

@login_required(login_url='login')
def edit_profile(request):
    userprofile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) 
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})
    
@login_required(login_url='login')
def order_detail(request, order_id):
    try:
        order = Order.objects.get(order_number=order_id, is_ordered=True)
        order_details = OrderProduct.objects.filter(order_id=order.id)
        subtotal = 0
        for i in order_details:
            subtotal += i.product_price * i.quantity

        context = {
            'order': order,
            'order_details': order_details,
            'subtotal': subtotal,
        }
        return render(request, 'accounts/order_detail.html', context)
    except (Order.DoesNotExist):
        return redirect('dashboard')
    
def generate_pdf_invoice(request, order_id):
    order = Order.objects.get(order_number=order_id, is_ordered=True)
    order_details = OrderProduct.objects.filter(order_id=order.id)
    subtotal = sum(item.product_price * item.quantity for item in order_details)
    
    context = {
        'order': order,
        'order_details': order_details,
        'subtotal': subtotal,
    }
    
    html_string = render_to_string('accounts/invoice_pdf.html', context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{order.order_number}.pdf"'

    HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(response)
    
    return response
