import json
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from urllib import request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# nltk.download("stopwords")
# nltk.download("punkt_tab")
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

API_KEY = "fb113353"
porter = nltk.PorterStemmer()
stopwordList = set(stopwords.words("english"))
vectorizer = TfidfVectorizer()
documentVocabs = []  # Stores the vocabularies representing the query and each movie
resultList = []      # Will contain the information of every movie returned in the intial title search
posters = []         # Will contain the urls for every poster in resultList
websites = []        # Will contain the urls of every movie's website
rankedMovieInfo = [] # Will contain the readable full information of each movie

def initializeQuery():
    title = input("Enter a movie title (optional): ").strip()
    genre = input("Enter a genre (optional): ").strip()
    plot = input("Describe the plot (e.g., 'horror movie with poltergeists'): ").strip()
    query = {"Title": title, "Genre": genre, "Plot": plot}
    return query

def getMovies(query):
    if query["Title"]:
        # Use the title to narrow the search
        searchUrl = f"https://www.omdbapi.com/?apikey={API_KEY}&s={query['Title'].replace(' ', '%20')}&type=movie"
    elif query["Genre"]:
        # Use a broad genre-based search
        searchUrl = f"https://www.omdbapi.com/?apikey={API_KEY}&s={query['Genre'].replace(' ', '%20')}&type=movie"
    else:
        # Fallback to a generic broad search
        searchUrl = f"https://www.omdbapi.com/?apikey={API_KEY}&s=movie&type=movie"

    try:
        searchJSON = request.urlopen(searchUrl).read().decode("utf8")
        searchJSON = json.loads(searchJSON)
        return searchJSON.get("Search", [])  # Return the list of movies or an empty list if none found
    except Exception as e:
        print(f"Error fetching movies: {e}")
        return []    # List of movies that matched the query's title

# Takes each movie from the search result, processes it, and returns an array of the weighted vectors
def processMovies(resultList):
    for movie in resultList:
        try:
            id = movie["imdbID"]
            movieUrl = f"https://www.omdbapi.com/?apikey={API_KEY}&i={id}&type=movie&plot=full"
            movieJSON = json.loads(request.urlopen(movieUrl).read().decode("utf8"))
            rankedMovieInfo.append(movieJSON)  # Store detailed movie info
            posters.append(movieJSON.get("Poster", "No poster available"))
            websites.append(movieJSON.get("Website", "No website available"))
            process(movieJSON, True)  # Process movie for document vocabulary
        except Exception as e:
            print(f"Error processing movie {movie['Title']}: {e}")

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
    documentVocabs.append(movieDoc)

# Function to Compute Semantic Similarity
def computeSemanticSimilarity(query, plots):
    queryEmbedding = model.encode(query, convert_to_tensor=True)
    plotEmbeddings = model.encode(plots, convert_to_tensor=True)
    scores = util.cos_sim(queryEmbedding, plotEmbeddings).squeeze().tolist()
    return scores

# Function to Rank Movies Based on Query Similarity
def getRankings(query):
    # Use semantic similarity for ranking
    titles = [movie["Title"] for movie in rankedMovieInfo]
    genres = [movie["Genre"] for movie in rankedMovieInfo]
    plots = [movie["Plot"] for movie in rankedMovieInfo]
    queryData = query["Title"] + " " + query["Genre"] + " " + query["Plot"]
    moviesData = [f"{title} {genre} {plot}" for title, genre, plot in zip(titles, genres, plots)]
    similarityScores = computeSemanticSimilarity(queryData, moviesData)

    # Map similarity scores to movie titles
    rankings = dict(zip([movie["Title"] for movie in rankedMovieInfo], similarityScores))
    rankings = sorted(rankings.items(), key=lambda x: x[1], reverse=True)  # Sort by score descending
    return dict(rankings)


query = initializeQuery()              
process(query, False)                 
resultList = getMovies(query)        
processMovies(resultList)         
rankings = getRankings(query)     

# Print Rankings
for title, score in rankings.items():
    print(f"{title}: {score}")
