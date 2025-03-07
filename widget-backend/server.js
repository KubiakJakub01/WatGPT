const express = require("express");
const WebSocket = require("ws");
const http = require("http");

const app = express();

const server = http.createServer(app);

const wss = new WebSocket.Server({ server });

const getRandomResponse = () => {
  const responses = ["yes", "no", "I don't know"];
  const randomIndex = Math.floor(Math.random() * responses.length);
  return responses[randomIndex];
};

wss.on("connection", (ws) => {
  console.log("New client connected");

  ws.on("message", (message) => {
    console.log(`Received: ${message}`);

    const response = getRandomResponse();
    ws.send(response);
  });

  ws.on("close", () => {
    console.log("Client disconnected");
  });
});

server.listen(5000, () => {
  console.log("Server is listening on port 5000");
});
