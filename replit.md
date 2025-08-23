# AI-Powered Resume Optimizer

## Overview

The AI-Powered Resume Optimizer is a comprehensive web application that analyzes, optimizes, and generates professional resumes in multiple formats. The system uses artificial intelligence and natural language processing to provide intelligent keyword matching, grammar checking, and resume scoring. Users can upload resumes in various formats (PDF, DOCX, TXT), input job descriptions, and receive detailed analysis with actionable suggestions for improvement.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **Flask Web Framework**: Lightweight Python web framework serving as the application foundation
- **File-based Data Persistence**: Uses JSON files for storing resume history and analysis data, avoiding database complexity while maintaining data persistence
- **Modular Design**: Clear separation of concerns with dedicated modules for text extraction, NLP analysis, grammar checking, resume generation, and scoring

### Text Processing Pipeline
- **Multi-format Text Extraction**: Supports PDF (PyPDF2), DOCX (python-docx), and TXT files with robust error handling
- **NLP Analysis Engine**: Utilizes spaCy and NLTK for advanced text processing, keyword extraction, and semantic analysis
- **TF-IDF Similarity Matching**: Employs scikit-learn for calculating semantic similarity between resumes and job descriptions
- **Grammar Analysis**: Integrates LanguageTool Python API for comprehensive grammar and style checking

### Resume Generation System
- **Template-based Architecture**: Four distinct resume formats (Chronological, Functional, Combination, Targeted) using Jinja2 templating
- **HTML-to-PDF Conversion**: WeasyPrint for high-quality PDF generation from HTML/CSS templates
- **Content Optimization**: Intelligent content restructuring based on job description analysis and keyword matching

### Scoring and Analysis Engine
- **Multi-factor Scoring**: Weighted scoring system combining keyword matching (35%), skills alignment (25%), semantic similarity (20%), grammar quality (15%), and completeness (5%)
- **Real-time Feedback**: Instant analysis results with detailed breakdowns and improvement suggestions
- **Performance Categorization**: Automatic classification of resume quality with targeted recommendations

### Frontend Architecture
- **Bootstrap-based UI**: Responsive design using Bootstrap with custom CSS for enhanced user experience
- **Progressive Enhancement**: JavaScript-enhanced interactions with graceful fallbacks
- **File Upload Interface**: Drag-and-drop file upload with real-time validation and preview
- **Mobile-first Design**: Fully responsive interface optimized for all device sizes

## External Dependencies

### Core NLP Libraries
- **spaCy (en_core_web_sm)**: English language model for named entity recognition, part-of-speech tagging, and text analysis
- **NLTK**: Natural Language Toolkit for tokenization, stopword removal, and text preprocessing
- **scikit-learn**: Machine learning library for TF-IDF vectorization and cosine similarity calculations

### File Processing
- **PyPDF2**: PDF text extraction and processing
- **python-docx**: Microsoft Word document text extraction
- **WeasyPrint**: HTML/CSS to PDF conversion for resume generation

### Web Framework Components
- **Flask**: Core web framework with session management and request handling
- **Jinja2**: Template engine for dynamic HTML generation
- **Werkzeug**: WSGI utilities and security helpers

### Grammar and Language Processing
- **LanguageTool Python**: Free grammar checking service for identifying writing issues and style improvements

### Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design and UI components
- **Font Awesome**: Icon library for enhanced visual interface
- **Custom CSS/JS**: Application-specific styling and interactive features

### Development and Deployment
- **Replit Environment**: Cloud-based development and hosting platform
- **File System Storage**: Local file system for uploads, downloads, and data persistence
- **Environment Variables**: Configuration management for sensitive settings