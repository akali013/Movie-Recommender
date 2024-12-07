from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
import json
import nltk
from nltk.corpus import stopwords
from urllib import request as url_request
from nltk import word_tokenize
from nltk import PorterStemmer

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# NLTK initialization
nltk.download("stopwords")
nltk.download("punkt")
stopwordList = set(stopwords.words("english"))
porter = PorterStemmer()

# Sentence-BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')
API_KEY = "fb113353"  # OMDb API key

queryData = []
moviesData = []

# Transforms a query/movie into a document containing its vocabulary (stemmed, stopword removed, and tokenized) terms of its JSON field values 
# isMovie is True when a movie is passed to it, and False when the query is passed to it
def process(movie, isMovie):
    if isMovie:
        # Remove unimportant fields for movies
        for key in ["Ratings", "Poster", "BoxOffice", "Production", "Website"]:
            movie.pop(key, None)

    # Apply stopword removal, stemming, and tokenization
    plotTerms = movie["Plot"].split()
    movie["Plot"] = [word for word in plotTerms if not word.lower() in stopwordList]  # Remove stopwords
    movie["Plot"] = " ".join([porter.stem(word) for word in plotTerms])# Stem each word
    rawMovie = " ".join(movie.values())  # Combine all text fields
    movieTerms = word_tokenize(rawMovie) # Tokenize
    movieDoc = " ".join(movieTerms)      # Convert back to string
    return movieDoc
    

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
        resultList = searchJSON.get("Search", [])   # Movies from the search request type
    except Exception as e:
        return {"error": f"Error fetching movies: {str(e)}"}, 500
    
    # If the search had no results
    if len(resultList) == 0:
        return "No results found"

    rankedMovieInfo = []
    titles = []
    posters = []

    for movie in resultList:
        try:
            id = movie["imdbID"]
            movieUrl = f"https://www.omdbapi.com/?apikey={API_KEY}&i={id}&type=movie&plot=full"  # Get genres and plot of current movie
            movieJSON = json.loads(url_request.urlopen(movieUrl).read().decode("utf8"))
            rankedMovieInfo.append(movieJSON)
            posters.append(movieJSON.get("Poster", ""))
            titles.append(movieJSON.get("Title", "Unknown Title"))
            moviesData.append(process(movieJSON, True))   # Process current movie

        except Exception as e:
            print(f"Error processing movie {movie['Title']}: {e}")

    # Compute semantic similarity between the query data and movies data
    print(queryData)
    print(moviesData)
    queryEmbedding = model.encode(queryData, convert_to_tensor=True)
    movieEmbeddings = model.encode(moviesData, convert_to_tensor=True)
    similarityScores = util.cos_sim(queryEmbedding, movieEmbeddings).squeeze().tolist()

    queryData.clear()
    # If only one movie is returned, do not sort it and return it as an array for the foreach in inputBoxes.js
    if len(moviesData) == 1:
        moviesData.clear()
        return [{"title": titles[0], "score": similarityScores, "poster": posters[0]}] 
    else:
        # Combine titles, scores, and posters into a sorted list
        rankedResults = sorted(
            zip(titles, similarityScores, posters), key=lambda x: x[1], reverse=True
        )
        moviesData.clear()
        return [{"title": title, "score": score, "poster": poster} for title, score, poster in rankedResults]

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
        query = {"Title": title, "Genre": genre, "Plot": plot}
        queryData.append(process(query, False))
        
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
