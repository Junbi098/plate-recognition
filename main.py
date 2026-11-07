import cv2
import easyocr

chemin = "images/voiture.jfif"
image = cv2.imread(chemin)

if image is None:
    print("Erreur lors du chargement de l'image.")
else:
    print("Dimensions de l'image : ", image.shape)
    x, y, largeur, hauteur = cv2.selectROI("Selectionne la plaque", image)
    cv2.destroyAllWindows()
    print("Zone de la plaque :", x, y, largeur, hauteur)

    if largeur > 0 and hauteur > 0:
        plaque = image[y:y + hauteur, x:x + largeur]
        cv2.imshow("Plaque decoupee", plaque)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        lecteur = easyocr.Reader(["en"], gpu=False)
        textes = lecteur.readtext(plaque, detail=0)
        print(" Texte lu sur la plaque : ", textes)
