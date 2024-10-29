from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('delete_transaction/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path('delete_block/<int:money_block_id>/', views.delete_block, name='delete_block'),
    path('top_up_balance/', views.top_up_balance, name='top_up_balance'),
    path('user/<uuid:unique_link>/', views.shared_page, name='shared_page'),
    path('get_graph_data/<int:money_block_id>/', views.get_graph_data, name='get_graph_data'),
    path('user/<uuid:unique_link>/get_graph_data/<int:money_block_id>/', views.get_graph_data_shared, name='get_graph_data_shared'),
]
