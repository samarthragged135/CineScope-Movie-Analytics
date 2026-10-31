
from click import style
import streamlit as st
import pandas as pd
import random
import os
import requests
import textwrap
from pathlib import Path
from urllib.parse import quote
from html import escape
from dotenv import load_dotenv
import streamlit.components.v1 as components
load_dotenv(Path(__file__).parent / ".env")
try:
    TMDB_API_KEY = os.getenv("TMDB_API_KEY") or st.secrets["TMDB_API_KEY"]
except Exception:
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# -----------------------------------
# PAGE CONFIGURATION
# -----------------------------------

st.set_page_config(
    page_title="CineScope",
    page_icon="🎬",
    layout="wide"
)

# -----------------------------------
# LOAD MOVIE DATA
# -----------------------------------

DATA_PATH = Path(__file__).parent / "data" / "movies_enriched.csv"

movies = pd.read_csv(DATA_PATH)

movies["Year"] = pd.to_numeric(movies["Year"], errors="coerce")
movies["Rating"] = pd.to_numeric(movies["Rating"], errors="coerce")
movies["Votes"] = pd.to_numeric(movies["Votes"], errors="coerce")
movies["Popularity"] = pd.to_numeric(movies["Popularity"], errors="coerce")
# -----------------------------------
# TMDB MOVIE INFORMATION
# -----------------------------------

