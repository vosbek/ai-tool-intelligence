# tests/test_github_analyzer.py - Unit tests for GitHub analyzer tool

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

from enhanced_strands_tools import enhanced_github_analyzer, _calculate_release_frequency, _is_actively_maintained


class TestEnhancedGitHubAnalyzer:
    """Test suite for enhanced GitHub analyzer"""
    
    def test_github_analyzer_success(self, mock_env_vars, mock_requests_response, 
                                   sample_github_repo_data, sample_github_contributors,
                                   sample_github_releases, sample_github_commits,
                                   sample_github_languages):
        """Test successful GitHub repository analysis"""
        
        # Mock all GitHub API endpoints
        def mock_request_side_effect(url, **kwargs):
            if url.endswith('/repos/testuser/test-repo'):
                return mock_requests_response(200, sample_github_repo_data)
            elif 'contributors' in url:
                return mock_requests_response(200, sample_github_contributors)
            elif 'releases' in url:
                return mock_requests_response(200, sample_github_releases)
            elif 'languages' in url:
                return mock_requests_response(200, sample_github_languages)
            elif 'commits' in url:
                return mock_requests_response(200, sample_github_commits)
            elif 'community/profile' in url:
                return mock_requests_response(200, {
                    "files": {
                        "readme": {"name": "README.md"},
                        "contributing": {"name": "CONTRIBUTING.md"},
                        "license": {"name": "LICENSE"},
                        "code_of_conduct": {"name": "CODE_OF_CONDUCT.md"}
                    }
                })
            elif 'stats/participation' in url:
                return mock_requests_response(200, {"all": [1, 2, 3, 4, 5]})
            elif 'topics' in url:
                return mock_requests_response(200, {"names": ["ai", "python"]})
            else:
                return mock_requests_response(404, {"message": "Not found"})
        
        with patch('enhanced_strands_tools.requests.get', side_effect=mock_request_side_effect):
            result = enhanced_github_analyzer("https://github.com/testuser/test-repo")
        
        # Verify success
        assert "error" not in result
        
        # Check basic stats
        basic_stats = result["basic_stats"]
        assert basic_stats["stars"] == 1500
        assert basic_stats["forks"] == 300
        assert basic_stats["watchers"] == 1500
        assert basic_stats["open_issues"] == 25
        
        # Check repository info
        repo_info = result["repository_info"]
        assert repo_info["default_branch"] == "main"
        assert repo_info["license"] == "MIT License"
        assert "ai" in repo_info["topics"]
        assert repo_info["archived"] is False
        
        # Check activity metrics
        activity = result["activity_metrics"]
        assert activity["total_contributors"] == 2
        assert "commit_analysis" in activity
        assert activity["latest_release"] == "v2.1.0"
        assert activity["is_actively_maintained"] is True
        
        # Check technology stack
        tech_stack = result["technology_stack"]
        assert tech_stack["primary_language"] == "Python"
        assert "Python" in tech_stack["languages"]
        assert "language_breakdown" in tech_stack
        
        # Check community health
        health = result["community_health"]
        assert health["has_readme"] is True
        assert health["has_contributing"] is True
        assert health["has_license"] is True
        assert health["health_score"] > 0
        
        # Check contributors and releases
        assert len(result["top_contributors"]) == 2
        assert len(result["recent_releases"]) == 2
        
        # Check metadata
        metadata = result["analysis_metadata"]
        assert "timestamp" in metadata
        assert metadata["api_calls_made"] > 0
        assert metadata["data_completeness"] > 0
    
    def test_github_analyzer_invalid_url(self):
        """Test GitHub analyzer with invalid URL"""
        result = enhanced_github_analyzer("https://invalid-url.com")
        
        assert "error" in result
        assert "Invalid GitHub URL format" in result["error"]
        assert result["url"] == "https://invalid-url.com"
    
    def test_github_analyzer_invalid_repo_name(self):
        """Test GitHub analyzer with invalid repository name"""
        result = enhanced_github_analyzer("https://github.com/test@user/invalid@repo")
        
        assert "error" in result
        assert "Invalid repository or owner name" in result["error"]
    
    def test_github_analyzer_repo_not_found(self, mock_env_vars, mock_requests_response):
        """Test GitHub analyzer with non-existent repository"""
        with patch('enhanced_strands_tools.requests.get') as mock_get:
            mock_get.return_value = mock_requests_response(404, {"message": "Not Found"})
            
            result = enhanced_github_analyzer("https://github.com/nonexistent/repo")
        
        assert "error" in result
        assert "Repository not found or private" in result["error"]
    
    def test_github_analyzer_rate_limit(self, mock_env_vars, mock_requests_response):
        """Test GitHub analyzer rate limit handling"""
        def mock_request_side_effect(url, **kwargs):
            response = mock_requests_response(403, {"message": "rate limit exceeded"})
            response.text = "rate limit exceeded"
            return response
        
        with patch('enhanced_strands_tools.requests.get', side_effect=mock_request_side_effect):
            with patch('enhanced_strands_tools.time.sleep'):  # Mock sleep to speed up test
                result = enhanced_github_analyzer("https://github.com/testuser/test-repo")
        
        assert "error" in result
        assert "GitHub API error" in result["error"]
    
    def test_github_analyzer_network_error(self, mock_env_vars):
        """Test GitHub analyzer with network error"""
        with patch('enhanced_strands_tools.requests.get', side_effect=requests.RequestException("Network error")):
            with patch('enhanced_strands_tools.time.sleep'):  # Mock sleep to speed up test
                result = enhanced_github_analyzer("https://github.com/testuser/test-repo")
        
        assert "error" in result
        assert "GitHub analysis failed" in result["error"]
    
    def test_github_analyzer_url_variations(self, mock_env_vars, mock_requests_response, sample_github_repo_data):
        """Test GitHub analyzer with various URL formats"""
        urls = [
            "https://github.com/user/repo",
            "https://github.com/user/repo.git",
            "https://github.com/user/repo?tab=readme",
            "https://github.com/user/repo#readme",
            "https://github.com/user/repo.git?ref=main"
        ]
        
        with patch('enhanced_strands_tools.requests.get') as mock_get:
            mock_get.return_value = mock_requests_response(200, sample_github_repo_data)
            
            for url in urls:
                result = enhanced_github_analyzer(url)
                assert "error" not in result
                assert result["basic_stats"]["stars"] == 1500
    
    def test_github_analyzer_commit_analysis(self, mock_env_vars, mock_requests_response,
                                           sample_github_repo_data):
        """Test commit analysis functionality"""
        # Create commits with different dates
        recent_commits = [
            {
                "commit": {"author": {"date": (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%dT%H:%M:%SZ')}},
                "author": {"login": "user1"}
            },
            {
                "commit": {"author": {"date": (datetime.now() - timedelta(days=50)).strftime('%Y-%m-%dT%H:%M:%SZ')}},
                "author": {"login": "user2"}
            },
            {
                "commit": {"author": {"date": (datetime.now() - timedelta(days=200)).strftime('%Y-%m-%dT%H:%M:%SZ')}},
                "author": {"login": "user1"}
            }
        ]
        
        def mock_request_side_effect(url, **kwargs):
            if url.endswith('/repos/testuser/test-repo'):
                return mock_requests_response(200, sample_github_repo_data)
            elif 'commits' in url:
                return mock_requests_response(200, recent_commits)
            else:
                return mock_requests_response(200, [])
        
        with patch('enhanced_strands_tools.requests.get', side_effect=mock_request_side_effect):
            result = enhanced_github_analyzer("https://github.com/testuser/test-repo")
        
        commit_analysis = result["activity_metrics"]["commit_analysis"]
        
        # Check different time periods
        assert "last_30_days" in commit_analysis
        assert "last_90_days" in commit_analysis
        assert "last_year" in commit_analysis
        
        # Recent commits should be counted
        assert commit_analysis["last_30_days"]["count"] >= 1
        assert commit_analysis["last_90_days"]["count"] >= 2
        
        # Unique authors should be tracked
        assert commit_analysis["last_90_days"]["unique_authors"] == 2
    
    def test_github_analyzer_language_breakdown(self, mock_env_vars, mock_requests_response,
                                              sample_github_repo_data, sample_github_languages):
        """Test language breakdown calculation"""
        def mock_request_side_effect(url, **kwargs):
            if url.endswith('/repos/testuser/test-repo'):
                return mock_requests_response(200, sample_github_repo_data)
            elif 'languages' in url:
                return mock_requests_response(200, sample_github_languages)
            else:
                return mock_requests_response(200, [])
        
        with patch('enhanced_strands_tools.requests.get', side_effect=mock_request_side_effect):
            result = enhanced_github_analyzer("https://github.com/testuser/test-repo")
        
        language_breakdown = result["technology_stack"]["language_breakdown"]
        
        # Check that percentages are calculated correctly
        assert "Python" in language_breakdown
        assert language_breakdown["Python"]["percentage"] == 75.0  # 75000/100000 * 100
        assert language_breakdown["JavaScript"]["percentage"] == 20.0
        
        # Check total bytes
        assert result["technology_stack"]["total_code_bytes"] == 100000
    
    def test_github_analyzer_community_health_scoring(self, mock_env_vars, mock_requests_response,
                                                     sample_github_repo_data):
        """Test community health scoring"""
        community_data = {
            "files": {
                "readme": {"name": "README.md"},
                "contributing": {"name": "CONTRIBUTING.md"}, 
                "license": {"name": "LICENSE"},
                "code_of_conduct": {"name": "CODE_OF_CONDUCT.md"},
                "issue_template": {"name": "ISSUE_TEMPLATE.md"},
                "pull_request_template": {"name": "PULL_REQUEST_TEMPLATE.md"}
            }
        }
        
        def mock_request_side_effect(url, **kwargs):
            if url.endswith('/repos/testuser/test-repo'):
                return mock_requests_response(200, sample_github_repo_data)
            elif 'community/profile' in url:
                return mock_requests_response(200, community_data)
            elif 'contributors' in url:
                return mock_requests_response(200, [{"login": "user1"}, {"login": "user2"}])
            elif 'commits' in url:
                return mock_requests_response(200, [
                    {"commit": {"author": {"date": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')}}}
                ])
            else:
                return mock_requests_response(200, [])
        
        with patch('enhanced_strands_tools.requests.get', side_effect=mock_request_side_effect):
            result = enhanced_github_analyzer("https://github.com/testuser/test-repo")
        
        health = result["community_health"]
        
        # Check individual health factors
        assert health["has_readme"] is True
        assert health["has_contributing"] is True
        assert health["has_license"] is True
        assert health["has_code_of_conduct"] is True
        assert health["has_issues_template"] is True
        assert health["has_pull_request_template"] is True
        assert health["recent_activity"] is True
        assert health["multiple_contributors"] is True
        
        # Health score should be high (100%)
        assert health["health_score"] == 100.0


class TestGitHubAnalyzerHelperFunctions:
    """Test suite for GitHub analyzer helper functions"""
    
    def test_calculate_release_frequency_insufficient_data(self):
        """Test release frequency calculation with insufficient data"""
        # Empty releases
        assert _calculate_release_frequency([]) == "insufficient_data"
        
        # Single release
        single_release = [{"published_at": "2024-01-01T12:00:00Z"}]
        assert _calculate_release_frequency(single_release) == "insufficient_data"
    
    def test_calculate_release_frequency_very_frequent(self):
        """Test very frequent release pattern"""
        releases = [
            {"published_at": "2024-01-30T12:00:00Z"},
            {"published_at": "2024-01-15T12:00:00Z"},
            {"published_at": "2024-01-01T12:00:00Z"}
        ]
        
        result = _calculate_release_frequency(releases)
        assert result == "very_frequent"
    
    def test_calculate_release_frequency_frequent(self):
        """Test frequent release pattern"""
        releases = [
            {"published_at": "2024-01-01T12:00:00Z"},
            {"published_at": "2023-11-01T12:00:00Z"},
            {"published_at": "2023-09-01T12:00:00Z"}
        ]
        
        result = _calculate_release_frequency(releases)
        assert result == "frequent"
    
    def test_calculate_release_frequency_moderate(self):
        """Test moderate release pattern"""
        releases = [
            {"published_at": "2024-01-01T12:00:00Z"},
            {"published_at": "2023-07-01T12:00:00Z"},
            {"published_at": "2023-01-01T12:00:00Z"}
        ]
        
        result = _calculate_release_frequency(releases)
        assert result == "moderate"
    
    def test_calculate_release_frequency_infrequent(self):
        """Test infrequent release pattern"""
        releases = [
            {"published_at": "2024-01-01T12:00:00Z"},
            {"published_at": "2022-01-01T12:00:00Z"}
        ]
        
        result = _calculate_release_frequency(releases)
        assert result == "infrequent"
    
    def test_calculate_release_frequency_invalid_dates(self):
        """Test release frequency with invalid dates"""
        releases = [
            {"published_at": "invalid-date"},
            {"published_at": "2024-01-01T12:00:00Z"}
        ]
        
        result = _calculate_release_frequency(releases)
        assert result == "unknown"
    
    def test_calculate_release_frequency_missing_dates(self):
        """Test release frequency with missing dates"""
        releases = [
            {"tag_name": "v1.0.0"},  # No published_at
            {"published_at": "2024-01-01T12:00:00Z"}
        ]
        
        result = _calculate_release_frequency(releases)
        assert result == "insufficient_data"
    
    def test_is_actively_maintained_recent_commits(self):
        """Test active maintenance detection with recent commits"""
        recent_commits = [
            {"commit": {"author": {"date": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ')}}}
        ]
        
        result = _is_actively_maintained(recent_commits, [])
        assert result is True
    
    def test_is_actively_maintained_old_commits_recent_release(self):
        """Test active maintenance with old commits but recent release"""
        old_commits = [
            {"commit": {"author": {"date": (datetime.now() - timedelta(days=200)).strftime('%Y-%m-%dT%H:%M:%SZ')}}}
        ]
        
        recent_releases = [
            {"published_at": (datetime.now() - timedelta(days=100)).strftime('%Y-%m-%dT%H:%M:%SZ')}
        ]
        
        result = _is_actively_maintained(old_commits, recent_releases)
        assert result is True
    
    def test_is_actively_maintained_inactive(self):
        """Test inactive maintenance detection"""
        old_commits = [
            {"commit": {"author": {"date": (datetime.now() - timedelta(days=200)).strftime('%Y-%m-%dT%H:%M:%SZ')}}}
        ]
        
        old_releases = [
            {"published_at": (datetime.now() - timedelta(days=400)).strftime('%Y-%m-%dT%H:%M:%SZ')}
        ]
        
        result = _is_actively_maintained(old_commits, old_releases)
        assert result is False
    
    def test_is_actively_maintained_empty_data(self):
        """Test maintenance detection with empty data"""
        result = _is_actively_maintained([], [])
        assert result is False
    
    def test_is_actively_maintained_invalid_dates(self):
        """Test maintenance detection with invalid dates"""
        invalid_commits = [
            {"commit": {"author": {"date": "invalid-date"}}}
        ]
        
        invalid_releases = [
            {"published_at": "invalid-date"}
        ]
        
        result = _is_actively_maintained(invalid_commits, invalid_releases)
        assert result is False


class TestGitHubAnalyzerEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_github_analyzer_empty_responses(self, mock_env_vars, mock_requests_response,
                                           sample_github_repo_data):
        """Test GitHub analyzer with empty API responses"""
        def mock_request_side_effect(url, **kwargs):
            if url.endswith('/repos/testuser/test-repo'):
                return mock_requests_response(200, sample_github_repo_data)
            else:
                return mock_requests_response(200, [])  # Empty responses for other endpoints
        
        with patch('enhanced_strands_tools.requests.get', side_effect=mock_request_side_effect):
            result = enhanced_github_analyzer("https://github.com/testuser/test-repo")
        
        # Should handle empty responses gracefully
        assert "error" not in result
        assert result["activity_metrics"]["total_contributors"] == 0
        assert result["activity_metrics"]["total_releases"] == 0
    
    def test_github_analyzer_malformed_json(self, mock_env_vars, mock_requests_response,
                                          sample_github_repo_data):
        """Test GitHub analyzer with malformed JSON responses"""
        def mock_request_side_effect(url, **kwargs):
            if url.endswith('/repos/testuser/test-repo'):
                return mock_requests_response(200, sample_github_repo_data)
            else:
                response = Mock()
                response.status_code = 200
                response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
                return response
        
        with patch('enhanced_strands_tools.requests.get', side_effect=mock_request_side_effect):
            result = enhanced_github_analyzer("https://github.com/testuser/test-repo")
        
        # Should handle JSON decode errors gracefully
        assert "error" not in result
        assert result["activity_metrics"]["total_contributors"] == 0
    
    def test_github_analyzer_partial_api_failures(self, mock_env_vars, mock_requests_response,
                                                 sample_github_repo_data, sample_github_contributors):
        """Test GitHub analyzer with partial API failures"""
        def mock_request_side_effect(url, **kwargs):
            if url.endswith('/repos/testuser/test-repo'):
                return mock_requests_response(200, sample_github_repo_data)
            elif 'contributors' in url:
                return mock_requests_response(200, sample_github_contributors)
            else:
                return mock_requests_response(500, {"message": "Internal server error"})
        
        with patch('enhanced_strands_tools.requests.get', side_effect=mock_request_side_effect):
            result = enhanced_github_analyzer("https://github.com/testuser/test-repo")
        
        # Should work with partial data
        assert "error" not in result
        assert result["activity_metrics"]["total_contributors"] == 2
        assert result["activity_metrics"]["total_releases"] == 0  # Failed to get releases
    
    def test_github_analyzer_no_auth_token(self):
        """Test GitHub analyzer without authentication token"""
        with patch.dict('os.environ', {}, clear=True):
            with patch('enhanced_strands_tools.requests.get') as mock_get:
                mock_get.return_value = Mock(status_code=403, text="Rate limit exceeded")
                
                result = enhanced_github_analyzer("https://github.com/testuser/test-repo")
        
        assert "error" in result
        assert "GitHub API error" in result["error"]
    
    def test_github_analyzer_commits_with_missing_author(self, mock_env_vars, mock_requests_response,
                                                        sample_github_repo_data):
        """Test commit analysis with missing author information"""
        commits_with_missing_author = [
            {
                "commit": {"author": {"date": "2024-01-01T12:00:00Z"}},
                "author": None  # Missing author
            },
            {
                "commit": {"author": {"date": "2024-01-01T12:00:00Z"}},
                "author": {"login": "user1"}
            }
        ]
        
        def mock_request_side_effect(url, **kwargs):
            if url.endswith('/repos/testuser/test-repo'):
                return mock_requests_response(200, sample_github_repo_data)
            elif 'commits' in url:
                return mock_requests_response(200, commits_with_missing_author)
            else:
                return mock_requests_response(200, [])
        
        with patch('enhanced_strands_tools.requests.get', side_effect=mock_request_side_effect):
            result = enhanced_github_analyzer("https://github.com/testuser/test-repo")
        
        # Should handle missing author gracefully
        assert "error" not in result
        commit_analysis = result["activity_metrics"]["commit_analysis"]
        assert commit_analysis["last_90_days"]["unique_authors"] == 1  # Only count valid authors
    
    def test_github_analyzer_very_large_repository(self, mock_env_vars, mock_requests_response):
        """Test GitHub analyzer with very large repository data"""
        large_repo_data = {
            "stargazers_count": 100000,
            "forks_count": 50000,
            "size": 1000000,  # 1GB
            "open_issues_count": 5000,
            "name": "large-repo",
            "default_branch": "main"
        }
        
        # Create large contributors list
        large_contributors = [{"login": f"user{i}", "contributions": 100-i} for i in range(100)]
        
        def mock_request_side_effect(url, **kwargs):
            if url.endswith('/repos/testuser/large-repo'):
                return mock_requests_response(200, large_repo_data)
            elif 'contributors' in url:
                return mock_requests_response(200, large_contributors)
            else:
                return mock_requests_response(200, [])
        
        with patch('enhanced_strands_tools.requests.get', side_effect=mock_request_side_effect):
            result = enhanced_github_analyzer("https://github.com/testuser/large-repo")
        
        # Should handle large data gracefully
        assert "error" not in result
        assert result["basic_stats"]["stars"] == 100000
        assert result["activity_metrics"]["total_contributors"] == 100
        # Should limit contributors in response
        assert len(result["top_contributors"]) == 10