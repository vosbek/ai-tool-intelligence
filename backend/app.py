#!/usr/bin/env python3
# app.py - Main Flask application with all endpoints

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import json
from typing import Dict, List, Optional

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ai_tools.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-in-production')

# Enable CORS for React frontend
CORS(app)

db = SQLAlchemy(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Models
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
    tools = db.relationship('Tool', backref='category')

class Tool(db.Model):
    __tablename__ = 'tools'
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
    
    # Relationships
    company = db.relationship('Company', backref='tool', uselist=False)
    features = db.relationship('ToolFeature', backref='tool')
    integrations = db.relationship('ToolIntegration', backref='tool')
    sdlc_mappings = db.relationship('SDLCMapping', backref='tool')
    research_logs = db.relationship('ResearchLog', backref='tool')

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    
    name = db.Column(db.String(200))
    website = db.Column(db.String(500))
    founded_year = db.Column(db.Integer)
    headquarters = db.Column(db.String(200))
    
    stock_symbol = db.Column(db.String(10))
    is_public = db.Column(db.Boolean, default=False)
    estimated_arr = db.Column(db.Numeric(15, 2))
    last_funding_round = db.Column(db.String(50))
    total_funding = db.Column(db.Numeric(15, 2))
    valuation = db.Column(db.Numeric(15, 2))
    
    employee_count = db.Column(db.Integer)
    employee_count_source = db.Column(db.String(100))
    key_executives = db.Column(db.Text)  # JSON
    
    strategic_focus = db.Column(db.Text)
    business_model = db.Column(db.String(100))
    target_market = db.Column(db.Text)
    competitors = db.Column(db.Text)  # JSON
    
    data_last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    stock_prices = db.relationship('StockPrice', backref='company')

class StockPrice(db.Model):
    __tablename__ = 'stock_prices'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    price = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(3), default='USD')
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

class ToolFeature(db.Model):
    __tablename__ = 'tool_features'
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    feature_category = db.Column(db.String(100))
    feature_name = db.Column(db.String(200))
    feature_description = db.Column(db.Text)
    is_core_feature = db.Column(db.Boolean, default=True)

class ToolIntegration(db.Model):
    __tablename__ = 'tool_integrations'
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    integration_type = db.Column(db.String(50))
    integration_name = db.Column(db.String(200))
    integration_description = db.Column(db.Text)
    integration_url = db.Column(db.String(500))

class SDLCMapping(db.Model):
    __tablename__ = 'sdlc_mappings'
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    sdlc_phase = db.Column(db.String(100))
    phase_description = db.Column(db.Text)
    relevance_score = db.Column(db.Integer)

class ResearchLog(db.Model):
    __tablename__ = 'research_logs'
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    research_type = db.Column(db.String(50))
    status = db.Column(db.String(20))
    bedrock_agent_id = db.Column(db.String(100))
    data_collected = db.Column(db.Text)  # JSON
    errors = db.Column(db.Text)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

