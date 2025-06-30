# 💼 Upwork Job Analyzer & Proposal Generator

An AI-powered application that helps freelancers analyze Upwork job postings, match them to their profile, and generate optimized proposals using LLaMA 3.3 via Groq API.

## 🚀 Features

### 🔍 Job Analysis
- **Multi-source job input**: Manual input, URL scraping, or selection from scraped jobs
- **Comprehensive analysis**: Client rating, pay rate, skill matching, and client history
- **Smart filtering**: Minimum $15/hour rate, 4.0+ client rating requirements
- **Skill matching**: Uses spaCy for semantic similarity analysis
- **Detailed recommendations**: Personalized suggestions for each job

### 🤖 AI-Powered Proposal Generation
- **LLaMA 3.3 Integration**: Uses Groq API for advanced AI proposal generation
- **Template fallback**: Professional template-based proposals when AI is unavailable
- **Personalized content**: Incorporates your profile, past projects, and job requirements
- **Smart formatting**: Professional structure with clear sections

### 📊 Web Scraping
- **RapidAPI Integration**: Real-time job data from Upwork via RapidAPI services
- **Live job listings**: Current job postings with actual client ratings and budgets
- **Fallback mechanism**: Realistic mock data when APIs are unavailable
- **Multiple API support**: Primary and backup RapidAPI services
- **Rate limiting**: Respectful API usage with built-in delays
- **BeautifulSoup integration**: Legacy scraping for URL-based job extraction
- **Keyword-based search**: Search for jobs by multiple keywords
- **Comprehensive data extraction**: Job details, client info, budget, skills, ratings

### 👤 Enhanced Profile Management
- **Comprehensive profiles**: Name, email, skills, experience, bio, portfolio, timezone
- **Past projects tracking**: Detailed project history with tech stack, outcomes, ratings
- **Successful proposals**: Store and reference past successful proposals
- **Multiple profiles**: Manage multiple freelancer profiles

### 📈 History & Analytics
- **Job analysis history**: Track all analyzed jobs and results
- **Proposal history**: View and manage past proposals
- **Project portfolio**: Comprehensive project tracking
- **Dashboard metrics**: Overview of profiles, jobs, and performance

### 🗄️ Structured Database
- **SQLite backend**: Reliable local data storage
- **Comprehensive schema**: Freelancer profiles, projects, proposals, job analysis, scraped jobs
- **Data relationships**: Proper foreign key relationships
- **Easy backup**: Simple file-based database

## 🛠️ Tech Stack

### Frontend
- **React 18**: Modern, responsive web interface
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API communication

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.9+**: Core application logic
- **SQLite**: Local database storage
- **BeautifulSoup**: Web scraping capabilities
- **spaCy**: Natural language processing for skill matching

### AI Integration
- **Groq API**: LLaMA 3.3 model access for advanced proposal generation
- **Template system**: Professional fallback proposal generation
- **Smart prompts**: Optimized AI prompts for better results
- **Automatic fallback**: Seamless transition between AI and template generation

### Data Extraction
- **BeautifulSoup**: HTML parsing and data extraction
- **Requests**: HTTP client for web scraping
- **Rate limiting**: Respectful scraping practices

## 📦 Installation

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Upwork-V2
   ```

2. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Install spaCy language model**
   ```bash
   python -m spacy download en_core_web_lg
   ```

4. **Set up environment variables**
   Create a `.env` file in the backend directory:
   ```bash
   cp env.example .env
   ```
   
   Edit the `.env` file and add your API keys:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   RAPIDAPI_KEY=be84506f4emsheb5fcce67290d7ep19dda7jsn270f1e5c28f1
   ```
   
   Get your API keys from:
   - **Groq API**: https://console.groq.com/ (free tier available)
   - **RapidAPI**: https://rapidapi.com/ (subscribe to Upwork Jobs API)
   
   **Important**: The Groq API key is required for AI-powered proposal generation. See `GROQ_SETUP_GUIDE.md` for detailed setup instructions.

5. **Test the RapidAPI integration**
   ```bash
   python test_rapidapi_scraper.py
   ```

6. **Initialize the database**
   ```bash
   python migrate_db.py
   ```

7. **Start the backend server**
   ```bash
   python main.py
   ```
   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Install Node.js dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server**
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

## 🧪 Testing

### Backend Tests
```bash
python test_backend.py
```

### Groq API Integration Tests
```bash
# Test Groq API integration
python test_groq.py

# Interactive test with custom inputs
python cli_test.py

# Quick test with default values
python cli_test.py --quick
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📖 Usage Guide

### 1. 🏠 Dashboard
- View application statistics
- See recent scraped jobs
- Monitor your profiles and performance

### 2. 👤 Profile Management
- Create comprehensive freelancer profiles
- Add past projects with detailed information
- Manage multiple profiles for different specializations

### 3. 📊 Job Scraping
- Enter keywords (one per line)
- Set maximum jobs per keyword
- Choose optional category filter
- Scraped jobs are automatically saved to database

### 4. 🔍 Job Analysis
Choose from three input methods:
- **Manual Input**: Enter job details manually
- **Job URL**: Scrape job details from Upwork URL
- **Scraped Jobs**: Select from previously scraped jobs

### 5. 📝 Proposal Generation
- Automatic analysis of job fit
- AI-powered proposal generation (if Groq API key is set)
- Template-based fallback proposals
- Save and manage proposals

## 🔧 Configuration

### API Keys
- **Groq API Key**: Required for AI-powered proposal generation
- **RapidAPI Key**: Required for real-time job scraping from Upwork
- Get your keys from:
  - Groq API: https://console.groq.com/
  - RapidAPI: https://rapidapi.com/ (subscribe to Upwork Jobs API)
- See `RAPIDAPI_INTEGRATION.md` for detailed setup instructions

### Database
- **Location**: `backend/data/freelancer.db`
- **Backup**: Simply copy the database file
- **Reset**: Delete the database file to start fresh

### Scraping Settings
- **Rate limiting**: Built-in delays to respect Upwork's servers
- **User agent**: Professional browser identification
- **Error handling**: Graceful failure with informative messages

## 📊 Database Schema

### Tables
1. **freelancer_profiles**: Comprehensive freelancer information
2. **past_projects**: Detailed project history and outcomes
3. **successful_proposals**: Proposal templates and responses
4. **job_analysis_history**: Track all job analyses
5. **scraped_jobs**: Store scraped job data

### Key Features
- **JSON storage**: Skills and tech stacks stored as JSON
- **Timestamps**: Created and updated timestamps
- **Foreign keys**: Proper relationships between tables
- **Unique constraints**: Prevent duplicate job URLs

## 🚨 Important Notes

### Web Scraping
- **Respectful scraping**: Built-in delays and rate limiting
- **Terms of service**: Ensure compliance with Upwork's terms
- **Error handling**: Graceful handling of scraping failures
- **Data accuracy**: Verify scraped data manually

### AI Integration
- **API costs**: Groq API usage incurs costs
- **Fallback system**: Template-based proposals when AI is unavailable
- **Prompt optimization**: Carefully crafted prompts for better results

### Data Privacy
- **Local storage**: All data stored locally in SQLite
- **No external sharing**: Data never leaves your system
- **Backup responsibility**: You are responsible for backing up your data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Create an issue on GitHub
3. Contact the development team 