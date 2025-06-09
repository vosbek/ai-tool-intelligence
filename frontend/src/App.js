// App.js - Main React application
import React, { useState, useEffect } from 'react';
import './App.css';

// API service
class ApiService {
  static BASE_URL = '/api';

  static async get(endpoint) {
    const response = await fetch(`${this.BASE_URL}${endpoint}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  }

  static async post(endpoint, data) {
    const response = await fetch(`${this.BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  }

  static async put(endpoint, data) {
    const response = await fetch(`${this.BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  }
}

// Tool status badge component
const StatusBadge = ({ status }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'never_run': return 'bg-gray-500';
      case 'processing': return 'bg-yellow-500';
      case 'completed': return 'bg-green-500';
      case 'needs_update': return 'bg-blue-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <span className={`px-2 py-1 rounded text-white text-xs ${getStatusColor(status)}`}>
      {status.replace('_', ' ').toUpperCase()}
    </span>
  );
};

// Tool form component
const ToolForm = ({ tool, categories, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    category_id: '',
    description: '',
    website_url: '',
    github_url: '',
    documentation_url: '',
    changelog_url: '',
    blog_url: '',
    is_open_source: false,
    pricing_model: '',
    internal_notes: '',
    enterprise_position: '',
    ...tool
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  return (
    <div className="max-w-4xl mx-auto bg-white p-6 rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-6">
        {tool ? 'Edit Tool' : 'Add New Tool'}
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Tool Name *</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Cursor"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Category</label>
            <select
              name="category_id"
              value={formData.category_id}
              onChange={handleChange}
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select category</option>
              {categories.map(cat => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Description</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows="3"
            className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Brief description of what this tool does..."
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Website URL *</label>
            <input
              type="url"
              name="website_url"
              value={formData.website_url}
              onChange={handleChange}
              required
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="https://example.com"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">GitHub URL</label>
            <input
              type="url"
              name="github_url"
              value={formData.github_url}
              onChange={handleChange}
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="https://github.com/owner/repo"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Documentation URL</label>
            <input
              type="url"
              name="documentation_url"
              value={formData.documentation_url}
              onChange={handleChange}
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="https://docs.example.com"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Changelog URL</label>
            <input
              type="url"
              name="changelog_url"
              value={formData.changelog_url}
              onChange={handleChange}
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="https://changelog.example.com"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Blog URL</label>
            <input
              type="url"
              name="blog_url"
              value={formData.blog_url}
              onChange={handleChange}
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="https://blog.example.com"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Pricing Model</label>
            <select
              name="pricing_model"
              value={formData.pricing_model}
              onChange={handleChange}
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select pricing model</option>
              <option value="free">Free</option>
              <option value="freemium">Freemium</option>
              <option value="subscription">Subscription</option>
              <option value="enterprise">Enterprise</option>
            </select>
          </div>
        </div>

        <div>
          <label className="flex items-center">
            <input
              type="checkbox"
              name="is_open_source"
              checked={formData.is_open_source}
              onChange={handleChange}
              className="mr-2"
            />
            <span className="text-sm font-medium">Open Source</span>
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Internal Notes</label>
          <textarea
            name="internal_notes"
            value={formData.internal_notes}
            onChange={handleChange}
            rows="3"
            className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Internal team notes about this tool..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Enterprise Position</label>
          <textarea
            name="enterprise_position"
            value={formData.enterprise_position}
            onChange={handleChange}
            rows="3"
            className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Our enterprise position or assessment of this tool..."
          />
        </div>

        <div className="flex gap-2 pt-4">
          <button
            type="submit"
            className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600 transition-colors"
          >
            Save Tool
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="bg-gray-500 text-white px-6 py-2 rounded hover:bg-gray-600 transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

// Tool detail view component
const ToolDetail = ({ tool, onEdit, onResearch, onClose }) => {
  const [isResearching, setIsResearching] = useState(false);
  const [researchResult, setResearchResult] = useState(null);

  const handleResearch = async () => {
    setIsResearching(true);
    setResearchResult(null);
    try {
      const result = await onResearch(tool.id);
      setResearchResult(result);
    } catch (error) {
      setResearchResult({ error: error.message });
    } finally {
      setIsResearching(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto bg-white p-6 rounded-lg shadow">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-3xl font-bold">{tool.name}</h2>
          <div className="mt-2">
            <StatusBadge status={tool.processing_status} />
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onEdit(tool)}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
          >
            Edit
          </button>
          <button
            onClick={handleResearch}
            disabled={isResearching}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition-colors disabled:opacity-50"
          >
            {isResearching ? 'Researching...' : 'Research'}
          </button>
          <button
            onClick={onClose}
            className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 transition-colors"
          >
            Close
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h3 className="font-semibold text-lg mb-3">Basic Information</h3>
          <div className="space-y-2 text-sm">
            <p><strong>Description:</strong> {tool.description || 'No description'}</p>
            <p><strong>Open Source:</strong> {tool.is_open_source ? 'Yes' : 'No'}</p>
            <p><strong>Pricing:</strong> {tool.pricing_model || 'Unknown'}</p>
            {tool.starting_price && (
              <p><strong>Starting Price:</strong> ${tool.starting_price}</p>
            )}
          </div>

          <h3 className="font-semibold text-lg mb-3 mt-6">URLs</h3>
          <div className="space-y-1 text-sm">
            {tool.website_url && (
              <p><a href={tool.website_url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">Website</a></p>
            )}
            {tool.github_url && (
              <p><a href={tool.github_url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">GitHub</a></p>
            )}
            {tool.documentation_url && (
              <p><a href={tool.documentation_url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">Documentation</a></p>
            )}
            {tool.changelog_url && (
              <p><a href={tool.changelog_url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">Changelog</a></p>
            )}
          </div>
        </div>

        <div>
          <h3 className="font-semibold text-lg mb-3">Processing Information</h3>
          <div className="space-y-2 text-sm">
            <p><strong>Status:</strong> <StatusBadge status={tool.processing_status} /></p>
            {tool.last_processed_at && (
              <p><strong>Last Processed:</strong> {new Date(tool.last_processed_at).toLocaleString()}</p>
            )}
            <p><strong>Created:</strong> {new Date(tool.created_at).toLocaleString()}</p>
            <p><strong>Updated:</strong> {new Date(tool.updated_at).toLocaleString()}</p>
          </div>

          {tool.company && (
            <>
              <h3 className="font-semibold text-lg mb-3 mt-6">Company Information</h3>
              <div className="space-y-2 text-sm">
                <p><strong>Company:</strong> {tool.company.name}</p>
                {tool.company.founded_year && (
                  <p><strong>Founded:</strong> {tool.company.founded_year}</p>
                )}
                {tool.company.employee_count && (
                  <p><strong>Employees:</strong> {tool.company.employee_count}</p>
                )}
                {tool.company.headquarters && (
                  <p><strong>Headquarters:</strong> {tool.company.headquarters}</p>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      {(tool.internal_notes || tool.enterprise_position) && (
        <div className="mt-6 pt-4 border-t">
          {tool.internal_notes && (
            <div className="mb-4">
              <h3 className="font-semibold text-lg mb-2">Internal Notes</h3>
              <p className="text-sm bg-gray-50 p-3 rounded">{tool.internal_notes}</p>
            </div>
          )}
          {tool.enterprise_position && (
            <div>
              <h3 className="font-semibold text-lg mb-2">Enterprise Position</h3>
              <p className="text-sm bg-blue-50 p-3 rounded">{tool.enterprise_position}</p>
            </div>
          )}
        </div>
      )}

      {researchResult && (
        <div className="mt-6 pt-4 border-t">
          <h3 className="font-semibold text-lg mb-2">Research Results</h3>
          {researchResult.error ? (
            <div className="bg-red-50 border border-red-200 p-4 rounded">
              <p className="text-red-700">Error: {researchResult.error}</p>
            </div>
          ) : (
            <div className="bg-green-50 border border-green-200 p-4 rounded">
              <p className="text-green-700 mb-2">Research completed successfully!</p>
              <p className="text-sm text-gray-600">Page will reload with updated data shortly...</p>
              <button 
                onClick={() => window.location.reload()} 
                className="mt-2 bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
              >
                Reload Now
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Main App component
const App = () => {
  const [tools, setTools] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedTool, setSelectedTool] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingTool, setEditingTool] = useState(null);
  const [filters, setFilters] = useState({
    category_id: '',
    status: '',
    search: ''
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setError(null);
      const [toolsData, categoriesData] = await Promise.all([
        ApiService.get('/tools'),
        ApiService.get('/categories')
      ]);
      setTools(toolsData.tools || []);
      setCategories(categoriesData || []);
    } catch (error) {
      console.error('Error loading data:', error);
      setError('Failed to load data. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveTool = async (toolData) => {
    try {
      if (editingTool) {
        const updated = await ApiService.put(`/tools/${editingTool.id}`, toolData);
        setTools(prev => prev.map(t => t.id === editingTool.id ? updated : t));
      } else {
        const newTool = await ApiService.post('/tools', toolData);
        setTools(prev => [...prev, newTool]);
      }
      setShowForm(false);
      setEditingTool(null);
    } catch (error) {
      console.error('Error saving tool:', error);
      alert('Failed to save tool. Please try again.');
    }
  };

  const handleResearch = async (toolId) => {
    try {
      const result = await ApiService.post(`/tools/${toolId}/research`);
      // Update the tool in the list
      setTools(prev => prev.map(t => 
        t.id === toolId ? { ...t, processing_status: result.tool?.processing_status || 'processing' } : t
      ));
      return result;
    } catch (error) {
      console.error('Error researching tool:', error);
      throw error;
    }
  };

  const filteredTools = tools.filter(tool => {
    if (filters.category_id && tool.category_id !== parseInt(filters.category_id)) {
      return false;
    }
    if (filters.status && tool.processing_status !== filters.status) {
      return false;
    }
    if (filters.search && !tool.name.toLowerCase().includes(filters.search.toLowerCase())) {
      return false;
    }
    return true;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading AI Tool Intelligence Platform...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">⚠️ Error</div>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={loadInitialData}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (selectedTool) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <ToolDetail
          tool={selectedTool}
          onEdit={(tool) => {
            setEditingTool(tool);
            setShowForm(true);
            setSelectedTool(null);
          }}
          onResearch={handleResearch}
          onClose={() => setSelectedTool(null)}
        />
      </div>
    );
  }

  if (showForm) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <ToolForm
          tool={editingTool}
          categories={categories}
          onSave={handleSaveTool}
          onCancel={() => {
            setShowForm(false);
            setEditingTool(null);
          }}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">AI Tool Intelligence Platform</h1>
              <p className="text-gray-600 mt-1">Comprehensive research and analysis of AI developer tools</p>
            </div>
            <button
              onClick={() => setShowForm(true)}
              className="bg-blue-500 text-white px-6 py-3 rounded hover:bg-blue-600 transition-colors font-medium"
            >
              Add New Tool
            </button>
          </div>

          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="text-2xl font-bold text-blue-600">{tools.length}</div>
              <div className="text-sm text-gray-600">Total Tools</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="text-2xl font-bold text-green-600">
                {tools.filter(t => t.processing_status === 'completed').length}
              </div>
              <div className="text-sm text-gray-600">Researched</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="text-2xl font-bold text-yellow-600">
                {tools.filter(t => t.processing_status === 'processing').length}
              </div>
              <div className="text-sm text-gray-600">Processing</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="text-2xl font-bold text-gray-600">
                {categories.length}
              </div>
              <div className="text-sm text-gray-600">Categories</div>
            </div>
          </div>

          {/* Filters */}
          <div className="bg-white p-4 rounded-lg shadow mb-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Search</label>
                <input
                  type="text"
                  value={filters.search}
                  onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                  placeholder="Search tools..."
                  className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Category</label>
                <select
                  value={filters.category_id}
                  onChange={(e) => setFilters(prev => ({ ...prev, category_id: e.target.value }))}
                  className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All categories</option>
                  {categories.map(cat => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Status</label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                  className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All statuses</option>
                  <option value="never_run">Never Run</option>
                  <option value="processing">Processing</option>
                  <option value="completed">Completed</option>
                  <option value="needs_update">Needs Update</option>
                  <option value="error">Error</option>
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={() => setFilters({ category_id: '', status: '', search: '' })}
                  className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 transition-colors"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          </div>

          {/* Tools table */}
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tool
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Pricing
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Updated
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredTools.map((tool) => {
                  const category = categories.find(c => c.id === tool.category_id);
                  return (
                    <tr key={tool.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{tool.name}</div>
                          <div className="text-sm text-gray-500">
                            {tool.description ? 
                              (tool.description.length > 100 ? 
                                tool.description.substring(0, 100) + '...' : 
                                tool.description
                              ) : 
                              'No description'
                            }
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {category?.name || 'Uncategorized'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <StatusBadge status={tool.processing_status} />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {tool.pricing_model || 'Unknown'}
                        {tool.starting_price && (
                          <div className="text-xs text-gray-400">from ${tool.starting_price}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {tool.last_processed_at ? 
                          new Date(tool.last_processed_at).toLocaleDateString() :
                          new Date(tool.updated_at).toLocaleDateString()
                        }
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                        <button
                          onClick={() => setSelectedTool(tool)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          View
                        </button>
                        <button
                          onClick={() => {
                            setEditingTool(tool);
                            setShowForm(true);
                          }}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleResearch(tool.id)}
                          className="text-green-600 hover:text-green-900"
                        >
                          Research
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            
            {filteredTools.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                <div className="text-xl mb-2">📊</div>
                <div className="text-lg font-medium mb-1">No tools found</div>
                <div className="text-sm">Try adjusting your filters or add a new tool to get started</div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="mt-8 text-center text-sm text-gray-500">
            <p>AI Tool Intelligence Platform - Powered by AWS Strands Agents</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;