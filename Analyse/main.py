import cv2
import numpy as np
import sys
import matplotlib.pyplot as plt

# création de l'image à partir d'un fichier
img = cv2.imread("./images/startImage.jpg")


# on applique un filtre passe-bas pour lisser l'image
img = cv2.GaussianBlur(img, (5, 5), 0)

# filtre median
img = cv2.medianBlur(img, 9)

# je veux que les couleurs soient plus saturées
# pour que les couleurs dominantes soient plus visibles
img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# on reconvertit l'image en BGR

img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)


# on convertit l'image en niveaux de gris
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Calcule l'histogramme des couleurs
hist = cv2.calcHist([img], [0], None, [256], [0, 256])

# Trouve l'intensité de gris qui a la fréquence la plus élevée dans l'histogramme
dominant_color = np.argmax(hist)

# Affiche la couleur dominante
print(f"Couleur dominante : {dominant_color}")

# # Affiche l'histogramme
# plt.plot(hist)
# plt.show()

cv2.imshow("Image", img)
cv2.waitKey(0)

# grace à l'intensité de gris on va pouvoir définir un seuil
# pour la binarisation de l'image
# appliquer une méthode de seuillage adaptatif
# thresh = cv2.adaptiveThreshold(
#     img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2
# )

# cv2.imshow("Image", thresh)
# cv2.waitKey(0)

tolerance = 12

# on parcourt l'image
for i in range(img.shape[0]):
    for j in range(img.shape[1]):
        # si la couleur est trop proche de la couleur dominante
        # on la considère comme étant la couleur dominante
        if abs(img[i, j] - dominant_color) < tolerance:
            # on chnage sur img la couleur de l'image
            img[i, j] = 255
            # on change sur img la couleur de l'image
        else:
            img[i, j] = 0


kernel = np.ones((6, 6), np.uint8)

# on applique une fermeture
closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
cv2.imshow("Imageclose", closing)

# on applique une ouverture
opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
cv2.imshow("Imageopen", opening)

img = cv2.bitwise_and(
    img, opening
)  # on applique un ET logique entre les deux images pour ne garder que les pixels qui sont à 1 dans les deux images


# affiche l'image
cv2.imshow("ImageFinale", img)

# attend une touche
cv2.waitKey(0)


key = cv2.waitKey(0) & 0x0FF
if key == 27:
    print("arrêt du programme par l'utilisateur")
    cv2.destroyAllWindows()
    sys.exit(0)
