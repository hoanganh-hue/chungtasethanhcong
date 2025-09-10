import React, { useState, useEffect } from 'react';

interface GeminiConfig {
  model: string;
  temperature: number;
  max_tokens: number;
  has_api_key: boolean;
}

interface GeminiConfigInterfaceProps {
  onConfigSaved?: () => void;
}

const GeminiConfigInterface: React.FC<GeminiConfigInterfaceProps> = ({ onConfigSaved }) => {
  const [config, setConfig] = useState<GeminiConfig | null>(null);
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('gemini-1.5-flash');
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(2048);
  const [isLoading, setIsLoading] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string; test_response?: string } | null>(null);
  const [availableModels, setAvailableModels] = useState<Array<{ id: string; name: string; description: string }>>([]);

  useEffect(() => {
    loadConfig();
    loadAvailableModels();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await fetch('/api/gemini/config');
      const data = await response.json();
      
      if (data.success && data.config) {
        setConfig(data.config);
        setModel(data.config.model);
        setTemperature(data.config.temperature);
        setMaxTokens(data.config.max_tokens);
      }
    } catch (error) {
      console.error('Error loading config:', error);
    }
  };

  const loadAvailableModels = async () => {
    try {
      const response = await fetch('/api/gemini/models');
      const data = await response.json();
      
      if (data.success) {
        setAvailableModels(data.models);
      }
    } catch (error) {
      console.error('Error loading models:', error);
    }
  };

  const testApiKey = async () => {
    if (!apiKey.trim()) {
      setTestResult({ success: false, message: 'Vui lòng nhập API key để test' });
      return;
    }

    setIsTesting(true);
    setTestResult(null);

    try {
      const response = await fetch('/api/gemini/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: apiKey,
          model: model
        })
      });

      const data = await response.json();
      setTestResult(data);
    } catch (error) {
      setTestResult({ 
        success: false, 
        message: `Lỗi khi test API key: ${error.message}` 
      });
    } finally {
      setIsTesting(false);
    }
  };

  const saveConfig = async () => {
    if (!apiKey.trim()) {
      alert('Vui lòng nhập Gemini API key');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('/api/gemini/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: apiKey,
          model: model,
          temperature: temperature,
          max_tokens: maxTokens
        })
      });

      const data = await response.json();
      
      if (data.success) {
        alert('Cấu hình Gemini đã được lưu thành công!');
        setApiKey(''); // Clear API key for security
        loadConfig(); // Reload config
        if (onConfigSaved) {
          onConfigSaved();
        }
      } else {
        alert(`Lỗi: ${data.message}`);
      }
    } catch (error) {
      alert(`Lỗi khi lưu cấu hình: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteConfig = async () => {
    if (!confirm('Bạn có chắc chắn muốn xóa cấu hình Gemini?')) {
      return;
    }

    try {
      const response = await fetch('/api/gemini/config', {
        method: 'DELETE'
      });

      const data = await response.json();
      
      if (data.success) {
        alert('Cấu hình Gemini đã được xóa!');
        setConfig(null);
        setApiKey('');
      } else {
        alert(`Lỗi: ${data.message}`);
      }
    } catch (error) {
      alert(`Lỗi khi xóa cấu hình: ${error.message}`);
    }
  };

  return (
    <div className="gemini-config-interface">
      <div className="config-header">
        <h3>🤖 Cấu hình Google Gemini AI</h3>
        <p>Nhập API key của Gemini để sử dụng AI Agent với khả năng xử lý ngôn ngữ tự nhiên và function calling.</p>
      </div>

      <div className="config-form">
        <div className="form-group">
          <label htmlFor="apiKey">Gemini API Key *</label>
          <input
            id="apiKey"
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Nhập Gemini API key của bạn..."
            className="form-input"
          />
          <small className="form-help">
            Lấy API key từ <a href="https://aistudio.google.com/" target="_blank" rel="noopener noreferrer">Google AI Studio</a>
          </small>
        </div>

        <div className="form-group">
          <label htmlFor="model">Model</label>
          <select
            id="model"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="form-select"
          >
            {availableModels.map((modelOption) => (
              <option key={modelOption.id} value={modelOption.id}>
                {modelOption.name} - {modelOption.description}
              </option>
            ))}
          </select>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="temperature">Temperature: {temperature}</label>
            <input
              id="temperature"
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="form-range"
            />
            <small className="form-help">Điều chỉnh độ sáng tạo (0 = chính xác, 2 = sáng tạo)</small>
          </div>

          <div className="form-group">
            <label htmlFor="maxTokens">Max Tokens: {maxTokens}</label>
            <input
              id="maxTokens"
              type="range"
              min="100"
              max="8192"
              step="100"
              value={maxTokens}
              onChange={(e) => setMaxTokens(parseInt(e.target.value))}
              className="form-range"
            />
            <small className="form-help">Độ dài tối đa của phản hồi</small>
          </div>
        </div>

        <div className="form-actions">
          <button
            onClick={testApiKey}
            disabled={isTesting || !apiKey.trim()}
            className="btn btn-secondary"
          >
            {isTesting ? '⏳ Đang test...' : '🧪 Test API Key'}
          </button>

          <button
            onClick={saveConfig}
            disabled={isLoading || !apiKey.trim()}
            className="btn btn-primary"
          >
            {isLoading ? '⏳ Đang lưu...' : '💾 Lưu cấu hình'}
          </button>

          {config && (
            <button
              onClick={deleteConfig}
              className="btn btn-danger"
            >
              🗑️ Xóa cấu hình
            </button>
          )}
        </div>
      </div>

      {testResult && (
        <div className={`test-result ${testResult.success ? 'success' : 'error'}`}>
          <h4>{testResult.success ? '✅ Test thành công!' : '❌ Test thất bại!'}</h4>
          <p>{testResult.message}</p>
          {testResult.test_response && (
            <div className="test-response">
              <strong>Phản hồi test:</strong>
              <pre>{testResult.test_response}</pre>
            </div>
          )}
        </div>
      )}

      {config && (
        <div className="config-status">
          <h4>✅ Cấu hình hiện tại</h4>
          <div className="status-grid">
            <div className="status-item">
              <span className="status-label">Model:</span>
              <span className="status-value">{config.model}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Temperature:</span>
              <span className="status-value">{config.temperature}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Max Tokens:</span>
              <span className="status-value">{config.max_tokens}</span>
            </div>
            <div className="status-item">
              <span className="status-label">API Key:</span>
              <span className="status-value">{config.has_api_key ? '✅ Đã cấu hình' : '❌ Chưa cấu hình'}</span>
            </div>
          </div>
        </div>
      )}

      <div className="config-help">
        <h4>📚 Hướng dẫn</h4>
        <ol>
          <li>Truy cập <a href="https://aistudio.google.com/" target="_blank" rel="noopener noreferrer">Google AI Studio</a></li>
          <li>Đăng nhập bằng tài khoản Google</li>
          <li>Tạo API key mới</li>
          <li>Copy API key và paste vào form trên</li>
          <li>Chọn model phù hợp (khuyến nghị: gemini-1.5-flash)</li>
          <li>Điều chỉnh temperature và max tokens theo nhu cầu</li>
          <li>Click "Test API Key" để kiểm tra</li>
          <li>Click "Lưu cấu hình" để hoàn tất</li>
        </ol>
        
        <div className="help-features">
          <h5>🚀 Tính năng sau khi cấu hình:</h5>
          <ul>
            <li>Trò chuyện tự nhiên với AI Agent</li>
            <li>Function calling cho các tác vụ cụ thể</li>
            <li>Tạo và kiểm tra CCCD</li>
            <li>Tra cứu mã số thuế</li>
            <li>Phân tích dữ liệu</li>
            <li>Web scraping và form automation</li>
            <li>Tạo báo cáo và xuất Excel</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default GeminiConfigInterface;