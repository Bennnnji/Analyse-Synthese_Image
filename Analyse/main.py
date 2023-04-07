import cv2
import numpy as np
import sys
import matplotlib.pyplot as plt
import os
import glob


# création de l'image à partir d'un fichier
img = cv2.imread("./images/startImage.jpg")

cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

list_widePieces = []
list_widePieces_mask = []
list_contours_sorted = []
list_cutPieces = []
list_cutPieces_mask = []


# vide les dossier
def clearFolder(filename):
    files = glob.glob(filename)
    for f in files:
        os.remove(f)


clearFolder("./Mask/cutMask/*")
clearFolder("./Mask/wideMask/*")
clearFolder("./images/cutPieces/*")
clearFolder("./images/widePieces/*")


def sort_contours(contours, img, tolerance_ratio=0.1):
    # Tri des contours par ordre croissant en fonction de leur position en Y, puis en X
    contours_sorted = sorted(
        contours, key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0])
    )

    # Calcul de la tolérance verticale pour déterminer si deux contours sont sur la même ligne
    tolerance = int(img.shape[0] * tolerance_ratio)

    # Initialisation des lignes et de la première ligne avec le premier contour
    lines = []
    current_line = [contours_sorted[0]]
    current_line_y = cv2.boundingRect(contours_sorted[0])[1]

    # Parcours des contours triés et regroupement par ligne
    for contour in contours_sorted[1:]:
        y = cv2.boundingRect(contour)[1]
        if abs(y - current_line_y) <= tolerance:  # Si le contour est sur la même ligne
            current_line.append(contour)
        else:  # Si le contour est sur une nouvelle ligne
            lines.append(current_line)
            current_line = [contour]
            current_line_y = y

    # Ajout de la dernière ligne de contours
    lines.append(current_line)

    # Tri des contours à l'intérieur de chaque ligne par ordre croissant en fonction de leur position en X
    sorted_lines = [
        sorted(line, key=lambda c: cv2.boundingRect(c)[0]) for line in lines
    ]

    # Fusion des contours triés par ligne pour obtenir la liste finale des contours triés par lignes et colonnes
    sorted_contours = [contour for line in sorted_lines for contour in line]

    return sorted_contours


