#!/usr/bin/env python3
"""
AI Tool Intelligence Platform - Main Application

A comprehensive platform for tracking and analyzing AI development tools,
featuring automated research using Strands Agents and competitive intelligence.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import json
import sys

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-in-production')

# Enable CORS for React frontend
CORS(app)

# Initialize database
db = SQLAlchemy(app)

# Database Models
class Category(db.Model):
    __tablename__ = 'categories'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
    tools = db.relationship('Tool', backref='category')

class Tool(db.Model):
    __tablename__ = 'tools'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    # Basic info
    description = db.Column(db.Text)
    website_url = db.Column(db.String(500))
    github_url = db.Column(db.String(500))
    documentation_url = db.Column(db.String(500))
    changelog_url = db.Column(db.String(500))
    blog_url = db.Column(db.String(500))
    
    # Tool details
    is_open_source = db.Column(db.Boolean, default=False)
    license_type = db.Column(db.String(100))
    primary_language = db.Column(db.String(50))
    supported_platforms = db.Column(db.Text)  # JSON
    
    # Pricing
    pricing_model = db.Column(db.String(50))
    free_tier_available = db.Column(db.Boolean, default=False)
    starting_price = db.Column(db.Numeric(10, 2))
    pricing_currency = db.Column(db.String(3), default='USD')
    pricing_details = db.Column(db.Text)
    
    # Processing status
    processing_status = db.Column(db.String(20), default='never_run')
    last_processed_at = db.Column(db.DateTime)
    next_process_date = db.Column(db.DateTime)
    
    # Manual fields
    internal_notes = db.Column(db.Text)
    enterprise_position = db.Column(db.Text)
    screenshots = db.Column(db.Text)  # JSON
    videos = db.Column(db.Text)  # JSON
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ResearchLog(db.Model):
    __tablename__ = 'research_logs'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    research_type = db.Column(db.String(50))
    status = db.Column(db.String(20))
    bedrock_agent_id = db.Column(db.String(100))
    data_collected = db.Column(db.Text)  # JSON
    errors = db.Column(db.Text)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    tool = db.relationship('Tool', backref='research_logs')

# Strands Agent Service
class StrandsAgentService:
    def __init__(self):
        try:
            from strands_agents import Agent
            from strands_agents.models import BedrockModel
            # Try to import available tools
            try:
                from strands_agents_tools import http_request, python_repl
                available_tools = [http_request, python_repl]
            except ImportError:
                available_tools = []
            
            # Configure Bedrock model
            model = BedrockModel(
                model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
                temperature=0.1,
                streaming=False
            )
            
            # Create agent
            self.agent = Agent(
                model=model,
                tools=available_tools,
                system_prompt="""You are a comprehensive AI tool research specialist.
                
