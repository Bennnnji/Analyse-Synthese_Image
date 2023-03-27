import cv2
import numpy as np
import sys
import matplotlib.pyplot as plt
import random

# Créer une image BGR vide avec numpy
# img = np.zeros((height,width,3), np.uint8)

# Créer une image BGR vide aux mêmes dimensions qu'une autre image
# img2 = np.zeros_like(img)

# Dimensions de l'image nd
# img.shape

# Pour accéder aux données couleurImage d'un pixel :
# (b, g, r) = img[100, 100]

# Pour modifier les données couleurImage d'un pixel :
# img[100,100] = [255,255,255]

# Pour accéder aux données d'une image en niveaux de gris (une seule composante) :
# gray = img[100,100]

# Pour modifier les données d'une image en niveaux de gris (une seule composante) :
# img[100,100] = 196

# Séparer les différentes composantes couleurImage d'une image :
#(B, G, R) = cv2.split(img)

# Combiner les images des différentes composantes pour former une image couleurImage :
#img = cv2.merge((B,G,R))

#Par exemple, pour passer de l'espace BGR à un niveau de gris :
#res = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

#Pour redimensionner une image
# cv2.resize(s, size,fx,fy,interpolation)

#Afficher une image 
#cv2.imshow(name,image)

#-----------------------------------------------------------------------------------------

# EXERCICE 1

def noircir(image):
    image[...] = 0
    cv2.imshow('image originale',image)

def colorierRandom(image, couleur):   
    image[...] = couleur
    cv2.imshow('image originale',image)

def dessinerRectangle(image, couleurRectangle):
    rectangle = np.zeros((HauteurRectangle,LargeurRectangle,3), np.uint8)
    height = image.shape[0]
    width = image.shape[1]
    heigthMin = int((height/2)-(HauteurRectangle/2))
    heightMax = int((height/2)+(HauteurRectangle/2))
    widthMin = int((width/2)-(LargeurRectangle/2))
    widthMax = int((width/2)+(LargeurRectangle/2))
    rectangle[...] = couleurRectangle
    img[heigthMin:heightMax, widthMin:widthMax] = rectangle
    cv2.imshow('image originale',image)

def couleurRandom():
    couleurB = random.randint(0,255)
    couleurG = random.randint(0,255)
    couleurR = random.randint(0,255) 
    return [couleurB, couleurG, couleurR]

def fonctionTrackbarLargeur(v):
    colorierRandom(img, couleurImage)
    global LargeurRectangle
    LargeurRectangle = v
    dessinerRectangle(img, couleurRectangle)
    
def fonctionTrackbarHauteur(v):
    colorierRandom(img, couleurImage)
    global HauteurRectangle
    HauteurRectangle = v
    dessinerRectangle(img, couleurRectangle)

global img 
img = np.zeros((480,640,3), np.uint8)

global rectangle

global isActive
isActive = False

global couleurImage 
couleurImage = img[0,0]

global couleurRectangle
couleurRectangle = [0,0,0]

cv2.namedWindow('image originale')
cv2.createTrackbar('LargeurRectangle','image originale',100,640,fonctionTrackbarLargeur)
cv2.createTrackbar('HauteurRectangle','image originale',100,480,fonctionTrackbarHauteur)
cv2.imshow('image originale',img)

while True:
    key = cv2.waitKey(30) & 0x0FF
    if key == 27 or key==ord('q'):
        print('arrêt du programme par l\'utilisateur')
        break;
    if key ==ord('n'):
        noircir(img)
    if key ==ord('c'):
        couleur = couleurRandom()
        colorierRandom(img, couleur)
    if key ==ord('r'):
        if(isActive):
            isActive = False
            couleurRectangle = couleurImage
            dessinerRectangle(img, couleurRectangle)
        else:
            isActive = True
            couleurRectangle = couleurRandom()
            dessinerRectangle(img, couleurRectangle)
        
            

cv2.destroyWindow('image originale')


#---------------------------Correction------------------------

# import cv2
# import numpy as np
# import matplotlib.pyplot as plt

# largeur = 100
# hauteur = 50
# posX = int(640/2)
# posY = int(480/2)
# dessin = False
# image = None
# couleur = [0,0,0]

# def remplirNoir(image):
#     global couleur
#     couleur = [0,0,0]
#     image[...] = couleur
#     return image

# def remplirCouleur(image):
#     global couleur
#     couleur = np.random.randint(0, 255,3,np.uint8)
#     image[...] = couleur
#     return image

# def remplirRectangle(image,posx,posy,largeur,hauteur):
#     image[...] = couleur
#     xmin = max(0,int(posX-largeur/2))
#     xmax = min(image.shape[1],int(posx+largeur/2))
#     ymin = max(0,int(posy-hauteur/2))
#     ymax = min(image.shape[0],int(posy+hauteur/2))
#     image[ymin:ymax,xmin:xmax] = np.random.randint(0, 255,3,np.uint8)
#     return image

# def setLargeur(v):
#     global largeur, image
#     largeur = v
#     if dessin:
#         image = remplirRectangle(image,posX,posY,largeur,hauteur)
#         cv2.imshow('image originale',image)

# def setHauteur(v):
#     global hauteur, image
#     hauteur = v
#     if dessin:
#         image = remplirRectangle(image,posX,posY,largeur,hauteur)
#         cv2.imshow('image originale',image)
        
# def evenementSouris(event,x,y,flags,data):
#     global posX, posY, image, dessin
#     if event==cv2.EVENT_LBUTTONUP:
#         posX = x
#         posY = y
#         dessin = True
#         image = remplirRectangle(image,posX,posY,largeur,hauteur)
#         cv2.imshow('image originale',image)
        
# image = np.zeros((480,640,3), np.uint8)

# cv2.namedWindow('image originale')
# cv2.createTrackbar('Largeur','image originale',largeur,image.shape[1],setLargeur)
# cv2.createTrackbar('Hauteur','image originale',hauteur,image.shape[0],setHauteur)
# cv2.setMouseCallback('image originale',evenementSouris)
# cv2.imshow('image originale',image)

# while True:
#     key = cv2.waitKey(30) & 0x0FF
#     if key == 27 or key==ord('q'):
#         break;
#     if key ==ord('n'):
#         image = remplirNoir(image)
#         dessin = False
#         cv2.imshow('image originale',image)
#     if key ==ord('c'):
#         image = remplirCouleur(image)
#         dessin = False
#         cv2.imshow('image originale',image)

# print('arrêt du programme par l\'utilisateur')
# cv2.destroyWindow('image originale')