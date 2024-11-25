let userTitle;
let userGenre;
let userPlot;

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

    if (data.error) {
        displayError(data.error);
        return;
    }

    if (data.length === 0) {
        resultsContainer.innerHTML = "<p>No results found. Try refining your search.</p>";
        return;
    }

    // Display each result
    data.forEach((movie) => {
        const movieElement = document.createElement("div");
        movieElement.classList.add("result");
        movieElement.innerHTML = `
            <strong>${movie.title}</strong> - Similarity Score: ${movie.score.toFixed(2)}
        `;
        resultsContainer.appendChild(movieElement);
    });
}

// Function to display errors in the results container
function displayError(message) {
    const resultsContainer = document.getElementById("results");
    resultsContainer.innerHTML = `<p style="color: red;">${message}</p>`;
}
