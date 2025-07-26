# Sports Betting Predictor Application

## Overview

This is a Streamlit-based sports betting prediction application that uses machine learning to analyze historical sports data and make predictions. The application provides educational insights into sports analytics and prediction modeling, with a strong emphasis on responsible gambling practices.

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

## Data Flow

1. **Data Input**: Sample data generation or user data upload
2. **Data Processing**: Cleaning, validation, and feature engineering
3. **Model Training**: Feature extraction and ML model training
4. **Prediction Generation**: Real-time predictions based on input parameters
5. **Visualization**: Interactive charts and performance metrics display
6. **Results Presentation**: Streamlit interface with organized tabs and sections

## External Dependencies

### Core Libraries
- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **plotly**: Interactive visualization library
- **scikit-learn**: Machine learning algorithms and tools
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