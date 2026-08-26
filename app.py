import duckdb
import streamlit as st

st.set_page_config(page_title="LEC Stats", layout="wide")

st.title("LEC Stats - Summer 2026")

tab_calendrier, tab_classement, tab_series, tab_joueurs, tab_equipes, tab_pickban = st.tabs(
    ["📅 Calendrier", "🏅 Classement", "🗂️ Séries", "📊 Stats Joueurs", "🛡️ Stats Équipes", "🎯 Pick / Ban"]
)

with duckdb.connect("lec_stats.duckdb", read_only=True) as con:
    with tab_calendrier:
        df_calendrier = con.sql("SELECT * FROM calendrier ORDER BY begin_at").df()
        st.dataframe(df_calendrier, use_container_width=True)

    with tab_classement:
        df_classement = con.sql("SELECT * FROM classement ORDER BY tournament_name, wins DESC").df()
        for tournament_name in df_classement["tournament_name"].unique():
            st.subheader(tournament_name)
            st.dataframe(
                df_classement[df_classement["tournament_name"] == tournament_name],
                use_container_width=True,
            )

with tab_series:
    st.write("Navigation entre series a venir")

with tab_joueurs:
    st.info("Comming Soon.")

with tab_equipes:
    st.info("Coming Soon.")

with tab_pickban:
    st.info("Coming Soon.")
