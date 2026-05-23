import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st

from website.components.assistant_sidebar import render_assistant
from website.components.ui_config import set_global_ui
from data.database import (
    get_portfolio_connection, get_portfolios, create_portfolio,
    rename_portfolio, delete_portfolio,
)
from data.security import hash_password, verify_password
from equities.equities import Portfolio

set_global_ui()
render_assistant()

if not st.session_state.get("logged_in", False):
    st.warning("Connecte-toi depuis la page d'accueil.")
    st.stop()

user_id = st.session_state.user_id
username = st.session_state.get("user_username", "Utilisateur")

st.title("Paramètres du Compte")
st.caption(f"Connecté en tant que **{username}**")

def load_user_info(uid: int) -> dict:
    try:
        conn = get_portfolio_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, created_at FROM users WHERE id = %s", (uid,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"username": row[0], "created_at": row[1]}
    except Exception:
        pass
    return {"username": username, "created_at": "—"}

user_info = load_user_info(user_id)

#Onglets
tab_profil, tab_portfolios, tab_pwd, tab_danger = st.tabs([
    "Profil",
    "Mes Portefeuilles",
    "Mot de Passe",
    "Supprimer le Compte",
])

#TAB 1 — Profil
with tab_profil:
    st.subheader("Informations du Profil")

    col1, col2 = st.columns(2)
    col1.metric("Nom d'utilisateur", user_info["username"])
    col2.metric("Compte créé le", str(user_info["created_at"])[:10] if user_info["created_at"] else "—")

    p = st.session_state.get("portfolio")
    if p:
        col3, col4 = st.columns(2)
        total_val = p.cash + sum(info["quantity"] * info["avg_price"] for info in p.positions.values())
        perf = ((total_val - p.initial_cash) / p.initial_cash) * 100
        col3.metric("Capital initial", f"{p.initial_cash:,.2f} €")
        col4.metric("Performance globale", f"{perf:+.2f} %")

        col5, col6 = st.columns(2)
        col5.metric("Liquidités", f"{p.cash:,.2f} €")
        col6.metric("Valeur totale (estimation)", f"{total_val:,.2f} €")

    st.markdown("---")
    st.info(
        "Votre mot de passe n'est jamais stocké en clair : il est haché avec "
        "**PBKDF2-HMAC-SHA256** (100 000 itérations) + sel aléatoire de 16 octets. "
        "Même les administrateurs ne peuvent pas lire votre mot de passe."
    )

#TAB 2 — Mes Portefeuilles
with tab_portfolios:
    st.subheader("Gestion des Portefeuilles")
    st.caption("Créez plusieurs portefeuilles pour tester différentes stratégies en parallèle.")

    portfolios = get_portfolios(user_id)

    if not portfolios:
        st.info("Aucun portefeuille trouvé. Créez-en un ci-dessous.")
    else:
        for ptf_id, ptf_name, ptf_initial, ptf_created in portfolios:
            with st.expander(f"**{ptf_name}** — #{ptf_id}  (créé le {str(ptf_created)[:10]})", expanded=False):
                col_a, col_b = st.columns(2)
                col_a.metric("Capital initial", f"{ptf_initial:,.2f} €")

                #Valeur actuelle depuis session_state si disponible
                p_obj = st.session_state.get(f"portfolio_{ptf_id}")
                if p_obj:
                    tot = p_obj.cash + sum(i["quantity"] * i["avg_price"] for i in p_obj.positions.values())
                    perf_val = ((tot - p_obj.initial_cash) / p_obj.initial_cash) * 100
                    col_b.metric("Performance estimée", f"{perf_val:+.2f} %")

                st.markdown("##### Renommer")
                new_name_key = f"rename_{ptf_id}"
                new_name_val = st.text_input("Nouveau nom", key=new_name_key, placeholder=ptf_name)
                if st.button("Renommer", key=f"btn_rename_{ptf_id}"):
                    if new_name_val.strip():
                        if rename_portfolio(ptf_id, user_id, new_name_val.strip()):
                            st.success(f"Portefeuille renommé en « {new_name_val.strip()} » !")
                            st.rerun()
                        else:
                            st.error("Erreur lors du renommage.")
                    else:
                        st.error("Le nom ne peut pas être vide.")

                if len(portfolios) > 1:
                    st.markdown("##### Supprimer ce portefeuille")
                    st.warning("Cette action est irréversible — toutes les positions et transactions seront perdues.")
                    confirm_del = st.checkbox(
                        "Je confirme la suppression définitive de ce portefeuille",
                        key=f"confirm_del_{ptf_id}"
                    )
                    if st.button("Supprimer", key=f"btn_del_{ptf_id}", type="primary"):
                        if confirm_del:
                            delete_portfolio(ptf_id, user_id)
                            #Nettoyer session_state
                            if f"portfolio_{ptf_id}" in st.session_state:
                                del st.session_state[f"portfolio_{ptf_id}"]
                            st.success("Portefeuille supprimé.")
                            st.rerun()
                        else:
                            st.error("Cochez la case de confirmation pour supprimer.")
                else:
                    st.info("Vous ne pouvez pas supprimer votre seul portefeuille.")

    st.divider()
    st.markdown("#### Créer un nouveau portefeuille")
    with st.form("form_new_portfolio"):
        new_ptf_name = st.text_input("Nom du portefeuille", placeholder="ex : Stratégie Croissance")
        new_ptf_cash = st.number_input(
            "Capital de départ (€)", min_value=100.0, max_value=10_000_000.0,
            value=10_000.0, step=1000.0
        )
        submitted_ptf = st.form_submit_button("Créer le portefeuille", type="primary")

    if submitted_ptf:
        if not new_ptf_name.strip():
            st.error("Entrez un nom.")
        else:
            pid = create_portfolio(user_id, new_ptf_name.strip(), new_ptf_cash)
            new_p = Portfolio(new_ptf_cash)
            new_p.save_to_db(user_id, pid)
            st.success(f"Portefeuille **« {new_ptf_name.strip()} »** créé avec {new_ptf_cash:,.0f} € de capital !")
            st.rerun()