@st.cache_data(ttl=3600)
def get_tmdb_movie(movie_id):

    if not TMDB_API_KEY:
        return None

    url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}"

    params = {
        "api_key": TMDB_API_KEY,
        "append_to_response": "credits,videos"
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    return response.json()

# -----------------------------------
# SESSION STATE
# -----------------------------------

if "featured_id" not in st.session_state:
    st.session_state.featured_id = random.choice(
        movies.index.tolist()
    )

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

movie_from_url = st.query_params.get("movie")

if movie_from_url:
    st.session_state.selected_movie = movie_from_url

# -----------------------------------
# CINE SCOPE DESIGN
# -----------------------------------

st.markdown("""
<style>
/* MAIN APP BACKGROUND */
.stApp {
    background:
        radial-gradient(ellipse at 8% 12%, rgba(137, 75, 230, 0.16), transparent 34%),
        radial-gradient(ellipse at 92% 35%, rgba(215, 48, 85, 0.11), transparent 32%),
        #09090D;
    color: #F7F4FC;
}

/* PAGE WIDTH AND SPACING */
.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

/* HEADINGS */
h1, h2, h3 {
    color: #FFFFFF !important;
    font-family: "Segoe UI", sans-serif;
    letter-spacing: -0.5px;
}

/* GENERAL TEXT */
p, label {
    color: #C2BDCC;
}

.movie-caption {
    color: #A6A3B2;
    font-size: 13px;
}

/* TOP HEADER */
header[data-testid="stHeader"] {
    background: transparent;
}

/* HIDE SIDEBAR */
section[data-testid="stSidebar"] {
    display: none;
}

/* BUTTONS */
div.stButton > button {
    background: linear-gradient(135deg, #191522, #211827);
    color: #F7F4FC;
    border: 1px solid #392B4B;
    border-radius: 10px;
    padding: 0.6rem 1rem;
    font-weight: 600;
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    background: linear-gradient(135deg, #7746C8, #B83E68);
    border-color: #A879FF;
    color: white;
    box-shadow: 0 0 18px rgba(152, 85, 245, 0.25);
    transform: translateY(-1px);
}

/* SEARCH INPUT */
.stTextInput input {
    background: #171321;
    color: white;
    border: 1px solid #392B4B;
    border-radius: 10px;
}

.stTextInput input:focus {
    border-color: #9855F5;
    box-shadow: 0 0 0 1px #9855F5;
}

/* MOVIE POSTERS */
div[data-testid="stImage"] img {
    border-radius: 12px;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    box-shadow: 0 5px 18px rgba(0, 0, 0, 0.3);
}

div[data-testid="stImage"] img:hover {
    transform: scale(1.025);
    box-shadow: 0 8px 25px rgba(137, 75, 230, 0.2);
}

/* DIVIDERS */
div[data-testid="stDivider"] hr {
    border-color: rgba(168, 121, 255, 0.2);
}

/* ALERTS */
div[data-testid="stAlert"] {
    background: #171321;
    border: 1px solid #392B4B;
    border-radius: 12px;
}

/* REMOVE EXTRA TOP SPACE */
div[data-testid="stVerticalBlock"] {
    gap: 1rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# TOP NAVIGATION
# -----------------------------------

nav1, nav2, nav3, nav4 = st.columns([2.5, 1, 1, 2])

with nav1:
    st.markdown(
        "<h2 style='color:#A879FF !important;'>🎬 CINE<span style='color:white;'>SCOPE</span></h2>",
        unsafe_allow_html=True
    )

with nav2:
    home_clicked = st.button("⌂  Home", use_container_width=True)

with nav3:
    explore_clicked = st.button("Explore", use_container_width=True)

with nav4:
    search = st.text_input(
        "Search",
        placeholder="Search movies...",
        label_visibility="collapsed"
    )

if home_clicked:
    st.session_state.search_query = ""
    st.rerun()

if explore_clicked:
    st.session_state.search_query = "EXPLORE"
    st.rerun()

st.divider()

# -----------------------------------
# SEARCH RESULTS
# -----------------------------------

if search:
    st.session_state.search_query = search
if st.session_state.selected_movie:

    selected = movies[
        movies["Movie"].astype(str) == str(st.session_state.selected_movie)
    ]

    if selected.empty:
        st.warning("Movie not found.")
    else:
        movie = selected.iloc[0]
        tmdb_data = get_tmdb_movie(movie["Movie_ID"])

        if st.button("← Back to Home"):
            st.session_state.selected_movie = None
            st.query_params.clear()
            st.rerun()

        st.divider()

        # -----------------------------------
        # CINEMATIC MOVIE HERO
        # -----------------------------------

        trailer_key = None

        if tmdb_data:
            videos = tmdb_data.get("videos", {}).get("results", [])

            trailers = [
                video for video in videos
                if video.get("site") == "YouTube"
                and video.get("type") == "Trailer"
                and video.get("key")
            ]

            if trailers:
                official = [
                    video for video in trailers
                    if video.get("official")
                ]

                trailer_key = (
                    official[0]["key"] if official
                    else trailers[0]["key"]
                )

        backdrop = movie.get("Backdrop_URL", "")
        poster = movie.get("Poster_URL", "")

        valid_backdrop = (
            pd.notna(backdrop)
            and str(backdrop).startswith("http")
        )

        valid_poster = (
            pd.notna(poster)
            and str(poster).startswith("http")
        )

        title = escape(str(movie["Movie"]))
        poster_url = escape(str(poster), quote=True) if valid_poster else ""
        backdrop_url = escape(str(backdrop), quote=True) if valid_backdrop else ""

        year = movie.get("Year", "N/A")
        rating = movie.get("Rating", 0)
        runtime = movie.get("Runtime", "N/A")

        director = "Not available"

        if tmdb_data:
            director = next(
                (
                    person["name"]
                    for person in tmdb_data.get("credits", {}).get("crew", [])
                    if person.get("job") == "Director"
                ),
                "Not available"
            )

        director = escape(str(director))

        video_html = ""

        if trailer_key:
            video_html = f"""
                <iframe
                    src="https://www.youtube.com/embed/{escape(trailer_key)}?autoplay=1&mute=1&loop=1&playlist={escape(trailer_key)}&controls=0&rel=0&playsinline=1"
                    frameborder="0"
                    allow="autoplay; encrypted-media; picture-in-picture"
                    allowfullscreen>
                </iframe>
            """
        elif valid_backdrop:
            video_html = f"""
                <div class="hero-backdrop"
                     style="background-image:url('{backdrop_url}');">
                </div>
            """
        
            

        
        
        components.html(
            textwrap.dedent(f"""
            <style>
                * {{
                    box-sizing: border-box;
                }}

                body {{
                    margin: 0;
                    padding: 0;
                    background: #09090D;
                }}

                .cinema-hero {{
                    position: relative;
                    width: 100%;
                    height: 620px;
                    overflow: hidden;
                    background: #09090D;
                    border-radius: 16px;
                }}

                .cinema-hero iframe,
                .cinema-hero .hero-backdrop {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    border: 0;
                    z-index: 0;
                }}

                .cinema-hero iframe {{
                    transform: scale(1.25);
                    pointer-events: none;
                }}

                .hero-backdrop {{
                    background-size: cover;
                    background-position: center;
                }}

                .cinema-overlay {{
                    position: absolute;
                    inset: 0;
                    z-index: 1;
                    background: linear-gradient(
                        to bottom,
                        rgba(9,9,13,0.05) 0%,
                        rgba(9,9,13,0.15) 40%,
                        rgba(9,9,13,0.75) 75%,
                        #09090D 100%
                    );
                }}

                .hero-content {{
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    right: 0;
                    z-index: 2;
                    display: flex;
                    align-items: flex-end;
                    gap: 28px;
                    padding: 35px;
                    color: white;
                }}

                .hero-poster {{
                    width: 175px;
                    min-width: 175px;
                    border-radius: 12px;
                    box-shadow: 0 12px 35px rgba(0,0,0,0.7);
                }}

                .hero-info {{
                    padding-bottom: 8px;
                    color: white;
                }}

                .hero-info h1 {{
                    font-size: 42px;
                    font-weight: 750;
                    margin: 0 0 12px 0;
                    color: white;
                }}

                .hero-meta {{
                    color: #dddddf;
                    font-size: 15px;
                    line-height: 1.9;
                }}

                .hero-director {{
                    color: #c4c4ce;
                    font-size: 14px;
                    margin-top: 8px;
                }}

                @media(max-width: 700px) {{
                    .cinema-hero {{
                        height: 540px;
                    }}

                    .hero-content {{
                        gap: 15px;
                        padding: 18px;
                    }}

                    .hero-poster {{
                        width: 115px;
                        min-width: 115px;
                    }}

                    .hero-info h1 {{
                        font-size: 25px;
                    }}
                }}
            </style>

            <div class="cinema-hero">
                {video_html}

                <div class="cinema-overlay"></div>

                <div class="hero-content">
                    {
                        f'<img class="hero-poster" src="{poster_url}">'
                        if valid_poster else ''
                    }

                    <div class="hero-info">
                        <h1>{title}</h1>

                        <div class="hero-meta">
                            {year} &nbsp; · &nbsp;
                            ⭐ {rating}/10 &nbsp; · &nbsp;
                            {runtime} min
                        </div>

                        <div class="hero-director">
                            Directed by {director}
                        </div>
                    </div>
                </div>
            </div>
            """),
            height=650,
            scrolling=False
        )

        # -----------------------------------
        # MOVIE OVERVIEW
        # -----------------------------------

        st.subheader("Overview")

        overview = movie.get("Overview", "No overview available.")

        if pd.isna(overview):
            overview = "No overview available."

        st.write(overview)


elif st.session_state.search_query == "EXPLORE":

    st.subheader("Explore Movies")
    st.caption("The full movie catalogue will be available here soon.")

elif st.session_state.search_query:

    results = movies[
        movies["Movie"].str.contains(
            st.session_state.search_query,
            case=False,
            na=False
        )
    ]

    st.subheader("Search Results")

    if results.empty:
        st.info("No movies found.")
    else:
        cols = st.columns(3)

        for i, (_, movie) in enumerate(results.head(12).iterrows()):
            with cols[i % 3]:
                if pd.notna(movie["Poster_URL"]):
                    st.image(movie["Poster_URL"], use_container_width=True)

                st.markdown(f"**{movie['Movie']}**")
                st.caption(f"{movie['Year']} · ⭐ {movie['Rating']}")

# -----------------------------------
# HOMEPAGE
# -----------------------------------

else:

  
            
    # -----------------------------------
    # FEATURED MOVIE
    # -----------------------------------

    featured_titles = [
        "The Shawshank Redemption",
        "The Godfather",
        "The Dark Knight",
        "Pulp Fiction",
        "Fight Club",
        "Interstellar",
        "Inception",
        "Parasite",
        "Whiplash",
        "Goodfellas",
        "The Prestige",
        "Se7en",
        "Schindler's List",
        "The Green Mile",
        "Forrest Gump",
        "Gladiator",
        "The Matrix",
        "12 Angry Men",
        "The Silence of the Lambs",
        "Spirited Away"
    ]

    featured_pool = movies[
        movies["Movie"].isin(featured_titles)
    ].copy()

    if featured_pool.empty:
        featured_pool = movies.nlargest(10, "Rating")

    featured_pool = featured_pool.reset_index(drop=True)

    import time

    @st.fragment(run_every="2m")
    def render_featured():

        if "featured_index" not in st.session_state:
            st.session_state.featured_index = 0

        now = time.monotonic()

        if "featured_last_rotation" not in st.session_state:
            st.session_state.featured_last_rotation = now

        elif now - st.session_state.featured_last_rotation >= 120:
            st.session_state.featured_index = (
                st.session_state.featured_index + 1
            ) % len(featured_pool)

            st.session_state.featured_last_rotation = now

        featured = featured_pool.iloc[
            st.session_state.featured_index % len(featured_pool)
        ]

        backdrop = featured.get("Backdrop_URL", "")

        if pd.isna(backdrop) or not str(backdrop).startswith("http"):
            backdrop = featured.get("Poster_URL", "")

        if pd.isna(backdrop) or not str(backdrop).startswith("http"):
            backdrop = ""

        title = featured["Movie"]
        year = int(featured["Year"]) if pd.notna(featured["Year"]) else "N/A"
        rating = featured["Rating"]
        genre = featured.get("Genre", "Movie")
        overview = featured.get("Overview", "")

        st.html(f"""
        <style>
        .cinema-hero {{
            position: relative;
            width: 100%;
            height: 460px;
            border-radius: 20px;
            overflow: hidden;
            background-color: #100d19;
            background-image:
                linear-gradient(
                    90deg,
                    rgba(12, 9, 20, 0.96) 0%,
                    rgba(12, 9, 20, 0.72) 40%,
                    rgba(12, 9, 20, 0.10) 100%
                ),
                linear-gradient(
                    0deg,
                    rgba(10, 7, 18, 0.85),
                    transparent 65%
                ),
                url("{backdrop}");
            background-size: cover;
            background-position: center;
            border: 1px solid rgba(177, 110, 255, 0.35);
            box-shadow:
                0 0 22px rgba(145, 75, 255, 0.20),
                0 0 55px rgba(145, 75, 255, 0.10);
        }}

        .cinema-content {{
            position: absolute;
            left: 5%;
            bottom: 12%;
            max-width: 55%;
            color: white;
            z-index: 2;
        }}

        .cinema-label {{
            color: #c69aff;
            font-size: 12px;
            letter-spacing: 3px;
            font-weight: 800;
        }}

        .cinema-content h1 {{
            color: white;
            font-size: 42px;
            font-weight: 850;
            margin: 12px 0;
            line-height: 1.15;
        }}

        .cinema-meta {{
            color: #d7c5f5;
            font-size: 14px;
            margin-bottom: 15px;
        }}

        .cinema-description {{
            color: #e1dce9;
            font-size: 14px;
            line-height: 1.7;
        }}

        .cinema-rating {{
            color: #d6adff;
            font-weight: 800;
        }}
        </style>

        <div class="cinema-hero">

            <div class="cinema-content">

                <div class="cinema-label">
                    ✦ C I N E S C O P E &nbsp; P I C K
                </div>

                <h1>{title}</h1>

                <div class="cinema-meta">
                    {year} &nbsp; • &nbsp; {genre}
                    &nbsp; • &nbsp;
                    <span class="cinema-rating">
                        ★ {rating:.1f}/10
                    </span>
                </div>

                <div class="cinema-description">
                    {str(overview)[:220]}
                </div>

            </div>

        </div>
        """)

    render_featured()

    st.divider()



               
    # MOVIE SECTION FUNCTION
    # MOVIE SECTION FUNCTION

    def movie_section(title, data):

        st.subheader(title)

        if data.empty:
            st.info("No movies available.")
            return

        columns = st.columns(6)

        for i, (_, movie) in enumerate(data.head(6).iterrows()):

            with columns[i]:

                poster = movie.get("Poster_URL")

                if pd.notna(poster) and str(poster).startswith("http"):

                    movie_link = quote(str(movie["Movie"]))

                    st.markdown(
                        f"""
                        <a href="?movie={movie_link}" target="_self">
                            <img src="{escape(str(poster), quote=True)}"
                                 style="width:100%; border-radius:12px; cursor:pointer;">
                        </a>
                        """,
                        unsafe_allow_html=True
                    )

                else:
                    st.markdown("🎬 Poster unavailable")

                st.markdown(f"**{movie['Movie']}**")

                year = int(movie["Year"]) if pd.notna(movie["Year"]) else "N/A"

                rating = movie["Rating"]

                st.caption(f"{year} · ⭐ {rating:.1f}")
                     

                
                    
                    
                    
                
                    
            

   
    
    # ACCLAIMED FILMMAKING

    acclaimed_titles = [
        "Interstellar",
        "Django Unchained",
        "The Grand Budapest Hotel",
        "Whiplash",
        "Parasite",
        "Dunkirk"
    ]

    acclaimed = movies.set_index("Movie").loc[acclaimed_titles].reset_index()

    movie_section("🎬 Acclaimed Filmmaking", acclaimed)


    # PSYCHOLOGICAL & CRIME THRILLERS

    thriller_titles = [
        "Shutter Island",
        "Gone Girl",
        "Prisoners",
        "Joker",
        "Get Out",
        "The Wolf of Wall Street"
    ]

    thrillers = movies.set_index("Movie").loc[thriller_titles].reset_index()

    movie_section("🧠 Psychological & Crime Thrillers", thrillers)


    # MODERN SCI-FI & CINEMATIC EPICS

    sci_fi_titles = [
        "Inception",
        "Arrival",
        "Blade Runner 2049",
        "The Martian",
        "Dune",
        "The Revenant"
    ]

    sci_fi = movies.set_index("Movie").loc[sci_fi_titles].reset_index()

    movie_section("🌌 Modern Sci-Fi & Cinematic Epics", sci_fi)



    # -----------------------------------
    # FOOTER
    # -----------------------------------

    st.divider()


st.markdown(
    "<center style='color:#777;'>CineScope · Discover your next favourite movie.</center>",
    unsafe_allow_html=True
)
