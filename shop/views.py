from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse # Pour enoyer les donnees sous forme de json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required # Pour les utilisateurs authentifies
from datetime import datetime
from .utiles import panier_cookie, data_cookie
from .models import Produit, Category
import json
# Create your views here.

def shop(request, *args, **kwargs):
     # Vue des produits
     produits = Produit.objects.all()

     data = data_cookie(request)

     articles = data['articles']

     commande = data['commande']
     
     nombre_article = data['nombre_article']

     context = {
          "articles": articles,
          "commande" : commande,
          "nombre_article": nombre_article,
          'produits': produits
     }

    
     return render(request, 'shop/index.html', context)

def panier(request, *args, **kwargs):
     
     data = data_cookie(request)

     articles = data['articles']

     commande = data['commande']
     
     nombre_article = data['nombre_article']

     context = {
          "articles": articles,
          "commande" : commande,
          "nombre_article": nombre_article
     }

     return render(request, 'shop/panier.html', context)


def commande(request, *args, **kwargs):
     data = data_cookie(request)

     articles = data['articles']

     commande = data['commande']
     
     nombre_article = data['nombre_article']

         
     context = {
          "articles": articles,
          "commande" : commande,
          "nombre_article": nombre_article
     }
     return render(request, 'shop/commande.html', context)

@login_required
def update_article(request, *args, **kwargs):
     # Pour ajouter un article au panier

     data = json.loads(request.body)
     produit_id = data['produit_id']
     #produit_id = int(produit_id)
     action = data['action']

     produit = Produit.objects.get(id = produit_id)
     client = request.user.client  # On recupere le client connecte
     commande, created =  Commande.objects.get_or_create(client=client, complete=False) # Commande liee a ce client : soit on la cree si elle n'existe ou on la recupere
     commande_article, created = CommandeArticle.objects.get_or_create(commande=commande, produit=produit)   # articles associes a lacommande

     if action == 'add':
          commande_article.quantite +=1
     
     if action == 'remove':
          commande_article.quantite -=1
     commande_article.save()

     if commande_article.quantite <= 0 :
          commande_article.delete()
     #print('id', produit_id, 'action', action)
     return JsonResponse('Panier modifie', safe=False)

def commandeAnonyme(request, data): # creation de la commande d'un utilisateur anonyme
     # Recuperation des info de  ses infos
     name = data['form']['name']
     print(data )
     print("Name", name)
     username = data['form']['username']
     email = data['form']['email']
     phone = data['form']['phone']

     cookie_panier = panier_cookie(request)

     articles = cookie_panier['articles']  # On recupere les articles

     # on cree maitena le client

     client, created = Client.objects.get_or_create(
          email=email # il doit avoir son email
     )

     client.name = name  # s'il a change de nom, on garde le nouveau nom
     client.save()

     # on cree la commande
     commande = Commande.objects.create(client=client)

     for article in articles:
          produit = Produit.objects.get(id=article['produit']['id'])
          CommandeArticle.objects.create(
               produit=produit,
               commande=commande,
               quantite=article['quantite']
          )
     
     return client, commande

def traitement_commande(request, *args, **kwargs):
     STATUS_TRANSACTION = ["ACCEPTED", "COMPLETED", "SUCCESS"]
     transaction_id = datetime.now().timestamp() # id de la transaction
     data = json.loads(request.body)

     # Verifions si les donnees proviennent d'un utilisateur authentifie
     if request.user.is_authenticated:
          #data = json.loads(request.body)
          client = request.user.client
          commande, created = Commande.objects.get_or_create(client=client, complete=False)
          
     else:
          print('utilisateur anonyme')
          client, commande = commandeAnonyme(request, data)

     
     total = float(data['form']['total'])
     commande.transaction_id = data['payment_info']["transaction_id"]
     commande.total_trans = data['payment_info']["total"]

     # Verifions que le total de la transaction qu'on a dans le front-end est celui dans le back-end
     if commande.get_panier_total == total :
          commande.complete = True
          commande.status = data['payment_info']["status"]
     
     else:
          commande.status = "REFUSED"
          commande.save()
          return JsonResponse("Attention Fraude Detectee !", safe=False)
     commande.save()

     if commande.produit_physique: # Verifions s'il ya un produit physique
          # Creation de l'addresse d'expedition
          AddressChipping.objects.create(
               client=client,
               commande=commande,
               addresse=data['shipping']['address'],
               ville=data['shipping']['city'],
               zipcode=data['shipping']['zipcode']
          )
     if not commande.status in STATUS_TRANSACTION:
          return JsonResponse("Desole, le paiement a echoue, veuillez reessayer" ,safe=False)

     return JsonResponse('Commande effectuee avec success. Elle vous sera livree bientot', safe=False)



# Ajout des vues pour les ajouts des commandes

