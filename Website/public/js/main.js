const cardTemplate = document.getElementById("card-template");
const cardContainer = document.getElementById("card-container");
const loader = document.querySelector(".loader");
const searchForm = document.getElementById("search-form");
const cardDataList = document.getElementById("card-list");
const searchInput = document.getElementById("search-input");
const title = document.querySelector("title");
const resultsCount = document.getElementById("results-count");

function populateCards() {
    if (validateInput() === false) {
        throw new Error("Card not valid.");
    }

    const cardName = searchInput.value;
    title.innerHTML = `Highlands - ${cardName}`;
    cardContainer.innerHTML = `<div><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br></div>`;
    loader.classList.remove("d-none");
    fetch(`http://localhost:8080/card/${cardName}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        }
    }).then(response => {
        return response.json();
    }).then(data => {
        cardContainer.innerHTML = "";
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
        resultsCount.innerHTML = `${cardContainer.children.length} results<br><br>`;
        if (cardContainer.children.length == 0) { 
            cardContainer.innerHTML = "No cards found. <div><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br></div>";
        }
        loader.classList.add("d-none");
    });
}

searchForm.addEventListener("submit", e => {
    e.preventDefault();
    populateCards();
});

function populateCardList() {
    fetch("http://localhost:8080/cardlist")
        .then(res => res.json())
        .then(cardList => {
            cardList.forEach(cardName => {
                let cardOption = document.createElement("option");
                cardOption.value = cardName;
                cardDataList.appendChild(cardOption);
            });
        });
}

populateCardList();

function validateInput() {
    const res = document.querySelector(`option[value="${searchInput.value}"]`)

    if (res === null || searchInput.value.length === 0) {
        alert("Not a valid card.");
        return false;
    }
    return true;
}

searchInput.value = "";