"""
7_⚙️_Paramètres.py — Gestion du compte utilisateur
====================================================
Permet à l'utilisateur de :
  1. Modifier son mot de passe
  2. Ajouter / modifier son adresse e-mail
  3. Supprimer son compte (avec confirmation)
  4. Voir les informations de sécurité de la base de données
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
from datetime import datetime

from website.components.assistant_sidebar import render_assistant
from website.components.ui_config import set_global_ui
from data.database import get_portfolio_connection
from data.security import hash_password, verify_password

set_global_ui()
render_assistant()

# ── Garde d'authentification ──────────────────────────────────────────────────
if not st.session_state.get("logged_in", False):
    st.warning("🔒 Connecte-toi depuis la page d'accueil.")
    st.stop()

user_id   = st.session_state.user_id
username  = st.session_state.get("user_username", "Utilisateur")

st.title("⚙️ Paramètres du Compte")
st.caption(f"Connecté en tant que **{username}**")

# ── Migration : ajout de la colonne email si absente ─────────────────────────
def ensure_email_column():
    """Ajoute la colonne email à la table users si elle n'existe pas encore."""
    try:
        conn   = get_portfolio_connection()
        cursor = conn.cursor()
        cursor.execute("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS email TEXT DEFAULT NULL
        """)
        conn.commit()
        conn.close()
    except Exception:
        pass  # La colonne existe déjà ou la DB ne supporte pas IF NOT EXISTS

ensure_email_column()

# ── Chargement des infos de l'utilisateur ─────────────────────────────────────
def load_user_info(uid: int) -> dict:
    try:
        conn   = get_portfolio_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, email, created_at FROM users WHERE id = %s", (uid,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"username": row[0], "email": row[1] or "", "created_at": row[2]}
    except Exception:
        pass
    return {"username": username, "email": "", "created_at": "—"}

user_info = load_user_info(user_id)

# ── Onglets ───────────────────────────────────────────────────────────────────
tab_profil, tab_pwd, tab_email, tab_securite, tab_danger = st.tabs([
    "👤 Profil",
    "🔑 Mot de Passe",
    "📧 Adresse E-mail",
    "🔒 Sécurité & DB",
    "🗑️ Supprimer le Compte",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Profil
# ═══════════════════════════════════════════════════════════════════════════════
with tab_profil:
    st.subheader("👤 Informations du Profil")

    col1, col2 = st.columns(2)
    col1.metric("Nom d'utilisateur", user_info["username"])
    col2.metric("E-mail",            user_info["email"] if user_info["email"] else "—  (non renseigné)")

    st.markdown("---")
    col3, col4 = st.columns(2)
    col3.metric("Compte créé le", str(user_info["created_at"])[:10] if user_info["created_at"] else "—")

    # Valeur du portefeuille
    p = st.session_state.get("portfolio")
    if p:
        total_val = p.cash + sum(
            info["quantity"] * info["avg_price"] for info in p.positions.values()
        )
        perf = ((total_val - p.initial_cash) / p.initial_cash) * 100
        col4.metric("Performance globale", f"{perf:+.2f} %")

    st.info(
        "💡 **Comment fonctionne la base de données ?**\n\n"
        "TradeDesk utilise **PostgreSQL Cloud (Supabase)** comme base de données.\n"
        "Ton mot de passe n'est **jamais stocké en clair** : il est haché avec "
        "**PBKDF2-HMAC-SHA256** (100 000 itérations) + un sel aléatoire de 16 octets "
        "unique par utilisateur. Même les administrateurs ne peuvent pas lire ton mot de passe.\n\n"
        "Format stocké : `sel_hexadécimal:hash_hexadécimal`"
    )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Modifier le mot de passe
# ═══════════════════════════════════════════════════════════════════════════════
with tab_pwd:
    st.subheader("🔑 Modifier le Mot de Passe")
    st.caption("Votre mot de passe est haché avec PBKDF2-SHA256 — il ne peut pas être récupéré, seulement réinitialisé.")

    with st.form("form_change_pwd"):
        current_pwd = st.text_input(
            "Mot de passe actuel", type="password", placeholder="••••••••"
        )
        new_pwd = st.text_input(
            "Nouveau mot de passe", type="password",
            placeholder="Minimum 6 caractères recommandés"
        )
        confirm_pwd = st.text_input(
            "Confirmer le nouveau mot de passe", type="password", placeholder="••••••••"
        )
        submitted = st.form_submit_button("🔑 Changer le mot de passe", type="primary")

    if submitted:
        if not current_pwd or not new_pwd or not confirm_pwd:
            st.error("Veuillez remplir tous les champs.")
        elif len(new_pwd) < 4:
            st.error("Le nouveau mot de passe doit faire au moins 4 caractères.")
        elif new_pwd != confirm_pwd:
            st.error("Les deux nouveaux mots de passe ne correspondent pas.")
        else:
            try:
                conn   = get_portfolio_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT password_hash FROM users WHERE id = %s", (user_id,)
                )
                row = cursor.fetchone()
                if row and verify_password(row[0], current_pwd):
                    new_hash = hash_password(new_pwd)
                    cursor.execute(
                        "UPDATE users SET password_hash = %s WHERE id = %s",
                        (new_hash, user_id)
                    )
                    conn.commit()
                    conn.close()
                    st.success("✅ Mot de passe modifié avec succès !")
                else:
                    conn.close()
                    st.error("❌ Mot de passe actuel incorrect.")
            except Exception as e:
                st.error(f"Erreur : {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Adresse e-mail
# ═══════════════════════════════════════════════════════════════════════════════
with tab_email:
    st.subheader("📧 Adresse E-mail")
    st.caption(
        "Ajoutez ou modifiez votre e-mail. Il servira à la récupération de compte "
        "(fonctionnalité d'envoi d'e-mail à activer côté serveur)."
    )

    current_email = user_info.get("email", "") or ""
    if current_email:
        st.info(f"📧 E-mail actuel : **{current_email}**")
    else:
        st.warning("⚠️ Aucun e-mail enregistré. Ajoutez-en un pour sécuriser votre compte.")

    with st.form("form_update_email"):
        new_email = st.text_input(
            "Nouvelle adresse e-mail",
            value=current_email,
            placeholder="exemple@email.com"
        )
        submitted_email = st.form_submit_button("💾 Enregistrer l'e-mail", type="primary")

    if submitted_email:
        if not new_email or "@" not in new_email or "." not in new_email.split("@")[-1]:
            st.error("Veuillez entrer une adresse e-mail valide.")
        else:
            try:
                conn   = get_portfolio_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET email = %s WHERE id = %s",
                    (new_email.strip().lower(), user_id)
                )
                conn.commit()
                conn.close()
                st.success(f"✅ E-mail mis à jour : **{new_email.strip().lower()}**")
                # Rafraîchir les infos localement
                user_info["email"] = new_email.strip().lower()
            except Exception as e:
                st.error(f"Erreur lors de la mise à jour : {e}")

    st.markdown("---")
    st.subheader("🔐 Mot de passe oublié — Procédure manuelle")
    st.markdown("""
> [!WARNING]
> La récupération automatique par e-mail nécessite un serveur SMTP configuré.
> En attendant, voici la procédure manuelle :

**Si tu as oublié ton mot de passe :**
1. Note ton nom d'utilisateur exact.
2. Contacte l'administrateur de TradeDesk.
3. Avec le nom d'utilisateur, l'admin peut exécuter en base de données :
   ```sql
   UPDATE users SET password_hash = '<nouveau_hash>' WHERE username = '<ton_pseudo>';
   ```
4. Le nouveau hash se génère avec : `python3 -c "from data.security import hash_password; print(hash_password('nouveau_mdp'))"`

**Sécurité du stockage** : Les mots de passe sont hachés avec **PBKDF2-HMAC-SHA256** +
sel de 16 octets + 100 000 itérations. Conforme aux recommandations NIST SP 800-132.
""")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Informations de sécurité
# ═══════════════════════════════════════════════════════════════════════════════
with tab_securite:
    st.subheader("🔒 Architecture de Sécurité & Base de Données")

    st.markdown("""
### 🗄️ Base de données PostgreSQL Cloud (Supabase)

TradeDesk utilise une base de données **PostgreSQL** hébergée sur Supabase Cloud.
Toutes les connexions passent par `psycopg2` avec les identifiants stockés dans les **secrets Streamlit**.

### 📊 Structure des tables

| Table | Contenu |
|---|---|
| `users` | `id`, `username`, `password_hash`, `email`, `created_at` |
| `portfolio_state` | `user_id`, `cash`, `initial_cash` |
| `portfolio_positions` | `user_id`, `asset`, `quantity`, `avg_price` |
| `portfolio_transactions` | `id`, `user_id`, `timestamp`, `type`, `asset`, `quantity`, `price`, `commission`, `total_net` |
| `bronze_prices` | Données brutes OHLCV de yfinance |
| `silver_prices` | Données nettoyées + indicateurs (SMA, RSI) |
| `gold_kpis` | KPIs agrégés (Sharpe, Bêta, Volatilité) |

### 🔐 Hachage des mots de passe — PBKDF2-HMAC-SHA256

```
Mot de passe brut  ──►  PBKDF2(password, sel_16_octets, 100_000_iterations, SHA-256)
                    ──►  Stockage : "sel_hex:hash_hex"
```

- **Sel unique** par utilisateur : même mot de passe = hash différent ✅
- **100 000 itérations** : attaque par force brute rendue très lente ✅  
- **`hmac.compare_digest()`** : protection contre les timing attacks ✅
- **Aucun mot de passe en clair** ne transite ou n'est stocké en base ✅

### 🌐 Secrets Streamlit

Les credentials de la base de données sont stockés dans `.streamlit/secrets.toml`
(exclu du dépôt Git via `.gitignore`) :

```toml
[postgres]
DB_USER     = "..."
DB_PASSWORD = "..."
DB_HOST     = "..."
DB_PORT     = "5432"
DB_NAME     = "postgres"
```
""")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Supprimer le compte
# ═══════════════════════════════════════════════════════════════════════════════
with tab_danger:
    st.subheader("🗑️ Supprimer mon Compte")

    st.error(
        "⚠️ **Zone de danger** — Cette action est **irréversible**. "
        "Toutes vos données (portefeuille, positions, historique des transactions) "
        "seront définitivement supprimées."
    )

    with st.expander("🔴 Je comprends les conséquences — Supprimer mon compte", expanded=False):
        st.warning(
            "Pour confirmer, saisissez votre nom d'utilisateur exact "
            f"(**{username}**) et votre mot de passe."
        )

        with st.form("form_delete_account"):
            confirm_username = st.text_input(
                "Confirmez votre nom d'utilisateur", placeholder=username
            )
            confirm_pwd_del = st.text_input(
                "Mot de passe", type="password", placeholder="••••••••"
            )
            understand = st.checkbox(
                "Je comprends que cette action supprimera TOUTES mes données et est irréversible."
            )
            submitted_del = st.form_submit_button(
                "🗑️ SUPPRIMER DÉFINITIVEMENT MON COMPTE",
                type="primary"
            )

        if submitted_del:
            if not understand:
                st.error("Cochez la case de confirmation pour continuer.")
            elif confirm_username.strip().lower() != username.strip().lower():
                st.error("Le nom d'utilisateur ne correspond pas.")
            elif not confirm_pwd_del:
                st.error("Veuillez entrer votre mot de passe.")
            else:
                try:
                    conn   = get_portfolio_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT password_hash FROM users WHERE id = %s", (user_id,)
                    )
                    row = cursor.fetchone()
                    if row and verify_password(row[0], confirm_pwd_del):
                        # Suppression en cascade grâce aux FOREIGN KEY ON DELETE CASCADE
                        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                        conn.commit()
                        conn.close()

                        # Déconnexion de la session
                        st.session_state.logged_in    = False
                        st.session_state.user_id      = None
                        st.session_state.user_username = None
                        if "portfolio" in st.session_state:
                            del st.session_state.portfolio

                        st.success("✅ Compte supprimé. Au revoir !")
                        st.rerun()
                    else:
                        conn.close()
                        st.error("❌ Mot de passe incorrect. Suppression annulée.")
                except Exception as e:
                    st.error(f"Erreur lors de la suppression : {e}")
