

var produitBtns = document.getElementsByClassName('update-panier')  /* Recuperation de tous les produits */

for(var i = 0; i < produitBtns.length; i++){
    /* Ajout de l'evevement click au bouton de chaque produit */
    produitBtns[i].addEventListener('click', function(){
        var produitId = this.dataset.produit; /* On secupere l'id du produit */
        var action = this.dataset.action;

        /* Pour savoir si l'utilisateur est anonyme ou authentifie */
        if (user ==='AnonymousUser'){
            addCookieArticle(produitId , action);
        }else{

            updateUserCommande(produitId , action);
        }
    })
}

function addCookieArticle(produitId, action){
    console.log("utilisateur anonyme");

    if( action == 'add'){ // verifions si l'action = ajouter
        if(panier[produitId] == undefined){  // si le produit n'existe pas encore dans le panier
            panier[produitId] = {'qte' : 1}; // onle cree
        }else{
            panier[produitId]['qte'] +=1 ; // on qugmente sa quantite
        }
    }

    if( action == 'remove'){
        panier[produitId]['qte'] -=1 ;

        if(panier[produitId]['qte'] <= 0){
            delete panier[produitId];
        }
    }

    document.cookie = "panier=" + JSON.stringify(panier) + ";domain=;path=/";    // On met a jour le cookie
    console.log(panier);
    location.reload();
}

//var csrftoken = window.csrfToken;
//var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
function updateUserCommande(produitId, action){

    var url = '/update_article/'; /* Recupere l'url */

    /* Pour pointer l'url */
    fetch(url, {
        method:'POST',
        headers: {
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken
        },

        body:JSON.stringify({'produit_id': produitId, 'action': action})
    })

    /* Retour d'une prommesse */
    .then((response) =>{
        return response.json();
    })

    .then((data) =>{
        console.log('data', data);
        location.reload();
    })

}