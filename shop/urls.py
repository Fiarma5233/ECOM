from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.shop, name='shop'),

    path('panier/', views.panier, name='panier'),

    path('commande/', views.commande, name='commande'),

    path("update_article/", views.update_article, name="update_article"),

    path('traitement_commande/', views.traitement_commande, name="traitement_commande"),

    path('category', views.category, name="category"),

    path('produit', views.produit, name="produit" ),

    path('listeProduit', views.listeProduit, name="listeProduit"),

    path('listeCategorie', views.listeCategorie, name="listeCategorie"),



    path('modifierCategorie/<int:category_id>/', views.modifierCategorie, name="modifierCategorie"),

    path('supprimerCategorie/<int:category_id>/', views.supprimerCategorie, name="supprimerCategorie"),

    path('supprimerProduit/<int:produit_id>/', views.supprimerProduit, name="supprimerProduit"),

    path('modifierProduit/<int:produit_id>/', views.modifierProduit, name="modifierProduit"),




]