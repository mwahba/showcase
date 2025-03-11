import redis from 'redis';
import dotenv from 'dotenv';
dotenv.config();
// require('dotenv').config();

const client = redis.createClient({
    host: process.env.REDIS_HOST,
    port: process.env.REDIS_PORT
});

client.on('error', (err) => console.log('Redis Error:', err));

// module.exports = client;
export default client;