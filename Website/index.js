const express = require("express");
const path = require("path");
const cors = require("cors");
require("dotenv").config()

const app = express();
app.use(express.static(path.join(__dirname, 'public')));

const PORT = process.env.PORT || 8888;

app.get("/", (req, res) => {
    res.sendFile("index.html");
});

app.listen(PORT, () => {
    console.log(`App listening on port ${PORT}`);
});