def category(request):

     if request.method == 'POST':
          name = request.POST.get('name')
          description = request.POST.get('description')
          #date_ajout = request.POST.get('date_ajout')

          if name == '':
            erreur1 = 'Ce champ ne doit pas être vide'
            return render(request, 'shop/modifierProduit.html', {'categories': categories, 'erreur1': erreur1})
        
          categorie = Category.objects.create(name=name, description=description)
          categorie.save()

          return render(request, 'shop/Produit.html')
     
     return render(request, 'shop/Categorie.html')


def modifierCategorie(request, category_id):
     if request.method == "GET":
          categories = Category.objects.all()

          return render(request, 'shop/mofifierCategorie.html', {"categories":categories})
     
     categorie = Category.objects.get(id=category_id)
     if request.method == "POST":
          name = request.POST.get('name')
          description = request.POST.get('description')

          categorie.name = name
          categorie.description = description

          categorie.save()

          return redirect('shop:listeCategorie')
     return render(request, 'shop/mofifierCategorie.html')

def listeCategorie(request):
       if request.method == 'GET':
          categories = Category.objects.all()
          #return render(request, 'shop/listeProduit.html', {'produits':produits})
          return render(request, 'shop/listeCategorie.html', {'categories':categories})
       
def supprimerCategorie(request, category_id):
     categorie = Category.objects.get(id = category_id)
     categorie.delete()
     return redirect('shop:listeCategorie')
     



def produit(request):

     categories = Category.objects.all()

     if request.method == 'POST':
          categorie_id = request.POST.get('categorie')
          categorie = Category.objects.get(id=categorie_id)

          name = request.POST.get('name')
          price = request.POST.get('price')
          digital = request.POST.get('digital')
          image = request.FILES.get('image')
          description = request.POST.get('description')
          stock = request.POST.get('stock')
          #date_ajout = request.POST.get('date_ajout')

          if name == '':
               erreur1 = 'Ce champ ne doit pas etre vide'
               return render(request, 'shop/Produit.html', {'erreur1': erreur1})
          
          if description == '':
               erreur4 = 'Ce champ ne doit pas etre vide'
               return render(request, 'shop/Produit.html', {'erreur4': erreur4})
          
          
          if price == '' or not price.isnumeric() or float(price) <= 0:
               erreur2 = 'Le prix doit depasser 0'
               return render(request, 'shop/Produit.html', {'erreur2': erreur2})

          if stock == '' or not stock.isnumeric() or float(stock) <= 0:
               erreur5 = 'Le stock doit depasser 0'
               return render(request, 'shop/Produit.html', {'erreur5': erreur5})

          if image == '':
               erreur3 = 'Ce champ ne doit pas etre vide'
               return render(request, 'shop/Produit.html', {'erreur3': erreur3})
          

          produit = Produit.objects.create(categorie=categorie, name=name, price=price, stock=stock, description= description, digital=digital, image=image)
          produit.save()

          #return render(request, 'shop/listeProduit.html')
          return redirect('shop:listeProduit')


     return render(request, 'shop/Produit.html', {'categories': categories})

def listeProduit(request):
     if request.method == 'GET':
          produits = Produit.objects.all()
          #return render(request, 'shop/listeProduit.html', {'produits':produits})
     return render(request, 'shop/listeProduit.html', {'produits':produits})

def supprimerProduit(request, produit_id):
     produit = Produit.objects.get(id = produit_id)
     produit.delete()
     return redirect('shop:listeProduit')


'''def modifierCategorie(request, category_id):
     if request.method == "GET":
          categories = Category.objects.all()

          return render(request, 'shop/mofifierCategorie.html', {"categories":categories})
     
     categorie = Category.objects.get(id=category_id)
     if request.method == "POST":
          name = request.POST.get('name')
          description = request.POST.get('description')

          if name == '':
            erreur1 = 'Ce champ ne doit pas être vide'
            return render(request, 'shop/modifierProduit.html', {'categories': categories, 'erreur1': erreur1})

          if description == '':
               erreur2 = 'Ce champ ne doit pas etre vide'
               return render(request, 'shop/Produit.html', {'erreur2': erreur2})
           

          categorie.name = name
          categorie.description = description

          categorie.save()

          return redirect('shop:listeCategorie')
     return render(request, 'shop/mofifierCategorie.html')'''



def modifierCategorie(request, category_id):
    categorie = Category.objects.get(id=category_id)

    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')

        if not name:
            erreur1 = 'Ce champ ne doit pas être vide'
            return render(request, 'shop/mofifierCategorie.html', {'categorie': categorie, 'erreur1': erreur1})

        if not description:
            erreur2 = 'Ce champ ne doit pas être vide'
            return render(request, 'shop/mofifierCategorie.html', {'categorie': categorie, 'erreur2': erreur2})

        categorie.name = name
        categorie.description = description
        categorie.save()

        return redirect('shop:listeCategorie')

    return render(request, 'shop/mofifierCategorie.html', {'categorie': categorie})


def listeCategorie(request):
       if request.method == 'GET':
          categories = Category.objects.all()
          #return render(request, 'shop/listeProduit.html', {'produits':produits})
          return render(request, 'shop/listeCategorie.html', {'categories':categories})
       
