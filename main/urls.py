from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
path('', views.home,name='home'),
path('pagedetail/<int:id>', views.page_detail, name='pagedetail'),
path('faq', views.faq_list, name='faq'),
path('enquiry', views.enquiry, name='enquiry'),
path('gallery', views.gallery, name='gallery'),
path('gallerydetail/<int:id>', views.gallery_detail, name='gallery_detail'),
path('pricing',views.pricing,name='pricing'),
path('accounts/signup',views.signup,name='signup'),
path('checkout/<int:plan_id>',views.checkout,name='checkout'),
path('checkout_session/<int:plan_id>',views.checkout_session,name='checkout_session'),
path('success',views.success,name='success'),
path('cancel',views.cancel,name='cancel'),
#start  user dashbard sections
path('user-dashboard',views.user_dashboard,name='user_dashboard'),
path('update-profile',views.update_profile,name='update_profile'),
# Trainer Login
path('trainerlogin',views.trainerlogin,name='trainerlogin'),
path('trainerlogout',views.trainerlogin,name='trainerlogout'),
path('trainer_profile',views.trainer_profile,name='trainer_profile'),
path('trainer_dashboard',views.trainer_dashboard,name='trainer_dashboard'),
path('trainer_subscribers',views.trainer_subscribers,name='trainer_subscribers'),
path('trainer_payments',views.trainer_payments,name='trainer_payments'),
path('trainer_changepassword',views.trainer_changepassword,name='trainer_changepassword'),

]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