When researching a tool, extract comprehensive data about the tool's features, 
capabilities, use cases, company information, and pricing. Return structured JSON data."""
            )
            self.available = True
            print("✅ Strands Agents initialized successfully")
        except ImportError as e:
            print(f"Warning: Strands Agents not available: {e}")
            self.available = False
    
    def research_tool(self, tool):
        """Research a tool using Strands Agent"""
        if not self.available:
            return {"error": "Strands Agents not available"}
        
        urls = [url for url in [tool.website_url, tool.github_url, tool.documentation_url] if url]
        
        prompt = f"""
        Research the AI development tool: {tool.name}
        
        Primary sources to investigate:
        {chr(10).join(f"- {url}" for url in urls)}
        
        Please provide a comprehensive research summary about this tool including:
        1. Detailed description and capabilities
        2. Primary features and use cases
        3. Pricing information
        4. Company information
        5. Technical details
        
        Format your response as a detailed summary.
        """
        
        try:
            response = self.agent(prompt)
            return {"research_summary": str(response), "status": "completed"}
        except Exception as e:
            return {"error": str(e)}

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    })

@app.route('/api/tools', methods=['GET'])
def get_tools():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status')
    
    query = Tool.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    if status:
        query = query.filter_by(processing_status=status)
    
    tools = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'tools': [tool_to_dict(tool) for tool in tools.items],
        'total': tools.total,
        'pages': tools.pages,
        'current_page': page
    })

@app.route('/api/tools', methods=['POST'])
def create_tool():
    data = request.json
    
    tool = Tool(
        name=data['name'],
        category_id=data.get('category_id'),
        description=data.get('description'),
        website_url=data.get('website_url'),
        github_url=data.get('github_url'),
        documentation_url=data.get('documentation_url'),
        changelog_url=data.get('changelog_url'),
        blog_url=data.get('blog_url'),
        is_open_source=data.get('is_open_source', False),
        pricing_model=data.get('pricing_model'),
        processing_status='never_run'
    )
    
    db.session.add(tool)
    db.session.commit()
    
    return jsonify(tool_to_dict(tool)), 201

@app.route('/api/tools/<int:tool_id>', methods=['GET'])
def get_tool(tool_id):
    tool = Tool.query.get_or_404(tool_id)
    return jsonify(tool_to_dict(tool, include_relations=True))

@app.route('/api/tools/<int:tool_id>', methods=['PUT'])
def update_tool(tool_id):
    tool = Tool.query.get_or_404(tool_id)
    data = request.json
    
    # Update fields
    for field in ['name', 'description', 'website_url', 'github_url', 
                  'documentation_url', 'changelog_url', 'blog_url',
                  'internal_notes', 'enterprise_position']:
        if field in data:
            setattr(tool, field, data[field])
    
    tool.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(tool_to_dict(tool))

@app.route('/api/tools/<int:tool_id>/research', methods=['POST'])
def research_tool(tool_id):
    tool = Tool.query.get_or_404(tool_id)
    
    # Create research log
    log = ResearchLog(
        tool_id=tool_id,
        research_type='full_research',
        status='started'
    )
    db.session.add(log)
    db.session.commit()
    
    # Update tool status
    tool.processing_status = 'processing'
    db.session.commit()
    
    try:
        # Research using Strands Agent
        agent_service = StrandsAgentService()
        result = agent_service.research_tool(tool)
        
        if 'error' not in result:
            # Update log
            log.status = 'completed'
            log.data_collected = json.dumps(result)
            log.completed_at = datetime.utcnow()
            
            # Update tool status and description
            tool.processing_status = 'completed'
            tool.last_processed_at = datetime.utcnow()
            tool.next_process_date = datetime.utcnow() + timedelta(weeks=1)
            
            # Update tool description if we got research data
            if result.get('research_summary'):
                tool.description = result['research_summary'][:1000] + "..." if len(result['research_summary']) > 1000 else result['research_summary']
                
        else:
            log.status = 'failed'
            log.errors = result['error']
            tool.processing_status = 'error'
        
        db.session.commit()
        
        return jsonify({
            'status': log.status,
            'tool': tool_to_dict(tool),
            'research_data': result
        })
        
    except Exception as e:
        log.status = 'failed'
        log.errors = str(e)
        tool.processing_status = 'error'
        db.session.commit()
        
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([category_to_dict(cat) for cat in categories])

@app.route('/api/categories', methods=['POST'])
def create_category():
    data = request.json
    
    category = Category(
        name=data['name'],
        parent_id=data.get('parent_id'),
        description=data.get('description')
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify(category_to_dict(category)), 201

# Helper functions
def tool_to_dict(tool, include_relations=False):
    data = {
        'id': tool.id,
        'name': tool.name,
        'category_id': tool.category_id,
        'description': tool.description,
        'website_url': tool.website_url,
        'github_url': tool.github_url,
        'documentation_url': tool.documentation_url,
        'changelog_url': tool.changelog_url,
        'blog_url': tool.blog_url,
        'is_open_source': tool.is_open_source,
        'license_type': tool.license_type,
        'pricing_model': tool.pricing_model,
        'starting_price': float(tool.starting_price) if tool.starting_price else None,
        'processing_status': tool.processing_status,
        'last_processed_at': tool.last_processed_at.isoformat() if tool.last_processed_at else None,
        'internal_notes': tool.internal_notes,
        'enterprise_position': tool.enterprise_position,
        'created_at': tool.created_at.isoformat(),
        'updated_at': tool.updated_at.isoformat()
    }
    
    if include_relations:
        data['category'] = category_to_dict(tool.category) if tool.category else None
    
    return data

def category_to_dict(category):
    return {
        'id': category.id,
        'name': category.name,
        'parent_id': category.parent_id,
        'description': category.description
    }

if __name__ == '__main__':
    # Initialize database
    with app.app_context():
        db.create_all()
        
        # Add sample data if database is empty
        if Category.query.count() == 0:
            sample_categories = [
                ('AI Developer Tools', None, 'All AI-powered developer tools'),
                ('IDEs & Editors', 1, 'Integrated Development Environments and code editors'),
                ('Agentic IDEs', 2, 'AI-powered IDEs that can act autonomously'),
                ('Code Assistants', 2, 'AI coding assistants and copilots'),
                ('Testing Tools', 1, 'AI-powered testing and QA tools'),
                ('Frameworks & Libraries', 1, 'Development frameworks and libraries'),
                ('Agent Frameworks', 6, 'Frameworks for building AI agents'),
                ('Context Tools', 1, 'Tools for managing context and knowledge'),
                ('Desktop Tools', 1, 'Desktop applications for developers'),
                ('Deployment & DevOps', 1, 'AI tools for deployment and operations')
            ]
            
            for name, parent_id, description in sample_categories:
                category = Category(name=name, parent_id=parent_id, description=description)
                db.session.add(category)
            
            # Add sample tools
            sample_tools = [
                ('Cursor', 3, 'AI-first code editor built for pair-programming with AI', 'https://cursor.sh', False, 'freemium'),
                ('Claude Code', 4, 'Agentic command line tool by Anthropic', 'https://claude.ai', False, 'subscription'),
                ('GitHub Copilot', 4, 'AI pair programmer by GitHub', 'https://github.com/features/copilot', False, 'subscription'),
                ('Tabnine', 4, 'AI code completion assistant', 'https://tabnine.com', False, 'freemium'),
                ('Codeium', 4, 'Free AI-powered code acceleration toolkit', 'https://codeium.com', True, 'freemium')
            ]
            
            for name, category_id, description, website_url, is_open_source, pricing_model in sample_tools:
                tool = Tool(
                    name=name,
                    category_id=category_id,
                    description=description,
                    website_url=website_url,
                    is_open_source=is_open_source,
                    pricing_model=pricing_model,
                    processing_status='never_run'
                )
                db.session.add(tool)
            
            db.session.commit()
            print("✅ Sample data added to database")
    
    # Start Flask development server
    print("🚀 Starting AI Tool Intelligence Platform")
    print("Frontend: http://localhost:3000")
    print("Backend API: http://localhost:5000")
    print("Health Check: http://localhost:5000/api/health")
    print("\n✅ Application ready for requests")
    
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    
    app.run(debug=debug_mode, host=host, port=port)