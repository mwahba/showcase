// const { default: mongoose } = require('mongoose');
import mongoose from 'mongoose';
// const mognoose = require('mongoose');

const UserSchema = new mongoose.Schema({
    username: {
        type: String,
        required: true,
        unique: true,
    },
    email: {
        type: String,
        required: true,
        unique: true,
    },
    password: {
        type: String,
        required: true,
    }
});

// module.exports = mongoose.model('User', UserSchema);

export default mongoose.model('User', UserSchema);