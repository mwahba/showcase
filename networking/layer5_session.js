/*
Layer 5: Session Layer
Establishes, manages, and terminates connections between applications.
Handles session setup, maintenance, and teardown.

Protocols: NetBIOS, RPC (Remote Procedure Call), SIP (Session Initiation Protocol)
*/

// Server (Node.js with ws package)
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', function connection(ws) {
  console.log('New session established');
  
  ws.on('message', function incoming(message) {
    console.log('Received: %s', message);
    ws.send('Server received: ' + message);
  });
  
  ws.on('close', function close() {
    console.log('Session terminated');
  });
  
  ws.send('Session initialized');
});

// Client (browser JavaScript)
const socket = new WebSocket('ws://localhost:8080');

socket.addEventListener('open', function (event) {
  console.log('Connected to server');
  socket.send('Hello Server!');
});

socket.addEventListener('message', function (event) {
  console.log('Message from server:', event.data);
});

socket.addEventListener('close', function (event) {
  console.log('Session closed');
});