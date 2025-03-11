import chai from 'chai';
import { expect } from 'chai';
import sinon from 'sinon';
import supertest from 'supertest';
import { createApp } from '../testUtils/testApp.js';
import Message from '../models/Message.js';
import redisClient from '../config/redis.js';
import mongoose from 'mongoose';

describe('Message Routes', () => {
    let app;
    let request;
    let messageStub;
    let redisStub;
    const mockUserId = new mongoose.Types.ObjectId();
    const mockConversationId = new mongoose.Types.ObjectId();
    
    const mockMessage = {
        _id: new mongoose.Types.ObjectId(),
        conversationId: mockConversationId,
        sender: mockUserId,
        text: 'Hello, world!',
        readBy: [],
        createdAt: new Date()
    };

    beforeEach(() => {
        // Setup stubs for Message model
        messageStub = {
            save: sinon.stub().resolves(mockMessage),
            populate: sinon.stub().returnsThis(),
            sort: sinon.stub().resolves([mockMessage])
        };
        sinon.stub(Message, 'find').returns({
            populate: () => ({
                sort: () => [mockMessage]
            })
        });
        sinon.stub(Message.prototype, 'save').resolves(mockMessage);
        
        // Setup stubs for redis
        redisStub = {
            lPush: sinon.stub().resolves(),
            expire: sinon.stub().resolves(),
            lRange: sinon.stub().resolves([])
        };
        sinon.stub(redisClient, 'lPush').resolves();
        sinon.stub(redisClient, 'expire').resolves();
        sinon.stub(redisClient, 'lRange').resolves([]);

        // Create test app with mocked auth middleware
        app = createApp({ userId: mockUserId });
        request = supertest(app);
    });

    afterEach(() => {
        sinon.restore();
    });

    describe('POST /messages', () => {
        it('should create a new message', async () => {
            const response = await request
                .post('/api/messages/messages')
                .send({
                    conversationId: mockConversationId.toString(),
                    text: 'Hello, world!'
                });

            expect(response.status).to.equal(200);
            expect(response.body).to.deep.equal({ success: true });
            expect(Message.prototype.save.calledOnce).to.be.true;
            expect(redisClient.lPush.calledOnce).to.be.true;
            expect(redisClient.expire.calledOnce).to.be.true;
        });

        it('should return 500 if message creation fails', async () => {
            sinon.restore();
            sinon.stub(Message.prototype, 'save').rejects(new Error('Database error'));

            const response = await request
                .post('/api/messages/messages')
                .send({
                    conversationId: mockConversationId.toString(),
                    text: 'Hello, world!'
                });

            expect(response.status).to.equal(500);
            expect(response.text).to.equal('Database error');
        });
    });

    describe('GET /messages/:conversationId', () => {
        it('should return messages from cache if available', async () => {
            const cachedMessage = JSON.stringify(mockMessage);
            sinon.restore();
            sinon.stub(redisClient, 'lRange').resolves([cachedMessage]);
            
            const response = await request
                .get(`/api/messages/messages/${mockConversationId}`);

            expect(response.status).to.equal(200);
            expect(response.body).to.be.an('array');
            expect(response.body[0]).to.deep.equal(JSON.parse(cachedMessage));
            expect(redisClient.lRange.calledOnce).to.be.true;
        });

        it('should fetch and cache messages from DB if not in cache', async () => {
            sinon.restore();
            sinon.stub(redisClient, 'lRange').resolves([]);
            sinon.stub(redisClient, 'lPush').resolves();
            sinon.stub(redisClient, 'expire').resolves();
            
            const mockFind = {
                populate: sinon.stub().returnsThis(),
                sort: sinon.stub().resolves([mockMessage])
            };
            sinon.stub(Message, 'find').returns(mockFind);
            
            const response = await request
                .get(`/api/messages/messages/${mockConversationId}`);

            expect(response.status).to.equal(200);
            expect(response.body).to.be.an('array');
            expect(Message.find.calledOnce).to.be.true;
            expect(redisClient.lPush.calledOnce).to.be.true;
            expect(redisClient.expire.calledOnce).to.be.true;
        });

        it('should return 500 if fetching messages fails', async () => {
            sinon.restore();
            sinon.stub(redisClient, 'lRange').rejects(new Error('Redis error'));
            
            const response = await request
                .get(`/api/messages/messages/${mockConversationId}`);

            expect(response.status).to.equal(500);
            expect(response.text).to.equal('Redis error');
        });
    });
});