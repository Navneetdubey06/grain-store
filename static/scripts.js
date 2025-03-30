// Basic JavaScript functionality

// Search function for marketplace
function searchListings() {
    const query = document.getElementById("search-query").value.toLowerCase();
    const listings = document.querySelectorAll("#listings li");

    listings.forEach(listing => {
        if (listing.textContent.toLowerCase().includes(query)) {
            listing.style.display = "block";
        } else {
            listing.style.display = "none";
        }
    });
}

// Pagination function
let currentPage = 1;
const listingsPerPage = 5;

function paginateListings() {
    const listings = Array.from(document.querySelectorAll("#listings li"));
    const totalPages = Math.ceil(listings.length / listingsPerPage);

    listings.forEach((listing, index) => {
        listing.style.display =
            index >= (currentPage - 1) * listingsPerPage && index < currentPage * listingsPerPage
                ? "block"
                : "none";
    });

    const paginationContainer = document.getElementById("pagination");
    paginationContainer.innerHTML = "";

    for (let i = 1; i <= totalPages; i++) {
        const button = document.createElement("button");
        button.textContent = i;
        button.onclick = () => {
            currentPage = i;
            paginateListings();
        };
        paginationContainer.appendChild(button);
    }
}

// Call pagination on page load
paginateListings();