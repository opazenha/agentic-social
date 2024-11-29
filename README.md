# Social Media Content Generator

A powerful AI-driven tool designed to generate engaging social media content with a focus on faith-based messages for Portuguese-speaking young adults (18-35). The system utilizes CrewAI and DALL-E to create both compelling post content and visually appealing images.

## Features

- **Automated Content Generation**: Creates three unique social media posts per run
- **AI-Powered Image Creation**: Generates custom background images optimized for text overlay
- **Portuguese-Focused**: Content tailored for Portuguese (PT-PT) audience
- **Faith-Based Integration**: Naturally incorporates biblical wisdom into modern contexts
- **Young Adult Target**: Content styled for 18-35 age demographic
- **Instagram-Ready**: 1:1 aspect ratio images with space for text overlay

## Prerequisites

- Python 3.12+
- OpenAI API key (for DALL-E image generation)
- CrewAI compatible environment

## Installation

1. Clone the repository:
```
git clone https://github.com/opazenha/agentic-social.git
cd social
```
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```
```
pip install -r requirements.txt
```
# Create a .env file and add your OpenAI API key
```
echo "OPENAI_API_KEY=your-api-key-here" > .env
```
```
social/
├── src/
│   └── social/
│       ├── config/
│       │   ├── agents.yaml    # Agent configurations
│       │   └── tasks.yaml     # Task definitions
│       ├── generated_posts/   # Output directory for posts
│       ├── generated_images/  # Output directory for images
│       ├── crew.py           # Core CrewAI implementation
│       └── main.py           # Flask API endpoints
├── .env                      # Environment variables
├── .gitignore
└── README.md
```
### Usage
Start the Flask server:
```
python -m src.social.main
```
Generate content by sending a POST request to /generate-ideas:
```
curl -X POST http://localhost:5000/generate-ideas \
     -H "Content-Type: application/json" \
     -d '{"topic": "prayer and meditation"}'
```
The system will generate:

Three unique social media posts in Portuguese
Custom background images for each post
A markdown file containing all generated content
Images saved in the generated_images directory


### Output Structure
The system generates two types of files:

1. Post Content (generated_posts/task_posts_[timestamp].md):
- Post captions in Portuguese
- Hashtags
- Biblical references
- Call-to-action

2. Images (generated_images/):
- 1:1 aspect ratio
- Optimized for text overlay
- Portuguese design elements
- Modern, abstract style

### Configuration
- `config/agents.yaml`: Define agent roles and behaviors
- `config/tasks.yaml`: Configure task descriptions and workflows
- `.env`: Store API keys and environment variables

### Development
To modify the system:

Adjust agent behaviors in `config/agents.yaml`
Modify task descriptions in `config/tasks.yaml`
Update image generation parameters in `crew.py`

Acknowledgments
CrewAI for the agent framework
DALL-E for image generation
OpenAI for language models