import React, { useState, useEffect, useRef } from 'react';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system' | 'typing' | 'error';
  content: string;
  timestamp: string;
  metadata?: any;
}

interface GeminiChatInterfaceProps {
  user?: {
    id: string;
    name: string;
  };
}

const GeminiChatInterface: React.FC<GeminiChatInterfaceProps> = ({ user }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [sessionId, setSessionId] = useState<string>('');
  const [geminiStatus, setGeminiStatus] = useState<{ status: string; message: string } | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    checkGeminiStatus();
    initializeWebSocket();
    
    // Add welcome message
    setMessages([
      {
        id: 'welcome',
        type: 'system',
        content: '🤖 **Chào mừng đến với OpenManus-Youtu AI Agent!**\n\nTôi được tích hợp với Google Gemini và có thể giúp bạn:\n\n🔧 **Các tính năng chính:**\n• Tạo và kiểm tra CCCD\n• Tra cứu mã số thuế\n• Phân tích dữ liệu\n• Thu thập dữ liệu web\n• Tự động hóa form\n• Tạo báo cáo\n• Xuất Excel\n\n💬 **Hãy thử:** "Tạo 100 CCCD cho tỉnh Hưng Yên, giới tính nữ, năm sinh 1965-1975"',
        timestamp: new Date().toISOString()
      }
    ]);

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [user?.id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const checkGeminiStatus = async () => {
    try {
      const response = await fetch('/api/gemini/status');
      const data = await response.json();
      setGeminiStatus(data);
    } catch (error) {
      console.error('Error checking Gemini status:', error);
    }
  };

  const initializeWebSocket = () => {
    const websocket = new WebSocket(`ws://localhost:8000/gemini/chat/ws?user_id=${user?.id || 'anonymous'}`);
    setWs(websocket);

    websocket.onopen = () => {
      setIsConnected(true);
      console.log('Connected to Gemini Chat WebSocket');
    };

    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        switch (data.type) {
          case 'system':
            addMessage({
              id: Date.now().toString(),
              type: 'system',
              content: data.content,
              timestamp: data.timestamp
            });
            break;
            
          case 'typing':
            setIsTyping(true);
            break;
            
          case 'chunk':
            // Handle streaming response
            setMessages(prev => {
              const lastMessage = prev[prev.length - 1];
              if (lastMessage && lastMessage.type === 'assistant' && lastMessage.id === 'streaming') {
                return [
                  ...prev.slice(0, -1),
                  {
                    ...lastMessage,
                    content: lastMessage.content + data.content
                  }
                ];
              } else {
                return [
                  ...prev,
                  {
                    id: 'streaming',
                    type: 'assistant',
                    content: data.content,
                    timestamp: data.timestamp
                  }
                ];
              }
            });
            break;
            
          case 'complete':
            setIsTyping(false);
            setMessages(prev => {
              const lastMessage = prev[prev.length - 1];
              if (lastMessage && lastMessage.id === 'streaming') {
                return [
                  ...prev.slice(0, -1),
                  {
                    ...lastMessage,
                    id: Date.now().toString()
                  }
                ];
              }
              return prev;
            });
            break;
            
          case 'error':
            setIsTyping(false);
            addMessage({
              id: Date.now().toString(),
              type: 'error',
              content: data.content,
              timestamp: new Date().toISOString()
            });
            break;
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    websocket.onclose = () => {
      setIsConnected(false);
      console.log('Disconnected from Gemini Chat WebSocket');
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };
  };

  const addMessage = (message: ChatMessage) => {
    setMessages(prev => [...prev, message]);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !ws || !isConnected) return;

    const message = inputMessage.trim();
    setInputMessage('');

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };

    addMessage(userMessage);

    // Send message via WebSocket
    try {
      ws.send(JSON.stringify({
        message: message,
        stream: true,
        session_id: sessionId
      }));
    } catch (error) {
      console.error('Error sending message:', error);
      addMessage({
        id: Date.now().toString(),
        type: 'error',
        content: 'Lỗi khi gửi tin nhắn. Vui lòng thử lại.',
        timestamp: new Date().toISOString()
      });
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = async () => {
    try {
      const response = await fetch('/api/gemini/chat/sessions/default', {
        method: 'DELETE'
      });
      
      if (response.ok) {
        setMessages([
          {
            id: 'welcome',
            type: 'system',
            content: '🤖 Cuộc trò chuyện đã được xóa. Tôi có thể giúp gì cho bạn?',
            timestamp: new Date().toISOString()
          }
        ]);
      }
    } catch (error) {
      console.error('Error clearing chat:', error);
    }
  };

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'user': return '👤';
      case 'assistant': return '🤖';
      case 'system': return 'ℹ️';
      case 'error': return '❌';
      default: return '💬';
    }
  };

  const formatMessage = (content: string) => {
    // Enhanced markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/•/g, '&bull;')
      .replace(/\n/g, '<br>');
  };

  const getStatusColor = () => {
    if (!geminiStatus) return '#666';
    return geminiStatus.status === 'active' ? '#4caf50' : '#f44336';
  };

  return (
    <div className="gemini-chat-interface">
      <div className="chat-header">
        <div className="chat-title">
          <span className="chat-icon">🤖</span>
          <span>OpenManus-Youtu AI Agent (Gemini)</span>
        </div>
        
        <div className="chat-status">
          <div className="gemini-status">
            <span 
              className="status-indicator"
              style={{ color: getStatusColor() }}
            >
              {geminiStatus?.status === 'active' ? '🟢 Gemini Active' : '🔴 Gemini Inactive'}
            </span>
          </div>
          
          <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '🟢 Kết nối' : '🔴 Mất kết nối'}
          </div>
          
          <button className="btn-clear" onClick={clearChat}>
            🗑️ Xóa chat
          </button>
        </div>
      </div>
      
      {geminiStatus?.status !== 'active' && (
        <div className="gemini-warning">
          <div className="warning-content">
            <span className="warning-icon">⚠️</span>
            <div className="warning-text">
              <strong>Gemini AI chưa được cấu hình</strong>
              <p>{geminiStatus?.message}</p>
              <p>Vui lòng cấu hình Gemini API key trong Settings để sử dụng AI Agent.</p>
            </div>
          </div>
        </div>
      )}
      
      <div className="chat-messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-header">
              <span className="message-icon">{getMessageIcon(message.type)}</span>
              <span className="message-time">
                {new Date(message.timestamp).toLocaleTimeString()}
              </span>
            </div>
            
            <div 
              className="message-content"
              dangerouslySetInnerHTML={{ 
                __html: formatMessage(message.content) 
              }}
            />
          </div>
        ))}
        
        {isTyping && (
          <div className="message assistant typing">
            <div className="message-header">
              <span className="message-icon">🤖</span>
              <span className="message-time">Gemini đang nhập...</span>
            </div>
            <div className="message-content">
              <span className="typing-indicator">
                <span>.</span><span>.</span><span>.</span>
              </span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <div className="chat-input">
        <div className="input-container">
          <input
            ref={inputRef}
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Nhập tin nhắn... (Enter để gửi, Shift+Enter để xuống dòng)"
            disabled={!isConnected || geminiStatus?.status !== 'active'}
            autoFocus
          />
          
          <button 
            onClick={sendMessage} 
            disabled={!inputMessage.trim() || !isConnected || geminiStatus?.status !== 'active'}
            className="btn-send"
          >
            📤
          </button>
        </div>
        
        <div className="input-suggestions">
          <span className="suggestion-label">💡 Gợi ý:</span>
          <button 
            className="suggestion-btn"
            onClick={() => setInputMessage('Tạo 100 CCCD cho tỉnh Hưng Yên, giới tính nữ, năm sinh 1965-1975')}
            disabled={geminiStatus?.status !== 'active'}
          >
            Tạo CCCD
          </button>
          <button 
            className="suggestion-btn"
            onClick={() => setInputMessage('Kiểm tra CCCD 031089011929')}
            disabled={geminiStatus?.status !== 'active'}
          >
            Kiểm tra CCCD
          </button>
          <button 
            className="suggestion-btn"
            onClick={() => setInputMessage('Tra cứu mã số thuế 037178000015')}
            disabled={geminiStatus?.status !== 'active'}
          >
            Tra cứu thuế
          </button>
          <button 
            className="suggestion-btn"
            onClick={() => setInputMessage('Phân tích dữ liệu thống kê')}
            disabled={geminiStatus?.status !== 'active'}
          >
            Phân tích dữ liệu
          </button>
        </div>
      </div>
    </div>
  );
};

export default GeminiChatInterface;