def Test_5(img, tolerance, tolH=0, tolS=0, tolV=0):
    img = cv2.medianBlur(img, 5)

    # enleve 5 pixels de chaque coté
    img = img[5:-5, 5:-5]

    # on convertit l'image en LAB
    img_lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)

    # Calcule l'histogramme LAB
    hist_l = cv2.calcHist([img_lab], [0], None, [256], [0, 256])
    hist_a = cv2.calcHist([img_lab], [1], None, [256], [0, 256])
    hist_b = cv2.calcHist([img_lab], [2], None, [256], [0, 256])

    # on récupère la couleur dominante
    dominant_color_l = np.argmax(hist_l)
    dominant_color_a = np.argmax(hist_a)
    dominant_color_b = np.argmax(hist_b)

    print("dominant_color : ", dominant_color_a, dominant_color_b)

    # on parcourt l'image
    for i in range(img_lab.shape[0]):
        for j in range(img_lab.shape[1]):
            # si la couleur est trop proche de la couleur dominante
            # on la considère comme étant la couleur dominante
            if (
                abs(img_lab[i, j][1] - dominant_color_a) < tolerance + tolH
                and abs(img_lab[i, j][2] - dominant_color_b) < tolerance + tolS
                and abs(img_lab[i, j][0] - dominant_color_l) < tolerance + tolV
            ):
                img_lab[i, j] = 0
            else:
                img_lab[i, j] = 255
    # fermeture
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (6, 6))
    img_lab = cv2.morphologyEx(img_lab, cv2.MORPH_CLOSE, kernel)

    # # ouverture
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (4, 4))
    img_lab = cv2.morphologyEx(img_lab, cv2.MORPH_OPEN, kernel)

    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (6, 6))
    img_lab = cv2.morphologyEx(img_lab, cv2.MORPH_CLOSE, kernel)

    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (8, 8))
    img_lab = cv2.morphologyEx(img_lab, cv2.MORPH_OPEN, kernel)

    # # dilate
    kernel = np.ones((1, 1), np.uint8)
    img_lab = cv2.dilate(img_lab, kernel, iterations=1)

    kernel = np.ones((1, 1), np.uint8)
    img_lab = cv2.erode(img_lab, kernel, iterations=1)

    img_labL = img_lab[:, :, 0]

    # # find contours
    contours, hierarchy = cv2.findContours(
        img_labL, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )

    # Regarde si les contours ont été trouvés
    if len(contours) > 0:
        print("Nombre de contours trouvés = " + str(len(contours)))

        contours = sort_contours(contours, img_labL)

        # enleve le dernier contour car c'est le logo
        contours = contours[:-1]

        # Créer une image vierge de la même taille que l'original
        img_pieces = np.zeros_like(img_labL)

        img_pieces = cv2.cvtColor(img_pieces, cv2.COLOR_GRAY2RGB)

        for i, cnt in enumerate(contours):
            # Remplir la pièce avec une nuance de gris différente
            new_col_R = np.random.randint(0, 255)
            new_col_G = np.random.randint(0, 255)
            new_col_B = np.random.randint(0, 255)
            cv2.drawContours(
                img_pieces, contours, i, (new_col_R, new_col_G, new_col_B), -1
            )

            x, y, w, h = cv2.boundingRect(cnt)
            center_x, center_y = x + w // 2, y + h // 2

            # Dessiner l'indice de la pièce au centre
            cv2.putText(
                img_pieces,
                str(i),
                (center_x, center_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.1,  # Taille de la police
                (0, 0, 255),  # Couleur en BGR (rouge)
                2,  # Epaisseur de la ligne
            )

        cv2.imshow("Pièces de puzzle en couleurs", img_pieces)
        cv2.waitKey(0)

        # avec chaque contour, on va créer un masque pour isoler la pièce
        # et on va la stocker dans une liste

        for i, cnt in enumerate(contours):
            # Créer un masque vide
            mask = np.zeros_like(img_labL)

            # Dessiner le contour sur le masque
            cv2.drawContours(mask, contours, i, 255, -1)

            # Extraire la pièce de l'image originale
            piece = cv2.bitwise_and(img_labL, img_labL, mask=mask)

            list_widePieces_mask.append(piece)

            x, y, w, h = cv2.boundingRect(cnt)

            # Extraire la pièce de l'image originale
            piece = piece[y : y + h, x : x + w]

            list_cutPieces_mask.append(piece)

        # on applique les masques sur l'image originale img
        for i, piece in enumerate(list_widePieces_mask):
            widePiece = cv2.bitwise_and(img, img, mask=piece)
            list_widePieces.append(widePiece)

            x, y, w, h = cv2.boundingRect(contours[i])

            cutPiece = img[y : y + h, x : x + w]
            list_cutPieces.append(cutPiece)

    else:
        print("No puzzle pieces found")

    return img_lab


# print("Test 1")
# Test_1(img)

# print("Test 2")
# Test_2(img)

# print("Test 3")
# Test_3(img)

# print("Test 4")
# Test_4(img)

print("Test 5")
Test_5(img, 12, 4, 5, 10)


def saveInFile(list, path):
    for i, piece in enumerate(list):
        cv2.imwrite(path + str(i) + ".jpg", piece)


saveInFile(list_cutPieces, "images/cutPieces/")
saveInFile(list_widePieces, "images/widePieces/")
saveInFile(list_cutPieces_mask, "Mask/cutMask/")
saveInFile(list_widePieces_mask, "Mask/wideMask/")


key = cv2.waitKey(0) & 0x0FF
if key == 27:
    print("arrêt du programme par l'utilisateur")
    cv2.destroyAllWindows()
    sys.exit(0)
