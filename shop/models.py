from django.db import models
from django.contrib.auth.models import User  # Model de djanngo pour creer les utilisateurs
from django.utils import timezone

class Client(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="client") # Notre client peut etre connecte ou non( utilisateur anonyme)
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=200, null=True)

def __str__(self): # la fonction str permet retourne un nom qui representera l'object.
    return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name
    
class Produit(models.Model):
    categorie = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=100, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    digital = models.BooleanField(default=False, null=True, blank=True)
    image = models.ImageField(upload_to='shop' , null=True, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    stock = models.IntegerField()
    description = models.TextField(null=True, blank=True)


    def __str__(self):
        return self.name
    
    # Afficher les produits par les plus recemment ajoutes
    class Meta:
        ordering = ['-date_ajout']
    

    # autorisation d'afficher un produit sans image
    @property
    def imageUrl(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Commande(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, blank=True, null=True) 
    date_commande = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=True) # un boolean qui permet de savoir si l'instance de commande a ete acheve ou non
    transaction_id = models.CharField(max_length=200, null=True, blank=True) # identifiant de transaction
    status = models.CharField(max_length=200, null=True, blank=True)  # status de la transation
    total_trans = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # total de la transaction

    def __str__(self):
        return str(self.id)
    
    # Calcul de la somme totale du panier ( le montant global de tous les achats)
    @property  # Pour dire que c'est une propriete
    def get_panier_total(self):
        articles = self.commandearticle_set.all() # liste des produits se trouvant dans le panier
        total = sum(article.get_total for article in articles)
        return total
    
    # Nombres d'articles (quantite) dans le panier
    @property
    def get_panier_article(self):
        articles = self.commandearticle_set.all()
        total = sum(article.quantite for article in articles)
        return total
    
    # Savoir s'il ya au moins un produit physique dans sa commande
    @property
    def produit_physique(self):
        articles = self.commandearticle_set.all() # liste des produits se trouvant dans le panier
        au_moins_un_produit_physique = any(article.produit.digital==False for article in articles)
        return au_moins_un_produit_physique




    
class CommandeArticle(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, blank=True, null=True)
    commande = models.ForeignKey(Commande, on_delete=models.SET_NULL, blank=True, null=True)
    quantite = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    # Calcul du prix total de chaque article en fonction de la quantite commandee
    @property
    def get_total(self):
        total = self.produit.price * self.quantite
        return total


class AddressChipping(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, blank=True, null=True)
    commande = models.ForeignKey(Commande, on_delete=models.SET_NULL, blank=True, null=True)
    addresse = models.CharField(max_length=100, null=True)
    ville = models.CharField(max_length=100, null=True)
    zipcode = models.CharField(max_length=100, null=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.addresse