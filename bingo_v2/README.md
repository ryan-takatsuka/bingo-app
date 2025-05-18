# Bingo App V2

A refactored version of the Bingo App that runs as a live web application on AWS.

## Overview

Bingo App V2 transforms the original static HTML bingo application into a full-featured web application with server-side functionality. This allows for:

- Multiple users to play simultaneously
- Persistent storage of bingo cards
- Real-time updates and interactions
- Easy deployment to AWS

## Technology Stack

### Backend
- **Framework**: Flask - A lightweight Python web framework that's easy to deploy and scale
- **Database**: SQLite for development, Amazon RDS (PostgreSQL) for production
- **Hosting**: AWS Elastic Beanstalk for easy deployment and scaling
- **Storage**: Amazon S3 for storing images and assets

### Frontend
- **Framework**: React.js - A modern JavaScript library for building user interfaces
- **Styling**: CSS with responsive design principles
- **Build Tool**: Webpack for bundling and optimization

## Architecture

The application follows a client-server architecture:

1. **Client**: React.js frontend that handles the UI and user interactions
2. **Server**: Flask API that handles data processing, storage, and business logic
3. **Database**: Stores bingo card data, user preferences, and game state
4. **Storage**: S3 bucket for storing images and other static assets

## Features

- All original functionality from V1 (randomization, tile revealing, win detection)
- User accounts and authentication
- Ability to save and load bingo cards
- Multiplayer functionality (optional)
- Mobile-responsive design
- Improved accessibility

## Directory Structure

```
bingo_v2/
├── backend/                # Flask application
│   ├── app.py              # Main application file
│   ├── models.py           # Database models
│   ├── routes/             # API routes
│   ├── services/           # Business logic
│   ├── templates/          # Jinja2 templates (for admin views)
│   └── utils/              # Utility functions
├── frontend/               # React application
│   ├── public/             # Static files
│   ├── src/                # Source code
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── pages/          # Page components
│   │   ├── services/       # API service functions
│   │   ├── styles/         # CSS styles
│   │   └── utils/          # Utility functions
│   └── package.json        # Dependencies and scripts
├── data/                   # Data files
│   └── bingo_tiles.csv     # Default bingo tiles
├── images/                 # Image assets
├── scripts/                # Deployment and utility scripts
├── .gitignore              # Git ignore file
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## Setup and Installation

### Prerequisites
- Python 3.11 or higher
- Node.js 16 or higher
- AWS account (for production deployment)

### Local Development Setup

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/bingo-app.git
   cd bingo-app/bingo_v2
   ```

2. Set up the backend
   ```bash
   cd backend
   conda activate bingo-app
   pip install -r requirements.txt
   flask run
   ```

3. Set up the frontend
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. Open your browser and navigate to http://localhost:3000

## Deployment to AWS

The application can be deployed to AWS using Elastic Beanstalk for the backend and S3/CloudFront for the frontend. Detailed deployment instructions are available in the `scripts/deploy.md` file.

## Migration from V1

If you have existing bingo cards from V1, you can import them using the migration tool:

```bash
python scripts/migrate_v1.py --input-dir /path/to/v1/files
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.