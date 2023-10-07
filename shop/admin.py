from django.contrib import admin
from .models import *


class ClientModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'name' , 'email')

class CategoryModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

class ProduitModelAdmin(admin.ModelAdmin):
    list_display = ('categorie', 'name', "price", "digital", "image", "date_ajout")

class CommandeModelAdmin(admin.ModelAdmin):
    list_display = ('client', 'date_commande', "complete", "transaction_id", "status", "total_trans")

class CommandeArticleModelAdmin(admin.ModelAdmin):
    list_display = ('produit', 'commande', "quantite", "date_added")

class AddressChippingModelAdmin(admin.ModelAdmin):
    list_display = ('client', 'commande', "addresse", "ville", "zipcode", "date_ajout")


admin.site.register(Client, ClientModelAdmin)

admin.site.register(Category, CategoryModelAdmin)

admin.site.register(Produit, ProduitModelAdmin)

admin.site.register(Commande, CommandeModelAdmin)

admin.site.register(CommandeArticle, CommandeArticleModelAdmin)

admin.site.register(AddressChipping, AddressChippingModelAdmin)

admin.site.site_title = "Fiarma e-commerce"

admin.site.site_header = "Fiarma e-commerce"

admin.site.index_title = "Fiarma e-commerce"