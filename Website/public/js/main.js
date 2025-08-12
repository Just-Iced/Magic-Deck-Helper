const cardTemplate = document.getElementById("card-template");
const cardContainer = document.getElementById("card-container");
const loader = document.querySelector(".loader");
const searchForm = document.getElementById("search-form");

function populateCards(cardName) {
    cardContainer.innerHTML = "";
    loader.classList.remove("d-none");
    fetch(`http://localhost:8080/card/${cardName}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        }
    }).then(response => {
        return response.json();
    }).then(data => {
        for (cardData of data) {
            if (cardData.name.includes(cardName)) {
                let newCard = cardTemplate.content.cloneNode(true);
                const price = Array.isArray(cardData.price) ? cardData.price[0] : cardData.price;
                newCard.querySelector(".card-price").innerHTML = `$${price.toFixed(2)}`;
                newCard.querySelector(".card-name").innerHTML = cardData.name;
                newCard.querySelector(".card-img").src = cardData.img;
                newCard.querySelector(".card-link").href = `https://www.${cardData.link}`;
                newCard.querySelector(".card-site").innerHTML = cardData.site;
                cardContainer.appendChild(newCard);
            }
        }
        if (cardContainer.children.length == 0) {cardContainer.innerHTML = "No cards found."} 
        loader.classList.add("d-none");
    });
}

searchForm.addEventListener("submit", e => {
    e.preventDefault();
    let cardName = searchForm.querySelector("input").value;
    populateCards(cardName);
});