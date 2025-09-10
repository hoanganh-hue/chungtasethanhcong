import React, { useState, useEffect } from 'react';

interface AgentCapabilities {
  agent_type: string;
  name: string;
  description: string;
  capabilities: Record<string, boolean>;
  gemini_model: string;
  function_calling_enabled: boolean;
  streaming_enabled: boolean;
  available_tools: string[];
  memory_enabled: boolean;
  state_tracking_enabled: boolean;
}

interface AgentInfo {
  name: string;
  capabilities: AgentCapabilities;
  status: 'active' | 'inactive' | 'error';
  error?: string;
}

interface UnifiedGeminiDashboardProps {
  user?: {
    id: string;
    name: string;
  };
}

const UnifiedGeminiDashboard: React.FC<UnifiedGeminiDashboardProps> = ({ user }) => {
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string>('');
  const [isCreatingAgent, setIsCreatingAgent] = useState(false);
  const [agentTypes, setAgentTypes] = useState<Record<string, any>>({});
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createFormData, setCreateFormData] = useState({
    agent_type: 'general',
    name: '',
    api_key: '',
    model: 'gemini-1.5-flash',
    temperature: 0.7,
    max_tokens: 2048
  });

  useEffect(() => {
    loadAgents();
    loadAgentTypes();
  }, []);

  const loadAgents = async () => {
    try {
      const response = await fetch('/api/agents');
      const data = await response.json();
      
      if (data.success) {
        setAgents(data.agents);
        if (data.agents.length > 0 && !selectedAgent) {
          setSelectedAgent(data.agents[0].name);
        }
      }
    } catch (error) {
      console.error('Error loading agents:', error);
    }
  };

  const loadAgentTypes = async () => {
    try {
      const response = await fetch('/api/agents/types');
      const data = await response.json();
      
      if (data.success) {
        setAgentTypes(data.agent_types);
      }
    } catch (error) {
      console.error('Error loading agent types:', error);
    }
  };

  const createAgent = async () => {
    if (!createFormData.name || !createFormData.api_key) {
      alert('Vui lòng điền đầy đủ thông tin');
      return;
    }

    setIsCreatingAgent(true);

    try {
      const response = await fetch('/api/agents/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(createFormData)
      });

      const data = await response.json();
      
      if (data.success) {
        alert(`Agent '${data.agent_name}' đã được tạo thành công!`);
        setShowCreateForm(false);
        setCreateFormData({
          agent_type: 'general',
          name: '',
          api_key: '',
          model: 'gemini-1.5-flash',
          temperature: 0.7,
          max_tokens: 2048
        });
        loadAgents();
      } else {
        alert(`Lỗi: ${data.message}`);
      }
    } catch (error) {
      alert(`Lỗi khi tạo agent: ${error.message}`);
    } finally {
      setIsCreatingAgent(false);
    }
  };

  const deleteAgent = async (agentName: string) => {
    if (!confirm(`Bạn có chắc chắn muốn xóa agent '${agentName}'?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/agents/${agentName}`, {
        method: 'DELETE'
      });

      const data = await response.json();
      
      if (data.success) {
        alert(`Agent '${agentName}' đã được xóa!`);
        loadAgents();
      } else {
        alert(`Lỗi: ${data.message}`);
      }
    } catch (error) {
      alert(`Lỗi khi xóa agent: ${error.message}`);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#4caf50';
      case 'inactive': return '#ff9800';
      case 'error': return '#f44336';
      default: return '#666';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return '🟢';
      case 'inactive': return '🟡';
      case 'error': return '🔴';
      default: return '⚪';
    }
  };

  return (
    <div className="unified-gemini-dashboard">
      <div className="dashboard-header">
        <h2>🤖 Unified Gemini AI Agents</h2>
        <p>Quản lý và tương tác với các AI Agent được tích hợp Google Gemini</p>
        
        <div className="header-actions">
          <button 
            className="btn btn-primary"
            onClick={() => setShowCreateForm(true)}
          >
            ➕ Tạo Agent Mới
          </button>
          <button 
            className="btn btn-secondary"
            onClick={loadAgents}
          >
            🔄 Làm mới
          </button>
        </div>
      </div>

      {showCreateForm && (
        <div className="create-agent-modal">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Tạo Agent Mới</h3>
              <button 
                className="btn-close"
                onClick={() => setShowCreateForm(false)}
              >
                ✕
              </button>
            </div>
            
            <div className="modal-body">
              <div className="form-group">
                <label>Loại Agent</label>
                <select
                  value={createFormData.agent_type}
                  onChange={(e) => setCreateFormData({
                    ...createFormData,
                    agent_type: e.target.value,
                    name: `${e.target.value}_agent_${Date.now()}`
                  })}
                >
                  {Object.entries(agentTypes).map(([key, type]) => (
                    <option key={key} value={key}>
                      {type.name} - {type.description}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Tên Agent</label>
                <input
                  type="text"
                  value={createFormData.name}
                  onChange={(e) => setCreateFormData({
                    ...createFormData,
                    name: e.target.value
                  })}
                  placeholder="Nhập tên agent..."
                />
              </div>

              <div className="form-group">
                <label>Gemini API Key *</label>
                <input
                  type="password"
                  value={createFormData.api_key}
                  onChange={(e) => setCreateFormData({
                    ...createFormData,
                    api_key: e.target.value
                  })}
                  placeholder="Nhập Gemini API key..."
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Model</label>
                  <select
                    value={createFormData.model}
                    onChange={(e) => setCreateFormData({
                      ...createFormData,
                      model: e.target.value
                    })}
                  >
                    <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                    <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                    <option value="gemini-1.0-pro">Gemini 1.0 Pro</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Temperature: {createFormData.temperature}</label>
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    value={createFormData.temperature}
                    onChange={(e) => setCreateFormData({
                      ...createFormData,
                      temperature: parseFloat(e.target.value)
                    })}
                  />
                </div>
              </div>
            </div>
            
            <div className="modal-footer">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowCreateForm(false)}
              >
                Hủy
              </button>
              <button 
                className="btn btn-primary"
                onClick={createAgent}
                disabled={isCreatingAgent}
              >
                {isCreatingAgent ? '⏳ Đang tạo...' : '✅ Tạo Agent'}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="agents-grid">
        {agents.map((agent) => (
          <div key={agent.name} className="agent-card">
            <div className="agent-header">
              <div className="agent-title">
                <h3>{agent.name}</h3>
                <span 
                  className="agent-status"
                  style={{ color: getStatusColor(agent.status) }}
                >
                  {getStatusIcon(agent.status)} {agent.status}
                </span>
              </div>
              
              <div className="agent-actions">
                <button 
                  className="btn btn-sm btn-primary"
                  onClick={() => setSelectedAgent(agent.name)}
                  disabled={agent.status !== 'active'}
                >
                  💬 Chat
                </button>
                <button 
                  className="btn btn-sm btn-danger"
                  onClick={() => deleteAgent(agent.name)}
                >
                  🗑️ Xóa
                </button>
              </div>
            </div>

            <div className="agent-info">
              <div className="info-item">
                <span className="label">Mô tả:</span>
                <span className="value">{agent.capabilities?.description || 'N/A'}</span>
              </div>
              
              <div className="info-item">
                <span className="label">Model:</span>
                <span className="value">{agent.capabilities?.gemini_model || 'N/A'}</span>
              </div>
              
              <div className="info-item">
                <span className="label">Function Calling:</span>
                <span className="value">
                  {agent.capabilities?.function_calling_enabled ? '✅' : '❌'}
                </span>
              </div>
              
              <div className="info-item">
                <span className="label">Streaming:</span>
                <span className="value">
                  {agent.capabilities?.streaming_enabled ? '✅' : '❌'}
                </span>
              </div>
              
              <div className="info-item">
                <span className="label">Tools:</span>
                <span className="value">
                  {agent.capabilities?.available_tools?.length || 0} tools
                </span>
              </div>
            </div>

            {agent.capabilities?.available_tools && agent.capabilities.available_tools.length > 0 && (
              <div className="agent-tools">
                <h4>🛠️ Available Tools:</h4>
                <div className="tools-list">
                  {agent.capabilities.available_tools.map((tool, index) => (
                    <span key={index} className="tool-tag">
                      {tool}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {agent.error && (
              <div className="agent-error">
                <span className="error-icon">❌</span>
                <span className="error-message">{agent.error}</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {agents.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🤖</div>
          <h3>Chưa có Agent nào</h3>
          <p>Tạo agent đầu tiên để bắt đầu sử dụng AI Agent với Google Gemini</p>
          <button 
            className="btn btn-primary"
            onClick={() => setShowCreateForm(true)}
          >
            ➕ Tạo Agent Đầu Tiên
          </button>
        </div>
      )}

      {selectedAgent && (
        <div className="selected-agent-info">
          <h3>📊 Thông tin Agent: {selectedAgent}</h3>
          <div className="agent-details">
            {(() => {
              const agent = agents.find(a => a.name === selectedAgent);
              if (!agent) return null;
              
              return (
                <div className="capabilities-grid">
                  {Object.entries(agent.capabilities?.capabilities || {}).map(([key, value]) => (
                    <div key={key} className="capability-item">
                      <span className="capability-name">{key.replace(/_/g, ' ')}</span>
                      <span className="capability-status">
                        {value ? '✅' : '❌'}
                      </span>
                    </div>
                  ))}
                </div>
              );
            })()}
          </div>
        </div>
      )}
    </div>
  );
};

export default UnifiedGeminiDashboard;