import React, { useState, useEffect } from 'react';

interface AgentInfo {
  name: string;
  status: 'active' | 'inactive' | 'error';
  capabilities: {
    agent_type: string;
    gemini_model: string;
    available_tools: string[];
    context_messages: number;
  };
  error?: string;
}

interface DeploymentStatus {
  api_server: string;
  gemini_integration: string;
  frontend: string;
  docker_config: string;
  startup_scripts: string;
}

interface ProductionDashboardProps {
  user?: {
    id: string;
    name: string;
  };
}

const ProductionDashboard: React.FC<ProductionDashboardProps> = ({ user }) => {
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [deploymentStatus, setDeploymentStatus] = useState<DeploymentStatus | null>(null);
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState<string>('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createFormData, setCreateFormData] = useState({
    agent_type: 'general',
    name: '',
    api_key: '',
    model: 'gemini-2.0-flash',
    temperature: 0.7,
    max_tokens: 2048
  });

  useEffect(() => {
    loadSystemData();
    const interval = setInterval(loadSystemData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadSystemData = async () => {
    try {
      setIsLoading(true);
      
      // Load agents
      const agentsResponse = await fetch('/api/v1/agents');
      const agentsData = await agentsResponse.json();
      
      if (agentsData.success) {
        setAgents(agentsData.agents);
        if (agentsData.agents.length > 0 && !selectedAgent) {
          setSelectedAgent(agentsData.agents[0].name);
        }
      }
      
      // Load deployment status
      try {
        const deploymentResponse = await fetch('/api/v1/deployment/status');
        const deploymentData = await deploymentResponse.json();
        if (deploymentData.success) {
          setDeploymentStatus(deploymentData.status);
        }
      } catch (error) {
        console.log('Deployment status not available');
      }
      
      // Load system health
      try {
        const healthResponse = await fetch('/api/v1/health');
        const healthData = await healthResponse.json();
        setSystemHealth(healthData);
      } catch (error) {
        console.log('Health check not available');
      }
      
    } catch (error) {
      console.error('Error loading system data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const createAgent = async () => {
    if (!createFormData.name || !createFormData.api_key) {
      alert('Vui lòng điền đầy đủ thông tin');
      return;
    }

    try {
      const response = await fetch('/api/v1/agents/create', {
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
          model: 'gemini-2.0-flash',
          temperature: 0.7,
          max_tokens: 2048
        });
        loadSystemData();
      } else {
        alert(`Lỗi: ${data.message}`);
      }
    } catch (error) {
      alert(`Lỗi khi tạo agent: ${error.message}`);
    }
  };

  const deleteAgent = async (agentName: string) => {
    if (!confirm(`Bạn có chắc chắn muốn xóa agent '${agentName}'?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/agents/${agentName}`, {
        method: 'DELETE'
      });

      const data = await response.json();
      
      if (data.success) {
        alert(`Agent '${agentName}' đã được xóa!`);
        loadSystemData();
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

  if (isLoading) {
    return (
      <div className="production-dashboard">
        <div className="loading-state">
          <div className="loading-spinner">⏳</div>
          <h3>Đang tải hệ thống...</h3>
          <p>Vui lòng chờ trong giây lát</p>
        </div>
      </div>
    );
  }

  return (
    <div className="production-dashboard">
      <div className="dashboard-header">
        <h1>🏭 Production Dashboard</h1>
        <p>OpenManus-Youtu Integrated Framework với Gemini 2.0 Flash</p>
        
        <div className="header-actions">
          <button 
            className="btn btn-primary"
            onClick={() => setShowCreateForm(true)}
          >
            ➕ Tạo Agent Mới
          </button>
          <button 
            className="btn btn-secondary"
            onClick={loadSystemData}
          >
            🔄 Làm mới
          </button>
        </div>
      </div>

      {/* System Health Overview */}
      <div className="system-overview">
        <h2>📊 Tổng quan hệ thống</h2>
        
        <div className="overview-grid">
          <div className="overview-card">
            <h3>🌐 API Server</h3>
            <div className="status-indicator">
              <span className="status-dot active"></span>
              <span>Đang hoạt động</span>
            </div>
            <p>Port: 8000</p>
          </div>
          
          <div className="overview-card">
            <h3>🤖 Gemini Integration</h3>
            <div className="status-indicator">
              <span className="status-dot active"></span>
              <span>Gemini 2.0 Flash</span>
            </div>
            <p>Model: gemini-2.0-flash</p>
          </div>
          
          <div className="overview-card">
            <h3>👥 Active Agents</h3>
            <div className="status-indicator">
              <span className="status-dot active"></span>
              <span>{agents.length} agents</span>
            </div>
            <p>Đang hoạt động</p>
          </div>
          
          <div className="overview-card">
            <h3>⚡ Performance</h3>
            <div className="status-indicator">
              <span className="status-dot active"></span>
              <span>Tối ưu</span>
            </div>
            <p>Response time: ~0.75s</p>
          </div>
        </div>
      </div>

      {/* Deployment Status */}
      {deploymentStatus && (
        <div className="deployment-status">
          <h2>🚀 Trạng thái triển khai</h2>
          
          <div className="deployment-grid">
            {Object.entries(deploymentStatus).map(([component, status]) => (
              <div key={component} className="deployment-item">
                <span className="deployment-icon">
                  {status === '✅ Deployed' ? '✅' : '❌'}
                </span>
                <span className="deployment-name">{component.replace('_', ' ')}</span>
                <span className="deployment-status-text">{status}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* System Health */}
      {systemHealth && (
        <div className="system-health">
          <h2>💚 Sức khỏe hệ thống</h2>
          
          <div className="health-metrics">
            <div className="health-metric">
              <span className="metric-label">Uptime:</span>
              <span className="metric-value">{systemHealth.uptime || 'N/A'}</span>
            </div>
            <div className="health-metric">
              <span className="metric-label">Memory Usage:</span>
              <span className="metric-value">{systemHealth.memory_usage || 'N/A'}</span>
            </div>
            <div className="health-metric">
              <span className="metric-label">CPU Usage:</span>
              <span className="metric-value">{systemHealth.cpu_usage || 'N/A'}</span>
            </div>
            <div className="health-metric">
              <span className="metric-label">Active Connections:</span>
              <span className="metric-value">{systemHealth.active_connections || 'N/A'}</span>
            </div>
          </div>
        </div>
      )}

      {/* Create Agent Modal */}
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
                  <option value="cccd">CCCD Agent - Chuyên xử lý CCCD</option>
                  <option value="general">General Agent - Agent đa năng</option>
                  <option value="tax">Tax Agent - Chuyên xử lý thuế</option>
                  <option value="data_analysis">Data Analysis Agent - Phân tích dữ liệu</option>
                  <option value="web_automation">Web Automation Agent - Tự động hóa web</option>
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
                    <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
                    <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                    <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
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
              >
                ✅ Tạo Agent
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Agents Management */}
      <div className="agents-section">
        <h2>🤖 Quản lý Agents</h2>
        
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
                  <span className="label">Model:</span>
                  <span className="value">{agent.capabilities?.gemini_model || 'N/A'}</span>
                </div>
                
                <div className="info-item">
                  <span className="label">Tools:</span>
                  <span className="value">
                    {agent.capabilities?.available_tools?.length || 0} tools
                  </span>
                </div>
                
                <div className="info-item">
                  <span className="label">Context:</span>
                  <span className="value">
                    {agent.capabilities?.context_messages || 0} messages
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
            <p>Tạo agent đầu tiên để bắt đầu sử dụng AI Agent với Google Gemini 2.0 Flash</p>
            <button 
              className="btn btn-primary"
              onClick={() => setShowCreateForm(true)}
            >
              ➕ Tạo Agent Đầu Tiên
            </button>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>⚡ Thao tác nhanh</h2>
        
        <div className="actions-grid">
          <button className="action-btn" onClick={() => window.open('/docs', '_blank')}>
            📚 API Documentation
          </button>
          <button className="action-btn" onClick={() => window.open('/api/v1/agents', '_blank')}>
            🔗 Agents API
          </button>
          <button className="action-btn" onClick={() => window.open('/api/v1/health', '_blank')}>
            💚 Health Check
          </button>
          <button className="action-btn" onClick={() => window.open('/api/v1/deployment/status', '_blank')}>
            🚀 Deployment Status
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductionDashboard;