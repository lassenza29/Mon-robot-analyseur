import streamlit as st
import yfinance as yf
import math

# Configuration de la page principale Streamlit
st.set_page_config(page_title="Analyseur Global: Actions, Rendements & ETFs", page_icon="📈", layout="wide")

# Titre de l'application de niveau professionnel
st.title("🚀 Analyseur Financier Universel v4")
st.write("Le tableau de bord ultime pour analyser instantanément les **Actions à haut rendement**, les **Actions de croissance** et les **ETFs**.")

# Barre de saisie globale du Ticker
ticker_symbole = st.text_input("🔍 Saisissez un symbole (ex: AAPL pour Apple, O pour Realty Income (Rendement), SPY pour le S&P 500, ou CW8.PA pour Amundi MSCI World) :", value="AAPL").upper().strip()

if ticker_symbole:
    with st.spinner(f"Analyse globale et extraction des données pour {ticker_symbole}..."):
        try:
            # Récupération du flux de données Yahoo Finance
            action = yf.Ticker(ticker_symbole)
            info = action.info

            # Vérification stricte de la validité du symbole saisi
            if not info or ('shortName' not in info and 'longName' not in info):
                st.error("❌ Impossible de trouver ce produit financier. Vérifiez l'exactitude du symbole (ex: TTE.PA pour TotalEnergies, VUAA.L, etc.).")
            else:
                # --- FONCTIONS DE SÉCURISATION DES DONNÉES ---
                def safe_float(key, multiplicateur=1.0, valeur_defaut=0.0):
                    val = info.get(key)
                    if val is None:
                        return valeur_defaut
                    try:
                        return float(val) * multiplicateur
                    except (ValueError, TypeError):
                        return valeur_defaut

                def safe_str(key, valeur_defaut="N/A"):
                    val = info.get(key)
                    return str(val).strip() if val is not None else valeur_defaut

                # Détection automatique de la nature du produit (Action classique ou ETF)
                quote_type = safe_str('quoteType').upper()
                nom = info.get('longName') or info.get('shortName') or ticker_symbole
                prix_actuel = safe_float('currentPrice') or safe_float('regularMarketPrice') or safe_float('navPrice') or 0.0

                # --- HEADER UNIVERSEL (Commun à tous les actifs) ---
                st.markdown(f"## 🏢 {nom} ({ticker_symbole}) — *Type : {quote_type}*")
                
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    st.metric("Prix actuel du marché", f"{prix_actuel:,.2f} $")
                with col_h2:
                    if quote_type == "ETF":
                        actifs_totaux = safe_float('totalAssets', 1 / 1_000_000)
                        st.metric("Actifs sous gestion (AUM)", f"{actifs_totaux:,.0f} M$")
                    else:
                        capitalisation = safe_float('marketCap', 1 / 1_000_000)
                        st.metric("Capitalisation Boursière", f"{capitalisation:,.0f} M$")

                st.divider()

                # --- ROUTAGE ET AFFICHAGE SELON LE TYPE : ETF vs ACTION ---
                if quote_type == "ETF":
                    # --- INTERFACE SPÉCIFIQUE POUR LES ETFS ---
                    tab_etf1, tab_etf2 = st.tabs(["📊 Profil & Caractéristiques", "💰 Rendement & Performance"])
                    
                    # Récupération des données clés de l'ETF
                    frais_gestion = safe_float('expenseRatio', 100.0) # ex: 0.0007 -> 0.07%
                    etf_yield = safe_float('trailingAnnualDividendYield', 100.0) or safe_float('yield', 100.0)
                    famille = safe_str('fundFamily')
                    categorie = safe_str('category')
                    
                    with tab_etf1:
                        st.markdown("### Structure et Frais de l'ETF")
                        e1, e2, e3 = st.columns(3)
                        e1.metric("Frais de gestion annuels", f"{frais_gestion:.2f} %")
                        e2.metric("Émetteur / Famille", famille)
                        e3.metric("Catégorie de fonds", categorie)
                        
                        # Conseils sur les frais de l'ETF
                        if 0 < frais_gestion <= 0.30:
                            st.caption("🟢 **Frais très bas :** Idéal pour une stratégie passive long terme.")
                        elif frais_gestion > 0.30:
                            st.caption("⚠️ **Frais modérés à élevés :** Comparez avec des alternatives équivalentes.")

                    with tab_etf2:
                        st.markdown("### Rendement des Dividendes de l'ETF")
                        ed1, ed2 = st.columns(2)
                        ed1.metric("Rendement des dividendes (Yield)", f"{etf_yield:.2f} %")
                        with ed2:
                            st.metric("Type de distribution", "Distribution / Capitalisation")
                            st.caption("Note : Consultez le site officiel de l'émetteur pour la politique exacte de distribution (Dist / Acc).")

                    # --- VERDICT ETF ---
                    st.divider()
                    st.markdown("### 📢 Analyse Automatique de l'ETF")
                    if frais_gestion <= 0.35:
                        st.success(f"🟢 **ETF EFFICIENT :** Les frais de gestion ({frais_gestion:.2f}%) sont compétitifs. Cet outil est structurellement sain pour une détention de long terme.")
                    else:
                        st.warning(f"⚠️ **ATTENTION AUX FRAIS :** Les frais de gestion de {frais_gestion:.2f}% grignoteront votre performance sur le long terme. Cherchez s'il existe un équivalent chez Amundi, iShares ou Vanguard.")

                else:
                    # --- INTERFACE SPÉCIFIQUE POUR LES ACTIONS (Incorpore les dividendes et rendements) ---
                    tab1, tab2, tab3 = st.tabs(["🛡️ Sécurité Financière", "📈 Performance & Rendements (Dividendes)", "💰 Valorisation & Formule de Graham"])
                    
                    # Récupération des données de l'Action
                    dette_brute = safe_float('totalDebt', 1 / 1_000_000)
                    tresorerie = safe_float('totalCash', 1 / 1_000_000)
                    dette_nette = dette_brute - tresorerie
                    ebitda = safe_float('ebitda', 1 / 1_000_000)
                    ratio_dette_ebitda = dette_nette / ebitda if ebitda > 0 else 0.0
                    
                    ca = safe_float('totalRevenue', 1 / 1_000_000)
                    marge_exploit = safe_float('operatingMargins', 100.0)
                    marge_nette = safe_float('profitMargins', 100.0)
                    roe = safe_float('returnOnEquity', 100.0)
                    
                    # BLOC RENDEMENT ET DIVIDENDES EXPLICITES
                    div_yield = safe_float('dividendYield', 100.0) or safe_float('trailingAnnualDividendYield', 100.0)
                    div_rate = safe_float('dividendRate')
                    payout_ratio = safe_float('payoutRatio', 100.0)
                    
                    bna = safe_float('trailingEps') or safe_float('forwardEps') or 0.0
                    per = safe_float('trailingPE') or 0.0
                    actif_net_action = safe_float('bookValue') or 0.0
                    
                    # Formule de Graham sécurisée contre les racines négatives
                    produit_graham = 22.5 * bna * actif_net_action
                    prix_graham = math.sqrt(produit_graham) if produit_graham > 0 else 0.0

                    with tab1:
                        st.markdown("### Analyse de la Dette et Solvabilité")
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Dette Brute", f"{dette_brute:,.0f} M$")
                        c2.metric("Trésorerie (Cash)", f"{tresorerie:,.0f} M$")
                        c3.metric("Dette Nette", f"{dette_nette:,.0f} M$")
                        with c4:
                            st.metric("Ratio Dette / EBITDA", f"{ratio_dette_ebitda:.2f} x")
                            if dette_nette <= 0:
                                st.caption("🟢 **Cash Net Élevé** (Entreprise Ultra-Sûre)")
                            elif ratio_dette_ebitda < 3:
                                st.caption("🟢 **Dette Maîtrisée** (< 3x)")
                            else:
                                st.caption("🔴 **Dette à Risque** (> 3x)")

                    with tab2:
                        st.markdown("### Performance de l'Entreprise & Dividendes (Rendements)")
                        
                        # Première ligne : Marges Opérationnelles
                        st.markdown("##### ⚙️ Efficacité Opérationnelle")
                        r1, r2, r3, r4 = st.columns(4)
                        r1.metric("Chiffre d'affaires", f"{ca:,.0f} M$")
                        with r2:
                            st.metric("Marge d'exploitation", f"{marge_exploit:.2f} %")
                            st.caption("🟢 Marges Saines (> 8%)" if marge_exploit > 8 else "🔴 Marges Faibles (< 8%)")
                        with r3:
                            st.metric("Marge Nette", f"{marge_nette:.2f} %")
                        with r4:
                            st.metric("ROE (Rentabilité)", f"{roe:.2f} %")
                            st.caption("🟢 Rentable (> 10%)" if roe > 10 else "🔴 Faible Rentabilité")
                        
                        st.write("")
                        
                        # Deuxième ligne : Analyse complète des dividendes demandée par l'utilisateur
                        st.markdown("##### 💰 Politique de Distribution & Rendements")
                        d1, d2, d3 = st.columns(3)
                        with d1:
                            st.metric("Rendement du Dividende (Yield)", f"{div_yield:.2f} %")
                            if div_yield >= 4.0:
                                st.caption("🔥 **Haut Rendement** (Générateur de Cash)")
                            elif 0 < div_yield < 4.0:
                                st.caption("👍 Rendement Modéré / Standard")
                            else:
                                st.caption("⚪ Aucun dividende distribué")
                        with d2:
                            st.metric("Montant annuel par action", f"{div_rate:.2f} $")
                        with d3:
                            st.metric("Ratio de Distribution (Payout)", f"{payout_ratio:.2f} %")
                            if 0 < payout_ratio <= 75:
                                st.caption("🟢 **Sûr & Pérenne :** L'entreprise couvre largement son dividende.")
                            elif payout_ratio > 75:
                                st.caption("⚠️ **Risque de Coupure :** L'entreprise distribue une trop grande part de ses gains.")

                    with tab3:
                        st.markdown("### Multiples de Marché & Objectif Graham")
                        v1, v2, v3 = st.columns(3)
                        with v1:
                            if per > 0:
                                st.metric("PER Actuel", f"{per:.2f} x")
                                st.caption("🟢 Sous-évaluée (< 20x)" if per < 20 else "🔴 Chère (> 20x)")
                            else:
                                st.metric("PER Actuel", "N/A")
                                st.caption("🔴 Entreprise en perte")
                        with v2:
                            st.metric("Actif Net par Action (Book Value)", f"{actif_net_action:.2f} $")
                        with v3:
                            if prix_graham > 0:
                                st.metric("Prix d'Achat Max (Graham)", f"{prix_graham:.2f} $")
                            else:
                                st.metric("Prix d'Achat Max (Graham)", "N/A")
                                st.caption("🔴 Non calculable (Bénéfices négatifs)")

                    # --- VERDICT UNIFIÉ DES ACTIONS ---
                    st.divider()
                    st.markdown("### 📢 Verdict Automatique du Robot")
                    
                    est_securise = (dette_nette <= 0) or (ratio_dette_ebitda < 3)
                    est_rentable = (marge_exploit > 8) and (roe > 10)
                    
                    if est_securise and est_rentable:
                        st.success("🟢 **ENTREPRISE EXCELLENTE :** La santé financière est solide et les marges d'exploitation respectent les critères de qualité.")
                        if 0 < prix_actuel < prix_graham:
                            st.balloons()
                            st.info("🔥 **TIMING PARFAIT :** L'action est sous-évaluée d'après la formule de Benjamin Graham et offre une marge de sécurité majeure pour investir.")
                        elif div_yield >= 4.0:
                            st.info("💎 **PROFIL RENTIER ACCESSIBLE :** La valorisation globale est normale, mais le dividende élevé en fait un excellent moteur de revenus.")
                        else:
                            st.warning("⚠️ **QUALITÉ TOP, MAIS LE PRIX EST ÉLEVÉ :** Les fondamentaux sont excellents, mais le prix actuel dépasse la valeur théorique de Graham. Attendez un repli.")
                    else:
                        st.error("🔴 **ATTENTION DANGER :** L'actif échoue sur un ou plusieurs filtres critiques (surendettement ou rentabilité dégradée). Procédez avec une extrême prudence.")

        except Exception as e:
            st.error(f"Une erreur technique est survenue lors de l'extraction : {e}")
