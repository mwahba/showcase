// Use in-memory MongoDB for testing
const { MongoMemoryServer } = require('mongodb-memory-server');
const mongoose = require('mongoose');

let mongoServer;

before(async () => {
    mongoServer = await MongoMemoryServer.create();
    const uri = mongoServer.getUri();
    await mongoose.connect(uri, { useNewUrlParser: true });
});

after(async () => {
    await mongoose.disconnect();
    await mongoServer.stop();
});
