import { exec } from 'child_process';
import mongoose from 'mongoose';
import dotenv from 'dotenv';
import net from 'net';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
dotenv.config();

const MONGODB_PORT = process.env.MONGODB_PORT || 27017;
const MONGODB_URI = process.env.MONGODB_URI || `mongodb://localhost:${MONGODB_PORT}/messaging`;
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DB_PATH = path.join(__dirname, '..', 'data/db'); // So long as current script is under 'config' parent folder.

// Check if MongoDB is running on the specified port
async function isMongoDBRunning() {
    return new Promise(resolve => {
        const socket = new net.Socket();
        socket.setTimeout(500);
        socket.on('connect', () => {
            socket.destroy();
            resolve(true);
        });
        socket.on('timeout', () => {
            socket.destroy();
            resolve(false);
        });
        socket.on('error', () => {
            socket.destroy();
            resolve(false);
        });
        socket.connect(MONGODB_PORT, 'localhost');
    });
}

// Ensure DB directory exists
async function ensureDbDir() {
    try {
        await fs.mkdir(DB_PATH, { recursive: true });
        console.log(`DB directory created: ${DB_PATH}`);
    } catch (err) {
        console.error("Error creating DB directory:", err);
    }
}

// Start MongoDB server with timeout
async function startMongoDB() {
    await ensureDbDir();

    return new Promise((resolve, reject) => {
        console.log(`Starting MongoDB on port ${MONGODB_PORT}...`);
        
        // Set timeout to avoid hanging
        const timeout = setTimeout(() => {
            console.log('MongoDB startup took too long, continuing anyway...');
            resolve(); // Resolve anyway after timeout
        }, 10000); // 10 second timeout
        
        const mongod = exec(`mongod --dbpath ${DB_PATH} --port ${MONGODB_PORT}`, 
            (error) => {
                if (error) {
                    console.error(`Error starting MongoDB: ${error}`);
                    clearTimeout(timeout);
                    reject(error);
                }
            }
        );

        let output = '';
        
        mongod.stdout.on('data', (data) => {
            output += data;
            // Look for various success indicators
            if (data.includes('waiting for connections') || 
                data.includes('Listening on') || 
                data.includes('port=27017')) {
                console.log('MongoDB started successfully');
                clearTimeout(timeout);
                resolve();
            }
        });
        
        mongod.stderr.on('data', (data) => {
            console.error(`MongoDB stderr: ${data}`);
        });
        
        mongod.on('close', (code) => {
            if (code !== 0) {
                console.error(`MongoDB process exited with code ${code}`);
                console.error('MongoDB output:', output);
                clearTimeout(timeout);
                reject(new Error(`MongoDB process exited with code ${code}`));
            }
        });

        // Keep MongoDB running in background
        mongod.unref();
    });
}

export const connectDB = async () => {
    try {
        const mongoRunning = await isMongoDBRunning();

        if (!mongoRunning) {
            try {
                await startMongoDB();
                // Give MongoDB a moment to be ready for connections
                await new Promise(resolve => setTimeout(resolve, 1000));
            } catch (err) {
                console.error('Failed to start MongoDB:', err);
                console.log('Attempting to connect anyway...');
            }
        } else {
            console.log(`MongoDB already running on port ${MONGODB_PORT}`);
        }

        try {
            await mongoose.connect(MONGODB_URI);
            console.log('MongoDB connected successfully');
        } catch (err) {
            console.error('Failed to connect to MongoDB:', err);
            console.log('Retrying connection in 5 seconds...');
            
            // Retry logic
            setTimeout(() => connectDB(), 5000);
        }
    } catch (err) {
        console.error('Unexpected error in connectDB:', err);
        process.exit(1);
    }
};