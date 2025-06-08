import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Toaster, toast } from 'react-hot-toast';
import { 
  Settings, 
  PenTool, 
  Calendar, 
  BarChart3, 
  Image, 
  FileText, 
  Download,
  Copy,
  Trash2,
  Plus,
  ChevronDown,
  CheckSquare,
  Square,
  Star,
  RefreshCw
} from 'lucide-react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// API Service
const apiService = {
  // Configuration
  getConfig: () => axios.get(`${API}/config`),
  updateConfig: (config) => axios.post(`${API}/config`, config),
  getAvailableModels: () => axios.get(`${API}/available-models`),
  
  // Post Generation
  generatePosts: (request) => axios.post(`${API}/generate-posts`, request),
  rewriteContent: (request) => axios.post(`${API}/rewrite-content`, request),
  analyzePost: (request) => axios.post(`${API}/analyze-post`, request),
  
  // Scheduling
  schedulePosts: (posts) => axios.post(`${API}/schedule-post`, posts),
  getScheduledPosts: () => axios.get(`${API}/scheduled-posts`),
  deleteScheduledPost: (id) => axios.delete(`${API}/scheduled-posts/${id}`),
  
  // Export
  exportPosts: (format, postIds) => axios.get(`${API}/export-posts/${format}`, { params: { post_ids: postIds } }),
  
  // Images (temporarily disabled)
  searchImages: (query, page = 1) => axios.get(`${API}/search-images`, { params: { query, page } })
};

