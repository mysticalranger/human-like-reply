# Social Reply Generator

A sophisticated AI-powered application that generates human-like replies to social media posts across different platforms (LinkedIn, Twitter, and Instagram).

## Features

- **Platform-Specific Replies**: Tailored responses that match the tone and style of each platform.
- **Multi-Stage Generation**: Employs a sophisticated 3-stage AI process (analyze → personalize → refine) for authentic and context-aware replies.
- **Caching**: Efficient in-memory response caching with TTL to improve performance and reduce API costs.
- **MongoDB Integration**: Persistent storage of generated replies in MongoDB with schema validation.
- **REST API**: Well-documented FastAPI endpoints for generating replies and retrieving metrics.
- **Interactive Demo**: Streamlit-based user interface for easy testing and demonstration.
- **Docker Support**: Fully containerized using Docker Compose for easy setup, development, and deployment.
- **Metrics & Logging**: Tracks request metrics, cache hit rates, generation times, and errors.

## Architecture

The application follows a modular architecture:

- **AI Module**: Handles the 3-stage reply generation using the Mistral AI API.
- **API Layer**: Built with FastAPI, providing endpoints for reply generation and metrics. Includes input validation and error handling.
- **Storage Layer**: Uses MongoDB (via Motor async driver) for storing generated replies, with schema validation enforced.
- **Caching Layer**: Implements an in-memory cache for frequently requested replies to reduce latency and API calls.
- **UI Layer**: An interactive demo built with Streamlit, allowing users to test the reply generation.
- **Metrics Module**: Collects and exposes operational metrics.

*architecture diagram:*

```text
[MongoDB] <--> [API Service (FastAPI + AI Module + Cache)] <--> [Streamlit UI]
                  |
                  +--> [Mistral AI API]
```

## Quick Start with Docker

This is the recommended way to run the application.

1. **Clone the Repository**:

    ```bash
    git clone <your-repository-url>
    cd social_reply_generator
    ```

2. **Create Environment File**:
    Copy the example environment file and add your Mistral API key:

    ```bash
    cp .env.example .env
    ```

    Then, edit `.env` and replace `your_mistral_api_key_here` with your actual Mistral API key.
    Ensure `MONGO_URI` in `.env` is `mongodb://mongo:27017/social_reply_db4` for Docker. (Note: Your local `.env` currently has `localhost`, which is fine for local non-Docker runs, but Docker services will use the service name `mongo`).

3. **Build and Start Services**:

    ```bash
    docker-compose build
    docker-compose up -d
    ```

    The `-d` flag runs the containers in detached mode. You can view logs using `docker-compose logs -f`.

4. **Initialize Database & Import Posts (One-Time Setup)**:
    In a separate terminal, run the initialization service. This creates the database schema and imports posts from the CSV.

    ```bash
    docker-compose --profile init up init-db
    ```

    This command will run the `init-db` service, execute `scripts/init_db.py` and then `scripts/import_posts.py`.

