import { expect } from 'chai';
import { createServer } from 'http';
import { Server } from 'socket.io';
import { io as ioclient } from 'socket.io-client';
import mongoose from 'mongoose';
import sinon from 'sinon';
import dotenv from 'dotenv';
import Message from '../models/Message.js';
import { MongoMemoryServer } from 'mongodb-memory-server';

dotenv.config();

describe('Socket.io Message Functionality', function() {
    let io, serverSocket, clientSocket, mongoServer;
    let messageStub;

    before(async function() {
        // Set up MongoDB memory server for testing
        mongoServer = await MongoMemoryServer.create();
        const mongoUri = mongoServer.getUri();
        await mongoose.connect(mongoUri);

        // Create a simple http server
        const httpServer = createServer();
        io = new Server(httpServer);
        
        // Import socket handlers from app.js
        io.on('connection', (socket) => {
            socket.on('sendMessage', async (data) => {
                const { conversationId, text } = data;

                try {
                    // Save to DB and Redis as in routes above
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
        });
        
        httpServer.listen(3000);
        
        // Set up message stub
        messageStub = sinon.stub(Message.prototype, 'save');
        messageStub.resolves({
            _id: '123456789012',
            conversationId: '987654321098',
            sender: 'user123',
            text: 'Test message',
            readBy: [],
            createdAt: new Date()
        });
    });

    beforeEach(function(done) {
        // Create a socket.io client before each test
        clientSocket = ioclient('http://localhost:3000');
        clientSocket.on('connect', done);
    });

    afterEach(function() {
        // Close the client socket after each test
        if (clientSocket.connected) {
            clientSocket.disconnect();
        }
    });

    after(async function() {
        // Clean up after all tests
        io.close();
        messageStub.restore();
        await mongoose.disconnect();
        await mongoServer.stop();
    });

    it('should establish a socket connection', function() {
        expect(clientSocket.connected).to.be.true;
    });

    it('should save a message to the database when sendMessage event is emitted', function(done) {
        const messageData = {
            conversationId: '987654321098',
            userId: 'user123',
            text: 'Test message'
        };

        // Emit the sendMessage event
        clientSocket.emit('sendMessage', messageData);
        
        // Give time for the asynchronous operations to complete
        setTimeout(() => {
            expect(messageStub.calledOnce).to.be.true;
            const savedMessage = messageStub.firstCall.thisValue;
            expect(savedMessage.conversationId).to.equal(messageData.conversationId);
            expect(savedMessage.sender).to.equal(messageData.userId);
            expect(savedMessage.text).to.equal(messageData.text);
            done();
        }, 50);
    });

    it('should broadcast newMessage event to other clients', function(done) {
        const messageData = {
            conversationId: '987654321098',
            userId: 'user123',
            text: 'Test message'
        };

        // Create a second client to receive the broadcast
        const secondClient = ioclient('http://localhost:3000');
        
        secondClient.on('connect', () => {
            secondClient.on('newMessage', (message) => {
                expect(message.conversationId).to.equal(messageData.conversationId);
                expect(message.sender).to.equal(messageData.userId);
                expect(message.text).to.equal(messageData.text);
                secondClient.disconnect();
                done();
            });

            // Emit from first client after second client is ready to receive
            clientSocket.emit('sendMessage', messageData);
        });
    });

    it('should handle errors during message creation', function(done) {
        // Restore the original stub and create one that rejects
        messageStub.restore();
        const errorStub = sinon.stub(Message.prototype, 'save');
        errorStub.rejects(new Error('Database error'));

        // Spy on console.error
        const consoleErrorSpy = sinon.spy(console, 'error');

        const messageData = {
            conversationId: '987654321098',
            userId: 'user123',
            text: 'Test message'
        };

        // Emit the sendMessage event
        clientSocket.emit('sendMessage', messageData);
        
        // Give time for the error to be logged
        setTimeout(() => {
            expect(consoleErrorSpy.calledOnce).to.be.true;
            expect(consoleErrorSpy.firstCall.args[0].message).to.equal('Database error');
            
            // Clean up
            consoleErrorSpy.restore();
            errorStub.restore();
            
            // Restore the original stub for other tests
            messageStub = sinon.stub(Message.prototype, 'save');
            messageStub.resolves({
                _id: '123456789012',
                conversationId: '987654321098',
                sender: 'user123',
                text: 'Test message',
                readBy: [],
                createdAt: new Date()
            });
            
            done();
        }, 50);
    });
});