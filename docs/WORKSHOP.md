# Atelier "Vibe Coding" — 45 minutes avec 30 jeunes trésoriers

> Objectif: leur faire **vivre** la force de l'IA pour développer un outil
> trésorerie utile, en partant du repo `Cash-flow-forecasting` que nous avons
> déjà construit. À la fin, ils doivent avoir vu **leur propre feature**
> arriver dans l'app — pas une démo regardée passivement.

Format: **6 équipes × 5 personnes**, chacune ajoute une mini-feature à l'app
existante en parallèle. Un facilitateur tournant aide aux blocages. Restitution
finale en 8 minutes.

---

## 1. Pourquoi partir d'un repo existant (et pas d'une page blanche)

En 45 minutes, partir de zéro, c'est mort. L'app `Helios Industries` qu'on a
déjà:

- a 24 mois de données réalistes (€38M d'AR, €13M d'AP, 8 comptes bancaires
  multi-devises, scénarios stress / base / optimiste calibrés),
- a 6 pages Streamlit qui marchent,
- a une couche `src/` (loader / metrics / forecasting) propre que les équipes
  vont étendre,
- est documentée (README, METHODOLOGY, DATA_MODEL, USER_GUIDE,
  PROJECT_REPORT).

Les jeunes trésoriers vont **reconnaître les KPIs** (DSO, DPO, runway, RCF,
buffer, aging, MAPE) — ça abaisse la barrière de domaine. Ils peuvent se
concentrer sur le prompt, pas sur la finance.

---

## 2. Pré-requis (à boucler J-7 → J-1)

### J-7

- Confirmer le dimensionnement: **6 postes** prêts, projecteur, wifi solide.
- Réserver 6 accès Claude Code (ou claude.ai) — un par équipe. Vérifier les
  quotas en cumul (30 personnes ≠ 30 sessions simultanées sur un même compte
  → risque de throttling).
- Préparer un repo "starter" forké de celui-ci, branche `workshop/` avec
  les données déjà générées et la baseline figée.

### J-1

- Sur chaque poste:
  - Python 3.11, repo cloné, `pip install -r requirements.txt` fait,
  - `python data/generate_data.py` exécuté (les CSV sont présents),
  - `streamlit run app.py` testé et fonctionnel,
  - Claude Code lancé dans le bon dossier, profil pré-loggé,
  - Un **terminal** et un **navigateur** ouverts côte à côte.

Critère d'acceptation J-1: **chaque poste affiche le dashboard Helios sans
erreur en moins de 30 secondes après ouverture**.

### Matériel pour chaque équipe (kit papier)

- 1 fiche défi (au tirage, voir §6),
- 1 fiche "rôles" (1 trésorier / 1 prompt-writer / 1 opérateur / 1 QA / 1
  pitcher — voir §5),
- 1 cookbook de prompts (3 exemples, voir §7),
- Le data model en 1 page (extrait de `docs/DATA_MODEL.md`).

---

## 3. Déroulé minute par minute

| Minute | Bloc | Qui parle | Ce qui se passe |
|--------|------|-----------|------------------|
| 00–05 | **Cadrage** | Facilitateur principal | Pitch de 5 minutes: "voici ce qu'on a déjà, voici ce que vous allez ajouter, voici la règle du jeu." |
| 05–10 | **Demo live d'un prompt** | Facilitateur | En public, face caméra: il ajoute un export CSV de la table d'aging avec un prompt unique. L'objectif est de **dédramatiser** — montrer qu'on échoue parfois et qu'on itère. |
| 10–12 | **Tirage des défis** | Animateur secondaire | Chaque équipe tire 1 carte parmi les 8. La carte précise: l'objectif business, le fichier à modifier, le critère d'acceptation. |
| 12–35 | **Construction en parallèle** | Les 6 équipes | 23 minutes nettes pour livrer. Les 2 facilitateurs tournent: 4 minutes par équipe en moyenne. Ils débloquent, ils ne codent pas à la place. |
| 35–43 | **Restitution** | 1 pitcher / équipe × 80 secondes | Chaque pitcher montre l'écran, dit *"on voulait répondre à X, voici la feature, voici la limite"*. |
| 43–45 | **Débrief & vote** | Facilitateur principal | Vote au pouce levé pour la feature la plus utile. Annonce de qui la mergera dans le repo principal. |

