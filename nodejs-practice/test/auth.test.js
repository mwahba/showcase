// import chai, { expect } from 'chai';
// import supertest from 'supertest';
// import app from '../app';

// describe('/auth endpoint', () => {
//     it('should register a new user', async () => {
//         const res = await supertest(app)
//             .post('/api/auth/register')
//             .send({ username: 'testuser', password: '123456' });
        
//         expect(res.status).to.equal(201);
//         expect(res.body.user.username).to.equal('testuser');
//     });

//     it('should return a JWT token on login', async() => {
//         const res = await supertest(app)
//             .post('/api/auth/login')
//             .send({ username: 'testuser', password: '123456' });

//         expect(res.status).to.equal(200);
//         expect(res.body.token).to.be.a('string');
//     });
// });