# SportsBet Pro - SaaS Sports Prediction Platform

## Overview

SportsBet Pro is now a complete SaaS (Software as a Service) platform for AI-powered sports predictions and analytics. The platform features subscription-based access, professional frontend/backend architecture, and enterprise-grade features including API access, real-time data, and advanced analytics.

## Recent Changes (July 28, 2025)

✓ **AI-Powered Analysis Integration**: Added ChatGPT and Gemini AI for intelligent game predictions
✓ **Smart Game Discovery**: AI-enhanced search and recommendation system
✓ **WNBA Games Integration**: Successfully added 2 live WNBA games with proper scheduling
✓ **Enhanced Monthly Calendar**: Comprehensive date-based game fetching for entire month
✓ **Responsible Gambling Features**: Educational betting insights with safety warnings
✓ **Multi-AI Comparison**: Side-by-side analysis from OpenAI GPT-4o and Google Gemini
✓ **Smart Date Filtering**: Games filtered by selected date, removing out-of-season matches
✓ **Professional Organization**: Tab-based navigation with AI predictions page

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application framework
- **Layout**: Wide layout with expandable sidebar navigation
- **Page Structure**: Multi-page application with session state management
- **Visualization**: Plotly for interactive charts and graphs

### Backend Architecture
- **Core Logic**: Python-based modular architecture with separate concerns
- **Machine Learning**: Scikit-learn for predictive modeling
- **Data Processing**: Pandas and NumPy for data manipulation
- **Model Architecture**: Ensemble methods (Random Forest) with feature engineering

### Data Storage Solutions
- **Current State**: In-memory data storage using Pandas DataFrames
- **Session Management**: Streamlit session state for maintaining application state
- **Sample Data**: Programmatically generated sample datasets for demonstration

## Key Components

### 1. Application Entry Point (`app.py`)
- Main Streamlit application with page configuration
- Session state initialization for core components
- Navigation sidebar with multiple analysis pages
- Responsible gambling disclaimer and warnings

### 2. Machine Learning Predictor (`models/predictor.py`)
- **SportsPredictor Class**: Core ML prediction engine
- **Models Supported**: Random Forest Classifier, Logistic Regression
- **Feature Engineering**: Historical performance metrics, team statistics
- **Model Evaluation**: Cross-validation, accuracy metrics, confusion matrices

### 3. Data Processing (`utils/data_processor.py`)
- **DataProcessor Class**: Data cleaning and transformation utilities
- **Capabilities**: Date parsing, filtering, score validation, team name standardization
- **Derived Features**: Winner determination, score differences, temporal features

### 4. Visualization Engine (`utils/visualization.py`)
- **Visualizer Class**: Interactive chart generation using Plotly
- **Chart Types**: Performance trends, team comparisons, statistical distributions
- **Color Scheme**: Consistent color palette for visual coherence

### 5. Sample Data Generator (`data/sample_data.py`)
- **Multi-Sport Support**: Football, basketball, baseball datasets
- **Realistic Data**: Appropriate score ranges and team names for each sport
- **Historical Depth**: 2 years of synthetic match data

### 6. Live Sports API Manager (`utils/sports_apis.py`)
- **Multi-API Integration**: ESPN, TheSportsDB, API-Football, MySportsFeeds
- **Free Tier Support**: ESPN and TheSportsDB require no API keys
- **Premium Features**: API-Football and MySportsFeeds with enhanced data
- **Data Aggregation**: Combines and cleans data from multiple sources
- **Real-time Updates**: Fetches live scores and recent game results
- **Connection Testing**: Validates API connectivity and key functionality

## Data Flow

1. **Data Input**: Live API data, sample data generation, or user data upload
2. **API Integration**: Real-time data fetching from multiple sports APIs
3. **Data Processing**: Cleaning, validation, and feature engineering
4. **Model Training**: Feature extraction and ML model training with live data
5. **Prediction Generation**: Real-time predictions based on current data
6. **Visualization**: Interactive charts and performance metrics display
7. **Results Presentation**: Streamlit interface with organized tabs and sections

## External Dependencies

### Core Libraries
- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **plotly**: Interactive visualization library
- **scikit-learn**: Machine learning algorithms and tools
- **requests**: HTTP requests for API integration
- **aiohttp**: Asynchronous HTTP client for enhanced API performance
- **datetime**: Date and time handling

### Machine Learning Stack
- **Random Forest**: Primary prediction algorithm
- **Logistic Regression**: Alternative classification method
- **StandardScaler**: Feature normalization
- **LabelEncoder**: Categorical variable encoding

## Deployment Strategy

### Current Configuration
- **Platform**: Replit-compatible Python application
- **Runtime**: Python with Streamlit server
- **Dependencies**: Requirements managed through standard Python imports
- **Scalability**: Single-instance application suitable for demonstration and development

### Architectural Decisions

1. **Streamlit Framework Choice**
   - **Problem**: Need for rapid prototyping of data science application
   - **Solution**: Streamlit for quick deployment and interactive features
   - **Pros**: Fast development, built-in widgets, easy visualization integration
   - **Cons**: Limited customization compared to full web frameworks

2. **Modular Architecture**
   - **Problem**: Separation of concerns for maintainability
   - **Solution**: Separate modules for prediction, processing, and visualization
   - **Pros**: Clean code organization, reusable components, easier testing
   - **Cons**: Slightly more complex import structure

3. **In-Memory Data Storage**
   - **Problem**: Simple data persistence for demonstration purposes
   - **Solution**: Session state and DataFrame-based storage
   - **Pros**: No database setup required, fast access, simple deployment
   - **Cons**: Data lost on session end, limited scalability

4. **Sample Data Generation**
   - **Problem**: Need for realistic demo data without real sports APIs
   - **Solution**: Programmatic generation of synthetic sports data
   - **Pros**: No external dependencies, consistent demo experience
   - **Cons**: Not real data, limited complexity compared to actual sports data

The application prioritizes educational value and responsible gambling messaging while providing a functional demonstration of sports analytics and machine learning techniques.