**Discipline temporelle**: une horloge de comptage à rebours visible de toute
la salle. À 35 minutes, on coupe la construction même si une équipe n'a pas
fini — on apprend autant d'un échec partagé.

---

## 4. Le pitch d'ouverture (5 minutes — script)

> *"Bonjour à tous. En tête de ce repo: une appli de cash-flow forecasting
> pour Helios Industries — un industriel fictif, 80M€ de CA, 12 clients, 8
> comptes bancaires en EUR/USD/GBP. Vous avez devant vous: un dashboard
> exécutif, un forecast 13 semaines, des scénarios stress, une analyse de
> variance. Tout ça a été codé en **2 heures** par une IA, sous le contrôle
> d'un humain qui a précisé ce qu'il voulait, vérifié les chiffres, et
> arbitré quand c'était parti dans le mur."*
>
> *"Aujourd'hui, vous êtes l'humain qui pilote. Pendant 25 minutes, vous allez
> ajouter votre propre feature à cette app. Pas en codant — en **décrivant**
> ce que vous voulez. C'est ça, le vibe coding: vous restez le métier,
> l'IA fait la plomberie."*
>
> *"Trois règles:*
> *1. Le prompt précise toujours: l'objectif business, le fichier à modifier,
>    le résultat attendu. Pas de 'fais une feature de risk management'.*
> *2. Vous lisez le diff avant d'accepter. Toujours. L'IA a tort 1 fois sur 5.*
> *3. Si vous bloquez plus de 4 minutes sur une erreur, vous appelez un
>    facilitateur. On n'est pas là pour devenir devs."*

---

## 5. Rôles dans chaque équipe de 5

L'équipe est **un mini-département trésorerie qui consomme une livraison IT**.

| Rôle | Mission | Profil idéal |
|------|---------|--------------|
| **Trésorier (PO)** | Articule le besoin métier en 2 phrases. Décide ce qui est in/out de scope. | Le plus expérimenté de l'équipe. |
| **Prompt-writer** | Traduit le besoin en prompt précis (objectif, fichier, format de sortie). Ré-écrit après chaque échec. | Quelqu'un à l'aise à l'écrit. |
| **Opérateur** | Pilote Claude Code / claude.ai. Lance les prompts, montre les diffs, accepte ou rejette. | Quelqu'un qui n'a pas peur d'un terminal. |
| **QA** | Recharge l'app après chaque change, vérifie que rien n'est cassé, valide le résultat sur les vraies données du repo. | Œil critique. |
| **Pitcher** | Note ce qui marche, ce qui foire. À 35 minutes, prépare 80 secondes de restitution. | Bon communicant. |

Cette répartition est **clé**: elle évite que toute l'équipe regarde
l'opérateur taper. Chacun a un rôle.

---

## 6. Les 8 fiches défi

Tirage au sort: chaque carte tient sur une feuille A5. Modèle:

```
🎯 DÉFI #N — <titre>
─────────────────────────
OBJECTIF MÉTIER (2 phrases)
DONNÉES DISPONIBLES        (fichiers / colonnes pertinents)
LIVRABLE ATTENDU            (page / KPI / chart / export)
CRITÈRE D'ACCEPTATION       (un test simple à passer)
DIFFICULTÉ                  ⭐ / ⭐⭐ / ⭐⭐⭐
```

### Catalogue (calibrés pour 23 minutes)

#### #1 — Alerte dérive DSO ⭐
- **Objectif**: prévenir le credit-control quand le DSO mensuel dérape de plus
  de 5 jours vs cible.
- **Données**: `ar_invoices.csv` + `assumptions.json → drivers.dso_target_days`.
- **Livrable**: bandeau rouge sur le dashboard si DSO > cible+5j; vert sinon.
- **Acceptation**: le bandeau s'affiche sur les données actuelles.

#### #2 — Heatmap des encaissements à venir ⭐⭐
- **Objectif**: visualiser semaine × jour les receipts attendus pour les 4
  prochaines semaines.