#TAB 3 — Modifier le mot de passe
with tab_pwd:
    st.subheader("Modifier le Mot de Passe")
    st.caption("Votre mot de passe est haché avec PBKDF2-SHA256 — il ne peut pas être récupéré, seulement réinitialisé.")

    with st.form("form_change_pwd"):
        current_pwd = st.text_input("Mot de passe actuel", type="password", placeholder="••••••••")
        new_pwd = st.text_input("Nouveau mot de passe", type="password", placeholder="Minimum 6 caractères recommandés")
        confirm_pwd = st.text_input("Confirmer le nouveau mot de passe", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Changer le mot de passe", type="primary")

    if submitted:
        if not current_pwd or not new_pwd or not confirm_pwd:
            st.error("Veuillez remplir tous les champs.")
        elif len(new_pwd) < 4:
            st.error("Le nouveau mot de passe doit faire au moins 4 caractères.")
        elif new_pwd != confirm_pwd:
            st.error("Les deux nouveaux mots de passe ne correspondent pas.")
        else:
            try:
                conn = get_portfolio_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
                row = cursor.fetchone()
                if row and verify_password(row[0], current_pwd):
                    new_hash = hash_password(new_pwd)
                    cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user_id))
                    conn.commit()
                    conn.close()
                    st.success("Mot de passe modifié avec succès !")
                else:
                    conn.close()
                    st.error("Mot de passe actuel incorrect.")
            except Exception as e:
                st.error(f"Erreur : {e}")

#TAB 4 — Supprimer le compte
with tab_danger:
    st.subheader("Supprimer mon Compte")

    st.error(
        "**Zone de danger** — Cette action est **irréversible**. "
        "Toutes vos données (portefeuille, positions, historique des transactions) "
        "seront définitivement supprimées."
    )

    with st.expander("Je comprends les conséquences — Supprimer mon compte", expanded=False):
        st.warning(
            f"Pour confirmer, saisissez votre nom d'utilisateur exact (**{username}**) et votre mot de passe."
        )

        with st.form("form_delete_account"):
            confirm_username = st.text_input("Confirmez votre nom d'utilisateur", placeholder=username)
            confirm_pwd_del = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            understand = st.checkbox("Je comprends que cette action supprimera TOUTES mes données et est irréversible.")
            submitted_del = st.form_submit_button("SUPPRIMER DÉFINITIVEMENT MON COMPTE", type="primary")

        if submitted_del:
            if not understand:
                st.error("Cochez la case de confirmation pour continuer.")
            elif confirm_username.strip().lower() != username.strip().lower():
                st.error("Le nom d'utilisateur ne correspond pas.")
            elif not confirm_pwd_del:
                st.error("Veuillez entrer votre mot de passe.")
            else:
                try:
                    conn = get_portfolio_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
                    row = cursor.fetchone()
                    if row and verify_password(row[0], confirm_pwd_del):
                        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                        conn.commit()
                        conn.close()
                        st.session_state.logged_in = False
                        st.session_state.user_id = None
                        st.session_state.user_username = None
                        if "portfolio" in st.session_state:
                            del st.session_state.portfolio
                        st.success("Compte supprimé. Au revoir !")
                        st.rerun()
                    else:
                        conn.close()
                        st.error("Mot de passe incorrect. Suppression annulée.")
                except Exception as e:
                    st.error(f"Erreur lors de la suppression : {e}")
