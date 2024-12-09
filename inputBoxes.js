let userTitle;
let userGenre;
let userPlot;
let defaultMovieURL = "https://cdn-icons-png.freepik.com/512/7271/7271342.png"

const genreSelect = document.getElementById("genre");
const selectedGenresContainer = document.getElementById("selected-genres");

// Array to store selected genres
let selectedGenres = [];

// Add event listener for change in the dropdown
genreSelect.addEventListener("change", function () {
    const selectedOptions = Array.from(genreSelect.selectedOptions);

    selectedOptions.forEach(option => {
        const genre = option.value;

        // Check if the genre is already selected
        if (!selectedGenres.includes(genre) && genre !== "") {
            selectedGenres.push(genre);
            addTag(genre);
        }
    });

    // Reset dropdown state
    genreSelect.blur(); // Close the dropdown
});

// Function to add a tag
function addTag(genre) {
    const tag = document.createElement("div");
    tag.classList.add("tag");
    tag.innerHTML = `
        ${genre}
        <button class="remove-tag" onclick="removeTag('${genre}')">&times;</button>
    `;
    selectedGenresContainer.appendChild(tag);
}

// Function to remove a tag
function removeTag(genre) {
    // Remove the tag from the array
    selectedGenres = selectedGenres.filter(g => g !== genre);

    // Remove the tag element from the DOM
    const tag = Array.from(selectedGenresContainer.children).find(tag => tag.textContent.includes(genre));
    if (tag) {
        selectedGenresContainer.removeChild(tag);
    }
}

// Function to handle form submission
function getSearchValues() {
    // Get input values from the form
    const userTitle = document.getElementById("title").value;
    const userPlot = document.getElementById("plot").value;

    // Send the selected genres and other inputs to the backend via Fetch API
    fetch("http://127.0.0.1:5000/search", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            title: userTitle,
            genres: selectedGenres, // Include selected genres
            plot: userPlot,
        }),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then((data) => {
            displayResults(data); // Call a function to display the results
        })
        .catch((error) => {
            console.error("Error:", error);
            displayError("An error occurred while fetching search results.");
        });
}
// Function to display results dynamically
function displayResults(data) {
    const resultsContainer = document.getElementById("results");
    resultsContainer.innerHTML = ""; // Clear previous results

    if (data == "No results found") {
        resultsContainer.innerHTML = "<p>No results found. Try refining your search.</p>";
        return;
    }

    if (data.error) {
        displayError(data.error);
        return;
    }

    // Display each result
    data.forEach((movie) => {
        const movieElement = document.createElement("div");
        movieElement.id = `movie-${movie.title.replace(/\s+/g, '-')}`; // Unique ID for each movie
        movieElement.style.width = "200px";
        movieElement.classList.add("result");
        movieElement.innerHTML = `
            <center>
            <img src="${movie.poster}" width="200" height="auto" onerror="this.onerror=null; this.src='https://cdn-icons-png.freepik.com/512/7271/7271342.png';">
            <br>
            <strong>${movie.title}</strong> - Similarity Score: ${movie.score.toFixed(2)}
            <br>
            <button onclick="fetchMovieDetails('${movie.title}', '${movieElement.id}')">View Details</button>
            </center>
            <div class="movie-details" style="display: none;"></div> <!-- Placeholder for details -->
        `;
        resultsContainer.appendChild(movieElement);
    });
}

// Function to fetch movie details
function fetchMovieDetails(title, containerId) {
    fetch(`http://127.0.0.1:5000/details?title=${encodeURIComponent(title)}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then((details) => {
            const container = document.getElementById(containerId);
            const detailsDiv = container.querySelector(".movie-details");

            // Toggle visibility
            if (detailsDiv.style.display === "none") {
                detailsDiv.style.display = "block";
                detailsDiv.innerHTML = `
                    <p><strong>Plot:</strong> ${details.Plot}</p>
                    <p><strong>Director:</strong> ${details.Director}</p>
                    <p><strong>Actors:</strong> ${details.Actors}</p>
                    <p><strong>Genre:</strong> ${details.Genre}</p>
                `;
            } else {
                detailsDiv.style.display = "none"; // Hide details if already displayed
            }
        })
        .catch((error) => {
            console.error("Error fetching movie details:", error);
            alert("An error occurred while fetching movie details.");
        });
}

// Function to display errors in the results container
function displayError(message) {
    const resultsContainer = document.getElementById("results");
    resultsContainer.innerHTML = `<p style="color: red;">${message}</p>`;
}