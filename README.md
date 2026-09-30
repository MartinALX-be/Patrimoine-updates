# Patrimoine — téléchargement et mises à jour

Suivi et gestion de patrimoine pour Windows : actions, ETF, épargne, immobilier, crédits,
fiscalité belge. Tes données restent sur ton ordinateur.

## Installer ou mettre à jour

➡️ **[Patrimoine-Setup.exe](https://github.com/MartinALX-be/Patrimoine-updates/raw/main/Patrimoine-Setup.exe)** (~40 Mo)

- Lance simplement le Setup : il met à jour une version déjà installée, **sans la désinstaller**.
  Tes données (dans `%APPDATA%\Patrimoine`) sont conservées.
- À partir de la version 1.2.3, l'application se met à jour **toute seule** : bouton
  « Mettre à jour maintenant » dans la bannière « Nouvelle version disponible ».
- Windows peut afficher un avertissement SmartScreen (application non encore reconnue) :
  « Informations complémentaires » → « Exécuter quand même ».

## Contenu de ce dépôt

Ce dépôt sert uniquement au canal de mise à jour lu par l'application installée :

| Fichier | Rôle |
|---|---|
| `VERSION.txt` | Dernière version publiée (annonce « Nouvelle version disponible ») |
| `update.json` | Mise à jour en un clic : fichier, empreinte SHA-256, taille |
| `baremes.json` | Barèmes fiscaux officiels (coefficient du revenu cadastral, exonérations, plafonds) |
| `Patrimoine-Setup.exe` | Installateur de la dernière version |
