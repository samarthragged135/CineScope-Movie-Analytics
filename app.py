
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------
# PAGE CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="CineScope | Movie Analytics",
    page_icon="🎬",
    layout="wide"
)

# --------------------------------
# SAMPLE MOVIE DATA
# --------------------------------


from pathlib import Path

# Load movie database
DATA_PATH = Path(__file__).parent / "data" / "movies_enriched.csv"

movies = pd.read_csv(DATA_PATH)

# Check data types
movies["Year"] = movies["Year"].astype(int)
movies["Rating"] = movies["Rating"].astype(float)
movies["Votes"] = movies["Votes"].astype(int)



# --------------------------------
# CUSTOM DESIGN - NETFLIX THEME
# --------------------------------

st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #080808;
    color: #ffffff;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #141414;
    border-right: 1px solid #292929;
}

/* Main content spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

/* Headings */
h1, h2, h3 {
    color: #ffffff !important;
    font-weight: 700;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: #181818;
    border: 1px solid #303030;
    padding: 20px;
    border-radius: 12px;
}

/* Metric values */
div[data-testid="stMetricValue"] {
    color: #E50914;
}

/* Metric labels */
div[data-testid="stMetricLabel"] {
    color: #b3b3b3;
}

/* Buttons */
.stButton > button {
    background-color: #E50914;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 600;
}

/* Button hover */
.stButton > button:hover {
    background-color: #b20710;
    color: white;
    border: none;
}

/* Input fields */
.stTextInput input {
    background-color: #222222;
    color: white;
    border: 1px solid #444444;
}

/* Dividers */
hr {
    border-color: #333333;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    border: 1px solid #303030;
    border-radius: 10px;
}

/* Movie card containers */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #333333;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------
# SIDEBAR
# --------------------------------

st.sidebar.title("🎬 CineScope")
st.sidebar.caption("MOVIE & OTT ANALYTICS")
st.sidebar.divider()

st.sidebar.subheader("Dashboard Filters")

genres = ["All"] + sorted(movies["Genre"].unique().tolist())


selected_genre = st.sidebar.selectbox(
    "Select Genre",
    genres
)

selected_platform = "All"
search_query = st.sidebar.text_input(
    "🔎 Search Movies",
    placeholder="Enter movie name..."
)
selected_year = st.sidebar.slider(
    "Release Year",
    min_value=int(movies["Year"].min()),
    max_value=int(movies["Year"].max()),
    value=(int(movies["Year"].min()), int(movies["Year"].max()))
)

st.sidebar.divider()
st.sidebar.caption("CineScope | Python Mini Project")

# --------------------------------
# FILTER DATA
# --------------------------------

filtered = movies.copy()

if selected_genre != "All":
    filtered = filtered[filtered["Genre"] == selected_genre]


    filtered = filtered[filtered["Platform"] == selected_platform]

filtered = filtered[
    filtered["Year"].between(selected_year[0], selected_year[1])
]
if search_query:
    filtered = filtered[
        filtered["Movie"].str.contains(
            search_query,
            case=False,
            na=False
        )
    ]
# --------------------------------
# MAIN DASHBOARD
# --------------------------------

st.title("🎬 CineScope")
st.markdown("### Your Movie & OTT Intelligence Dashboard")

st.caption(
    "Explore movies, discover genres and compare streaming platforms."
)

st.divider()

# --------------------------------
# METRIC CARDS
# --------------------------------

col1, col2, col3, col4 = st.columns(4)

total_movies = len(filtered)

average_rating = (
    filtered["Rating"].mean() if total_movies else 0
)

total_genres = filtered["Genre"].nunique()

col1.metric("🎞️ Total Movies", total_movies)

col2.metric("⭐ Average Rating", f"{average_rating:.2f}/10")

col3.metric("🎭 Genres", total_genres)

col4.metric("🗳️ Total Votes", f"{filtered['Votes'].sum():,}")

st.divider()


# --------------------------------
# FEATURED MOVIE - HERO SECTION
# --------------------------------

featured = movies[movies["Movie"] == "Inception"].iloc[0]

hero_col1, hero_col2 = st.columns([1.4, 1])


with hero_col1:

    st.markdown("### 🔴 CINESCOPE | FEATURED")

    st.title(featured["Movie"])

    st.write(
        f"📅 {featured['Year']}  |  "
        f"🎭 {featured['Genre']}"
    )

    st.subheader(f"⭐ {featured['Rating']}/10")

    

    st.caption("FEATURED MOVIE")

with hero_col2:

    st.image(
        "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
        use_container_width=True
    )




# --------------------------------
# CHARTS
# --------------------------------

