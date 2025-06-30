# Groq API Setup Guide for AI-Powered Proposal Generation

This guide will help you set up Groq API integration for generating AI-powered freelance proposals using LLaMA 3.3.

## What is Groq?

Groq is a high-performance AI inference platform that provides fast access to large language models like LLaMA 3.3. It's perfect for generating high-quality, personalized freelance proposals quickly.

## Prerequisites

1. Python 3.8+ installed
2. Access to the Orion Freelancer Application backend
3. Internet connection for API calls

## Step 1: Get Your Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up for a free account
3. Navigate to the API Keys section
4. Create a new API key
5. Copy the API key (it starts with `gsk_`)

## Step 2: Set Up Environment Variables

### Option A: Using .env file (Recommended)

1. Copy the example environment file:
   ```bash
   cp backend/env.example backend/.env
   ```

2. Edit the `.env` file and replace the placeholder with your actual API key:
   ```
   GROQ_API_KEY=gsk_your_actual_api_key_here
   ```

### Option B: Set Environment Variable Directly

#### Windows (PowerShell):
```powershell
$env:GROQ_API_KEY="gsk_your_actual_api_key_here"
```

#### Windows (Command Prompt):
```cmd
set GROQ_API_KEY=gsk_your_actual_api_key_here
```

#### Linux/Mac:
```bash
export GROQ_API_KEY="gsk_your_actual_api_key_here"
```

## Step 3: Install Dependencies

The Groq library is already included in `requirements.txt`, but make sure it's installed:

```bash
cd backend
pip install -r requirements.txt
```

## Step 4: Test the Integration

1. Start the backend server:
   ```bash
   cd backend
   python main.py
   ```

2. You should see one of these messages:
   - ✅ AI-powered proposal generation enabled with LLaMA 3.3
   - ⚠️ Warning: Could not initialize Groq client: [error message]
   - ℹ️ Note: Using template-based proposal generation. Set GROQ_API_KEY for AI-powered proposals.

## Step 5: Generate AI-Powered Proposals

Once set up, you can generate AI-powered proposals through:

1. **API Endpoint**: `POST /api/v1/proposals/generate`
2. **Frontend Interface**: Use the proposal generation feature in the web app

### API Request Example:
```json
{
  "freelancer_id": 1,
  "job_title": "Full-Stack Web Developer",
  "job_description": "We need a skilled developer to build a modern web application...",
  "required_skills": ["React", "Node.js", "MongoDB"],
  "use_ai": true
}
```

## Features of AI-Powered Proposals

The AI integration provides:

1. **Personalized Content**: Tailored to specific job requirements
2. **Relevant Experience Highlighting**: Automatically matches your skills to job needs
3. **Professional Structure**: Well-organized sections with clear formatting
4. **Smart Questions**: Generates thoughtful questions to engage clients
5. **Value Proposition**: Emphasizes your unique selling points
6. **Fallback Support**: Automatically falls back to template-based generation if AI fails

## Troubleshooting

### Common Issues:

1. **"Groq library not installed"**
   - Solution: Run `pip install groq`

2. **"Could not initialize Groq client"**
   - Check your API key is correct
   - Verify internet connection
   - Ensure API key has proper permissions

3. **"Using template-based proposal generation"**
   - Verify GROQ_API_KEY is set correctly
   - Check the .env file is in the right location
   - Restart the server after setting environment variables

4. **API Rate Limits**
   - Groq has generous free tier limits
   - Monitor usage in the Groq console

### Debug Mode:

To see detailed error messages, set:
```
DEBUG=True
```

## Cost Considerations

- Groq offers a generous free tier
- Pricing is based on token usage
- Typical proposal generation costs: $0.01-$0.05 per proposal
- Monitor usage in the Groq console

## Security Best Practices

1. **Never commit API keys to version control**
2. **Use environment variables for sensitive data**
3. **Rotate API keys regularly**
4. **Monitor API usage for unusual activity**

## Advanced Configuration

### Custom Model Selection:
You can modify the model in `backend/utils/proposal_generator.py`:
```python
self.model = "llama-3.3-70b-versatile"  # Current model
# Alternative models:
# "llama-3.1-8b-instant"
# "llama-3.1-70b-versatile"
# "mixtral-8x7b-32768"
```

### Temperature and Token Settings:
Adjust creativity and length in the `_generate_ai_proposal` method:
```python
temperature=0.7,  # 0.0 = conservative, 1.0 = creative
max_tokens=2000,  # Maximum response length
top_p=0.9         # Nucleus sampling parameter
```

## Support

If you encounter issues:

1. Check the console output for error messages
2. Verify your API key is valid
3. Test with a simple API call to Groq
4. Check the Groq documentation: https://console.groq.com/docs

## Next Steps

Once Groq is set up, you can:

1. Generate proposals through the web interface
2. Customize the AI prompts for different industries
3. Integrate with job scraping for automated proposal generation
4. Analyze proposal success rates and optimize prompts

Happy proposal generating! 🚀 