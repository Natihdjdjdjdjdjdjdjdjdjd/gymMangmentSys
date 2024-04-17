from django.shortcuts import render,redirect
from . import models
from . import forms
from django.db.models import Count
from django.template.loader import get_template

from datetime import timedelta
import stripe

# Home page
def home(request):
	banners=models.Banners.objects.all()
	g_imgs=models.GalleryImage.objects.all().order_by('id')[:9]
	services=models.Service.objects.all()[:3]
	return render(request, 'home.html',{'banners': banners,'services':services,'g_imgs':g_imgs})


# Page detail
def page_detail(request, id):
	page=models.Page.objects.get(id=id)

	return render(request, 'page.html',{'page':page})

# FAQ quest
def faq_list(request):
	faq=models.Faq.objects.all()[:3]
	return render(request, 'faq.html',{'faqs':faq})

# Enquiry
def enquiry(request):
	message=''
	if request.method=='POST':
		form=forms.EnquiryForm(request.POST)
		if form.is_valid():
			form.save()
			message='The Data has been saved'
	form=forms.EnquiryForm
	return render(request, 'enquiry.html',{'form':form,'message':message})

# show gallery

def gallery(request):
	gallery=models.Gallery.objects.all().order_by('-id')
	return render(request, 'gallery.html',{'gallerys':gallery})

# show gallery detail

def gallery_detail(request, id):
	gallery=models.Gallery.objects.get(id=id)
	gallery_imgs=models.GalleryImage.objects.filter(gallery=gallery).order_by('-id')
	return render(request, 'gallery_imgs.html',{'gallery_imgs':gallery_imgs})

# Subscription Plans
def pricing(request):
	pricing=models.SubPlan.objects.annotate(total_members=Count('subscription__id')).all().order_by('price')
	dfeatures=models.SubPlanFeature.objects.distinct('title');
	return render(request, 'pricing.html',{'plans':pricing,'dfeatures':dfeatures})

#Signup
def signup(request):
	message=None
	if request.method=='POST':
		form=forms.SignUp(request.POST)
		if form.is_valid():
			form.save()
			message='Thank you for register.'
	form=forms.SignUp
	return render(request, 'registration/signup.html',{'form':form,'message':message})

	# Subscription Plans
def checkout(request, plan_id):
	detailplan=models.SubPlan.objects.get(pk=plan_id)
	return render(request, 'checkout.html',{'plan':detailplan})


stripe.api_key='sk_test_51OxCMV03wdSJHu0rBuJT5DxQghVGoD4wiAI80iSOudZBs82qRwjNHw1ZbXQuXkITS5VDFgbHfMQWTIketRWYMS2P00k937Wiag'
def checkout_session(request,plan_id):
	plan=models.SubPlan.objects.get(pk=plan_id)
	session=stripe.checkout.Session.create(
		payment_method_types=['card'],
		line_items=[{
	      'price_data': {
	        'currency': 'usd',
	        'product_data': {
	          'name': plan.title,
	        },
	        'unit_amount': plan.price*100,
	      },
	      'quantity': 1,
	    }],
	    mode='payment',

	    success_url='http://127.0.0.1:8000/success?session_id={CHECKOUT_SESSION_ID}',
	    cancel_url='http://127.0.0.1:8000/cancel',
	    client_reference_id=plan_id
	)
	return redirect(session.url, code=303)

# Success
from django.core.mail import EmailMessage


def success(request):
	session = stripe.checkout.Session.retrieve(request.GET['session_id'])
	plan_id=session.client_reference_id
	plan=models.SubPlan.objects.get(pk=plan_id)
	user=request.user
	models.Subscription.objects.create(
		plan=plan,
		user=user,
		price=plan.price
	)
	subject='Order Email'
	html_content=get_template('orderemail.html').render({'title':plan.title})
	from_email='natasbest@gmail.com'

	msg = EmailMessage(subject, html_content, from_email, ['natasbest@gmail.com'])
	msg.content_subtype = "html"  # Main content is now text/html
	msg.send()

	return render(request, 'success.html')

