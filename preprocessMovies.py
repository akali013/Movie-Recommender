import json
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from urllib import request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# nltk.download("stopwords")
# nltk.download("punkt_tab")

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
    documentVocabs.clear()   # Clear old vocabularies
    # Replace with values from JS frontend
    query = {
        "Title": "dragon ball",
        "Genre": "Animation",
        "Plot": "androids"
    }
    return query

def getMovies():
    searchUrl = f"https://www.omdbapi.com/?apikey={API_KEY}&s={query['Title'].replace(' ', '%20')}&type=movie"
    searchJSON = request.urlopen(searchUrl).read().decode("utf8") 
    searchJSON = json.loads(searchJSON)
    return searchJSON["Search"]    # List of movies that matched the query's title

# Takes each movie from the search result, processes it, and returns an array of the weighted vectors
def processMovies(resultList):
    for i in range(len(resultList)):
        id = resultList[i]["imdbID"]
        movieUrl = f"https://www.omdbapi.com/?apikey={API_KEY}&i={id}&type=movie&plot=full"   # Get movie's full information via its IMDb ID
        movieJSON = request.urlopen(movieUrl).read().decode("utf8")
        movieJSON = json.loads(movieJSON)
        rankedMovieInfo.append(movieJSON)
        process(movieJSON, True)

# Transforms a query/movie into a document containing its vocabulary (stemmed, stopword removed, and tokenized) terms of its JSON field values 
# isMovie is True when a movie is passed to it, and False when the query is passed to it
def process(movie, isMovie):
    if isMovie:
        # Remove redundant or unimportant fields
        del movie["Ratings"]       # Ratings already covered by metascore and imdbrating values
        posters.append(movie["Poster"])  
        websites.append(movie["Website"])  
        del movie["Poster"]
        del movie["BoxOffice"]
        del movie["Production"]
        del movie["Website"]
        
    # Apply the same processing to the query and movies
    plotTerms = movie["Plot"].split()
    movie["Plot"] = [word for word in plotTerms if not word.lower() in stopwordList]  # Remove stopwords from plot
    movie["Plot"] = " ".join([porter.stem(word) for word in plotTerms])    # Stem each plot term and convert from list to string
    rawMovie = " ".join(movie.values()) 
    movieTerms = word_tokenize(rawMovie)        # Tokenize the entire movie
    movieDoc = " ".join(movieTerms) 
    documentVocabs.append(movieDoc)

# Computes the cosine similarity between the query and every movie, and then rank them
def getRankings():
    # TF-IDF weigh each document into a vector  
    # Query is the first row, the documents are the remaining rows
    TFIDFMatrix = vectorizer.fit_transform(documentVocabs)
    rankedScores = [0 for _ in range(TFIDFMatrix.shape[0])]     # Initialize ranking list of similarity measures
    
    for i in range(TFIDFMatrix.shape[0]):
        rankedScores[i] = cosine_similarity(TFIDFMatrix[0], TFIDFMatrix[i])
    del rankedScores[0]

    # Map each movie title to its score and sort them
    rankings = dict(zip([movie["Title"] for movie in rankedMovieInfo], rankedScores))
    rankings = sorted(rankings.items(), key=lambda x: x[1], reverse=True)   # Sort titles by their similarity measures (x[1]) in descending order
    rankings = dict(rankings)
    return rankings


query = initializeQuery()
process(query, False)
resultList = getMovies()
processMovies(resultList)
rankings = getRankings()
print(rankings)