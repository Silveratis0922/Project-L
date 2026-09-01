import duckdb
import streamlit as st

st.set_page_config(page_title="LEC Stats", layout="wide")

st.title("LEC Stats - Summer 2026")

MOIS_FR = {
    1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
    7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre",
}


def format_date_fr(dt) -> str:
    return f"{dt.day} {MOIS_FR[dt.month]} {dt.year}"


def toggle_equipe(team_id):
    if st.session_state.equipe_ouverte == team_id:
        st.session_state.equipe_ouverte = None
    else:
        st.session_state.equipe_ouverte = team_id


@st.cache_data(ttl=600)
def get_calendrier():
    with duckdb.connect("lec_stats.duckdb", read_only=True) as con:
        return con.sql("""
            SELECT 
                begin_at, status,
                team1_name, team1_logo, team1_acronym,
                team2_name, team2_logo, team2_acronym,
                team1_score, team2_score
            FROM calendrier
            ORDER BY begin_at
        """).df()


@st.cache_data(ttl=600)
def get_classement():
    with duckdb.connect("lec_stats.duckdb", read_only=True) as con:
        return con.sql("""
            SELECT tournament_name, team_id, team_name, team_logo, team_acronym, wins, losses
            FROM classement
            ORDER BY tournament_name, wins DESC
        """).df()


@st.cache_data(ttl=600)
def get_historique(team_id):
    with duckdb.connect("lec_stats.duckdb", read_only=True) as con:
        return con.sql("""
            SELECT
                begin_at,
                CASE WHEN team1_id = ? THEN team2_name ELSE team1_name END AS adversaire,
                CASE WHEN team1_id = ? THEN team2_logo ELSE team1_logo END AS logo_adversaire,
                CASE WHEN team1_id = ? THEN team2_acronym ELSE team1_acronym END AS acronyme_adversaire,
                CASE WHEN team1_id = ? THEN team1_score ELSE team2_score END AS score_pour,
                CASE WHEN team1_id = ? THEN team2_score ELSE team1_score END AS score_contre,
                winner_id
            FROM stg_matches
            WHERE (team1_id = ? OR team2_id = ?) AND status = 'finished'
            ORDER BY begin_at DESC
            LIMIT 5
        """, params=[team_id] * 7).df()


tab_calendrier, tab_classement, tab_series, tab_joueurs, tab_equipes, tab_pickban = st.tabs(
    ["📅 Calendrier", "🏅 Classement", "🗂️ Séries", "📊 Stats Joueurs", "🛡️ Stats Équipes", "🎯 Pick / Ban"]
)

