import duckdb
import streamlit as st

st.set_page_config(page_title="LEC Stats", layout="wide")

st.title("LEC Stats - Summer 2026")

tab_calendrier, tab_classement, tab_series, tab_joueurs, tab_equipes, tab_pickban = st.tabs(
    ["📅 Calendrier", "🏅 Classement", "🗂️ Séries", "📊 Stats Joueurs", "🛡️ Stats Équipes", "🎯 Pick / Ban"]
)

with duckdb.connect("lec_stats.duckdb", read_only=True) as con:
    MOIS_FR = {
        1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
        7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre",
    }

    def format_date_fr(dt) -> str:
        return f"{dt.day} {MOIS_FR[dt.month]} {dt.year}"

    with tab_calendrier:
        df_calendrier = con.sql("""
            SELECT begin_at, status, team1_name, team2_name, team1_score, team2_score 
            FROM calendrier 
            ORDER BY begin_at
        """).df()

        df_calendrier["date"] = df_calendrier["begin_at"].apply(format_date_fr)
        df_calendrier["heure"] = df_calendrier["begin_at"].dt.strftime("%H:%M")

        for date_str in df_calendrier["date"].unique():
            st.subheader(date_str)
            match_du_jour = df_calendrier[df_calendrier["date"] == date_str]

            for _, match in match_du_jour.iterrows():
                col_heure, col_team1, col_score, col_team2 = st.columns([1, 3, 2, 3])
                col_heure.write(match["heure"])
                col_team1.write(match["team1_name"])
                if match["status"] == "finished":
                    col_score.write(f"{match['team1_score']} - {match['team2_score']}")
                else:
                    col_score.write("vs")
                col_team2.write(match["team2_name"])

            st.divider()

    with tab_classement:
        st.markdown("""
            <style>
            div[class*="st-key-team_row_"] {
                padding: 1px 175px 1px 175px;
                border-radius: 12px;
                transition: background-color 0.2s;
            }
            div[class*="st-key-team_"]:hover {
                background-color: rgba(255, 255, 255, 0.08);
            }
            </style>
        """, unsafe_allow_html=True)

        df_classement = con.sql("""
            SELECT tournament_name, team_id, team_name, team_logo, wins, losses
            FROM classement
            ORDER BY tournament_name, wins DESC
        """).df()

        if "equipe_ouverte" not in st.session_state:
            st.session_state.equipe_ouverte = None

        for tournament_name in df_classement["tournament_name"].unique():
            col_gauche, col_centre, col_droite = st.columns([1, 2, 1])
            with col_centre:
                st.subheader(tournament_name)
                df_t = df_classement[df_classement["tournament_name"] == tournament_name].reset_index(drop=True)

                for i, row in df_t.iterrows():
                    key_ligne = f"team_row_{tournament_name.replace(' ', '_')}_{i}"
                    with st.container(key=key_ligne):
                        col_rang, col_logo, col_nom, col_score = st.columns([1, 1, 4, 2])
                        col_rang.write(f"**{i + 1}**")
                        col_logo.image(row["team_logo"], width=30)
                        if col_nom.button(row["team_name"], key=f"btn_{key_ligne}", type="tertiary"):
                            if st.session_state.equipe_ouverte == row["team_id"]:
                                st.session_state.equipe_ouverte = None
                            else:
                                st.session_state.equipe_ouverte = row["team_id"]
                        col_score.write(f"{row['wins']} - {row['losses']}")
                
                    if st.session_state.equipe_ouverte == row["team_id"]:
                        historique = con.sql("""
                            SELECT
                                begin_at,
                                CASE WHEN team1_id = ? THEN team2_name ELSE team1_name END AS adversaire,
                                CASE WHEN team1_id = ? THEN team1_score ELSE team2_score END AS score_pour,
                                CASE WHEN team1_id = ? THEN team2_score ELSE team1_score END AS score_contre,
                                winner_id
                            FROM stg_matches
                            WHERE (team1_id = ? OR team2_id = ?) AND status = 'finished'
                            ORDER BY begin_at DESC
                            LIMIT 5
                        """, params=[row["team_id"]] * 5).df()

                        for _, match in historique.iterrows():
                            texte = f"vs {match['adversaire']} - {match['score_pour']} - {match['score_contre']}"
                            if match["winner_id"] == row["team_id"]:
                                st.success(texte)
                            else:
                                st.error(texte )
                st.divider()

with tab_series:
    st.write("Navigation entre series a venir")

with tab_joueurs:
    st.info("Comming Soon.")

with tab_equipes:
    st.info("Coming Soon.")

with tab_pickban:
    st.info("Coming Soon.")
