# Krishi 🌾

A simple agricultural assistant application built with FastAPI.

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Redis (for background tasks)
- uv (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd krishi
   ```

2. **Install uv (if not already installed)**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies**
   ```bash
   uv sync
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root with the following keys:
   ```
   OGD_API_KEY=your_ogd_api_key
   ROBOFLOW_API_KEY=your_roboflow_api_key
   GEMINI_API_KEY=your_gemini_api_key
   TAVILY_API_KEY=your_tavily_api_key
   WEATHER_API_KEY=your_weather_api_key
   SUPABASE_URI=your_supabase_uri
   SUPABASE_KEY=your_supabase_key
   ```

5. **Add Firebase credentials**
   
   Place your `firebase-creds.json` file in the project root.

6. **Start Redis** (in a separate terminal)
   ```bash
   redis-server
   ```

### Running the Application

1. **Start the FastAPI server**
   ```bash
   uv run uvicorn main:app --reload
   ```

2. **Open your browser**
   
   Navigate to: `http://localhost:8000`
   
   API Documentation: `http://localhost:8000/docs`

## 📁 Project Structure

```
krishi/
├── api/          # API routes and models
├── agent/        # Bot and tools logic
├── config/       # Configuration settings
├── lib/          # Database and utility modules
└── main.py       # FastAPI application entry point
```

## 🛠️ Features

- Farmer management
- Chat functionality
- Market information
- Weather data
- Crop recommendations
- Image detection for agriculture

## 🤝 Need Help?

If you run into any issues:
1. Make sure all environment variables are set correctly
2. Ensure Redis is running
3. Check that Python 3.11+ is installed

Happy farming! 🌱
