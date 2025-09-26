# User Management System

## Overview

A Flask-based web application that provides user registration, authentication, and messaging capabilities. The system allows users to register with their credentials, log in securely, and send messages to other users via email through a dashboard interface. Built with a traditional server-side rendering approach using Flask templates and Bootstrap for styling.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask for server-side rendering
- **UI Framework**: Bootstrap 5.1.3 for responsive design and styling
- **Base Template Pattern**: Uses template inheritance with a base.html that includes common navigation and layout
- **Client-Side Interaction**: Minimal JavaScript for form interactions and messaging functionality

### Backend Architecture
- **Web Framework**: Flask with modular route handling
- **Authentication System**: Flask-Login for session management with custom User class
- **Password Security**: Werkzeug for password hashing and verification
- **Form Handling**: WTForms for form validation and processing
- **Session Management**: Flask sessions with configurable secret key from environment variables

### Data Storage
- **Database**: SQLite for user data persistence
- **Schema Design**: Single users table with fields for id, username, email, phone, and password_hash
- **Database Initialization**: Programmatic table creation with proper constraints
- **Data Access**: Direct SQLite connections with manual query execution

### Authentication & Authorization
- **User Authentication**: Email/password based login system
- **Session Security**: Flask-Login handles user sessions and login state
- **Password Storage**: Salted and hashed passwords using Werkzeug security utilities
- **Route Protection**: Login-required decorators for protected endpoints
- **User Model**: Custom User class implementing UserMixin for Flask-Login compatibility

### Application Structure
- **MVC Pattern**: Clear separation between routes (controllers), templates (views), and data models
- **Modular Services**: External email service separated into dedicated module
- **Configuration Management**: Environment-based configuration for secrets and API keys
- **Error Handling**: Flash messaging system for user feedback and error display

## External Dependencies

### Email Service Integration
- **SendGrid API**: Third-party email service for sending messages to users
- **Configuration**: Requires SENDGRID_API_KEY environment variable
- **Service Module**: Dedicated sendgrid_service.py for email functionality
- **Error Handling**: Graceful fallback and error reporting for email failures

### Frontend Dependencies
- **Bootstrap CDN**: External CSS and JavaScript framework for responsive UI
- **CDN Delivery**: Uses Bootstrap 5.1.3 from jsdelivr CDN for styling and components

### Python Package Dependencies
- **Flask**: Core web framework
- **Flask-Login**: User session management
- **Werkzeug**: Security utilities and password hashing
- **WTForms**: Form validation and processing
- **SendGrid**: Email API client library
- **SQLite3**: Built-in Python database interface

### Environment Configuration
- **SESSION_SECRET**: Flask session encryption key (falls back to development key)
- **SENDGRID_API_KEY**: Required for email functionality
- **Database**: SQLite file-based storage (users.db)