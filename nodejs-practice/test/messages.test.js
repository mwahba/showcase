const chai = require('chai');
const supertest = require('supertest');
const app = require('../app');
const { expect } = chai;

describe('/messages endpoint', () => {
    it('should create a new message', async () => {
        const authToken = 'your_mock_token_here';

        const res = await supertest(app)
            .post('/api/messages')
            .set('Authorization', `Bearer ${authToken}`)
            .send({
                sender: 'testuser',
                recipients: ['friend1'],
                content: 'Hello!'
            });
        
        expect(res.status).to.equal(201);
        expect(res.body.message.content).to.equal('Hello!');
    });

    it('should mark a message as read', async () => {
        const messageId = 'some_mock_id';
        const res = await supertest(app)
            .put(`/api/messages/${messageId}/read`)
            .set('Authorization', `Bearer ${authToken}`);
        
        expect(res.status).to.equal(204);
    });
});