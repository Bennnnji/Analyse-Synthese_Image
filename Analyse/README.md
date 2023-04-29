# Partie analyse : Identification pièces de puzzle

## Contributeurs

- p2006010 - [Boulet Benjamin]

## Demarches utilisées

image d'origine : 
![image d'origine](./images/startImage.jpg)

### 1. Création du masque binaire

- on applique un filtre median pour réduire le bruit et applatir les couleurs

- On convertit l'image en LAB pour pouvoir séparer les couleursa

- On calcul grâce à des histogrammes la valeur dominante de chaque canal donc L A et B

- Sur, l'image flouté, on regarde si la valeurs de chaque pixel est proche de la valeur dominante de chaque canal. Si c'est le cas, on colorie le pixel en noir sinon en blanc

- On applique ensuite plusieurs fermeture et ouvertures pour supprimer les petits trous et les petits points blancs

### 2. Détection des contours => Identification des pièces

- On utilise la fonction findContours pour trouver les contours de sur le masque binaire

- on les trie par odre croissant de haut gauche à bas droite ( afin de nous faciliter la tache pour la suite )

### 3. Extraction des pièces

#### Extraction des masques : 

- on créer un maque vide de la taille de du masque binaire

- pour chaque pièce, indépendement des autres, on dessine le contour de la pièce sur le masque vide et on fait un bitwise_and ( ET ) avec le masque binaire pour ne garder que le masque de la pièce.

![masque pièce ( grand ) : ](./)

- On rogne ensuite avec le boundingRect du contour de la pièce pour extraire juste le masque de la pièce ( rogné )

![masque pièce rogné :](./)

---

#### Extraction des pièces : 



- On prend le masque de la pièce trouvé précedemment et on fait un bitwise_and ( ET ) avec l'image de base

![image pièce n°5 :](./)

- De même, on rogne avec le boundingRect du contour de la pièce pour extraire juste la pièce ( rogné ).

![image pièce n°5 rogné :](./)
___
#### On enregistre les images donnée dans leur dossier réspéctif :  

- **Mask/** , avec `wideMask/` pour les grands masques et `cutMask/` pour les masques rognés  

- **images/**, avec pareil, `widePieces/` et `cutPieces/`  


#### Après toute ces étapes, on arrive à afficher la pièce coupé, son masque, ses contours :
![exemple, pièce n°5 découpage :](./)

___

### 4. Identification des contours 

- On simplifie les contours de la pièce avec `approxPolyDP()`

- On trace des lignes horizontal et vertical sur chaques bords de la pièce. cad. :
    - **Vertical 1 :** P1:{18, 0} à P2:{18, Hauteur}
    - **Vertical 2 :** P1:{Longeur - 23, 0 } à P2:{Longeur - 23, Hauteur}
    - **Horizontal 1 :** P1:{0 ; 23} à P2:{Longeur ; 23}
    - **Horizontal 2 :** P1:{0 ; Hauteur - 23} à P2:{Longeur ; Hauteur - 23}

