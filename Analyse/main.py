import cv2
import numpy as np
import sys
import matplotlib.pyplot as plt


# création de l'image à partir d'un fichier
img = cv2.imread("./images/startImage.jpg")

cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

if not cv2.cuda.getCudaEnabledDeviceCount():
    print("Aucun GPU compatible CUDA trouvé. Utilisez la version CPU d'OpenCV.")
    exit(0)

gpu_image = cv2.cuda_GpuMat()
gpu_image.upload(img)


def Test_1(img):
    print("Lancement du test 1 : ...")
    # on applique un filtre passe-bas pour lisser l'image
    img = cv2.GaussianBlur(img, (5, 5), 0)
    # on convertit l'image en niveaux de gris
    img_grey = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Calcule l'histogramme des couleurs
    hist = cv2.calcHist([img_grey], [0], None, [256], [0, 256])

    # Trouve l'intensité de gris qui a la fréquence la plus élevée dans l'histogramme
    dominant_color = np.argmax(hist)

    print("dominant_color : ", dominant_color)

    tolerance = 12

    # on parcourt l'image
    for i in range(img_grey.shape[0]):
        for j in range(img_grey.shape[1]):
            # si la couleur est trop proche de la couleur dominante
            # on la considère comme étant la couleur dominante
            if abs(img_grey[i, j] - dominant_color) < tolerance:
                # on chnage sur img la couleur de l'image
                img_grey[i, j] = 255
                # on change sur img la couleur de l'image
            else:
                img_grey[i, j] = 0

    # on affiche l'image
    cv2.imshow("Step2", img_grey)
    cv2.waitKey(0)

    # on affiche l'image
    cv2.imshow("ImageFinale", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def Test_2(img):
    # Appliquer un filtre moyen
    kernel_size = 15
    mean_kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size**2)
    img_mean = cv2.filter2D(img, -1, mean_kernel)

    # Appliquer un filtre gaussien
    kernel_size = 5
    sigma = 1
    img_gaussian = cv2.GaussianBlur(img, (kernel_size, kernel_size), sigma)

    img = cv2.bitwise_or(img_mean, img_gaussian)

    img_grey = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    hist = cv2.calcHist([img_grey], [0], None, [256], [0, 256])

    # Trouve l'intensité de gris qui a la fréquence la plus élevée dans l'histogramme
    dominant_color = np.argmax(hist)

    print("dominant_color : ", dominant_color)

    tolerance = 12

    # on parcourt l'image
    for i in range(img_grey.shape[0]):
        for j in range(img_grey.shape[1]):
            # si la couleur est trop proche de la couleur dominante
            # on la considère comme étant la couleur dominante
            if abs(img_grey[i, j] - dominant_color) < tolerance:
                # on chnage sur img la couleur de l'image
                img_grey[i, j] = 255
                # on change sur img la couleur de l'image
            else:
                img_grey[i, j] = 0

    # on affiche l'image
    cv2.imshow("Step2", img_grey)
    cv2.waitKey(0)

    kernel = np.ones((6, 6), np.uint8)

    # on applique une fermeture
    closing = cv2.morphologyEx(img_grey, cv2.MORPH_CLOSE, kernel)

    # on applique une ouverture
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)

    # on applique un ET logique entre les deux images pour ne garder que les pixels qui sont à 1 dans les deux images
    img_grey = cv2.bitwise_and(img_grey, opening)

    cv2.imshow("Image_après_ET", img_grey)
    cv2.waitKey(0)
    kernel = np.ones((2, 2), np.uint8)
    img_grey = cv2.morphologyEx(img_grey, cv2.MORPH_OPEN, kernel)

    cv2.imshow("Image_après_fermeture", img_grey)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def Test_3(img):
    print("Lancement du test 3 : ...")
    img = cv2.GaussianBlur(img, (5, 5), 3)

    # convertir l'image en niveaux de gris avec un seuillage adaptatif
    gray = cv2.adaptiveThreshold(
        cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,
        2,
    )

    cv2.imshow("Image_after_seuillage_auto", gray)
    cv2.waitKey(0)

    # appliquer une opération de fermeture pour combler les petits trous
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    closed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

    cv2.imshow("Image_after_CLOSE", closed)
    cv2.waitKey(0)

    # appliquer une opération d'ouverture pour combler les petits trous
    opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel)

    cv2.imshow("Image_after_OPEN", opened)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def Test_4(img):
    img = cv2.GaussianBlur(img, (5, 5), 3)

    img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    h, s, v = cv2.split(img)

    ret_h, th_h = cv2.threshold(h, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    ret_s, th_s = cv2.threshold(s, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    ret_v, th_v = cv2.threshold(v, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # cv2.imshow("Image_after_seuillage_auto_h", th_h)
    # cv2.imshow("Image_after_seuillage_auto_s", th_s)
    # cv2.imshow("Image_after_seuillage_auto_v", th_v)
    # cv2.waitKey(0)

    cv2.bitwise_and(th_h, th_s, th_h)
    cv2.bitwise_and(th_h, th_v, th_h)
    cv2.imshow("Image_after_seuillage_auto_hsv", th_h)
    cv2.waitKey(0)

    kernel = np.ones((8, 8), np.uint8)
    th = cv2.morphologyEx(th_h, cv2.MORPH_OPEN, kernel)

    cv2.imshow("Image_after_seuillage_auto_hsv", th)
    cv2.waitKey(0)

    # cannay
    edges = cv2.Canny(th, 100, 200)
    cv2.imshow("Image_after_seuillage_auto_hsv", edges)
    cv2.waitKey(0)

    # dilate
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=1)
    cv2.imshow("Image_after_seuillage_auto_hsv", dilated)
    cv2.waitKey(0)

    # find contours
    contours, hierarchy = cv2.findContours(
        dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )

    # draw contours
    img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)
    cv2.drawContours(img, contours, -1, (0, 255, 0), 3)

    cv2.imshow("Image_after_seuillage_auto_hsv", img)
    cv2.waitKey(0)


def Test_5(img, tolerance):
    img = cv2.medianBlur(img, 5)
    # on convertit l'image en niveaux de gris
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
                abs(img_lab[i, j][1] - dominant_color_a) < tolerance
                and abs(img_lab[i, j][2] - dominant_color_b) < tolerance
                and abs(img_lab[i, j][0] - dominant_color_l) < tolerance
            ):
                img_lab[i, j] = 0
            else:
                img_lab[i, j] = 255

    # fermeture
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
    img_lab = cv2.morphologyEx(img_lab, cv2.MORPH_CLOSE, kernel)

    # on affiche l'image
    cv2.imshow("Step2", img_lab)
    cv2.waitKey(0)

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
cv2.cuda(Test_5(gpu_image, 20))


key = cv2.waitKey(0) & 0x0FF
if key == 27:
    print("arrêt du programme par l'utilisateur")
    cv2.destroyAllWindows()
    sys.exit(0)
