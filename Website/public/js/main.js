const cardTemplate = document.getElementById("card-template");
const cardContainer = document.getElementById("card-container");

function init() {
    for (let i = 0; i < 4; i++) {
        let card = cardTemplate.content.cloneNode(true);
        cardContainer.appendChild(card);
    }    
}

init();