def supprimerCategorie(request, category_id):
     categorie = Category.objects.get(id = category_id)
     categorie.delete()
     return redirect('shop:listeCategorie')
     



'''def modifierProduit(request, produit_id):
    categories = Category.objects.all()
    produit = Produit.objects.get(id=produit_id)

    if request.method == 'POST':
        categorie_id = request.POST.get('categorie')
        categorie = Category.objects.get(id=categorie_id)
        name = request.POST.get('name')
        price = request.POST.get('price')
        digital = request.POST.get('digital')
        image = request.FILES.get('image')

        if name == '':
            erreur1 = 'Ce champ ne doit pas être vide'
            return render(request, 'shop/modifierProduit.html', {'categories': categories, 'erreur1': erreur1})
        
        if price == '' or not price.isnumeric() or float(price) <= 0:
            erreur2 = 'Le prix doit dépasser 0'
            return render(request, 'shop/modifierProduit.html', {'categories': categories, 'erreur2': erreur2})

        if not image:
          erreur3 = 'Ce champ ne doit pas être vide'
          return render(request, 'shop/modifierProduit.html', {'categories': categories, 'erreur3': erreur3})

        # Mettez à jour les données du produit
          
        produit.categorie = categorie
        produit.name = name
        produit.price = price
        produit.digital = digital
        produit.image = image
        produit.save()

        return redirect('shop:listeProduit')
          

     
         

    return render(request, 'shop/modifierProduit.html', {'categories': categories, 'produit': produit})'''

def modifierProduit(request, produit_id):
    categories = Category.objects.all()
    produit = Produit.objects.get(id=produit_id)

    if request.method == 'POST':
        categorie_id = request.POST.get('categorie')
        categorie = Category.objects.get(id=categorie_id)
        name = request.POST.get('name')
        price = request.POST.get('price')
        digital = request.POST.get('digital')
        new_image = request.FILES.get('image')  # Nouvelle image téléchargée
        description = request.POST.get('description')
        stock = request.POST.get('stock')
        

        if name == '':
            erreur1 = 'Ce champ ne doit pas être vide'
            return render(request, 'shop/modifierProduit.html', {'categories': categories, 'erreur1': erreur1})
        
        if price == '' or not price.isnumeric() or float(price) <= 0:
            erreur2 = 'Le prix doit dépasser 0'
            return render(request, 'shop/modifierProduit.html', {'categories': categories, 'erreur2': erreur2})


        if stock == '' or not stock.isnumeric() or float(stock) <= 0:
               erreur5 = 'Le stock doit depasser 0'
               return render(request, 'shop/Produit.html', {'erreur5': erreur5})
        if description == '':
               erreur4 = 'Ce champ ne doit pas etre vide'
               return render(request, 'shop/Produit.html', {'erreur4': erreur4})
          

        # Mettez à jour les données du produit
        produit.categorie = categorie
        produit.name = name
        produit.price = price
        produit.digital = digital
        produit.description = description
        produit.stock = stock



        # Si une nouvelle image a été téléchargée, mettez à jour l'image du produit
        if new_image:
            produit.image = new_image

        produit.save()

        return redirect('shop:listeProduit')
    
    return render(request, 'shop/modifierProduit.html', {'categories': categories, 'produit': produit})



'''def modifierProduit(request, produit_id):
     categories = Category.objects.all()
     produit = Produit.objects.get(id=produit_id)

     if request.method == 'POST':
          categorie_id = request.POST.get('categorie')
          categorie = Category.objects.get(id=categorie_id)
          name = request.POST.get('name')
          price = request.POST.get('price')
          digital = request.POST.get('digital')
          image = request.FILES.get('image')

          if name == '':
               erreur1 = 'Ce champ ne doit pas être vide'
          elif price == '' or not price.isnumeric() or float(price) <= 0:
               erreur2 = 'Le prix doit être supérieur à 0'
          elif not image:
               erreur3 = 'Veuillez sélectionner une image'
          else:
               # Mettre à jour les informations du produit
               produit.categorie = categorie
               produit.name = name
               produit.price = price
               produit.digital = digital
               produit.image = image
               produit.save()

               # Rediriger vers la liste des produits ou une autre page appropriée
               return redirect('shop:listeProduit')

     else:
          # Chargement des informations du produit pour pré-remplir le formulaire
          data = {
               'categorie': produit.categorie.id,
               'name': produit.name,
               'price': produit.price,
               'digital': produit.digital,
               # Vous pouvez ajouter d'autres champs ici
          }
          return render(request, 'shop/modifierProduit.html', {'categories': categories, 'data': data})

     return render(request, 'shop/modifierProduit.html', {'categories': categories, 'erreur1': erreur1, 'erreur2': erreur2, 'erreur3': erreur3, 'data': data})'''

# Voir les details du produit si on clique sur voir

def voir(request, produit_id):
     produits = Produit.objects.get(id=produit_id)
     detail ={'produits': produits}
     return render(request, 'shop/voir.html', detail)