with tab_calendrier:
    st.markdown("""
        <style>
        .match-calendrier {
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: rgba(255, 255, 255, 0.04);
            border-radius: 10px;
            padding: 10px 16px;
            margin-bottom: 8px;
            transition: background-color 0.2s;
        }
        .match-calendrier:hover {
            background-color: rgba(255, 255, 255, 0.09);
        }
        </style>
    """, unsafe_allow_html=True)

    df_calendrier = get_calendrier()
    df_calendrier["date"] = df_calendrier["begin_at"].apply(format_date_fr)
    df_calendrier["heure"] = df_calendrier["begin_at"].dt.strftime("%H:%M")

    for date_str in df_calendrier["date"].unique():
        col_gauche, col_centre, col_droite = st.columns([1, 2, 1])
        with col_centre:
            st.subheader(date_str)

        matchs_du_jour = df_calendrier[df_calendrier["date"] == date_str]

        for _, match in matchs_du_jour.iterrows():
            if match["status"] == "finished":
                case_central = f"{match['team1_score']} - {match['team2_score']}"
                team1_gagne = match["team1_score"] > match["team2_score"]
                team2_gagne = match["team2_score"] > match["team1_score"]
            else:
                case_central = match["heure"]
                team1_gagne = False
                team2_gagne = False

            style1 = "font-weight: 800; color: #FFFFFF;" if team1_gagne else(
                "font-weight: 400; color: rgba(255, 255, 255, 0.28);" if match["status"] == "finished" else "font-weight: 600;"
            )
            style2 = "font-weight: 800; color: #FFFFFF;" if team2_gagne else (
                "font-weight: 400; color: rgba(255, 255, 255, 0.28);" if match["status"] == "finished" else "font-weight: 600;"
            )

            col_gauche, col_centre, col_droite = st.columns([1, 2, 1])
            with col_centre:
                st.markdown(f"""
                    <div class="match-calendrier">
                        <div style="display: flex; align-items: center; justify-content: flex-end; width: 140px;">
                            <strong style="margin-right: 8px; {style1}">{match['team1_acronym']}</strong>
                            <img src="{match['team1_logo']}" width="28">
                        </div>
                        <div style="width: 70px; text-align: center; font-weight: bold;
                                    border: 1px solid rgba(255, 255, 255, 0.25); border-radius: 6px;
                                    padding: 4px 0; margin: 0 12px; background-color: rgba(0, 0, 0, 0.25);">
                            {case_central}
                        </div>
                        <div style="display: flex; align-items: center; justify-content: flex-start; width: 140px;">
                            <img src="{match['team2_logo']}" width="28" style="margin-right: 8px;">
                            <strong style="{style2}">{match['team2_acronym']}</strong>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        st.divider()
# with tab_calendrier:
#     df_calendrier = get_calendrier()
#     df_calendrier["date"] = df_calendrier["begin_at"].apply(format_date_fr)
#     df_calendrier["heure"] = df_calendrier["begin_at"].dt.strftime("%H:%M")

#     for date_str in df_calendrier["date"].unique():
#         st.subheader(date_str)
#         match_du_jour = df_calendrier[df_calendrier["date"] == date_str]

#         for _, match in match_du_jour.iterrows():
#             col_heure, col_team1, col_score, col_team2 = st.columns([1, 3, 2, 3])
#             col_heure.write(match["heure"])
#             col_team1.write(match["team1_name"])
#             if match["status"] == "finished":
#                 col_score.write(f"{match['team1_score']} - {match['team2_score']}")
#             else:
#                 col_score.write("vs")
#             col_team2.write(match["team2_name"])

#         st.divider()

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
        .match-historique:hover {
            filter: brightness(1.4);
        }
        </style>
    """, unsafe_allow_html=True)

    df_classement = get_classement()

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
                    col_logo.image(row["team_logo"], width=40)
                    col_nom.button(
                        row["team_name"],
                        key=f"btn_{key_ligne}",
                        type="tertiary",
                        use_container_width=True,
                        on_click=toggle_equipe,
                        args=(row["team_id"],),
                    )
                    col_score.write(f"{row['wins']} - {row['losses']}")

                if st.session_state.equipe_ouverte == row["team_id"]:
                    historique = get_historique(row["team_id"])
                    for _, match in historique.iterrows():
                        victoire = match["winner_id"] == row["team_id"]
                        couleur = "rgba(46, 204, 113, 0.25)" if victoire else "rgba(231, 76, 60, 0.25)"

                        col_gauche2, col_centre2, col_droite2 = st.columns([1, 1, 1])
                        with col_centre2:
                            st.markdown(f"""
                                <div class="match-historique" style="display: flex; align-items: center; justify-content: center;
                                            background-color: {couleur}; border-radius: 8px;
                                            padding: 8px; margin-bottom: 6px;">
                                    <div style="display: flex; align-items: center; justify-content: flex-end; width: 100px;">
                                        <img src="{row['team_logo']}" width="24" style="margin-right: 6px;">
                                        <strong>{row['team_acronym']}</strong>
                                    </div>
                                    <div style="width: 50px; text-align: center; font-weight: bold; border: 1px solid rgba(255, 255, 255, 0.25); border-radius: 6px; padding: 2px 0; background-color: rgba(0, 0, 0, 0.25); margin: 0 8px;">
                                        {match['score_pour']} - {match['score_contre']}
                                    </div>
                                    <div style="display: flex; align-items: center; justify-content: flex-start; width: 100px;">
                                        <strong>{match['acronyme_adversaire']}</strong>
                                        <img src="{match['logo_adversaire']}" width="24" style="margin-left: 6px; margin-right: 6px;">
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)

                            # st.markdown(f"""
                            #     # <div style="background-color: {couleur}; border-radius: 8px;
                            #     #         padding: 8px; text-align: center; margin-bottom: 6px;">
                            #     #     <img src="{row['team_logo']}" width="24" style="vertical-align: middle; margin-right: 4px;">
                            #     #     <strong>{row['team_acronym']}</strong>
                            #     #     &nbsp;&nbsp;{match['score_pour']} - {match['score_contre']}&nbsp;&nbsp;
                            #     #     <strong>{match['acronyme_adversaire']}</strong>
                            #     #     <img src="{match['logo_adversaire']}" width="24" style="vertical-align: middle; margin-left: 4px;">
                            #     # </div>
                            # """, unsafe_allow_html=True)

            st.divider()

with tab_series:
    st.write("Navigation entre series a venir")

with tab_joueurs:
    st.info("Comming Soon.")

with tab_equipes:
    st.info("Coming Soon.")

with tab_pickban:
    st.info("Coming Soon.")
