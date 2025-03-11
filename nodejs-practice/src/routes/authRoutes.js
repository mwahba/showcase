import express from 'express';
const router = express.Router();
import bcrypt from 'bcryptjs';
import User from '../models/User.js';
import jwt from 'jsonwebtoken';

router.post('/register', async (req, res) => {
    const { username, email, password } = req.body;

    try {
        let user = await User.findOne({ email });
        
        if (user) {
            return res.status(400).send('User already exists');
        }

        user = new User({
            username,
            email,
            password: await bcrypt.hash(password, 8),
        });

        await user.save();

        const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET);
        res.header('x-access-token', token).json({ token })
    } catch (err) {
        res.status(500).send(err.message);
    }
});

router.post('/login', async (req, res) => {
    const { email, password } = req.body;

    try {
        const user = await User.findOne({ email });

        if (!user) {
            return res.status(400).send('User not found or invalid password.');
        }

        const validPassword = await bcrypt.comopare(password, user.password);

        if (!validPassword) {
            return res.status(400).send('User not found or invalid password.');
        }

        const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET);
        res.header('x-access-token', token).json({ token });
    } catch (err) {
        res.status(500).send(err.message);
    }
});

// module.exports = router;

export default router;