# AWS Strands Agent Service
class StrandsAgentService:
    def __init__(self):
        try:
            # Import Strands Agents and all our custom tools
            from strands import Agent
            from strands.models import BedrockModel
            # Import available tools - try different import patterns
            try:
                from strands_tools import http_request, python_repl
                available_tools = [http_request, python_repl]
            except ImportError:
                try:
                    from strands.tools import http_request, python_repl
                    available_tools = [http_request, python_repl]
                except ImportError:
                    # Fallback to basic tools if specific ones aren't available
                    available_tools = []
            
            # Configure Bedrock model (or use any other provider)
            model = BedrockModel(
                model_id="us.anthropic.claude-3-7-sonnet-20241109-v1:0",
                temperature=0.1,
                streaming=False
            )
            
            # Create agent with basic research tools (custom tools will be imported later)
            self.agent = Agent(
                model=model,
                tools=available_tools,
                system_prompt="""You are a comprehensive AI tool research specialist.
                
When researching a tool, you should:
                1. Visit the provided URLs to gather information
                2. Extract comprehensive data about the tool's features, capabilities, and use cases
                3. Research the company behind the tool (funding, team size, strategic focus)
                4. Find pricing information and subscription models
                5. Identify integrations and SDLC phase alignment
                6. Return structured JSON data
                
Always be thorough and cite sources when possible. If information is not available, clearly indicate uncertainty rather than making assumptions."""
            )
            self.available = True
        except ImportError as e:
            print(f"Warning: Strands Agents not available: {e}")
            self.available = False
    
    def research_tool(self, tool: Tool) -> Dict:
        """Research a tool using Strands Agent"""
        if not self.available:
            return {"error": "Strands Agents not available. Please install with: pip install strands-agents strands-agents-tools"}
        
        prompt = self._build_research_prompt(tool)
        
        try:
            # Use Strands Agent to research
            response = self.agent(prompt)
            
            # Parse response as JSON if possible
            result = self._parse_agent_response(response)
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def _build_research_prompt(self, tool: Tool) -> str:
        """Build research prompt for the agent"""
        urls = [url for url in [tool.website_url, tool.github_url, tool.documentation_url, 
                               tool.changelog_url, tool.blog_url] if url]
        
        return f"""
        Research the AI development tool: {tool.name}
        
        Primary sources to investigate:
        {chr(10).join(f"- {url}" for url in urls)}
        
        Use available tools to fetch content from these URLs and gather comprehensive information.
        
        Please research and provide:
        
        1. Tool Information:
           - Detailed description and capabilities
           - Primary features and use cases
           - Target audience (developers, teams, enterprises)
           - Integration capabilities
           - SDLC phase alignment (rate 1-5 for: planning, design, development, testing, deployment, monitoring)
           
        2. Company Information:
           - Company name and website
           - Founding information and headquarters
           - Team size and key executives
           - Funding rounds and financial data
           - Strategic focus and business model
           - Main competitors
           
        3. Pricing and Availability:
           - Pricing model (free, freemium, subscription, enterprise)
           - Specific pricing tiers and monthly/annual costs
           - Free tier limitations
           - Enterprise features and custom pricing
           
        4. Technical Details:
           - Open source status and license type
           - Programming languages supported
           - Platform compatibility (Windows, Mac, Linux, Web)
           - API availability and documentation
           - Integration options with other tools
           
        Format your final response as valid JSON with this structure:
        {{
            "tool": {{
                "description": "detailed description",
                "primary_use_cases": ["use case 1", "use case 2"],
                "target_audience": ["developers", "teams", "enterprises"],
                "license_type": "MIT|Commercial|etc",
                "open_source": true/false,
                "supported_platforms": ["Windows", "Mac", "Linux"],
                "languages_supported": ["Python", "JavaScript"]
            }},
            "company": {{
                "name": "Company Name",
                "website": "https://company.com",
                "founded_year": 2020,
                "headquarters": "City, Country",
                "employee_count": 50,
                "employee_count_source": "LinkedIn|estimated",
                "key_executives": [
                    {{"name": "CEO Name", "role": "CEO", "background": "brief background"}}
                ],
                "funding_status": "Series A|public|etc",
                "total_funding": 10000000,
                "estimated_arr": 5000000,
                "stock_symbol": "TICK",
                "is_public": false,
                "business_model": "subscription|freemium",
                "strategic_focus": "AI development tools"
            }},
            "features": [
                {{
                    "feature_category": "IDE|testing|deployment",
                    "feature_name": "Feature Name",
                    "feature_description": "What it does",
                    "is_core_feature": true
                }}
            ],
            "integrations": [
                {{
                    "integration_type": "IDE|API|plugin",
                    "integration_name": "VS Code",
                    "integration_description": "Native extension available"
                }}
            ],
            "sdlc_mappings": [
                {{
                    "sdlc_phase": "development",
                    "relevance_score": 5,
                    "phase_description": "Primary development tool"
                }}
            ],
            "pricing": {{
                "pricing_model": "freemium",
                "free_tier_available": true,
                "free_tier_limitations": ["limited API calls"],
                "subscription_tiers": [
                    {{
                        "name": "Pro",
                        "price_monthly": 29,
                        "price_annual": 290,
                        "features": ["unlimited API", "priority support"]
                    }}
                ]
            }},
            "confidence_score": 0.8
        }}
        """
    
    def _parse_agent_response(self, response: str) -> Dict:
        """Parse the agent response"""
        try:
            # Look for JSON in the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"raw_response": response, "parsed": False}
        except Exception as e:
            return {"raw_response": response, "parsed": False, "parse_error": str(e)}

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "version": "MVP"
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
            # Update tool with research data
            update_tool_from_research(tool, result)
            
            # Update log
            log.status = 'completed'
            log.data_collected = json.dumps(result)
            log.completed_at = datetime.utcnow()
            
            # Update tool status
            tool.processing_status = 'completed'
            tool.last_processed_at = datetime.utcnow()
            tool.next_process_date = datetime.utcnow() + timedelta(weeks=1)
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
        data['company'] = company_to_dict(tool.company) if tool.company else None
        data['features'] = [feature_to_dict(f) for f in tool.features]
        data['integrations'] = [integration_to_dict(i) for i in tool.integrations]
    
    return data

