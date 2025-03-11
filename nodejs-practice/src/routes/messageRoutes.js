import express from 'express';
const router = express.Router();
import Message from '../models/Message.js';
import redisClient from '../config/redis.js';

router.post('/messages', async (req, res) => {
    const { conversationId, text } = req.body;

    try {
        const message = new Message({
            conversationId,
            sender: req.userId,
            text
        });

        await message.save();

        // Update Redis cache for this conversation
        redisClient.lPush(`messages:${conversationId}`, JSON.stringify(message));
        redisClient.expire(`messages:${conversationId}`, 60 * 60); // Expire in 1 hour

        res.json({ success: true });
    } catch (err) {
        res.status(500).send(err.message);
    }
});

router.get('/messages/:conversationId', async (req, res) => {
    const { conversationId } = req.params;

    try {
        let messagesFromCache = await redisClient.lRange(`messages:${conversationId}`, 0, -1);

        if (messagesFromCache.length > 0) {
            return res.json(messagesFromCache.map(msg => JSON.parse(msg)));
        }

        const messages = await Message.find({ conversationId })
            .populate('sender')
            .sort({ createdAt: 'asc' });

        // Save to Redis
        redisClient.lPush(`messages:${conversationId}`, ...messages.map(JSON.stringify));
        redisClient.expire(`messages:${conversationId}`, 60 * 60);

        res.json(messages);
    } catch (err) {
        res.status(500).send(err.message);
    }
});

router.get('/conversations', async (req, res) => {
    try {
        // Find all unique conversationIds where the user is a participant
        const userConversations = await Message.aggregate([
            // Find messages where current user is either sender or recipient
            { $match: { $or: [
                { sender: req.userId },
                { 'readBy': { $ne: req.userId } }
            ]}},
            // Group by conversation
            { $group: {
                _id: "$conversationId",
                latestMessage: { $max: "$createdAt" },
                messages: { $push: "$$ROOT" }
            }},
            // Add the latest message details
            { $addFields: {
                lastMessage: {
                    $arrayElemAt: [
                        { $filter: {
                            input: "$messages",
                            as: "message",
                            cond: { $eq: ["$$message.createdAt", "$latestMessage"] }
                        }},
                        0
                    ]
                }
            }},
            // Lookup users in the conversation
            { $lookup: {
                from: "users",
                let: { messages: "$messages" },
                pipeline: [
                    { $match: { $expr: { $in: ["$_id", "$$messages.sender"] } } }
                ],
                as: "participants"
            }},
            // Format the output
            { $project: {
                _id: 0,
                conversationId: "$_id",
                name: {
                    $reduce: {
                        input: "$participants",
                        initialValue: "",
                        in: {
                            $cond: {
                                if: { $eq: ["$$value", ""] },
                                then: "$$this.username",
                                else: { $concat: ["$$value", ", ", "$$this.username"] }
                            }
                        }
                    }
                },
                unread: { 
                    $cond: {
                        if: { $in: [req.userId, "$lastMessage.readBy"] },
                        then: false,
                        else: true
                    }
                },
                lastMessageText: "$lastMessage.text",
                lastMessageDate: "$lastMessage.createdAt"
            }}
        ]);

        res.json(userConversations);
    } catch (err) {
        console.error("Error fetching conversations:", err);
        res.status(500).send(err.message);
    }
});

export default router;