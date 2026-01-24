from django.shortcuts import render, redirect
from accounts.models import Banner
from store.models import Product
from .forms import RegistrationForm
from .models import Account
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from carts.models import Cart, CartItem
from carts.views import _cart_id
import requests

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
    return render(request,'accounts/dashboard.html')

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