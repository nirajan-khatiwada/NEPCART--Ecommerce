from django.shortcuts import render,redirect
from django.urls import reverse
from django.conf import settings

#from django.http import HttpResponse
from category.models import category
from django.template.loader import render_to_string
from . import forms
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Account
from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator,PasswordResetTokenGenerator
from cart.models import CartItem
# Create your views here.


def logins(request):
    

    if request.user.is_authenticated:
        return redirect(reverse('homepage'))
    
    
    form=forms.LoginForm()
    if request.method=="POST":
        form=forms.LoginForm(request.POST)
        #print(request.POST)
        if(form.is_valid()):
            username=form.cleaned_data.get('phone_number')
            password=form.cleaned_data.get('password')
          
            #print(user)
            if not(Account.objects.filter(username=form.cleaned_data['phone_number']).exists()):
                messages.error(request,"Invalid PhoneNumber")
                return redirect(reverse('login'))
            user=authenticate(username=username,password=password)
            if user is None:
                messages.error(request,"Invalid Crentials")
                return redirect(reverse('login'))
            if not user.is_verified:
                messages.error(request,"Please Verify Your Account Using Email")
                messages.error(request,"if you dont find please reregister")
                return redirect(reverse('login'))
            cart=CartItem.objects.filter(cart__cart_id=request.session.session_key)
        
            if(cart.exists()):
                for x in cart:
                    x.user=user
                    x.save()

            login(request,user)
           
            referer=request.META.get('HTTP_REFERER')
            if referer is None:
                return redirect(reverse('homepage'))
            else:
                try:
                    data=referer.split("=")
                    if(len(data)>2):
                        return redirect(reverse('homepage'))
                    else:
                        return redirect(data[1])
                except:
                    return redirect(reverse('homepage'))



            
            
            

            
    return render(request,"account/signin.html",{'catogery':category.objects.all(),'form':form})

@login_required(login_url='login')
def logouts(request):
        logout(request)
        return redirect(reverse('login'))


def signup(request):    
    if request.user.is_authenticated:
        return redirect(reverse('homepage'))
    form=forms.RegisterForm()
    if request.method=="POST":
        form=forms.RegisterForm(request.POST)
        if(form.is_valid()):
            first_name=form.cleaned_data.get('first_name')
            last_name=form.cleaned_data.get('last_name')
            email=form.cleaned_data.get('email')
            password=form.cleaned_data.get('password')
            phone_number=form.cleaned_data.get('phone_number')
            username=phone_number
            has_error=False

            if(Account.objects.filter(username=username,is_verified=True).exists()):
                messages.error(request,"Another Account is Already Created By This PhoneNumber")
                has_error=True
            
        
            
            if has_error:
                return redirect(reverse("signup"))
            user=Account.objects.filter(username=username).exists()
            if not user:
                user=Account.objects.create(first_name=first_name,last_name=last_name,email=email,username=username,phone_number=phone_number)
                user.set_password(password)
                user.save()
            else:
                user=Account.objects.filter(username=username).first()
                user.first_name=first_name
                user.last_name=last_name
                user.email=email
                user.set_password(password)
                user.save()
            token=default_token_generator.make_token(user)
            mail_subject="ACtivate Your account"
            host=f'http://{request.META["HTTP_HOST"]}'
            body=render_to_string("account/email/activate_your_account.html",{'token':token,'username':username,'host':host})
            email=EmailMultiAlternatives(mail_subject,body,settings.DEFAULT_FROM_EMAIL,to=[user.email])
            email.attach_alternative(body, "text/html")
            email.send()
            messages.success(request,"Account Sucessfully Created")
            return redirect(reverse("login"))
    return render(request,"account/register.html",{"catogery":category.objects.all(),'form':form})

def forgotpassword(request):
    if request.user.is_authenticated:
        return redirect(reverse("homepage"))
    form=forms.ForgotPass()
    if request.method=="POST":
        form=forms.ForgotPass(request.POST)
        if form.is_valid():
            username=form.cleaned_data.get('phone_number')
            user=Account.objects.filter(username=username)
            if user.exists():
                token=PasswordResetTokenGenerator().make_token(user.first())
                host=f'http://{request.META["HTTP_HOST"]}'
                email=EmailMultiAlternatives("Forgot Password","Do you forgot your password",settings.DEFAULT_FROM_EMAIL,[user.first().email])
                email.attach_alternative(render_to_string("account/email/forgotpass.html",{'token':token,'username':username,'host':host}),"text/html")
                email.send()
                messages.success(request,"Email Sended")
            else:
                messages.error(request,"Account Doesnt Exists")


    categori=category.objects.all()
    return render(request,"account/forgotpass.html",{'catogery':categori,'form':form})

def activate(request,username):
    if request.method=="GET":
        form=forms.ActivateForm(request.GET)
        if(form.is_valid()):
            user=Account.objects.filter(username=username).first()
            if default_token_generator.check_token(user,form.cleaned_data['token']):
                user.is_verified=True
                user.save()
                messages.success(request,"Account Sucessfully Activated")
            
            else:
                messages.error(request,"Account Sucessfully Activated")
            
        
        return redirect(reverse('login'))
    
def fp_validate(request,username):
    if request.method=="GET":
        form=forms.ActivateForm(request.GET)
        if form.is_valid():
            user=Account.objects.filter(username=username)
            if(user.exists()):
                if(PasswordResetTokenGenerator().check_token(user.first(),form.cleaned_data.get('token'))):
                    request.session['username']=user.first().username
                    return redirect(reverse("reset"))
                else:
                    messages.error(request,"Token Expired")
                    return redirect(reverse("forgotpassword"))
            else:
                messages.error(request,"No user Found BY this number")
                return redirect(reverse("login"))

        else:
            return HttpResponse("Dont CHange Any THing")
        
def resetpassword(request):
    if request.user.is_authenticated:
        return redirect(reverse("homepage"))
    
    if not request.session.get('username') is None:
        form=forms.ResetPass()
        if request.method=="POST":
            form=forms.ResetPass(request.POST)
            if form.is_valid():
                password=form.cleaned_data.get('password')
                cpassword=form.cleaned_data.get('cpassword')
                if password==cpassword:
                    user=Account.objects.filter(username=request.session.get('username')).first()
                    user.set_password(password)
                    user.is_verified=True
                    user.save()
                    request.session['username']=None
                    messages.success(request,"Changed password Sucessfully")
                    return redirect(reverse("login"))
                    
                else:
                    messages.error(request,"Password doesnt match")
        return render(request,"account/resetpassword.html",{"catogery":category.objects.all(),'form':form})
    else:
        return redirect(reverse("forgotpassword"))
        
    

    

        