5. **Access Services**:
    - **API**: [http://localhost:8000](http://localhost:8000) (Swagger UI for docs: [http://localhost:8000/docs](http://localhost:8000/docs))
    - **Streamlit UI**: [http://localhost:8501](http://localhost:8501)

## Manual Setup (Without Docker)

### Prerequisites

- Python 3.11+
- MongoDB instance (running locally or on a cloud service like MongoDB Atlas)
- Mistral AI API key

### Environment Setup

1. **Clone the Repository**:

    ```bash
    git clone <your-repository-url>
    cd social_reply_generator
    ```

2. **Create a Virtual Environment (Recommended)**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables**:
    Copy `.env.example` to `.env`:

    ```bash
    cp .env.example .env
    ```

    Edit the `.env` file:
    - Set `MISTRAL_API_KEY` to your actual Mistral API key.
    - Set `MONGO_URI` to your MongoDB connection string (e.g., `mongodb://localhost:27017/social_reply_db4`).

5. **Initialize the Database**:
    This script creates the `replies` collection and applies schema validation.

    ```bash
    python scripts/init_db.py
    ```

6. **Import Sample Posts (Optional but Recommended for Testing)**:
    This script reads posts from `scripts/posts - Sheet1.csv`, generates replies using the AI, and stores them in the database.

    ```bash
    python scripts/import_posts.py
    ```

7. **Run the API Server**:

    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

8. **Run the Streamlit Interface**:
    In a new terminal:

    ```bash
    streamlit run app/demo.py
    ```

## Docker Components

The `docker-compose.yml` file defines the following services:

- **`mongo`**: MongoDB database service.
  - Data is persisted in a Docker volume named `mongo_data`.
  - Includes a healthcheck to ensure it's running before dependent services start.
- **`api`**: The FastAPI backend service.
  - Builds from the main `Dockerfile`.
  - Depends on `mongo` being healthy.
  - Mounts `./app:/app/app` for live code reloading during development.
- **`streamlit`**: The Streamlit UI frontend.
  - Builds from `Dockerfile.streamlit`.
  - Depends on `mongo` (healthy) and `api` (started).
- **`init-db`**: A service to initialize the database and import posts.
  - Runs only when the `init` profile is activated (`docker-compose --profile init up init-db`).
  - Executes `scripts/init_db.py` and `scripts/import_posts.py`.
  - Mounts `./scripts:/app/scripts`.
- **`tests`** (Optional - if you add this service to `docker-compose.yml`): A service to run tests within a Docker container.
  - Would typically run only when a `test` profile is activated.

*Note on Database Name*: Ensure all services in `docker-compose.yml` and your scripts consistently use the same database name (e.g., `social_reply_db4`). The `api` service in your current `docker-compose.yml` uses `social_reply_db2` for `MONGO_URI`, which should be updated to `social_reply_db4` for consistency.

## Database Initialization and Data Import

The `init-db` service in `docker-compose.yml` handles the initial setup:

1. **Schema Creation**: `scripts/init_db.py` connects to MongoDB, creates the `replies` collection if it doesn't exist, and applies schema validation rules.
2. **Data Import**: `scripts/import_posts.py` reads social media posts from `scripts/posts - Sheet1.csv`. For each post:
    - It generates an AI reply using the `generate_reply` function (which includes retry logic for API rate limits).
    - It saves the post, generated reply, and timestamp to the MongoDB `replies` collection.
    - Progress is tracked in `scripts/import_progress.txt`, allowing the script to resume from where it left off if interrupted.

To run this process:

```bash
docker-compose --profile init up init-db
```

This command needs to be run only once, or whenever you want to re-initialize the database with fresh data from the CSV.

## Approach to Human-Like Reply Generation

The core AI logic in `app/ai.py` uses a three-stage process to generate high-quality, authentic replies:

1. **Stage 1: Analyze Post (`analyze_post`)**:
    - The input social media post is analyzed to determine its tone, intent, key topics, likely audience, and any relevant context.
    - This analysis is structured as JSON for consistent processing.

2. **Stage 2: Personalize Reply (`personalize_reply`)**:
    - Based on the platform (LinkedIn, Twitter, Instagram) and the detailed analysis from Stage 1, a draft reply is generated.
    - A specific persona is adopted for each platform (e.g., "thoughtful professional" for LinkedIn, "witty, engaged user" for Twitter).
    - The prompt guides the AI to create a reply that shows authentic engagement, matches the platform's style, and adds value.

3. **Stage 3: Refine Reply (`refine_reply`)**:
    - The draft reply from Stage 2 is further refined to enhance its authenticity.
    - This stage focuses on adjusting length, adding natural language elements (like contractions), removing AI-like patterns, and ensuring the reply doesn't sound like a template.

This multi-stage approach, combined with platform-specific personas and refinement, helps in generating replies that are more nuanced, contextually appropriate, and human-sounding than simpler, single-prompt methods.

## API Endpoints

The API is documented using Swagger UI, available at `/docs` when the API service is running.

- **`POST /reply`**:
  - **Description**: Generates a human-like reply to a given social media post.
  - **Request Body**:

    ```json
    {
      "platform": "string (e.g., 'twitter', 'linkedin', 'instagram')",
      "post_text": "string"
    }
    ```

  - **Response Body**:

    ```json
    {
      "platform": "string",
      "post_text": "string",
      "generated_reply": "string",
      "timestamp": "string (ISO 8601 format)"
    }
    ```

  - **Behavior**: Checks cache first. If not cached, generates a new reply, caches it, and saves it to the database. Logs metrics for the request.

- **`GET /metrics`**:
  - **Description**: Retrieves a summary of operational metrics.
  - **Response Body**:

    ```json
    {
      "total_requests": "integer",
      "cache_hit_rate": "string (e.g., '50.0%')",
      "avg_generation_time": "string (e.g., '1.23s')",
      "platform_distribution": {
        "linkedin": "integer",
        "twitter": "integer",
        "instagram": "integer"
      },
      "error_rate": "string (e.g., '5.0%')",
      "avg_reply_length": "integer"
    }
    ```

### Example API Request (using cURL)

```bash
curl -X POST "http://localhost:8000/reply" \
     -H "Content-Type: application/json" \
     -d '{
           "platform": "twitter",
           "post_text": "Just launched my new open-source project! Check it out on GitHub. #opensource #dev"
         }'
```

## Testing

The project includes a suite of tests using `pytest`.

### Running Tests Locally

1. **Install Test Dependencies** (if not already installed with `requirements.txt`):

    ```bash
    pip install pytest pytest-asyncio httpx pytest-cov
    ```

2. **Run All Tests**:
    Ensure your `.env` file is configured, especially if tests interact with services that need API keys (though mocks should prevent actual calls for Mistral).

    ```bash
    pytest
    ```

3. **Run Tests with Coverage Report**:

    ```bash
    pytest --cov=app tests/
    ```

    This will generate a coverage report showing which parts of your `app` code are covered by tests.

### Test Structure

- **`tests/conftest.py`**: Contains shared fixtures, including mocks for database operations (`mock_db`) and Mistral AI client (`mock_mistral_client`). These mocks are crucial for isolating tests and avoiding external dependencies.
- **`tests/test_api.py`**: Tests for the FastAPI endpoints, ensuring correct responses, status codes, and error handling.
- **`tests/test_ai.py`**: Unit tests for the AI reply generation logic (`analyze_post`, `generate_reply`), verifying that the stages work as expected with mocked AI responses.
- **`tests/test_db.py`**: Tests for database interactions (`save_reply`), ensuring data is correctly stored and retrieved (using the mocked database).

### Running Tests with Docker (Recommended for CI/CD)

To run tests in a consistent Docker environment, you can add a `tests` service to your `docker-compose.yml`:

```yaml
# Add this service to your docker-compose.yml
  tests:
    build: .
    environment:
      - MONGO_URI=mongodb://mongo:27017/social_reply_db4 # Use a test-specific DB if needed
      - MISTRAL_API_KEY=${MISTRAL_API_KEY} # Mocks should prevent actual use
    depends_on:
      mongo:
        condition: service_healthy
    volumes:
      - ./app:/app/app
      - ./tests:/app/tests
    command: ["pytest", "-v"] # Or ["pytest", "--cov=app", "tests/"]
    profiles:
      - test
```

Then, run the tests using:

```bash
docker-compose --profile test up --build --exit-code-from tests tests
```

The `--build` flag ensures the image is up-to-date, and `--exit-code-from tests` will propagate the test exit code.

## Data Processing Flow

1. **User Interaction**: A user submits a social media post and platform choice via the Streamlit UI or directly to the API (`/reply` endpoint).
2. **Platform Normalization**: The platform name is normalized (e.g., "insta" becomes "instagram").
3. **Cache Check**: The system checks an in-memory cache (`app/cache.py`) for an existing reply to the same post on the same platform.
    - If a valid, non-expired cached reply exists, it's returned immediately. Metrics are logged for a cache hit.
4. **AI Reply Generation (if not cached)**:
    - The `generate_reply` function in `app/ai.py` is called.
    - **Stage 1 (Analysis)**: The post is analyzed for tone, intent, topics, etc.
    - **Stage 2 (Personalization)**: A draft reply is generated based on the analysis and platform-specific persona.
    - **Stage 3 (Refinement)**: The draft is refined for authenticity and natural language.
5. **Caching New Reply**: The newly generated reply is stored in the cache with a timestamp for future requests.
6. **Database Storage**: If the reply was newly generated (not from cache), the original post, generated reply, platform, and timestamp are saved to the MongoDB `replies` collection (`app/db.py`).
7. **Metrics Logging**: Details of the request (platform, cached status, generation time, reply length, errors) are logged asynchronously (`app/metrics.py`).
8. **Response to User**: The generated (or cached) reply is returned to the user.

## Troubleshooting

- **Docker Build Failures**:
  - If you encounter snapshot errors or caching issues during `docker-compose build`:

    ```bash
    docker builder prune -f
    docker-compose build --no-cache
    ```

- **MongoDB Connection Issues in Docker**:
  - Ensure the `MONGO_URI` in `docker-compose.yml` for `api` and `streamlit` services is `mongodb://mongo:27017/social_reply_db4`. `mongo` is the service name of the MongoDB container.
  - Check MongoDB container logs: `docker-compose logs mongo`.
- **`init-db` Service Not Running / No Data**:
  - The `init-db` service runs only when explicitly called with its profile: `docker-compose --profile init up init-db`. If you run `docker-compose up` without the profile, it won't execute.
- **Mistral API Key Errors**:
  - Ensure `MISTRAL_API_KEY` is correctly set in your `.env` file and that this file is loaded by the application/Docker service.
  - For Docker, ensure the `MISTRAL_API_KEY=${MISTRAL_API_KEY}` line in `docker-compose.yml` correctly passes the variable from your host's environment (or the `.env` file if Docker Compose is configured to use it).
- **Database Validation Errors**:
  - The MongoDB schema (`scripts/init_db.py` and `app/db.py`) enforces rules on `platform`, `post_text`, `generated_reply`, and `timestamp`. Ensure data being saved conforms to these rules (e.g., `platform` must be one of "twitter", "linkedin", "instagram").
- **Pylance "Import could not be resolved" Errors in VS Code**:
  - If Pylance complains about imports like `from tests.mocks import ...` in `conftest.py`:
    - Ensure you have an empty `__init__.py` file in the `tests/` directory.
    - Alternatively, adjust your VS Code Python interpreter path or `python.analysis.extraPaths` in `settings.json` if needed, though the `sys.path.insert` in `conftest.py` usually handles this for runtime.
- **Rate Limits (429 Errors) from Mistral API**:
  - The `scripts/import_posts.py` and `app/demo.py` include retry logic with exponential backoff for 429 errors. If these persist, you might be exceeding your API plan's limits. Consider adding longer delays or processing fewer items in batch.

## Acknowledgements

- [Mistral AI](https://mistral.ai/) for their powerful language models.
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent API framework.
- [Streamlit](https://streamlit.io/) for the easy-to-use UI library.
- [MongoDB](https://www.mongodb.com/) for the flexible NoSQL database.
- [Docker](https://www.docker.com/) for containerization.
