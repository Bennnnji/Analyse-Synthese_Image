import cv2
import numpy as np

# Charger l'image bruitée
img = cv2.imread('image.png')

# Appliquer le filtre gaussien avec un noyau de taille 5x5 et une variance de 1.5
img_filtre = cv2.GaussianBlur(img, (5, 5), 1.5)

# Afficher les deux images côte à côte pour comparer
cv2.imshow('Image bruitee', img)
cv2.imshow('Image filtree', img_filtre)
cv2.waitKey(0)
cv2.destroyAllWindows()