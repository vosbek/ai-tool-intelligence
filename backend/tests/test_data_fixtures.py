# backend/tests/test_data_fixtures.py - Test data fixtures and factories

import pytest
import factory
from datetime import datetime, timedelta
from backend.models.database import db, Tool, Category, ResearchResult
from backend.app import app

class CategoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating test categories"""
    
    class Meta:
        model = Category
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"
    
    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"Test Category {n}")
    description = factory.Faker('text', max_nb_chars=200)
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)

class ToolFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating test tools"""
    
    class Meta:
        model = Tool
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"
    
    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"Test Tool {n}")
    description = factory.Faker('text', max_nb_chars=500)
    website_url = factory.Faker('url')
    github_url = factory.Faker('url')
    documentation_url = factory.Faker('url')
    pricing_model = factory.Iterator(['free', 'freemium', 'paid', 'enterprise'])
    status = factory.Iterator(['pending', 'processing', 'completed', 'failed'])
    category_id = factory.SubFactory(CategoryFactory)
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)
    last_researched = factory.LazyFunction(lambda: datetime.utcnow() - timedelta(days=1))

class ResearchResultFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating test research results"""
    
    class Meta:
        model = ResearchResult
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"
    
    id = factory.Sequence(lambda n: n)
    tool_id = factory.SubFactory(ToolFactory)
    research_type = factory.Iterator(['basic', 'comprehensive', 'competitive'])
    status = factory.Iterator(['pending', 'processing', 'completed', 'failed'])
    result_data = factory.LazyFunction(lambda: {
        'summary': 'Test research summary',
        'features': ['Feature 1', 'Feature 2', 'Feature 3'],
        'pricing': {'model': 'freemium', 'details': 'Free tier available'},
        'competitors': ['Competitor 1', 'Competitor 2'],
        'market_position': 'Growing',
        'strengths': ['Easy to use', 'Good documentation'],
        'weaknesses': ['Limited features', 'High price'],
        'opportunities': ['Mobile app', 'API integration'],
        'threats': ['Strong competition', 'Market saturation']
    })
    error_message = None
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)
    completed_at = factory.LazyFunction(datetime.utcnow)

class TestDataFixtures:
    """Test data fixtures and setup utilities"""
    
    @pytest.fixture
    def app_context(self):
        """Provide Flask application context for tests"""
        with app.app_context():
            yield app
    
    @pytest.fixture
    def db_session(self, app_context):
        """Provide database session for tests"""
        db.create_all()
        yield db.session
        db.session.rollback()
        db.drop_all()
    
    @pytest.fixture
    def sample_categories(self, db_session):
        """Create sample categories for testing"""
        categories = [
            Category(
                name='Code Assistants',
                description='AI-powered code completion and assistance tools'
            ),
            Category(
                name='Data Analysis',
                description='Tools for data analysis and visualization'
            ),
            Category(
                name='Content Generation',
                description='AI tools for generating text, images, and other content'
            ),
            Category(
                name='Development Tools',
                description='General software development and DevOps tools'
            ),
            Category(
                name='Research Tools',
                description='Tools for research and information gathering'
            )
        ]
        
        db_session.add_all(categories)
        db_session.commit()
        
        return categories
    
    @pytest.fixture
    def sample_tools(self, db_session, sample_categories):
        """Create sample tools for testing"""
        tools = [
            Tool(
                name='GitHub Copilot',
                description='AI pair programmer that helps you write code faster',
                website_url='https://github.com/features/copilot',
                github_url='https://github.com/github/copilot',
                pricing_model='paid',
                status='completed',
                category_id=sample_categories[0].id,  # Code Assistants
                internal_notes='Popular AI coding assistant'
            ),
            Tool(
                name='Cursor',
                description='AI-first code editor built for productivity',
                website_url='https://cursor.sh',
                github_url='https://github.com/getcursor/cursor',
                pricing_model='freemium',
                status='completed',
                category_id=sample_categories[0].id,  # Code Assistants
                internal_notes='VSCode-based editor with AI features'
            ),
            Tool(
                name='Tableau',
                description='Data visualization and business intelligence platform',
                website_url='https://tableau.com',
                pricing_model='enterprise',
                status='pending',
                category_id=sample_categories[1].id,  # Data Analysis
                internal_notes='Enterprise-grade data visualization'
            ),
            Tool(
                name='ChatGPT',
                description='Conversational AI for various tasks',
                website_url='https://chat.openai.com',
                pricing_model='freemium',
                status='completed',
                category_id=sample_categories[2].id,  # Content Generation
                internal_notes='Popular conversational AI'
            ),
            Tool(
                name='Docker',
                description='Platform for developing, shipping, and running applications',
                website_url='https://docker.com',
                github_url='https://github.com/docker/docker',
                pricing_model='freemium',
                status='completed',
                category_id=sample_categories[3].id,  # Development Tools
                internal_notes='Containerization platform'
            )
        ]
        
        db_session.add_all(tools)
        db_session.commit()
        
        return tools
    
    @pytest.fixture
    def sample_research_results(self, db_session, sample_tools):
        """Create sample research results for testing"""
        research_results = []
        
        for tool in sample_tools[:3]:  # Create research for first 3 tools
            result = ResearchResult(
                tool_id=tool.id,
                research_type='comprehensive',
                status='completed',
                result_data={
                    'summary': f'Comprehensive analysis of {tool.name}',
                    'features': [
                        'Feature 1',
                        'Feature 2', 
                        'Feature 3'
                    ],
                    'pricing': {
                        'model': tool.pricing_model,
                        'details': f'{tool.pricing_model.title()} pricing model'
                    },
                    'competitors': [
                        'Competitor A',
                        'Competitor B'
                    ],
                    'market_analysis': {
                        'position': 'Leading',
                        'growth': 'High',
                        'market_share': '25%'
                    },
                    'swot_analysis': {
                        'strengths': ['Strong brand', 'Good UX'],
                        'weaknesses': ['High price', 'Limited integrations'],
                        'opportunities': ['Mobile market', 'Enterprise sales'],
                        'threats': ['New competitors', 'Regulatory changes']
                    }
                },
                completed_at=datetime.utcnow()
            )
            research_results.append(result)
        
        db_session.add_all(research_results)
        db_session.commit()
        
        return research_results
    
    @pytest.fixture
    def large_dataset(self, db_session):
        """Create a large dataset for performance testing"""
        # Create categories using factory
        categories = CategoryFactory.create_batch(10)
        
        # Create many tools using factory
        tools = []
        for _ in range(100):
            tool = ToolFactory.create(
                category_id=factory.random.randgen.choice(categories).id
            )
            tools.append(tool)
        
        # Create research results for some tools
        research_results = []
        for tool in tools[:50]:  # Research for half the tools
            result = ResearchResultFactory.create(tool_id=tool.id)
            research_results.append(result)
        
        db_session.commit()
        
        return {
            'categories': categories,
            'tools': tools,
            'research_results': research_results
        }
    
    @pytest.fixture
    def minimal_dataset(self, db_session):
        """Create minimal dataset for basic testing"""
        category = CategoryFactory.create(name='Test Category')
        tool = ToolFactory.create(
            name='Test Tool',
            category_id=category.id,
            status='completed'
        )
        research = ResearchResultFactory.create(
            tool_id=tool.id,
            status='completed'
        )
        
        db_session.commit()
        
        return {
            'category': category,
            'tool': tool,
            'research': research
        }
    
    @pytest.fixture
    def failed_research_data(self, db_session):
        """Create test data with failed research results"""
        category = CategoryFactory.create(name='Failed Research Category')
        tool = ToolFactory.create(
            name='Failed Research Tool',
            category_id=category.id,
            status='failed'
        )
        failed_research = ResearchResultFactory.create(
            tool_id=tool.id,
            status='failed',
            error_message='Research failed due to network timeout',
            result_data=None,
            completed_at=None
        )
        
        db_session.commit()
        
        return {
            'category': category,
            'tool': tool,
            'failed_research': failed_research
        }
    
    @pytest.fixture
    def competitive_analysis_data(self, db_session):
        """Create test data for competitive analysis testing"""
        # Create a category with multiple competing tools
        category = CategoryFactory.create(name='Competitive Analysis Category')
        
        # Create competing tools
        tools = []
        for i in range(5):
            tool = ToolFactory.create(
                name=f'Competitor Tool {i+1}',
                category_id=category.id,
                status='completed',
                pricing_model=['free', 'freemium', 'paid', 'enterprise'][i % 4]
            )
            tools.append(tool)
        
        # Create research results for competitive analysis
        research_results = []
        for tool in tools:
            result = ResearchResultFactory.create(
                tool_id=tool.id,
                research_type='competitive',
                status='completed',
                result_data={
                    'competitive_analysis': {
                        'market_position': f'Position {tools.index(tool) + 1}',
                        'competitive_advantages': [
                            f'Advantage {i+1}' for i in range(3)
                        ],
                        'competitive_disadvantages': [
                            f'Disadvantage {i+1}' for i in range(2)
                        ],
                        'direct_competitors': [
                            t.name for t in tools if t != tool
                        ][:3]
                    }
                }
            )
            research_results.append(result)
        
        db_session.commit()
        
        return {
            'category': category,
            'tools': tools,
            'research_results': research_results
        }

def create_test_user_data():
    """Create test data that simulates real user scenarios"""
    return {
        'realistic_tools': [
            {
                'name': 'GPT-4',
                'category': 'Language Models',
                'description': 'Advanced language model for text generation and understanding',
                'website_url': 'https://openai.com/gpt-4',
                'pricing_model': 'paid',
                'status': 'completed'
            },
            {
                'name': 'Claude',
                'category': 'Language Models', 
                'description': 'AI assistant for various tasks with strong reasoning capabilities',
                'website_url': 'https://claude.ai',
                'pricing_model': 'freemium',
                'status': 'completed'
            },
            {
                'name': 'Midjourney',
                'category': 'Image Generation',
                'description': 'AI-powered image generation from text descriptions',
                'website_url': 'https://midjourney.com',
                'pricing_model': 'paid',
                'status': 'completed'
            }
        ],
        'realistic_categories': [
            {
                'name': 'Language Models',
                'description': 'Large language models for text processing and generation'
            },
            {
                'name': 'Image Generation',
                'description': 'AI tools for creating and editing images'
            },
            {
                'name': 'Code Generation',
                'description': 'AI-powered programming and code assistance tools'
            }
        ]
    }

def cleanup_test_data(db_session):
    """Clean up test data after tests"""
    try:
        # Delete in reverse order of dependencies
        db_session.query(ResearchResult).delete()
        db_session.query(Tool).delete()
        db_session.query(Category).delete()
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e