if not filtered.empty:

    left, right = st.columns(2, gap="large")

    # GENRE DISTRIBUTION
    with left:

        st.subheader("🎭 Movies by Genre")
        st.caption("Explore the genre breakdown of your collection.")

        genre_data = (
            filtered.groupby("Genre")
            .size()
            .reset_index(name="Movies")
        )

        fig_genre = px.pie(
            genre_data,
            names="Genre",
            values="Movies",
            hole=0.62,
            color_discrete_sequence=[
                "#E50914",
                "#F05A67",
                "#B20710",
                "#8C8C8C",
                "#D9D9D9",
                "#6B6B6B",
                "#A8323E"
            ]
        )

        fig_genre.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(
                line=dict(color="#080808", width=3)
            ),
            hovertemplate="<b>%{label}</b><br>Movies: %{value}<br>Share: %{percent}<extra></extra>"
        )

        fig_genre.update_layout(
            template="plotly_dark",
            paper_bgcolor="#080808",
            plot_bgcolor="#080808",
            font=dict(
                family="Arial",
                color="#FFFFFF",
                size=12
            ),
            showlegend=False,
            margin=dict(t=25, b=25, l=15, r=15),
            height=390
        )

        st.plotly_chart(
            fig_genre,
            use_container_width=True
        )

       # MOVIE LANGUAGE DISTRIBUTION
    with right:

        st.subheader("🌍 Movie Language Distribution")
        st.caption("Explore the languages represented in the movie collection.")

        language_data = (
            filtered["Language"]
            .fillna("Unknown")
            .value_counts()
            .head(10)
            .sort_values(ascending=True)
            .reset_index()
        )

        language_data.columns = ["Language", "Movies"]

        fig_language = px.bar(
            language_data,
            x="Movies",
            y="Language",
            orientation="h",
            color="Movies",
            text="Movies",
            color_continuous_scale=["#5C1017", "#E50914"]
        )

        fig_language.update_traces(
            textposition="outside",
            marker_line_width=0,
            hovertemplate="<b>%{y}</b><br>Movies: %{x}<extra></extra>"
        )

        fig_language.update_layout(
            template="plotly_dark",
            paper_bgcolor="#080808",
            plot_bgcolor="#080808",
            font=dict(
                family="Arial",
                color="#FFFFFF",
                size=12
            ),
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(t=25, b=35, l=15, r=35),
            height=390,
            xaxis=dict(
                title="Number of Movies",
                showgrid=True,
                gridcolor="#292929",
                zeroline=False
            ),
            yaxis=dict(
                title="",
                showgrid=False
            )
        )

        st.plotly_chart(
            fig_language,
            use_container_width=True
        )


    # --------------------------------
    # TOP MOVIES
    # --------------------------------

    st.divider()
    
   
    # --------------------------------
    # MOVIE EXPLORER
    # --------------------------------
    movie_columns = st.columns(3)
    for index, (_, movie) in enumerate(filtered.iterrows()):

        with movie_columns[index % 3]:

            with st.container(border=True):

                poster = movie["Poster_URL"]

                if pd.notna(poster) and str(poster).strip():
                    st.image(
                        poster,
                        width="stretch"
                    )
                else:
                    st.markdown(
                        """
                        <div style="
                            height: 350px;
                            background: linear-gradient(135deg, #181818, #303030);
                            border-radius: 10px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: #E50914;
                            font-size: 55px;">
                            🎬
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown(f"### {movie['Movie']}")

                st.markdown(
                    f"⭐ **{movie['Rating']}/10**  ·  {movie['Year']}"
                )

                st.caption(
                    f"{movie['Genre']}  •  {movie['Language']}"
                )

                st.progress(float(movie["Rating"]) / 10)



    
    # --------------------------------
    # TOP RATED MOVIES
    # --------------------------------

    st.divider()
    st.header("🏆 Top 10 Highest Rated Movies")

    st.caption("The highest-rated movies in the selected collection.")

    top_movies = filtered.sort_values(
        by="Rating",
        ascending=False
    ).head(10)

    ranking_columns = st.columns(2, gap="large")

    for index, (_, movie) in enumerate(top_movies.iterrows()):

        with ranking_columns[index % 2]:

            with st.container(border=True):

                poster_col, details_col = st.columns([1, 2])

                with poster_col:

                    if pd.notna(movie["Poster_URL"]) and str(movie["Poster_URL"]).strip():
                        st.image(
                            movie["Poster_URL"],
                            width="stretch"
                        )
                    else:
                        st.markdown("🎬")

                with details_col:

                    st.markdown(f"### #{index + 1}")

                    st.markdown(f"**{movie['Movie']}**")

                    st.markdown(
                        f"⭐ **{movie['Rating']}/10**"
                    )

                    st.caption(
                        f"{movie['Year']} · {movie['Genre']}"
                    )

                    

                    st.progress(float(movie["Rating"]) / 10)


    # --------------------------------
    # RATING ANALYSIS
    # --------------------------------

    st.divider()
    st.subheader("📊 Movie Rating Analysis")

    fig_rating = px.bar(
        filtered.sort_values("Rating", ascending=False),
        x="Movie",
        y="Rating",
        color="Rating",
        color_continuous_scale="Purples",
        hover_data=["Genre", "Year", "Language"]
    )

    fig_rating.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b0d14",
        plot_bgcolor="#0b0d14",
        xaxis_title="Movie",
        yaxis_title="Rating",
        yaxis_range=[0, 10]
    )

    st.plotly_chart(
        fig_rating,
        use_container_width=True
    )

else:
    st.warning("No movies match the selected filters.")

# --------------------------------
# FOOTER
# --------------------------------

st.divider()

st.caption(
    "CineScope | Built with Python, Streamlit, Pandas and Plotly"
)

st.caption(
    "Note: This is prototype data for demonstration. "
    "Ratings and vote counts are illustrative, not verified live statistics."
)
