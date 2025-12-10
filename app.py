import pickle
import streamlit as st
import requests
import pandas as pd



API_KEY = "8265bd1679663a7ea12ac168da84d2e8"

session = requests.Session()   # GLOBAL session for FAST requests


@st.cache_data
def fetch_poster(movie_id):
    """Fast poster fetch with session reuse"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    data = session.get(url).json()
    poster_path = data.get('poster_path')
    return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else ""


@st.cache_data
def fetch_movie_details(movie_id):
    """Fast rating + overview fetch with session reuse"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    data = session.get(url).json()

    rating = data.get('vote_average', 'N/A')
    overview = data.get('overview', 'No description available.')

    return rating, overview


def recommend(movie):
    """Recommend 5 similar movies"""
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])),
                       reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_ratings = []
    recommended_overviews = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]]['id']

        # FAST fetching
        poster = fetch_poster(movie_id)
        rating, overview = fetch_movie_details(movie_id)

        recommended_movie_posters.append(poster)
        recommended_movie_names.append(movies.iloc[i[0]]['title'])
        recommended_ratings.append(rating)
        recommended_overviews.append(
            overview[:150] + "..." if len(overview) > 150 else overview
        )

    return recommended_movie_names, recommended_movie_posters, recommended_ratings, recommended_overviews




st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)



st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #141414 0%, #1c1c1c 100%);
        color: white;
        font-family: 'Arial', sans-serif;
    }
    .main {
        background: linear-gradient(135deg, #141414 0%, #1c1c1c 100%);
        color: white;
    }
    h1 {
        color: #E50914 !important;
        text-align: center;
        font-family: 'Trebuchet MS', sans-serif;
        font-size: 3.5em;
        margin-top: -20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .subtitle {
        text-align: center;
        color: #b3b3b3;
        font-size: 1.2em;
        margin-bottom: 30px;
    }
    .stSelectbox, .stButton>button {
        background-color: #E50914 !important;
        color: white !important;
        border-radius: 10px;
        border: none;
        font-size: 16px;
        padding: 10px;
        transition: background-color 0.3s ease;
    }
    .stSelectbox:hover, .stButton>button:hover {
        background-color: #f40612 !important;
    }
    .movie-card {
        text-align: center;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 15px;
        margin: 10px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    .movie-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.5);
    }
    .movie-card img {
        border-radius: 10px;
        width: 100%;
        height: auto;
        transition: transform 0.3s ease;
    }
    .movie-title {
        color: white;
        font-size: 18px;
        font-weight: bold;
        margin-top: 10px;
    }
    .movie-rating {
        color: #E50914;
        font-size: 16px;
        margin: 5px 0;
    }
    .movie-overview {
        color: #b3b3b3;
        font-size: 14px;
        margin-top: 10px;
        line-height: 1.4;
    }
    .footer {
        text-align: center;
        color: #b3b3b3;
        margin-top: 50px;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------- Load Models ----------------------

movies = pickle.load(open('model/movie_list.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))

if isinstance(movies, dict):
    movies = pd.DataFrame(movies)

# ---------------------- UI Layout ----------------------

st.markdown("<h1>🎬 Movie Recommender</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Discover your next favorite movie with AI-powered recommendations!</p>",
            unsafe_allow_html=True)

with st.sidebar:
    st.header("About")
    st.write("This app recommends movies using machine learning.")
    st.write("Powered by TMDB API and Streamlit.")

movie_list = movies['title'].tolist()
selected_movie = st.selectbox("🎥 Type or select a movie from the list", movie_list)

if st.button("🔍 Show Recommendations"):
    with st.spinner("Fetching recommendations..."):
        names, posters, ratings, overviews = recommend(selected_movie)

    st.markdown("### Recommended Movies")
    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            st.markdown(f"""
                <div class="movie-card">
                    <img src="{posters[i]}" alt="{names[i]}">
                    <div class="movie-title">{names[i]}</div>
                    <div class="movie-rating"> {ratings[i]}</div>
                    <div class="movie-overview">{overviews[i]}</div>
                </div>
            """, unsafe_allow_html=True)

st.markdown("<div class='footer'>Made with  using Streamlit | Data from TMDB</div>",
            unsafe_allow_html=True)
