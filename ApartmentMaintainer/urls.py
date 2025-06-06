"""
URL configuration for ApartmentMaintainer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from Контор import views
from Welcome import views as v
from Residents import views as v1
from HOA import views as v2
from API import views as v3
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    #dashboardGlobal
    path('', v.dashboardGlobal, name='dashboardGlobal'),
    path('login_options/', v.login_options, name='login_options'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('user_login/', v1.user_login, name='user_login'),

    #HOA
    path('hoa_login/', v2.hoa_login, name='hoa_login'),
    path('staff_login/', v2.staff_login, name='staff_login'),
    path('executive_dashboard/<int:id>/', v2.executive_dashboard, name='executive_dashboard'),
    path('staff_dashboard/<int:id>/', v2.staff_dashboard, name='staff_dashboard'),
    path('add_staff/<int:id>/', v2.add_staff, name='add_staff'),
    path('hoa_staffs/<int:id>/', v2.hoa_staffs, name='hoa_staffs'),
    path('edit_staff/<int:staff_id>/<int:id>/', v2.edit_staff, name='edit_staff'),
    path('delete_staff/<int:staff_id>/<int:id>/', v2.delete_staff, name='delete_staff'),
    path('add_common_properties/<str:placeholder>/<str:placeholder1>/<int:exec_id>/', v2.add_common_properties, name='add_common_properties'),
    path('property/<str:story>/<str:unit>/<str:placeholder>/<str:placeholder1>/<int:exec_id>/', v2.property, name='property'),
    path('property_maintenance/<str:property_category>/<int:property_id>/<str:apartmentblock>/<int:exec_id>/', v2.property_maintenance, name='property_maintenance'),
    path('create_budget/<int:id>/', v2.create_budget, name='create_budget'),
    path('budget_list', v2.budget_list, name='budget_list'),
    path('create_staff_salary/<int:staff_id>/<int:id>/', v2.create_staff_salary, name='create_staff_salary'),
    path('staff_salary_list/', v2.staff_salary_list, name='staff_salary_list'),
    path('salary_processing/<int:staff_id>/<int:id>/', v2.salary_processing, name='salary_processing'),
    path('create_monthly_timetable/<int:staff_id>/<int:id>/', v2.create_monthly_timetable, name='create_monthly_timetable'),
    path('update_timetable/<int:staff_id>/<str:timetable_message>/<int:id>/', v2.update_timetable, name='update_timetable'),
    path('see_timetable/<int:id>/', v2.see_timetable, name='see_timetable'),
    path('staff_timetable/<int:user_id>/<int:timetable_id>/<int:id>/', v2.staff_timetable, name='staff_timetable'),
    path('budget_request/<int:id>/', v2.budget_request, name='budget_request'),
    path('see_budget_request/<int:id>/', v2.see_budget_request, name='see_budget_request'),
    path('update_decision/<int:request_id>/<int:id>/', v2.update_decision, name='update_decision'),
    path('request_state/<int:id>/', v2.request_state, name='request_state'),
    path('logout_confirmation/<int:id>/', v2.logout_confirmation, name='logout_confirmation'),
    path('view_apartments/<int:id>/', v2.view_apartments, name='view_apartments'),
    path('property_of_apartment_block/<int:block_id>/<int:id>/<str:message>/', v2.property_of_apartment_block, name='property_of_apartment_block'),
    path('logout_staff/<int:id>/', v2.logout_staff, name='logout_staff'),

    #resident
    path('user_dashboard/<int:resident_id>/', v1.user_dashboard, name='user_dashboard'),
    path('user_profile/<int:resident_id>/', v1.user_profile, name='user_profile'),
    path('usage_history/<int:id>/', v1.usage_history, name='usage_history'),
    path('payment_history/<int:id>/', v1.payment_history, name='payment_history'),
    path('logout_confirmation_user/<int:id>/', v1.logout_confirmation_user, name='logout_confirmation_user'),

    #API
    path('make_payment_monthly_usage/<int:resident_id>/<int:payment_id>/ ', v3.make_payment_monthly_usage, name='make_payment_monthly_usage'),
    path('processing_payment/<int:resident_id>/', v3.processing_payment, name='processing_payment'),

    #Контур
    path('dashboard/<int:id>/', views.dashboard, name='dashboard'),  # Home page
    path('add_apartment_block/<int:id>/', views.add_apartment_block, name='add_apartment_block'),
    path('delete_apartment_block/<int:block_id>/<int:id>/', views.delete_apartment_block, name='delete_apartment_block'),
    path('edit_apartment_block/<int:block_id>/<int:id>/', views.edit_apartment_block, name='edit_apartment_block'),
    path('view_apartment_block/<int:block_id>/<int:id>/', views.view_apartment_block, name='view_apartment_block'),

    path('add_resident/<int:block_id>/', views.add_resident, name='add_resident'),
    path('edit_resident/<int:block_id>/<int:resident_id>/', views.edit_resident, name='edit_resident'),
    path('delete_resident/<int:resident_id>/<int:block_id>/', views.delete_resident, name='delete_resident'),

    path('register/', views.register, name='register'),  # Registration URL
    path('logout/confirm/', views.logout_confirmation, name='logout_confirmation'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
   
    
    path('add_utility_rates/', views.add_utility_rates, name='add_utility_rates'),
    path('monthly_usage/<int:resident_id>/<int:block_id>/', views.monthly_usage, name='monthly_usage'),
    path('utilities/<int:resident_id>/<int:block_id>/', views.utilities, name='utilities'),     

    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)