- **Données**: `ar_invoices.csv` open + `expected_payment_date`.
- **Livrable**: heatmap calendaire sur la page Forecast.
- **Acceptation**: la cellule du jour J montre le bon EUR.

#### #3 — Simulateur M&A ⭐⭐
- **Objectif**: ajouter un slider "acquisition X M€ le YYYY-MM-DD" sur la
  page Forecast et voir l'impact sur la trajectoire.
- **Données**: forecast existant + nouveau line item.
- **Livrable**: slider montant + date picker, impact visible sur le
  closing balance.
- **Acceptation**: closing balance baisse exactement du montant choisi.

#### #4 — Cash pooling notionnel ⭐⭐⭐
- **Objectif**: simuler un sweep zero-balance sur les 4 comptes EUR — montrer
  le solde "groupé" vs solde par compte.
- **Données**: `bank_accounts.csv` + transactions par compte.
- **Livrable**: nouvelle page "Cash Pooling" avec toggle on/off.
- **Acceptation**: le total EUR consolidé est inchangé (juste re-réparti).

#### #5 — Détecteur d'anomalies sur frais bancaires ⭐⭐
- **Objectif**: flagger toute transaction `Bank Fees` > 1.5× la moyenne
  glissante 12 mois.
- **Données**: `cash_transactions.csv` (catégorie Bank Fees).
- **Livrable**: tableau des anomalies sur une nouvelle page "Anomalies".
- **Acceptation**: au moins 1 anomalie détectée sur l'historique synthétique.

#### #6 — Score de concentration client ⭐⭐
- **Objectif**: calculer l'indice de Herfindahl + part du top-3 sur les
  factures ouvertes.
- **Données**: `ar_invoices.csv` open.
- **Livrable**: 2 KPIs sur la page AR + alerte si top-3 > 40%.
- **Acceptation**: si on supprime artificiellement le plus gros client,
  l'indice baisse.

#### #7 — Leaderboard de précision du forecast ⭐⭐⭐
- **Objectif**: MAPE par catégorie sur les 6 derniers vintages hebdo.
- **Données**: variance déjà existante + extension par catégorie.
- **Livrable**: tableau ranké par MAPE croissant sur la page Variance.
- **Acceptation**: les 3 meilleures catégories sont celles attendues
  (Payroll, Rent, Debt Service — recurring fixes).

#### #8 — Export PDF du commentaire CFO ⭐
- **Objectif**: bouton "Export PDF" qui produit un 1-pager des KPIs +
  trajectoire base.
- **Données**: dashboard existant.
- **Livrable**: téléchargement déclenché par un bouton.
- **Acceptation**: le PDF contient les 4 KPIs principaux et la courbe 13
  semaines.

**Choix du panier**: 8 cartes pour 6 équipes — laisser 2 cartes en réserve
permet aux équipes les plus rapides de prendre une 2ème carte si elles ont
fini en avance.

---

## 7. Cookbook de prompts (à donner aux équipes)

Trois exemples concrets que les équipes peuvent copier-coller-adapter.

### Exemple A — Ajouter un KPI au dashboard

> *"Dans `app.py`, ajouter un KPI 'Concentration client (top 3)' qui calcule
> la part en EUR des 3 plus gros clients dans l'open AR total. Afficher en
> pourcentage avec une couleur rouge si > 40%, vert sinon. Le calcul doit
> utiliser `src.metrics` — créer une nouvelle fonction `top_n_concentration(ar, n=3)`
> qui retourne un float entre 0 et 1. Mettre à jour `docs/METHODOLOGY.md`
> pour documenter la nouvelle métrique."*

### Exemple B — Créer une nouvelle page Streamlit

> *"Créer une nouvelle page `pages/7_Anomalies.py` qui détecte les frais
> bancaires anormaux. Critère: une transaction de catégorie 'Bank Fees' est
> anormale si son montant absolu dépasse 1.5× la moyenne glissante 12 mois
> de la même catégorie. Afficher: un compteur d'anomalies, un tableau triable
> des transactions anormales, un chart timeline avec les anomalies en rouge.
> Utiliser `src.data_loader.load_transactions()`. Suivre le même style que
> `pages/3_Receivables_Payables.py`."*

### Exemple C — Modifier un comportement existant

