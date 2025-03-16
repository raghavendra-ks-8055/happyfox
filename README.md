# Email Rules Engine

A production-grade email rules engine that allows users to create and manage rules for processing emails, similar to Apple Mail's rules functionality.

## Table of Contents

1. [Features](#features)
2. [Quick Start](#quick-start)
   - [Using Docker](#using-docker-recommended)
   - [Using Poetry](#using-poetry)
3. [API Documentation](#api-documentation)
4. [Gmail API Integration](#gmail-api-integration)
5. [Project Structure](#project-structure)
6. [Architecture](#architecture)
7. [Usage Examples](#usage-examples)
8. [Rule Configuration](#rule-configuration)
9. [Testing](#testing)
10. [Development](#development)
11. [License](#license)

## Features

- Define rules with conditions based on email fields (From, Subject, Message, Received Date/Time)
- Support for different predicates (Contains, Does not Contain, Equals, Does not Equal)
- Date-specific predicates (Less than, Greater than) for days/months
- Actions including "Mark as read/unread" and "Move Message"
- Support for "All" and "Any" condition matching logic
- RESTful API for rule management
- Gmail API integration for fetching and processing real emails

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd email-rules-engine
   ```

2. **Start the application**
   ```bash
   make docker-up
   ```

3. **Access the application**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs

4. **Managing Docker containers**
   ```bash
   # Stop the application
   make docker-down

   # Stop the application and remove volumes
   make docker-down-v

   # View logs
   make docker-logs

   # Rebuild containers
   make docker-build
   ```

### Using Poetry

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd email-rules-engine
   ```

2. **Install dependencies**
   ```bash
   make install
   ```

3. **Run the application**
   ```bash
   make run
   ```

4. **Access the application**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs

## API Documentation

### Accessing Swagger UI

The API documentation is available through:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key API Endpoints

| Category | Endpoint | Method | Description |
|----------|----------|--------|-------------|
| **Rules** | `/api/rules` | GET | List all rules |
| | `/api/rules` | POST | Create a new rule |
| | `/api/rules/{rule_id}` | GET | Get a specific rule |
| | `/api/rules/{rule_id}` | PUT | Update a rule |
| | `/api/rules/{rule_id}` | DELETE | Delete a rule |
| **Email Processing** | `/api/process-email` | POST | Process an email against all rules |
| **Gmail Integration** | `/api/gmail/authorize` | GET | Start Gmail OAuth flow |
| | `/api/gmail/callback` | GET | OAuth callback handler |
| | `/api/gmail/fetch` | GET | Fetch emails from Gmail |
| | `/api/gmail/process` | POST | Process fetched emails against rules |
| | `/api/gmail/results` | GET | View processing results |

## Gmail API Integration

### Setting Up Gmail API

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it

2. **Configure OAuth Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Web application" as the application type
   - Set a name for your OAuth client
   - Add authorized redirect URIs:
     - `http://localhost:8000/api/gmail/callback` (for local development)
     - Add your production URLs if deploying to production
   - Click "Create" and download the credentials JSON file

3. **Configure the Application**
   - Rename the downloaded file to `credentials.json`
   - Place it in the project root directory or configure the path in `.env`:

   ```bash
   # Example .env configuration
   GOOGLE_CREDENTIALS_FILE=path/to/credentials.json
   GOOGLE_TOKEN_FILE=path/to/token.json
   ```

### Authorizing the Application

1. **Start the application** (if not already running)
   ```bash
   # Using Docker
   make docker-up
   
   # Or using Poetry
   make run
   ```

2. **Initiate OAuth flow**
   - Visit `http://localhost:8000/api/gmail/authorize` in your browser
   - You'll be redirected to Google's OAuth consent screen

3. **Grant permissions**
   - Select the Google account you want to use
   - Review and accept the requested permissions
   - After authorization, you'll be redirected back to the application

4. **Verify authorization**
   - The application will store the OAuth token
   - You should see a success message in the browser

### Testing with Gmail

Once authorized, you can interact with Gmail using the following endpoints:

1. **Fetch emails**
   ```bash
   # Fetch the 10 most recent emails
   curl -X GET "http://localhost:8000/api/gmail/fetch?max_results=10"
   
   # Fetch emails with a specific query
   curl -X GET "http://localhost:8000/api/gmail/fetch?query=from:example.com&max_results=5"
   ```

2. **Process fetched emails against rules**
   ```bash
   # Process all fetched emails
   curl -X POST "http://localhost:8000/api/gmail/process"
   
   # Process emails with specific IDs
   curl -X POST "http://localhost:8000/api/gmail/process" \
     -H "Content-Type: application/json" \
     -d '{"email_ids": ["id1", "id2"]}'
   ```

3. **View processing results**
   ```bash
   # View all results
   curl -X GET "http://localhost:8000/api/gmail/results"
   
   # View results for specific emails
   curl -X GET "http://localhost:8000/api/gmail/results?email_ids=id1,id2"
   ```

## Project Structure

```
email-rules-engine/
├── app/                    # Application code
│   ├── api/                # API endpoints
│   │   └── routes.py       # API route definitions
│   ├── core/               # Core business logic
│   │   ├── config.py       # Application configuration
│   │   ├── database.py     # Database connection setup
│   │   └── rule_engine.py  # Rule processing engine
│   ├── models/             # Data models
│   │   ├── email.py        # Email model
│   │   └── rule.py         # Rule, Condition, Action models
│   ├── schemas/            # Pydantic schemas
│   │   ├── email.py        # Email schemas
│   │   └── rule.py         # Rule schemas
│   ├── services/           # Business services
│   │   ├── email.py        # Email service
│   │   ├── gmail_service.py # Gmail integration service
│   │   └── rule.py         # Rule service
│   └── version.py          # Version management
├── tests/                  # Test suite
│   ├── integration/        # Integration tests
│   └── unit/               # Unit tests
├── migrations/             # Alembic migrations
├── pyproject.toml          # Poetry configuration and project metadata
├── Makefile                # Common development tasks
└── README.md               # Project documentation
```

## Architecture

The Email Rules Engine follows a clean architecture pattern with the following components:

### Core Components

1. **Rule Engine**: The central component that evaluates rules against emails and determines which actions to apply.
2. **Data Models**: SQLAlchemy models representing rules, conditions, actions, and emails.
3. **API Layer**: FastAPI routes that expose the functionality as RESTful endpoints.
4. **Services**: Business logic for interacting with rules, emails, and external services like Gmail.

### Data Flow

1. Emails are fetched from Gmail via API
2. Emails are stored in the database
3. Rules are applied to emails
4. Actions are determined based on rule matches
5. Actions can be executed (mark as read/unread, move message)

## Usage Examples

### Creating a Rule

```bash
curl -X POST "http://localhost:8000/api/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Interview Emails",
    "match_type": "all",
    "conditions": [
      {
        "field": "from",
        "predicate": "contains",
        "value": "tenmiles.com"
      },
      {
        "field": "subject",
        "predicate": "contains",
        "value": "Interview"
      }
    ],
    "actions": [
      {
        "type": "mark_as_read"
      }
    ]
  }'
```

### Testing a Rule with an Email

```bash
curl -X POST "http://localhost:8000/api/process-email" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "recruiter@tenmiles.com",
    "subject": "Interview Schedule",
    "message": "We would like to schedule an interview with you.",
    "received_date": "2023-11-15T14:30:00"
  }'
```

## Rule Configuration

### Rule Conditions

Rules can use the following conditions:

| Field | Predicates | Example |
|-------|------------|---------|
| from | contains, does_not_contain, equals, does_not_equal | "from": "gmail.com" |
| subject | contains, does_not_contain, equals, does_not_equal | "subject": "Important" |
| message | contains, does_not_contain | "message": "meeting" |
| received_date | less_than, greater_than | "received_date": "2", "unit": "days" |

### Rule Actions

Available actions:

| Action | Parameters | Description |
|--------|------------|-------------|
| mark_as_read | none | Mark the email as read |
| mark_as_unread | none | Mark the email as unread |
| move_message | target (folder name) | Move the email to a folder |

### Example Test Cases

#### Test Case 1: All Conditions Match

```json
{
  "from": "recruiter@tenmiles.com",
  "subject": "Interview Schedule",
  "message": "We would like to schedule an interview with you.",
  "received_date": "2023-11-15T14:30:00"
}
```

Expected result: All actions are returned.

#### Test Case 2: One Condition Doesn't Match (Wrong Sender)

```json
{
  "from": "recruiter@example.com",
  "subject": "Interview Schedule",
  "message": "We would like to schedule an interview with you.",
  "received_date": "2023-11-15T14:30:00"
}
```

Expected result: Empty array (no actions) for "all" match type.

#### Test Case 3: Testing "Any" Match Type

First, create a rule with "any" match type:

```bash
curl -X POST "http://localhost:8000/api/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Any Match Rule",
    "match_type": "any",
    "conditions": [
      {
        "field": "from",
        "predicate": "contains",
        "value": "tenmiles.com"
      },
      {
        "field": "subject",
        "predicate": "contains",
        "value": "Urgent"
      }
    ],
    "actions": [
      {
        "type": "mark_as_read"
      }
    ]
  }'
```

Then test with an email that matches only one condition:

```json
{
  "from": "someone@example.com",
  "subject": "Urgent: Please respond",
  "message": "This is an urgent message.",
  "received_date": "2023-11-15T14:30:00"
}
```

Expected result: The action is returned because at least one condition matches.

## Testing

The project includes comprehensive test coverage with both unit and integration tests.

### Running Tests

1. **Run all tests**
   ```bash
   make test
   ```

2. **Run unit tests only**
   ```bash
   poetry run pytest tests/unit
   ```

3. **Run integration tests only**
   ```bash
   poetry run pytest tests/integration
   ```

4. **Run with coverage report**
   ```bash
   poetry run pytest --cov=app tests/
   ```

## Development

### Common Tasks

1. **Install dependencies**
   ```bash
   make install
   ```

2. **Run the application**
   ```bash
   make run
   ```

3. **Code quality**
   ```bash
   # Format code
   make format

   # Run linting
   make lint
   ```

4. **Database management**
   ```bash
   # Generate migration
   make migration message="your migration message"

   # Apply migrations
   make migrate
   ```

5. **Docker operations**
   ```bash
   # Build Docker images
   make docker-build

   # Start containers
   make docker-up

   # Stop containers
   make docker-down
   ```

## License

[MIT License](LICENSE)