// Configuration Component
const ConfigurationPage = () => {
  const [config, setConfig] = useState({});
  const [models, setModels] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadConfig();
    loadModels();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await apiService.getConfig();
      setConfig(response.data);
    } catch (error) {
      console.error('Error loading config:', error);
    }
  };

  const loadModels = async () => {
    try {
      const response = await apiService.getAvailableModels();
      setModels(response.data);
    } catch (error) {
      console.error('Error loading models:', error);
    }
  };

  const saveConfig = async () => {
    setLoading(true);
    try {
      await apiService.updateConfig(config);
      toast.success('Configuration saved successfully!');
    } catch (error) {
      toast.error('Error saving configuration');
      console.error('Error saving config:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateConfigField = (field, value) => {
    setConfig(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6 flex items-center">
          <Settings className="mr-2" />
          API Configuration
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* OpenAI */}
          <div>
            <label className="block text-sm font-medium mb-2">OpenAI API Key</label>
            <input
              type="password"
              className="w-full border rounded-lg px-3 py-2"
              placeholder="sk-..."
              value={config.openai_api_key || ''}
              onChange={(e) => updateConfigField('openai_api_key', e.target.value)}
            />
            <p className="text-xs text-gray-500 mt-1">Available models: {models.openai?.join(', ')}</p>
          </div>

          {/* Anthropic */}
          <div>
            <label className="block text-sm font-medium mb-2">Anthropic API Key</label>
            <input
              type="password"
              className="w-full border rounded-lg px-3 py-2"
              placeholder="sk-ant-..."
              value={config.anthropic_api_key || ''}
              onChange={(e) => updateConfigField('anthropic_api_key', e.target.value)}
            />
            <p className="text-xs text-gray-500 mt-1">Available models: {models.anthropic?.join(', ')}</p>
          </div>

          {/* Gemini */}
          <div>
            <label className="block text-sm font-medium mb-2">Gemini API Key</label>
            <input
              type="password"
              className="w-full border rounded-lg px-3 py-2"
              placeholder="AIza..."
              value={config.gemini_api_key || ''}
              onChange={(e) => updateConfigField('gemini_api_key', e.target.value)}
            />
            <p className="text-xs text-gray-500 mt-1">Available models: {models.gemini?.join(', ')}</p>
          </div>

          {/* Groq */}
          <div>
            <label className="block text-sm font-medium mb-2">Groq API Key</label>
            <input
              type="password"
              className="w-full border rounded-lg px-3 py-2"
              placeholder="gsk_..."
              value={config.groq_api_key || ''}
              onChange={(e) => updateConfigField('groq_api_key', e.target.value)}
            />
            <p className="text-xs text-gray-500 mt-1">Available models: {models.groq?.join(', ')}</p>
          </div>

          {/* Unsplash */}
          <div className="md:col-span-2">
            <label className="block text-sm font-medium mb-2">Unsplash API Key (Optional)</label>
            <input
              type="password"
              className="w-full border rounded-lg px-3 py-2"
              placeholder="Access Key..."
              value={config.unsplash_api_key || ''}
              onChange={(e) => updateConfigField('unsplash_api_key', e.target.value)}
            />
            <p className="text-xs text-gray-500 mt-1">For image suggestions feature</p>
          </div>
        </div>

        <button
          onClick={saveConfig}
          disabled={loading}
          className="mt-6 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
        >
          {loading && <RefreshCw className="animate-spin mr-2 w-4 h-4" />}
          Save Configuration
        </button>
      </div>
    </div>
  );
};

// Post Generator Component
const PostGenerator = () => {
  const [request, setRequest] = useState({
    platforms: [],
    post_type: 'General Update',
    product_description: '',
    tone_style: 'Professional',
    include_hashtags: false,
    include_emojis: false,
    include_seo_optimization: false,
    seo_keywords: '',
    variants_count: 1,
    audience_target: {
      age_range: '',
      gender: '',
      interests: '',
      location: ''
    },
    ai_provider: 'openai',
    ai_model: 'gpt-4o-mini'
  });
  
  const [generatedPosts, setGeneratedPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState({});

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      const response = await apiService.getAvailableModels();
      setModels(response.data);
    } catch (error) {
      console.error('Error loading models:', error);
    }
  };

  const platforms = [
    { id: 'facebook', name: 'Facebook' },
    { id: 'instagram', name: 'Instagram' },
    { id: 'twitter', name: 'Twitter/X' },
    { id: 'linkedin', name: 'LinkedIn' },
    { id: 'tiktok', name: 'TikTok' },
    { id: 'google_ads', name: 'Google Ads' }
  ];

  const postTypes = [
    'General Update', 'Promotional', 'Product Launch', 
    'Event Announcement', 'Customer Testimonial', 
    'Behind the Scenes', 'Tips & Tricks'
  ];

  const toneStyles = [
    'Professional', 'Friendly', 'Playful', 'Urgency', 'Inspirational'
  ];

  const providers = [
    { id: 'openai', name: 'OpenAI' },
    { id: 'anthropic', name: 'Anthropic (Claude)' },
    { id: 'gemini', name: 'Google Gemini' },
    { id: 'groq', name: 'Groq' }
  ];

  const togglePlatform = (platformId) => {
    setRequest(prev => ({
      ...prev,
      platforms: prev.platforms.includes(platformId)
        ? prev.platforms.filter(p => p !== platformId)
        : [...prev.platforms, platformId]
    }));
  };

  const generatePosts = async () => {
    if (request.platforms.length === 0) {
      toast.error('Please select at least one platform');
      return;
    }
    if (!request.product_description.trim()) {
      toast.error('Please enter a product description');
      return;
    }

    setLoading(true);
    try {
      const response = await apiService.generatePosts(request);
      setGeneratedPosts(response.data);
      toast.success('Posts generated successfully!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error generating posts');
      console.error('Error generating posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const exportPosts = async (format) => {
    if (generatedPosts.length === 0) {
      toast.error('No posts to export');
      return;
    }

    try {
      const postIds = generatedPosts.map(post => post.id);
      const response = await apiService.exportPosts(format, postIds);
      
      // Create and download file
      const blob = new Blob([response.data.content], { 
        type: format === 'csv' ? 'text/csv' : 'text/plain' 
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = response.data.filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast.success(`Posts exported as ${format.toUpperCase()}`);
    } catch (error) {
      toast.error('Error exporting posts');
      console.error('Export error:', error);
    }
  };

  const schedulePost = async (postContent, platform) => {
    // For now, schedule for 1 hour from now - in a real app, user would select date/time
    const scheduledDate = new Date();
    scheduledDate.setHours(scheduledDate.getHours() + 1);

    try {
      await apiService.schedulePosts({
        platform: platform,
        content: postContent.content,
        hashtags: postContent.hashtags,
        scheduled_date: scheduledDate.toISOString()
      });
      toast.success('Post scheduled successfully!');
    } catch (error) {
      toast.error('Error scheduling post');
      console.error('Scheduling error:', error);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Generator Form */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold mb-6 flex items-center">
            <PenTool className="mr-2" />
            Generate Posts
          </h2>

          {/* Platform Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-3">Select Platforms</label>
            <div className="grid grid-cols-2 gap-2">
              {platforms.map(platform => (
                <div
                  key={platform.id}
                  onClick={() => togglePlatform(platform.id)}
                  className={`p-3 border rounded-lg cursor-pointer flex items-center ${
                    request.platforms.includes(platform.id)
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  {request.platforms.includes(platform.id) ? 
                    <CheckSquare className="w-4 h-4 mr-2" /> : 
                    <Square className="w-4 h-4 mr-2" />
                  }
                  {platform.name}
                </div>
              ))}
            </div>
          </div>

          {/* Post Type */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Post Type</label>
            <select
              value={request.post_type}
              onChange={(e) => setRequest(prev => ({ ...prev, post_type: e.target.value }))}
              className="w-full border rounded-lg px-3 py-2"
            >
              {postTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          {/* Product Description */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Product/Content Description</label>
            <textarea
              value={request.product_description}
              onChange={(e) => setRequest(prev => ({ ...prev, product_description: e.target.value }))}
              className="w-full border rounded-lg px-3 py-2 h-24"
              placeholder="Describe your product, service, or the content you want to promote..."
            />
          </div>

          {/* Tone Style */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Tone & Style</label>
            <select
              value={request.tone_style}
              onChange={(e) => setRequest(prev => ({ ...prev, tone_style: e.target.value }))}
              className="w-full border rounded-lg px-3 py-2"
            >
              {toneStyles.map(tone => (
                <option key={tone} value={tone}>{tone}</option>
              ))}
            </select>
          </div>

          {/* Options */}
          <div className="mb-4 space-y-2">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={request.include_hashtags}
                onChange={(e) => setRequest(prev => ({ ...prev, include_hashtags: e.target.checked }))}
                className="mr-2"
              />
              Include Hashtags
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={request.include_emojis}
                onChange={(e) => setRequest(prev => ({ ...prev, include_emojis: e.target.checked }))}
                className="mr-2"
              />
              Include Emojis
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={request.include_seo_optimization}
                onChange={(e) => setRequest(prev => ({ ...prev, include_seo_optimization: e.target.checked }))}
                className="mr-2"
              />
              SEO Optimization
            </label>
          </div>

          {request.include_seo_optimization && (
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">SEO Keywords</label>
              <input
                type="text"
                value={request.seo_keywords}
                onChange={(e) => setRequest(prev => ({ ...prev, seo_keywords: e.target.value }))}
                className="w-full border rounded-lg px-3 py-2"
                placeholder="keyword1, keyword2, keyword3"
              />
            </div>
          )}

          {/* Variants */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Number of Variants</label>
            <select
              value={request.variants_count}
              onChange={(e) => setRequest(prev => ({ ...prev, variants_count: parseInt(e.target.value) }))}
              className="w-full border rounded-lg px-3 py-2"
            >
              {[1, 2, 3, 4, 5].map(num => (
                <option key={num} value={num}>{num}</option>
              ))}
            </select>
          </div>

          {/* AI Provider */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">AI Provider</label>
            <select
              value={request.ai_provider}
              onChange={(e) => setRequest(prev => ({ ...prev, ai_provider: e.target.value, ai_model: models[e.target.value]?.[0] || '' }))}
              className="w-full border rounded-lg px-3 py-2"
            >
              {providers.map(provider => (
                <option key={provider.id} value={provider.id}>{provider.name}</option>
              ))}
            </select>
          </div>

          {/* AI Model */}
          {models[request.ai_provider] && (
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">AI Model</label>
              <select
                value={request.ai_model}
                onChange={(e) => setRequest(prev => ({ ...prev, ai_model: e.target.value }))}
                className="w-full border rounded-lg px-3 py-2"
              >
                {models[request.ai_provider].map(model => (
                  <option key={model} value={model}>{model}</option>
                ))}
              </select>
            </div>
          )}

          {/* Audience Targeting */}
          <div className="mb-6 border-t pt-4">
            <h4 className="text-sm font-medium mb-3">Audience Targeting (Optional)</h4>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-gray-600 mb-1">Age Range</label>
                <input
                  type="text"
                  value={request.audience_target.age_range}
                  onChange={(e) => setRequest(prev => ({ 
                    ...prev, 
                    audience_target: { ...prev.audience_target, age_range: e.target.value }
                  }))}
                  className="w-full border rounded px-2 py-1 text-sm"
                  placeholder="25-35"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Gender</label>
                <select
                  value={request.audience_target.gender}
                  onChange={(e) => setRequest(prev => ({ 
                    ...prev, 
                    audience_target: { ...prev.audience_target, gender: e.target.value }
                  }))}
                  className="w-full border rounded px-2 py-1 text-sm"
                >
                  <option value="">Any</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Non-binary">Non-binary</option>
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Interests</label>
                <input
                  type="text"
                  value={request.audience_target.interests}
                  onChange={(e) => setRequest(prev => ({ 
                    ...prev, 
                    audience_target: { ...prev.audience_target, interests: e.target.value }
                  }))}
                  className="w-full border rounded px-2 py-1 text-sm"
                  placeholder="technology, fitness"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Location</label>
                <input
                  type="text"
                  value={request.audience_target.location}
                  onChange={(e) => setRequest(prev => ({ 
                    ...prev, 
                    audience_target: { ...prev.audience_target, location: e.target.value }
                  }))}
                  className="w-full border rounded px-2 py-1 text-sm"
                  placeholder="United States"
                />
              </div>
            </div>
          </div>

          <button
            onClick={generatePosts}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center"
          >
            {loading && <RefreshCw className="animate-spin mr-2 w-4 h-4" />}
            Generate Posts
          </button>
        </div>

        {/* Generated Posts */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold">Generated Posts</h3>
            {generatedPosts.length > 0 && (
              <div className="flex space-x-2">
                <button
                  onClick={() => exportPosts('csv')}
                  className="text-sm bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 flex items-center"
                >
                  <Download className="w-3 h-3 mr-1" />
                  CSV
                </button>
                <button
                  onClick={() => exportPosts('txt')}
                  className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 flex items-center"
                >
                  <Download className="w-3 h-3 mr-1" />
                  TXT
                </button>
                <button
                  onClick={() => exportPosts('json')}
                  className="text-sm bg-purple-600 text-white px-3 py-1 rounded hover:bg-purple-700 flex items-center"
                >
                  <Download className="w-3 h-3 mr-1" />
                  JSON
                </button>
              </div>
            )}
          </div>
          
          {generatedPosts.length === 0 ? (
            <div className="text-gray-500 text-center py-8">
              No posts generated yet. Fill out the form and click "Generate Posts" to get started.
            </div>
          ) : (
            <div className="space-y-6">
              {generatedPosts.map((postGroup, groupIndex) => (
                <div key={groupIndex} className="border rounded-lg p-4">
                  <h4 className="font-semibold mb-3">Variant {postGroup.variant_number}</h4>
                  
                  {postGroup.post_contents.map((post, postIndex) => (
                    <div key={postIndex} className="mb-4 border-l-4 border-blue-200 pl-4">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium text-blue-600 capitalize">{post.platform}</span>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => schedulePost(post, post.platform)}
                            className="text-gray-500 hover:text-gray-700"
                            title="Schedule Post"
                          >
                            <Calendar className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => copyToClipboard(post.content)}
                            className="text-gray-500 hover:text-gray-700"
                            title="Copy Content"
                          >
                            <Copy className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                      
                      <p className="text-gray-800 mb-2">{post.content}</p>
                      
                      {post.hashtags && (
                        <p className="text-blue-500 text-sm">
                          {post.hashtags.map(tag => `#${tag}`).join(' ')}
                        </p>
                      )}
                      
                      {post.meta_description && (
                        <p className="text-gray-600 text-sm mt-2">
                          <strong>Meta Description:</strong> {post.meta_description}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Content Rewriter Component
const ContentRewriter = () => {
  const [originalContent, setOriginalContent] = useState('');
  const [toneStyle, setToneStyle] = useState('Professional');
  const [platform, setPlatform] = useState('facebook');
  const [provider, setProvider] = useState('openai');
  const [model, setModel] = useState('gpt-4o-mini');
  const [rewrittenContent, setRewrittenContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState({});

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      const response = await apiService.getAvailableModels();
      setModels(response.data);
    } catch (error) {
      console.error('Error loading models:', error);
    }
  };

  const rewriteContent = async () => {
    if (!originalContent.trim()) {
      toast.error('Please enter content to rewrite');
      return;
    }

    setLoading(true);
    try {
      const response = await apiService.rewriteContent({
        original_content: originalContent,
        tone_style: toneStyle,
        platform,
        ai_provider: provider,
        ai_model: model
      });
      setRewrittenContent(response.data.rewritten_content);
      toast.success('Content rewritten successfully!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error rewriting content');
      console.error('Error rewriting content:', error);
    } finally {
      setLoading(false);
    }
  };

  const toneStyles = ['Professional', 'Friendly', 'Playful', 'Urgency', 'Inspirational'];
  const platforms = [
    { id: 'facebook', name: 'Facebook' },
    { id: 'instagram', name: 'Instagram' },
    { id: 'twitter', name: 'Twitter/X' },
    { id: 'linkedin', name: 'LinkedIn' },
    { id: 'tiktok', name: 'TikTok' },
    { id: 'google_ads', name: 'Google Ads' }
  ];
  const providers = [
    { id: 'openai', name: 'OpenAI' },
    { id: 'anthropic', name: 'Anthropic (Claude)' },
    { id: 'gemini', name: 'Google Gemini' },
    { id: 'groq', name: 'Groq' }
  ];

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6 flex items-center">
          <RefreshCw className="mr-2" />
          Content Rewriter
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Settings */}
          <div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Platform</label>
              <select
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
                className="w-full border rounded-lg px-3 py-2"
              >
                {platforms.map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Tone Style</label>
              <select
                value={toneStyle}
                onChange={(e) => setToneStyle(e.target.value)}
                className="w-full border rounded-lg px-3 py-2"
              >
                {toneStyles.map(tone => (
                  <option key={tone} value={tone}>{tone}</option>
                ))}
              </select>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">AI Provider</label>
              <select
                value={provider}
                onChange={(e) => {
                  setProvider(e.target.value);
                  setModel(models[e.target.value]?.[0] || '');
                }}
                className="w-full border rounded-lg px-3 py-2"
              >
                {providers.map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>

            {models[provider] && (
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">AI Model</label>
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full border rounded-lg px-3 py-2"
                >
                  {models[provider].map(m => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* Content Input */}
          <div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Original Content</label>
              <textarea
                value={originalContent}
                onChange={(e) => setOriginalContent(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 h-32"
                placeholder="Paste your existing content here..."
              />
            </div>

            <button
              onClick={rewriteContent}
              disabled={loading}
              className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center justify-center"
            >
              {loading && <RefreshCw className="animate-spin mr-2 w-4 h-4" />}
              Rewrite Content
            </button>
          </div>
        </div>

        {/* Rewritten Content */}
        {rewrittenContent && (
          <div className="mt-6 border-t pt-6">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-lg font-semibold">Rewritten Content</h3>
              <button
                onClick={() => navigator.clipboard.writeText(rewrittenContent)}
                className="text-blue-600 hover:text-blue-700"
              >
                <Copy className="w-4 h-4" />
              </button>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-gray-800">{rewrittenContent}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Navigation Component
const Navigation = () => {
  return (
    <nav className="bg-white shadow-lg border-b">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-gray-800">
              AI Marketing Assistant
            </Link>
          </div>
          
          <div className="flex space-x-8">
            <Link
              to="/generate"
              className="flex items-center text-gray-600 hover:text-gray-800 px-3 py-2 rounded-md"
            >
              <PenTool className="w-4 h-4 mr-2" />
              Generate
            </Link>
            <Link
              to="/rewrite"
              className="flex items-center text-gray-600 hover:text-gray-800 px-3 py-2 rounded-md"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Rewrite
            </Link>
            <Link
              to="/analyze"
              className="flex items-center text-gray-600 hover:text-gray-800 px-3 py-2 rounded-md"
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              Analyze
            </Link>
            <Link
              to="/config"
              className="flex items-center text-gray-600 hover:text-gray-800 px-3 py-2 rounded-md"
            >
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

// Home Page
const HomePage = () => {
  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          AI-Powered Marketing Assistant
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Generate, optimize, and schedule marketing content across multiple platforms
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-12">
          <Link
            to="/generate"
            className="bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
          >
            <PenTool className="w-12 h-12 text-blue-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Generate Posts</h3>
            <p className="text-gray-600">Create optimized content for multiple platforms</p>
          </Link>
          
          <Link
            to="/rewrite"
            className="bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
          >
            <RefreshCw className="w-12 h-12 text-green-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Rewrite Content</h3>
            <p className="text-gray-600">Improve existing posts with AI</p>
          </Link>
          
          <Link
            to="/analyze"
            className="bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
          >
            <BarChart3 className="w-12 h-12 text-purple-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Analyze Posts</h3>
            <p className="text-gray-600">Get engagement scores and improvement tips</p>
          </Link>
          
          <Link
            to="/config"
            className="bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
          >
            <Settings className="w-12 h-12 text-orange-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Configuration</h3>
            <p className="text-gray-600">Set up your AI API keys</p>
          </Link>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-2xl font-bold mb-6">Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold mb-2">🤖 Multi-AI Support</h3>
            <p className="text-gray-600">OpenAI, Claude, Gemini, and Groq integration</p>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-2">📱 Multi-Platform</h3>
            <p className="text-gray-600">Facebook, Instagram, Twitter, LinkedIn, TikTok, Google Ads</p>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-2">🎨 Tone & Style Control</h3>
            <p className="text-gray-600">Professional, Friendly, Playful, Urgency, Inspirational</p>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-2">📈 A/B Testing</h3>
            <p className="text-gray-600">Generate multiple variants for testing</p>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-2">🏷️ Smart Hashtags</h3>
            <p className="text-gray-600">Auto-generate relevant hashtags</p>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-2">🎯 Audience Targeting</h3>
            <p className="text-gray-600">Customize content for specific demographics</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Post Analyzer Component
const PostAnalyzer = () => {
  const [content, setContent] = useState('');
  const [platform, setPlatform] = useState('facebook');
  const [provider, setProvider] = useState('openai');
  const [model, setModel] = useState('gpt-4o-mini');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState({});

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      const response = await apiService.getAvailableModels();
      setModels(response.data);
    } catch (error) {
      console.error('Error loading models:', error);
    }
  };

  const analyzePost = async () => {
    if (!content.trim()) {
      toast.error('Please enter content to analyze');
      return;
    }

    setLoading(true);
    try {
      const response = await apiService.analyzePost({
        content,
        platform,
        ai_provider: provider,
        ai_model: model
      });
      setAnalysis(response.data);
      toast.success('Post analyzed successfully!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error analyzing post');
      console.error('Error analyzing post:', error);
    } finally {
      setLoading(false);
    }
  };

  const platforms = [
    { id: 'facebook', name: 'Facebook' },
    { id: 'instagram', name: 'Instagram' },
    { id: 'twitter', name: 'Twitter/X' },
    { id: 'linkedin', name: 'LinkedIn' },
    { id: 'tiktok', name: 'TikTok' },
    { id: 'google_ads', name: 'Google Ads' }
  ];

  const providers = [
    { id: 'openai', name: 'OpenAI' },
    { id: 'anthropic', name: 'Anthropic (Claude)' },
    { id: 'gemini', name: 'Google Gemini' },
    { id: 'groq', name: 'Groq' }
  ];

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBackground = (score) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6 flex items-center">
          <BarChart3 className="mr-2" />
          Post Analyzer
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Analysis Form */}
          <div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Platform</label>
              <select
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
                className="w-full border rounded-lg px-3 py-2"
              >
                {platforms.map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">AI Provider</label>
              <select
                value={provider}
                onChange={(e) => {
                  setProvider(e.target.value);
                  setModel(models[e.target.value]?.[0] || '');
                }}
                className="w-full border rounded-lg px-3 py-2"
              >
                {providers.map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>

            {models[provider] && (
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">AI Model</label>
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full border rounded-lg px-3 py-2"
                >
                  {models[provider].map(m => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>
            )}

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Post Content</label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 h-32"
                placeholder="Paste your post content here to analyze..."
              />
            </div>

            <button
              onClick={analyzePost}
              disabled={loading}
              className="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center justify-center"
            >
              {loading && <RefreshCw className="animate-spin mr-2 w-4 h-4" />}
              Analyze Post
            </button>
          </div>

          {/* Analysis Results */}
          <div>
            {!analysis ? (
              <div className="text-center py-12 text-gray-500">
                <BarChart3 className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <p>Enter your post content and click "Analyze Post"</p>
                <p className="text-sm">Get engagement scores and improvement tips.</p>
              </div>
            ) : (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Analysis Results</h3>
                
                {/* Score Cards */}
                <div className="grid grid-cols-2 gap-3">
                  <div className={`p-3 rounded-lg ${getScoreBackground(analysis.engagement_score)}`}>
                    <div className="text-sm text-gray-600">Engagement</div>
                    <div className={`text-2xl font-bold ${getScoreColor(analysis.engagement_score)}`}>
                      {analysis.engagement_score}
                    </div>
                  </div>
                  
                  <div className={`p-3 rounded-lg ${getScoreBackground(analysis.readability_score)}`}>
                    <div className="text-sm text-gray-600">Readability</div>
                    <div className={`text-2xl font-bold ${getScoreColor(analysis.readability_score)}`}>
                      {analysis.readability_score}
                    </div>
                  </div>
                  
                  <div className={`p-3 rounded-lg ${getScoreBackground(analysis.tone_consistency_score)}`}>
                    <div className="text-sm text-gray-600">Tone</div>
                    <div className={`text-2xl font-bold ${getScoreColor(analysis.tone_consistency_score)}`}>
                      {analysis.tone_consistency_score}
                    </div>
                  </div>
                  
                  <div className={`p-3 rounded-lg ${getScoreBackground(analysis.platform_best_practices_score)}`}>
                    <div className="text-sm text-gray-600">Platform</div>
                    <div className={`text-2xl font-bold ${getScoreColor(analysis.platform_best_practices_score)}`}>
                      {analysis.platform_best_practices_score}
                    </div>
                  </div>
                </div>

                {/* Overall Score */}
                <div className={`p-4 rounded-lg ${getScoreBackground(analysis.overall_score)} border-2 border-current`}>
                  <div className="text-center">
                    <div className="text-sm text-gray-600 mb-1">Overall Score</div>
                    <div className={`text-3xl font-bold ${getScoreColor(analysis.overall_score)}`}>
                      {analysis.overall_score}/100
                    </div>
                  </div>
                </div>

                {/* Improvement Tips */}
                {analysis.improvement_tips && analysis.improvement_tips.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2 flex items-center">
                      <Star className="w-4 h-4 mr-2 text-yellow-500" />
                      Improvement Tips
                    </h4>
                    <ul className="space-y-2">
                      {analysis.improvement_tips.map((tip, index) => (
                        <li key={index} className="text-sm text-gray-700 flex items-start">
                          <span className="w-2 h-2 bg-blue-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                          {tip}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        
        <main className="py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/generate" element={<PostGenerator />} />
            <Route path="/rewrite" element={<ContentRewriter />} />
            <Route path="/analyze" element={<PostAnalyzer />} />
            <Route path="/config" element={<ConfigurationPage />} />
          </Routes>
        </main>
        
        <Toaster position="top-right" />
      </div>
    </BrowserRouter>
  );
}

export default App;