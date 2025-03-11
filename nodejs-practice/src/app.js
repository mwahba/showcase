import express from 'express';
import http from 'http';
import { Server } from 'socket.io';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';
import { connectDB } from './config/database.js';
import { setupSocketHandlers } from './config/socketio.js';
import { setupRoutes } from './config/routes.js';

// import mongoose from 'mongoose';
// import Message from './models/Message.js';
// import AuthRoutes from './routes/authRoutes.js';
// import MessageRoutes from './routes/messageRoutes.js';

dotenv.config();

connectDB();

// if (!process.env.MONGODB_URI) {
//     throw new Error('Error attempting to obtain MONGODB_URI from env variables, please recheck. Exiting.')
// }

// // MongoDB connection
// mongoose.connect(process.env.MONGODB_URI);

const app = express();
app.use(express.json());

setupRoutes(app);
// // app.use('/api/auth', require('./routes/authRoutes'));
// app.use('/api/auth', AuthRoutes);
// // app.use('/api/messages', require('./routes/messageRoutes.js'));
// app.use('/api/messages', MessageRoutes);

// Serve static files (e.g. React/Angular frontend)
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
app.use(express.static(path.join(__dirname, '..', 'chat-client/build')));

app.get('*', (req, res) => {
    res.sendFile(path.resolve(__dirname, '..', 'chat-client', 'build', 'index.html'));
});

const server = http.createServer(app);
const io = new Server(server);

setupSocketHandlers(io);

// io.on('connection', (socket) => {
//     console.log('New client connected:', socket.id);

//     socket.on('sendMessage', async (data) => {
//         const { conversationId, text } = data;

//         try {
//             // Save to DB and Redis as in routes above
//             const message = new Message({
//                 conversationId,
//                 sender: data.userId,
//                 text
//             });

//             await message.save();

//             // Broadcast to all clients in the conversation
//             socket.broadcast.emit('newMessage', message);
//         } catch (err) {
//             console.error(err);
//         }
//     });
// });

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => console.log(`Server running on port ${PORT}`));

export default app;