> *"Dans `pages/1_Forecast.py`, ajouter un slider 'Acquisition stratégique'
> avec 2 inputs: un montant en M€ (de 0 à 50, step 1) et une date (entre
> aujourd'hui et la fin du horizon). Quand le montant est > 0, ajouter un
> outflow ponctuel à la date choisie dans la trajectoire de cash. Le min
> balance et le closing balance doivent refléter cet outflow. Ne pas casser
> le statistical overlay."*

### Anti-patterns à interdire

- ❌ *"Améliore le dashboard"* — pas d'objectif, pas de fichier, pas de critère.
- ❌ *"Refais l'app en React"* — hors scope, hors temps.
- ❌ *"Ajoute du Machine Learning"* — buzzword, pas de besoin métier.

---

## 8. Risques et plans B

| Risque | Probabilité | Plan B |
|--------|-------------|--------|
| Wifi tombe | Moyen | 4G partagé + repo en local, modèle accessible offline si Claude Code est déjà initié |
| Rate limit IA | Moyen-Élevé | Pré-charger 1 compte par équipe; étaler les exécutions de 30 sec entre les équipes au démarrage |
| Une équipe finit en 10 min | Bas | Tirer une 2e carte (réserve §6) ou aider une équipe en retard |
| Une équipe est perdue à 25 min | Élevé | Le facilitateur "fork" leur défi — version réduite (juste afficher la valeur, pas de chart) |
| Bug de génération de données | Bas | CSV figés sur le repo, ne pas relancer `generate_data.py` pendant la session |
| Quelqu'un veut "tout refaire" | Moyen | Recadrer: "incrément, pas refonte. Tu as 25 minutes." |

**Plan B catastrophique** (rien ne marche): le facilitateur fait les 6 défis
en live à l'écran en 25 minutes. Les équipes notent les prompts et donnent
leur avis. Moins immersif mais sauve la session.

---

## 9. Critères de succès de l'atelier

À évaluer en débrief à chaud (dernière minute):

1. **Chaque équipe a livré quelque chose qui tourne** (même imparfait).
2. **Au moins 4 features sur 6 sont mergeable** dans la branche principale
   sans rework majeur.
3. **80%+ des participants disent: "j'ai compris ce que je peux faire en
   solo lundi matin"** (sondage 1 question).
4. **Au moins 2 personnes posent une question d'extension** (ex: "comment je
   plug ma vraie data MT940 dedans?") — signal d'engagement.

---

## 10. Suite logique (si la session se passe bien)

Pitcher au sponsor une **suite en 2 ateliers**:

- **Atelier 2 (90 min)** — *"Du synthétique au réel"*: connecter une vraie
  source MT940/CAMT.053 sur la place de l'export CSV synthétique. Aborder
  l'authentification, le secret management, la séparation prod/dev.
- **Atelier 3 (90 min)** — *"De l'app perso à l'outil partagé"*: déployer
  sur Streamlit Cloud / Hugging Face Spaces, gérer les rôles, ajouter un
  audit log.

Le tout devient un **parcours d'acculturation IA pour les trésoriers** —
~4h cumulées pour passer de "spectateur" à "ils peuvent prototyper en
autonomie".

---

## 11. Ce que vous emportez de la session (mémo distribué)

Une fiche A4 imprimée qu'ils gardent:

```
VIBE CODING POUR TRÉSORIER — LES 5 RÉFLEXES

1. SCOPE       — Une feature à la fois. Une page, un KPI, un chart.
2. ANCRE       — Toujours nommer le fichier exact à modifier.
3. DATA-FIRST  — Préciser quelles données, quelles colonnes.
4. TEST        — Décrire le critère d'acceptation AVANT de prompter.
5. ITÈRE       — L'IA a tort 1 fois sur 5. Lis le diff. Recommence.

LE PROMPT-TYPE
──────────────
Dans <fichier>, ajouter <feature>.
Critère: <description du résultat attendu, mesurable>.
Données: <colonnes / fichiers à utiliser>.
Style: suivre <fichier de référence>.
```

C'est ce mémo qu'ils auront sur leur bureau lundi matin. C'est lui qui
détermine si la session sert à quelque chose au-delà de 45 minutes.