# Cancel
def cancel(request):
	return render(request, 'cancel.html')

# User dashboard
def user_dashboard(request):
	current_plan=models.Subscription.objects.get(user=request.user)
	my_trainer=models.AssignSubscriber.objects.get(user=request.user)
	enddate=current_plan.reg_date+timedelta(days=current_plan.plan.validty_days)
	return render(request, 'user/dashboard.html',{
		'current_plan':current_plan,
		'my_trainer':my_trainer,
		'enddate':enddate
		})

def update_profile(request):
	message=None
	if request.method=='POST':
		form=forms.ProfileForm(request.POST,instance=request.user)
		if form.is_valid():
			form.save()
			message='The data has been saved'
	form=forms.ProfileForm(instance=request.user)
	return render(request, 'user/update-profile.html',{'form':form,'message':message})

# Create trainer login

def trainerlogin(request):
	msg=''
	if request.method=='POST':
		username=request.POST['username']
		pwd=request.POST['pwd']
		trainer=models.Trainer.objects.filter(username=username,pwd=pwd).count()
		if trainer > 0:
			trainer=models.Trainer.objects.filter(username=username,pwd=pwd).first()
			request.session['trainerLogin']=True
			request.session['trainerid']=trainer.id
			return redirect('/trainer_dashboard')
		else:
			msg='Invalid!!'
	form=forms.TrainerLoginForm
	return render(request, 'trainer/login.html',{'form':form,'msg':msg})

# Trainer Logout
def trainerlogout(request):
	del request.session['trainerLogin']
	return redirect('/trainerlogin')

# Trainer Dashboard
def trainer_dashboard(request):
	return render(request, 'trainer/dashboard.html')

# Trainer Profile
def trainer_profile(request):
	t_id=request.session['trainerid']
	trainer=models.Trainer.objects.get(pk=t_id)
	msg=None
	if request.method=='POST':
		form=forms.TrainerProfileForm(request.POST,request.FILES,instance=trainer)
		if form.is_valid():
			form.save()
			msg='Profile has been updated'
	form=forms.TrainerProfileForm(instance=trainer)
	return render(request, 'trainer/profile.html',{'form':form,'msg':msg})
# Trainer Subscribers
def trainer_subscribers(request):
	trainer=models.Trainer.objects.get(pk=request.session['trainerid'])
	trainer_subs=models.AssignSubscriber.objects.filter(trainer=trainer).order_by('-id')
	return render(request, 'trainer/trainer_subscribers.html',{'trainer_subs':trainer_subs})

	# Trainer Payments
def trainer_payments(request):
	trainer=models.Trainer.objects.get(pk=request.session['trainerid'])
	trainer_pays=models.TrainerSalary.objects.filter(trainer=trainer).order_by('-id')
	return render(request, 'trainer/trainer_payments.html',{'trainer_pays':trainer_pays})

# Trainer Change Password
def trainer_changepassword(request):
	msg=None
	if request.method=='POST':
		new_password=request.POST['new_password']
		updateRes=models.Trainer.objects.filter(pk=request.session['trainerid']).update(pwd=new_password)
		if updateRes:
			del request.session['trainerLogin']
			return redirect('/trainerlogin')
		else:
			msg='Something is wrong!!'
	form=forms.TrainerChangePassword
	return render(request, 'trainer/trainer_changepassword.html',{'form':form})

# Trainer Change Password
def trainer_changepassword(request):
	msg=None
	if request.method=='POST':
		new_password=request.POST['new_password']
		updateRes=models.Trainer.objects.filter(pk=request.session['trainerid']).update(pwd=new_password)
		if updateRes:
			del request.session['trainerLogin']
			return redirect('/trainerlogin')
		else:
			msg='Something is wrong!!'
	form=forms.TrainerChangePassword
	return render(request, 'trainer/trainer_changepassword.html',{'form':form})
