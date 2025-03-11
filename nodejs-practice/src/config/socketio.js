import Message from '../models/Message.js';

export const setupSocketHandlers = (io) => {
    io.on('connection', (socket) => {
        console.log('New client connected:', socket.id);

        socket.on('sendMessage', async (data) => {
            const { conversationId, text } = data;

            try {
                const message = new Message({
                    conversationId,
                    sender: data.userId,
                    text
                });

                await message.save();

                // Broadcast to all clients in the conversation
                socket.broadcast.emit('newMessage', message);
            } catch (err) {
                console.error(err);
            }
        });

        socket.on('disconnect', () => {
            console.log('Client disconnected:', socket.id);
        });
    });
};