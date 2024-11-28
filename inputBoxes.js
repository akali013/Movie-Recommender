let userTitle;
let userGenre;
let userPlot;
let defaultMovieURL = "https://cdn-icons-png.freepik.com/512/7271/7271342.png"

function getSearchValues() {
    // Get input values from the form
    userTitle = document.getElementById("title").value;
    userGenre = document.getElementById("genre").value;
    userPlot = document.getElementById("plot").value;

    // Send the input data to the backend via Fetch API
    fetch("http://127.0.0.1:5000/search", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            title: userTitle,
            genre: userGenre,
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
        movieElement.id = "movie-grid-element"
        movieElement.style.width = "200px"
        movieElement.classList.add("result");
        movieElement.innerHTML = `
            <center>
            <img src="${movie.poster}" width="200" height="auto" onerror="this.onerror=null; this.src='${defaultMovieURL}';">
            <br>
            <strong>${movie.title}</strong> - Similarity Score: ${movie.score.toFixed(2)}
            </center>
        `;
        resultsContainer.appendChild(movieElement);
    });
}

// Function to display errors in the results container
function displayError(message) {
    const resultsContainer = document.getElementById("results");
    resultsContainer.innerHTML = `<p style="color: red;">${message}</p>`;
}
