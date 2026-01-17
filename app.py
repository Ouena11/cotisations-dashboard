import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# CONFIGURATION DE LA PAGE
# -----------------------------
st.set_page_config(page_title="Situation des cotisations", layout="wide", page_icon="💰")

# -----------------------------
# CHARGEMENT DES DONNÉES
# -----------------------------
df = pd.read_excel("cotisations.xlsx")

# -----------------------------
# TITRE
# -----------------------------
st.title("💰 Tableau de bord des cotisations")
st.markdown("""
Ce tableau de bord permet de suivre les cotisations du groupe par **membre**, **mois**, **année**.
""")

# -----------------------------
# BARRE LATERALE : FILTRES
# -----------------------------
st.sidebar.header("🎛️ Filtres interactifs")

annees = sorted(df["ANNEE"].unique())
membres = sorted(df["NOM"].unique())
mois = ["Janvier","Février","Mars","Avril","Mai","Juin",
        "Juillet","Août","Septembre","Octobre","Novembre","Décembre"]

annee_select = st.sidebar.multiselect("Choisir année(s)", annees, default=annees)
membre_select = st.sidebar.multiselect("Choisir membre(s)", membres, default=membres)
mois_select = st.sidebar.multiselect("Choisir mois", mois, default=mois)

df_filtre = df[df["ANNEE"].isin(annee_select) & df["NOM"].isin(membre_select) & df["MOIS"].isin(mois_select)]

# -----------------------------
# INDICATEURS CLÉS
# -----------------------------
total_cotisations = df_filtre["MONTANT"].sum()
nb_paiements = (df_filtre["MONTANT"] > 0).sum()
nb_non_paiements = (df_filtre["MONTANT"] == 0).sum()
nb_membres = df_filtre["NOM"].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total cotisations", f"{total_cotisations:,.0f} FCFA")
col2.metric("👥 Membres actifs", nb_membres)
col3.metric("✅ Paiements effectués", nb_paiements)
col4.metric("❌ Non-paiements", nb_non_paiements)

# -----------------------------
# GRAPHIQUE PAR ANNÉE
# -----------------------------
st.subheader("📅 Cotisations par année")
total_par_annee = df_filtre.groupby("ANNEE")["MONTANT"].sum().reset_index()
fig_annee = px.bar(total_par_annee, x="ANNEE", y="MONTANT",
                   text="MONTANT", color="MONTANT",
                   color_continuous_scale="Blues",
                   title="Montant total par année")
fig_annee.update_traces(texttemplate="%{text:.0f}", textposition="outside")
st.plotly_chart(fig_annee, use_container_width=True)

# -----------------------------
# GRAPHIQUE PAR MEMBRE
# -----------------------------
st.subheader("👥 Cotisations par membre")
total_par_membre = df_filtre.groupby("NOM")["MONTANT"].sum().reset_index()
fig_membre = px.bar(total_par_membre, x="NOM", y="MONTANT",
                    text="MONTANT", color="MONTANT",
                    color_continuous_scale="Greens",
                    title="Montant total par membre")
fig_membre.update_traces(texttemplate="%{text:.0f}", textposition="outside")
st.plotly_chart(fig_membre, use_container_width=True)

# -----------------------------
# GRAPHIQUE PAR MOIS
# -----------------------------
st.subheader("🗓️ Cotisations par mois")
total_par_mois = df_filtre.groupby("MOIS")["MONTANT"].sum().reindex(mois).reset_index()
fig_mois = px.line(total_par_mois, x="MOIS", y="MONTANT",
                   markers=True, title="Montant total par mois",
                   color_discrete_sequence=["#FF5733"])
st.plotly_chart(fig_mois, use_container_width=True)

# -----------------------------
# PIE CHART (Répartition par membre)
# -----------------------------
st.subheader("🥧 Répartition des cotisations par membre")
fig_pie = px.pie(total_par_membre, names="NOM", values="MONTANT",
                 color_discrete_sequence=px.colors.qualitative.Set3,
                 title="Part de chaque membre dans les cotisations")
st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------
# HEATMAP (paiements vs mois/membre)
# -----------------------------
st.subheader("🔥 Heatmap des paiements")
pivot = df_filtre.pivot_table(index="NOM", columns="MOIS", values="MONTANT", aggfunc="sum", fill_value=0)
fig_heatmap = px.imshow(pivot, text_auto=True, aspect="auto",
                        labels=dict(x="Mois", y="Membre", color="Montant"),
                        color_continuous_scale="Turbo")
st.plotly_chart(fig_heatmap, use_container_width=True)

# -----------------------------
# TABLEAU DETAILLE
# -----------------------------
st.subheader("📌 Données filtrées")
st.dataframe(df_filtre, use_container_width=True)

# -----------------------------
# EXPORT DES DONNÉES
# -----------------------------
st.sidebar.subheader("📤 Exporter les données")
export_csv = st.sidebar.button("Exporter en CSV")
if export_csv:
    df_filtre.to_csv("cotisations_filtrees.csv", index=False)
    st.sidebar.success("✅ Fichier CSV exporté")

export_excel = st.sidebar.button("Exporter en Excel")
if export_excel:
    df_filtre.to_excel("cotisations_filtrees.xlsx", index=False)
    st.sidebar.success("✅ Fichier Excel exporté")

# -----------------------------
# ANIMATION AVANCÉE : Evolution par année
# -----------------------------
st.subheader("🎬 Animation des cotisations par année")
fig_anim = px.bar(df_filtre, x="NOM", y="MONTANT", color="NOM",
                  animation_frame="ANNEE", animation_group="NOM",
                  range_y=[0, df_filtre["MONTANT"].max()+2000],
                  title="Évolution des cotisations par membre et par année",
                  color_discrete_sequence=px.colors.qualitative.Bold)
st.plotly_chart(fig_anim, use_container_width=True)

# -----------------------------
# MESSAGE FINAL
# -----------------------------
st.markdown("✨ Tableau de bord complet avec filtres, animations et export.")
