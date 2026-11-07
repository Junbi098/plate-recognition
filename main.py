import cv2
import easyocr

chemin = "images/voiture.jfif"
image = cv2.imread(chemin)

if image is None:
    print("Erreur lors du chargement de l'image :", chemin)
else:
    print("Dimensions de l'image :", image.shape)

    gris = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bords = cv2.Canny(gris, 50, 150)
    contours, _ = cv2.findContours(bords, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    print("Nombre de contours trouvés :", len(contours))

    # Garder les rectangles dont la forme et la taille conviennent à cet essai.
    candidats = []
    largeur_max = 0.4 * image.shape[1]

    for contour in contours:
        x, y, largeur, hauteur = cv2.boundingRect(contour)
        rapport = largeur / hauteur

        if 2.5 <= rapport <= 6 and 60 <= largeur <= largeur_max and hauteur >= 15:
            candidats.append((x, y, largeur, hauteur))

    print("Nombre de zones candidates :", len(candidats))

    # Dessiner sur une copie pour préserver les pixels utilisés par EasyOCR.
    apercu = image.copy()
    for x, y, largeur, hauteur in candidats:
        coin_fin = (x + largeur - 1, y + hauteur - 1)
        cv2.rectangle(apercu, (x, y), coin_fin, (0, 255, 0), 2)

    print("Aperçu des candidats : appuie sur Espace dans la fenêtre pour continuer.")
    cv2.imshow("Zones candidates", apercu)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print("Lecture des zones candidates en cours...")

    # Lire chaque zone candidate avec le même lecteur.
    lecteur = easyocr.Reader(["en"], gpu=False)

    meilleur_score = -1.0
    meilleure_lecture = None

    for numero, (x, y, largeur, hauteur) in enumerate(candidats, start=1):
        zone = image[y:y + hauteur, x:x + largeur]
        resultats = lecteur.readtext(zone, detail=1)

        for _, texte, confiance in resultats:
            if confiance > meilleur_score:
                meilleur_score = confiance
                meilleure_lecture = (numero, texte)

    if meilleure_lecture is None:
        print("Aucun texte détecté dans les zones candidates.")
    else:
        numero, texte = meilleure_lecture
        x, y, largeur, hauteur = candidats[numero - 1]
        zone_retenue = image[y:y + hauteur, x:x + largeur]
        zone_agrandie = cv2.resize(zone_retenue, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        textes_agrandis = lecteur.readtext(zone_agrandie, detail=0)
        print("Lecture après agrandissement :", textes_agrandis)
        
        for texte_lu in textes_agrandis:
            immatriculation = "".join(c for c in texte_lu.upper() if c.isalnum())
            print("Immatriculation normalisée :", immatriculation)

        cv2.imshow("Zone retenue par le programme", zone_retenue)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        print(f"Lecture retenue : candidat {numero} | {texte!r} | score = {meilleur_score:.3f}")