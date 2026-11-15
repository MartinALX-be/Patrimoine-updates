# Patrimoine — téléchargement et mises à jour

Suivi et gestion de patrimoine pour Windows : actions, ETF, épargne, immobilier, crédits,
fiscalité belge.

> **🔒 100 % local.** Tes données ne quittent jamais ton ordinateur : pas de compte, pas de
> serveur qui lit tes avoirs. L'application travaille hors ligne et ne consulte que les barèmes
> publics et les cours. Tes sauvegardes restent dans tes fichiers, à toi.

> **🇧🇪 Prêt pour la taxe sur les plus-values 2026.** Valeur de référence au 31/12/2025,
> exonération de 10 000 € par personne (reportable jusqu'à 15 000 € sur cinq ans), part Reynders
> exclue de la base : l'application calcule la taxe de 10 % à ta place et tient tes codes de
> déclaration à jour.

## Installer ou mettre à jour

➡️ **[Patrimoine-Setup.exe](https://github.com/MartinALX-be/Patrimoine-updates/raw/main/Patrimoine-Setup.exe)** (~40 Mo)

- Lance simplement le Setup : il met à jour une version déjà installée, **sans la désinstaller**.
  Tes données (dans `%APPDATA%\Patrimoine`) sont conservées.
- À partir de la version 1.2.3, l'application se met à jour **toute seule** : bouton
  « Mettre à jour maintenant » dans la bannière « Nouvelle version disponible ».
- Windows peut afficher un avertissement SmartScreen (application non encore reconnue) :
  « Informations complémentaires » → « Exécuter quand même ».

## Application mobile (Android)

➡️ **[Patrimoine-mobile.apk](https://github.com/MartinALX-be/Patrimoine-updates/raw/main/Patrimoine-mobile.apk)** (~3 Mo · version 2.0 · français, néerlandais, anglais)

Ton patrimoine dans la poche, en consultation : valeur à jour avec les cours en direct,
objectifs, revenus, marchés, même hors ligne. Aucun compte, aucun serveur : tes positions
arrivent du PC par un transfert **chiffré de bout en bout**.

1. Ouvre le lien sur le téléphone (ou copie l'APK dessus), puis ouvre le fichier téléchargé.
2. Android demande d'autoriser l'installation d'applications inconnues pour ton navigateur ou
   l'appli Fichiers : accepte, puis **Installer**. Si Play Protect affiche « Application non
   vérifiée » : **Installer quand même**.
3. Dans l'app : **Synchroniser avec le PC**. Sur le PC (Patrimoine 1.18 ou plus récent) :
   *Paramètres → Sauvegardes & données → Envoyer vers le téléphone*, puis scanne le QR code
   animé. Pour essayer d'abord : **Découvrir avec un exemple**.

Android 5.1 ou plus récent. Une nouvelle version s'installe par-dessus l'ancienne, sans perte
de données. Pas encore disponible sur iPhone.
Empreinte SHA-256 : `6f06ea3848c372a6d537313dae8f737e16412cce64c12688bc6431e085de546c`

## Gratuit ou Patrimoine Pro ?

Chaque installation démarre avec **14 jours d'essai de Patrimoine Pro**. Ensuite :

| | Gratuit | ⭐ Pro (abonnement annuel) |
|---|---|---|
| Prix (TVA comprise) | 0 € | **39 € / an** — offre de lancement : 29 € la 1ʳᵉ année |
| Actifs suivis | 8 par portefeuille | Illimités |
| Portefeuille, ventes, liquidités, marchés, calendrier, budget, watchlist, alertes, DCA | ✓ | ✓ |
| Fiscalité belge : précompte, plus-values 2026, TOB, codes de déclaration, exports et PDF fiscal | — | ✓ |
| Analyse & diagnostic, risque, corrélations, analyse de frais, comparateur ETF | — | ✓ |
| Crédits détaillés, projections & simulations, rapport PDF | — | ✓ |
| Barèmes fiscaux officiels mis à jour automatiquement | — | ✓ |

Pas encore prêt à saisir tes données ? Le bouton **« Voir une démo complète »** ouvre un
portefeuille d'exemple, dans une base séparée.

## Contenu de ce dépôt

Ce dépôt sert uniquement au canal de mise à jour lu par l'application installée :

| Fichier | Rôle |
|---|---|
| `VERSION.txt` | Dernière version publiée (annonce « Nouvelle version disponible ») |
| `update.json` | Mise à jour en un clic : fichier, empreinte SHA-256, taille |
| `baremes.json` | Barèmes fiscaux officiels (coefficient du revenu cadastral, exonérations, plafonds) |
| `Patrimoine-Setup.exe` | Installateur de la dernière version |
| `Patrimoine-mobile.apk` | Application mobile Android (consultation, synchronisation chiffrée avec le PC) |
