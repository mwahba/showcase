import { fileURLToPath } from 'url';
import path from 'path';
import express from 'express';
import AuthRoutes from '../routes/authRoutes.js';
import MessageRoutes from '../routes/messageRoutes.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

export const setupRoutes = (app) => {
    // API routes
    app.use('/api/auth', AuthRoutes);
    app.use('/api/messages', MessageRoutes);

    // Serve static files
    app.use(express.static(path.join(rootDir, 'chat-client/build')));

    // Catch-all route for SPA
    app.get('*', (req, res) => {
        res.sendFile(path.resolve(rootDir, 'chat-client', 'build', 'index.html'));
    });
};