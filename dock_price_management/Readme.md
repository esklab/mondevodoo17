# 📘 Documentation Module : Dock Price Management

## 📝 Description Générale du module
Le module **Dock Price Management** vous permet de gérer efficacement les **prix d'acconage et relevage**, ainsi que la gestion structurée et sécurisée des univers de commandes sur Odoo.

Ce module offre :
- Gestion complète des prix (ajout, édition, consultation, suppression).
- Définition et configuration d'univers de commandes (aérien, terrestre, maritime).
- Sécurisation fine des accès utilisateurs.
- Intégration étroite avec le flux standard `sale.order` pour un contrôle renforcé.

## 📌 Fonctionnalités détaillées

### 🔸 Gestion des Prix
- Créez et modifiez les prix associés à vos prestations.
- Historisation des modifications appliquées aux prix.
- Contrôle d'accès précis selon droits utilisateurs définis.

### 🔸 Gestion des Univers de Commandes
- Définissez différents univers de commande (Aérien, Terrestre, Maritime, ...).
- Liez chaque univers à des catégories d'articles spécifiques.
- Assurez-vous que vos utilisateurs ne choisissent que les articles autorisés selon l'univers sélectionné directement depuis les commandes.

### 🔸 Intégration aux Commandes ventes (`sale.order`)
- Sélection claire obligatoire de l'univers dès la création des devis ou commandes.
- Filtrage dynamique automatique lors du choix des articles selon l'univers sélectionné :
    - 🟢 Évite les erreurs de sélection articles hors-univers.
    - ⚠️ Affiche clairement une alerte lorsque sélection d'article non autorisé tente d'être validée.

## ⚙️ Configuration & Installation

### 🔧 Installation Classique
- **Copier** le dossier `dock_price_management` vers votre répertoire addons Odoo.
- Relancez Odoo et activez en mode développeur.
- Installez (`Dock Price Management`) depuis : **Applications > Dock Price Management > Installer**.

### 📍 Dépendances obligatoires :
- Module standard : `sale_management`
- Module Odoo standard : `product`
- Module Odoo standard : `base`

## 🛠 Modèles introduits par ce module

| Modèles ajoutés | Description |
| --- | --- |
| `dock.price` | Gestion principale des prix |
| `dock.price.history` | Historique de tous les mouvements de prix |
| `order.universe` | Univers de commandes liés aux catégories articles |

| Modèles étendus | Description des ajouts |
| --- | --- |
| `product.category` | Liaison catégories articles aux univers |
| `sale.order` | Intègre l'univers directement dans la commande |
| `sale.order.line` | Applique filtre dynamique sur articles |

## 🔑 Gestion des droits et sécurité

Le module offre trois groupes de sécurité clairement définis afin d’assurer la confidentialité et l'intégrité des données :

| Groupe | Accès Lecture | Modification | Création | Suppression | Administration |
| --- | --- | --- | --- | --- | --- |
| Utilisateur prix (Lecteur simple) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Gestionnaire des prix | ✅ | ✅ | ✅ | ✅ | ❌ |
| Administrateur | ✅ | ✅ | ✅ | ✅ | ✅ |

Le module permet également aux utilisateurs du module "Ventes" (groupe standard `sale_management`) de consulter sans modification tous les univers de commande afin d'assurer un workflow opérationnel fluide :

| Groupe Module Ventes Standard | Accès Lecture Univers | Modification Univers |
| --- | --- | --- |
| Vendeur | ✅ Oui | ❌ Non |
| Vendeur complet | ✅ Oui | ❌ Non |
| Responsable Ventes | ✅ Oui | ❌ Non |

## 🖥 Écran et Interfaces clés (Menus principaux)

Après installation, le module introduit des menus spécifiques dans votre interface utilisateur Odoo :
- **Gestion des Prix**
    - Prix Acconage & Relevage : Lister et gérer les tarifs.
    - Configuration Univers : Définissez vos univers et catégories associées.

- **Devis & Commandes (extension du modèle Ventes)**
    - Formulaire Détail commande : sélection obligatoire de l'univers et contrôle automatique des produits autorisés.

## 🚩 Alertes & Notifications utilisateurs

En cas de sélection d'article hors-univers à la ligne commande :
- Une alerte claire et automatique est affichée à l'utilisateur.
- Impossibilité de sauvegarder un produit hors-univers dans la commande.

> ⚠️ **Exemple d’alerte affichée :**  
> **Titre :** Produit Invalide  
> **Message :** _Ce produit ne fait pas partie de l'univers de commande sélectionné._

## 🤖 Développement Technique complémentaire

- Type : **Module application Odoo**
- Version spécifique : **Développé pour Odoo 17 & versions supérieures**
- Langage de développement : **Python 3.13.2**
- Frontend Framework : Odoo Standard XML & JavaScript.

## 🔐 Fichiers de sécurité inclus

- `security/dock_price_security.xml` (définition des groupes & catégories sécurité)
- `security/ir.model.access.csv` (droits précis des accès aux modèles)

## 📦 Structure du Module

```plaintext
dock_price_management/
├── __init__.py
├── __manifest__.py
├── controllers/
├── models/
│   ├── __init__.py
│   ├── dock_price.py                # Modèle principal prix
│   ├── order_universe.py            # Modèle univers commande
│   ├── product_category.py          # Extension catégorie produit
│   └── sale_order.py                # Extension commandes ventes
│
├── security/
│   ├── dock_price_security.xml      # Définitions des groupes sécurité
│   └── ir.model.access.csv          # Droits d'accès précis
│
└── views/
    ├── dock_price_menu.xml          # Définition Menus
    ├── dock_price_views.xml         # Vues Gestion Prix
    ├── order_universe_views.xml     # Vues Univers de Commande
    ├── product_category_views.xml   # Extension vues catégorie produit
    └── sale_order_views.xml         # Extension formulaire vente