def category_to_dict(category):
    return {
        'id': category.id,
        'name': category.name,
        'parent_id': category.parent_id,
        'description': category.description
    }

def company_to_dict(company):
    return {
        'id': company.id,
        'name': company.name,
        'website': company.website,
        'founded_year': company.founded_year,
        'headquarters': company.headquarters,
        'stock_symbol': company.stock_symbol,
        'is_public': company.is_public,
        'estimated_arr': float(company.estimated_arr) if company.estimated_arr else None,
        'employee_count': company.employee_count,
        'strategic_focus': company.strategic_focus,
        'business_model': company.business_model
    }

def feature_to_dict(feature):
    return {
        'id': feature.id,
        'feature_category': feature.feature_category,
        'feature_name': feature.feature_name,
        'feature_description': feature.feature_description,
        'is_core_feature': feature.is_core_feature
    }

def integration_to_dict(integration):
    return {
        'id': integration.id,
        'integration_type': integration.integration_type,
        'integration_name': integration.integration_name,
        'integration_description': integration.integration_description,
        'integration_url': integration.integration_url
    }

def update_tool_from_research(tool, research_data):
    """Update tool with data from research"""
    if 'tool' in research_data:
        tool_data = research_data['tool']
        tool.description = tool_data.get('description', tool.description)
        tool.license_type = tool_data.get('license_type')
        tool.primary_language = tool_data.get('languages_supported', [None])[0]
        if tool_data.get('supported_platforms'):
            tool.supported_platforms = json.dumps(tool_data['supported_platforms'])
    
    # Update or create company
    if 'company' in research_data:
        company_data = research_data['company']
        if not tool.company:
            tool.company = Company(tool_id=tool.id)
        
        company = tool.company
        company.name = company_data.get('name', company.name)
        company.website = company_data.get('website', company.website)
        company.founded_year = company_data.get('founded_year')
        company.headquarters = company_data.get('headquarters')
        company.employee_count = company_data.get('employee_count')
        company.employee_count_source = company_data.get('employee_count_source')
        company.estimated_arr = company_data.get('estimated_arr')
        company.total_funding = company_data.get('total_funding')
        company.stock_symbol = company_data.get('stock_symbol')
        company.is_public = company_data.get('is_public', False)
        company.business_model = company_data.get('business_model')
        company.strategic_focus = company_data.get('strategic_focus')
        
        if company_data.get('key_executives'):
            company.key_executives = json.dumps(company_data['key_executives'])
    
    # Update features
    if 'features' in research_data:
        # Clear existing features
        ToolFeature.query.filter_by(tool_id=tool.id).delete()
        
        for feature in research_data['features']:
            new_feature = ToolFeature(
                tool_id=tool.id,
                feature_category=feature.get('feature_category'),
                feature_name=feature.get('feature_name'),
                feature_description=feature.get('feature_description'),
                is_core_feature=feature.get('is_core_feature', True)
            )
            db.session.add(new_feature)
    
    # Update integrations
    if 'integrations' in research_data:
        # Clear existing integrations
        ToolIntegration.query.filter_by(tool_id=tool.id).delete()
        
        for integration in research_data['integrations']:
            new_integration = ToolIntegration(
                tool_id=tool.id,
                integration_type=integration.get('integration_type'),
                integration_name=integration.get('integration_name'),
                integration_description=integration.get('integration_description')
            )
            db.session.add(new_integration)
    
    # Update SDLC mappings
    if 'sdlc_mappings' in research_data:
        # Clear existing mappings
        SDLCMapping.query.filter_by(tool_id=tool.id).delete()
        
        for mapping in research_data['sdlc_mappings']:
            new_mapping = SDLCMapping(
                tool_id=tool.id,
                sdlc_phase=mapping.get('sdlc_phase'),
                relevance_score=mapping.get('relevance_score'),
                phase_description=mapping.get('phase_description')
            )
            db.session.add(new_mapping)
    
    # Update pricing information
    if 'pricing' in research_data:
        pricing_data = research_data['pricing']
        tool.pricing_model = pricing_data.get('pricing_model')
        tool.free_tier_available = pricing_data.get('free_tier_available', False)
        tool.pricing_details = json.dumps(pricing_data)
        
        # Extract starting price if available
        if pricing_data.get('subscription_tiers'):
            paid_tiers = [tier for tier in pricing_data['subscription_tiers'] 
                         if tier.get('price_monthly', 0) > 0]
            if paid_tiers:
                tool.starting_price = min(tier['price_monthly'] for tier in paid_tiers)

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
    
    app.run(debug=True, host='0.0.0.0', port=5000)