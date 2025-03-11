import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import axios from 'axios';

const App = () => {
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  const [messages, setMessages] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [newMessageText, setNewMessageText] = useState('');
  const [selectedConversationId, setSelectedConversationId] = useState(null);
  const [error, setError] = useState(null);
  const [isLogin, setIsLogin] = useState(true); // State to toggle between login and register
  const [showNewConvoModal, setShowNewConvoModal] = useState(false);
  const [users, setUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [initialMessage, setInitialMessage] = useState('');

  // Socket.io connection
  const socket = io(); // Use default URL so it connects to same server

  useEffect(() => {
    if (token) {
      // Use the x-access-token header that backend expects
      axios.defaults.headers.common['x-access-token'] = token;
      fetchConversations();
      if (selectedConversationId) {
        fetchMessages(selectedConversationId);
      }
    }
    
    socket.on('newMessage', (message) => {
      if (selectedConversationId === message.conversationId) {
        setMessages(prev => [...prev, message]);
      } else {
        // Update conversations list to show unread messages
        setConversations(prev =>
          prev.map(conv => 
            conv.id === message.conversationId ? {...conv, unread: conv.unread + 1} : conv
          )
        );
      }
    });

    return () => socket.disconnect();
  }, [token, selectedConversationId]);

  // Authentication functions
  const handleAuth = async (email, password, username) => {
    try {
      // Use the correct endpoint based on login/register state
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
      const data = isLogin ? { email, password } : { email, password, username };
      
      const response = await axios.post(
        endpoint,
        data,
        { headers: { 'Content-Type': 'application/json' } }
      );
      
      setToken(response.data.token);
      localStorage.setItem('authToken', response.data.token);
      setError(null);
    } catch (err) {
      setError(err.response ? err.response.data : 'An error occurred');
    }
  };

  // Message functions
  const handleSendMessage = async () => {
    if (!newMessageText.trim()) return;

    try {
      await axios.post(
        '/api/messages',
        { 
          conversationId: selectedConversationId,
          text: newMessageText
        }
      );

      socket.emit('sendMessage', {
        conversationId: selectedConversationId,
        text: newMessageText
      });

      setNewMessageText('');
    } catch (err) {
      setError(err.response ? err.response.data : 'An error occurred');
    }
  };

  // Conversation functions
  const fetchConversations = async () => {
    try {
      const response = await axios.get('/api/messages/conversations');
      setConversations(response.data);
    } catch (err) {
      setError(err.response ? err.response.data : 'An error occurred');
    }
  };

  const fetchMessages = async (conversationId) => {
    if (!conversationId) return;

    try {
      const response = await axios.get(`/api/messages/${conversationId}`);
      setMessages(response.data);
      setSelectedConversationId(conversationId);
    } catch (err) {
      setError(err.response ? err.response.data : 'An error occurred');
    }
  };

  // Fetch users for new conversation
  const fetchUsers = async () => {
    try {
      const response = await axios.get('/api/users');
      setUsers(response.data);
    } catch (err) {
      setError(err.response ? err.response.data : 'Failed to load users');
    }
  };

  // Create a conversation or use existing one
  const createConversation = async () => {
    if (!selectedUser || !initialMessage.trim()) {
      setError('Please select a user and enter a message');
      return;
    }

    try {
      // Try to find existing conversation first
      const response = await axios.post('/api/conversations', {
        participantId: selectedUser._id,
        initialMessage: initialMessage.trim()
      });

      // Add new conversation to list or update if exists
      const newConversation = response.data;
      setConversations(prevConvos => {
        // Check if conversation already exists
        const existingIndex = prevConvos.findIndex(c => c.id === newConversation.id);
        if (existingIndex >= 0) {
          const updated = [...prevConvos];
          updated[existingIndex] = newConversation;
          return updated;
        } else {
          return [...prevConvos, newConversation];
        }
      });

      // Select the new/existing conversation
      setSelectedConversationId(newConversation.id);
      fetchMessages(newConversation.id);
      
      // Reset and close modal
      setShowNewConvoModal(false);
      setSelectedUser(null);
      setInitialMessage('');
      setError(null);
    } catch (err) {
      setError(err.response ? err.response.data : 'Failed to create conversation');
    }
  };

  // UI components
  const LoginRegisterForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [username, setUsername] = useState('');

    return (
      <div className="auth-form">
        <h2>{isLogin ? 'Login' : 'Register'}</h2>
        
        {!isLogin && (
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Username"
          />
        )}
        
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
        />
        
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
        />
        
        <button onClick={() => handleAuth(email, password, username)}>
          {isLogin ? 'Login' : 'Register'}
        </button>
        
        <p className="auth-toggle">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button 
            className="toggle-link"
            onClick={() => setIsLogin(!isLogin)}
          >
            {isLogin ? 'Register' : 'Login'}
          </button>
        </p>
      </div>
    );
  };

  const ConversationsList = () => {
    return (
      <div className="conversations-list">
        {(!conversations || !conversations.length) && (<h3>No conversations found for user.</h3>)}
        {!!conversations.length && conversations.map(conv => (
          <div
            key={conv.id}
            onClick={() => fetchMessages(conv.id)}
            className={`conversation-item ${selectedConversationId === conv.id ? 'active' : ''}`}
          >
            <h3>{conv.name}</h3>
            {conv.unread > 0 && <span className="unread">{conv.unread}</span>}
          </div>
        ))}
        <div className="new-conversation">
          <button onClick={() => {
            fetchUsers(); // Get users when opening modal
            setShowNewConvoModal(true);
          }}>
            New Conversation
          </button>
        </div>
      </div>
    );
  };

  const ChatWindow = () => {
    if (!selectedConversationId) return null;

    return (
      <div className="chat-window">
        {messages.map(msg => (
          <div key={msg.id} className={`message ${msg.sender === 'me' ? 'me' : 'other'}`}>
            {msg.text}
          </div>
        ))}
        <input
          type="text"
          value={newMessageText}
          onChange={(e) => setNewMessageText(e.target.value)}
          placeholder="Type your message..."
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    );
  };

  // New component for creating conversations
  const CreateConversationModal = () => {
    // Filter users based on search term
    const filteredUsers = users.filter(user => 
      user.username.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
      <div className="modal-overlay">
        <div className="modal-content">
          <h2>New Conversation</h2>
          
          <div className="search-container">
            <input
              type="text"
              placeholder="Search users..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
            />
          </div>
          
          <div className="users-list">
            {filteredUsers.length === 0 && <p>No users found</p>}
            
            {filteredUsers.map(user => (
              <div 
                key={user._id} 
                className={`user-item ${selectedUser?._id === user._id ? 'selected' : ''}`}
                onClick={() => setSelectedUser(user)}
              >
                <span className="username">{user.username}</span>
                <span className="email">{user.email}</span>
              </div>
            ))}
          </div>
          
          {selectedUser && (
            <div className="selected-user">
              <p>Start conversation with {selectedUser.username}</p>
              <textarea
                placeholder="Write your first message..."
                value={initialMessage}
                onChange={e => setInitialMessage(e.target.value)}
              />
            </div>
          )}
          
          <div className="modal-actions">
            <button 
              className="cancel-btn"
              onClick={() => {
                setShowNewConvoModal(false);
                setSelectedUser(null);
                setInitialMessage('');
              }}
            >
              Cancel
            </button>
            
            <button 
              className="create-btn"
              disabled={!selectedUser || !initialMessage.trim()}
              onClick={createConversation}
            >
              Start Conversation
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="app">
      {!token ? (
        <LoginRegisterForm />
      ) : (
        <>
          <ConversationsList />
          {selectedConversationId && <ChatWindow />}
          {!selectedConversationId && <div className="no-conversation">Select a conversation or start a new one</div>}
          <button 
            className="logout-button"
            onClick={() => {
              localStorage.removeItem('authToken');
              setToken(null);
            }}
          >
            Logout
          </button>
          {showNewConvoModal && <CreateConversationModal />}
        </>
      )}
      {error && <div className="error">{error}</div>}
    </div>
  );
};

export default App;
