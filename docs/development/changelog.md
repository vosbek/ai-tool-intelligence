# Changelog

All notable changes to the AI Tool Intelligence Platform will be documented in this file.

## [v0.2.0] - 2024-01-11

### 🎉 New Features

#### Progress Indicators & Real-time Feedback
- **Visual Progress Bars**: Added real-time progress indicators for research operations
- **Estimated Time Display**: Shows estimated completion time during research
- **Global Progress Tracking**: Tracks progress across bulk operations
- **Live Status Updates**: Real-time updates without page refresh

#### Smart Notification System  
- **Browser Notifications**: Desktop notifications when research completes (requires permission)
- **In-app Notifications**: Toast-style notifications for all operations
- **Auto-dismiss**: Notifications auto-clear after 5 seconds with manual dismiss option
- **Status Indicators**: Success/error/info notification types with color coding

#### Bulk Operations & Research Queue
- **Bulk Research**: Select multiple tools for batch research operations  
- **Research Queue**: Visual queue showing active, completed, and failed research
- **Bulk Selection**: Checkbox-based selection with "select all" functionality
- **Queue Management**: Clear completed items and monitor real-time progress

#### Enhanced User Interface
- **Improved Table**: Added checkboxes for bulk selection
- **Responsive Design**: Better mobile and tablet experience
- **Status Badges**: Enhanced visual status indicators
- **Loading States**: Better loading indicators during operations

### 🔧 Technical Improvements

#### Strands SDK Compatibility
- **Fixed Import Patterns**: Updated to use official Strands SDK import structure
- **Python 3.10+ Support**: Added proper Python version requirements
- **Error Handling**: Improved fallback handling for missing dependencies
- **Agent Creation**: Updated agent initialization to match official SDK patterns

#### Windows Compatibility
- **Windows Setup Guide**: Added comprehensive `WINDOWS_SETUP.md`
- **PowerShell Scripts**: Enhanced Windows PowerShell support
- **Troubleshooting**: Windows-specific installation and runtime fixes
- **Environment Setup**: Improved virtual environment handling on Windows

### 📚 Documentation Updates
- **Updated README**: Added new features documentation and usage guides
- **Windows Guide**: Comprehensive Windows installation instructions
- **Troubleshooting**: Enhanced troubleshooting section with new features
- **Keyboard Shortcuts**: Documented new keyboard shortcuts
- **SBOM Documentation**: Added Software Bill of Materials in SPDX format

### 🐛 Bug Fixes
- Fixed Strands SDK import issues causing startup failures
- Resolved Windows-specific installation problems
- Improved error messages and user feedback
- Enhanced browser compatibility for notifications

### ⚡ Performance Improvements
- Optimized research queue updates
- Reduced unnecessary re-renders in React components
- Improved notification system performance
- Better memory management for bulk operations

## [v0.1.0] - 2024-01-01

### Initial Release
- Basic AI tool research functionality
- Flask backend with SQLite database
- React frontend with Tailwind CSS
- AWS Strands Agents integration
- 13 specialized research tools
- Tool categorization and management
- Basic CRUD operations for tools
- Company and pricing research
- GitHub repository analysis
- Feature extraction and integration detection

---

## Coming Soon

### Planned Features
- **Export/Import**: CSV and JSON export/import functionality  
- **Advanced Analytics**: Market trend analysis and reporting
- **API Access**: REST API for external integrations
- **Template Tools**: Save and reuse tool configurations
- **Advanced Filtering**: More sophisticated search and filter options
- **Collaboration**: Team features and shared workspaces