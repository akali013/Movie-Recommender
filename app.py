from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
import json
import nltk
from nltk.corpus import stopwords
from urllib import request as url_request

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# NLTK initialization
nltk.download("stopwords")
nltk.download("punkt")
stopwordList = set(stopwords.words("english"))

# Sentence-BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')
API_KEY = "fb113353"  # Replace with your OMDb API key

# Movie search logic (from the enhanced program)
def search_and_rank_movies(title, genre, plot):
    # Fetch movies from OMDb
    if title:
        searchUrl = f"https://www.omdbapi.com/?apikey={API_KEY}&s={title.replace(' ', '%20')}&type=movie"
    elif genre:
        searchUrl = f"https://www.omdbapi.com/?apikey={API_KEY}&s={genre.replace(' ', '%20')}&type=movie"
    else:
        searchUrl = f"https://www.omdbapi.com/?apikey={API_KEY}&s=movie&type=movie"

    try:
        searchJSON = url_request.urlopen(searchUrl).read().decode("utf8")
        searchJSON = json.loads(searchJSON)
        resultList = searchJSON.get("Search", [])
    except Exception as e:
        return {"error": f"Error fetching movies: {str(e)}"}, 500

    rankedMovieInfo = []
    plots = []
    titles = []

    for movie in resultList:
        try:
            id = movie["imdbID"]
            movieUrl = f"https://www.omdbapi.com/?apikey={API_KEY}&i={id}&type=movie&plot=full"
            movieJSON = json.loads(url_request.urlopen(movieUrl).read().decode("utf8"))
            rankedMovieInfo.append(movieJSON)
            plots.append(movieJSON.get("Plot", ""))
            titles.append(movieJSON.get("Title", "Unknown Title"))
        except Exception as e:
            print(f"Error processing movie {movie['Title']}: {e}")

    # Compute semantic similarity between the query plot and movie plots
    queryEmbedding = model.encode(plot, convert_to_tensor=True)
    plotEmbeddings = model.encode(plots, convert_to_tensor=True)
    similarityScores = util.cos_sim(queryEmbedding, plotEmbeddings).squeeze().tolist()

    # Combine titles and scores into a sorted list
    rankedResults = sorted(
        zip(titles, similarityScores), key=lambda x: x[1], reverse=True
    )
    return [{"title": title, "score": score} for title, score in rankedResults]

# API Endpoint
@app.route("/search", methods=["POST"])
def search_movies():
    try:
        # Retrieve input data from the frontend
        data = request.json
        print("Received Data:", data)

        title = data.get("title", "")
        genre = data.get("genre", "")
        plot = data.get("plot", "")
        print(f"Title: {title}, Genre: {genre}, Plot: {plot}")

        # Perform search and ranking
        results = search_and_rank_movies(title, genre, plot)
        print("Results:", results)

        return jsonify(results)
    except Exception as e:
        print("Error in search_movies:", str(e))
        return jsonify({"error": "Internal server error occurred"}), 500


# Main entry point
if __name__ == "__main__":
    app.run(debug=True)
