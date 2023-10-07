from . models import *
import json

def panier_cookie(request):

    articles = []  # articles vide au depart

          # iniatialisation de la commande
    commande = {
        'get_panier_total' : 0,
        "get_panier_article" :0,
        'produit_physique':True
    }

    nombre_article = commande['get_panier_article'] # nombre d'articles de la commande


    try:
        panier = json.loads(request.COOKIES.get('panier')) # on recupere le panier a partir des cookies
        for obj in panier:  # pour un objet appartenant au panier

            nombre_article += panier[obj]['qte'] # calcul de la quantite totale de chaque article dans le panier

            produit = Produit.objects.get(id = obj)  # On cree le produit identifie par l'object appartenant au panier

            total = produit.price * panier[obj]['qte']  # calcul du prix total de chq article en fonction de sa quantitr

            commande['get_panier_article'] += panier[obj]['qte'] # Calcul du nombre total des articles de la commande

            commande['get_panier_total'] += total # Calcul du cout total de la commande

            article = {  # Creation d'un article
                    "produit":{  # produit avec ses attributs
                        'id': produit.id,
                        'name': produit.name,
                        'price':produit.price,
                        'imageUrl':produit.imageUrl
                    },

                    'quantite': panier[obj]['qte'], # quantite de l'article

                    'get_total': total # prix total de chq article en fonction de sa quantite avec la propriete 'get_total'

            }

            articles.append(article)  # ajout de l'article dans la liste des articles

            if produit.digital == False:
                    commande['produit_physique'] = True
    except:
      pass



    context = {
    "articles": articles,
    "commande" : commande,
    "nombre_article": nombre_article
    }
    
    return context


def data_cookie(request):


# On verifie si l'utilisateur est authentifier
    if request.user.is_authenticated:
        client = request.user.client
        commande, created =  Commande.objects.get_or_create(client=client, complete=False) # Commande liee a ce client : soit on la cree si elle n'existe ou on la recupere

        # Articles lies a la commande (relation OneToMany)
        articles = commande.commandearticle_set.all()
        nombre_article = commande.get_panier_article

    
    else:
        cookie_panier = panier_cookie(request)
        articles = cookie_panier['articles']
        commande = cookie_panier['commande']
        nombre_article = cookie_panier['nombre_article']

        
    context = {
        "articles": articles,
        "commande" : commande,
        "nombre_article": nombre_article
    }

    return context