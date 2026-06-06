#  SkopjeTransit - Smart Transportation App

A comprehensive Django-based transportation platform designed for Skopje, Macedonia, combining carpooling services with public bus schedules. The app enables users to switch between driver and passenger roles, book rides, access real-time bus information with interactive maps, and chat with an AI assistant powered by Llama 3.3.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation & Requirements](#installation--requirements)
- [Configuration](#configuration)
- [Usage](#usage)
- [AI Assistant](#ai-assistant)
- [Datasets / Static Data](#datasets--static-data)
- [Contributors & Acknowledgments](#contributors--acknowledgments)

##  Project Overview

SkopjeTransit is a smart transportation solution that addresses urban mobility challenges in Skopje by providing:

- **Carpooling Platform**: Connect drivers with passengers for shared rides
- **Public Bus Integration**: Access to JSP's (Javen Skopski Prevoz) bus schedules and routes
- **AI Transit Assistant**: Conversational AI to search rides, check buses, and answer FAQ — all in one chat

The application serves as a bridge between private carpooling and public transportation, offering users flexible mobility options while promoting sustainable transportation practices.

##  Features

### Core Functionality
- **User Registration & Authentication**: Secure account creation with role-based access
- **Dual Role System**: Switch between driver and passenger modes
- **Ride Management**: Create, search, and book rides with custom routes
- **Real-time Status Tracking**: Monitor ride status (pending, confirmed, ongoing, completed)
- **Interactive Maps**: Leaflet integration for visual route planning
- **Payment Processing**: Digital wallet with balance management and a driver/platform fee split
- **Review & Rating System**: 5-star rating system for drivers from passengers
- **Transaction History**: Full transaction log per booking

### Transportation Features
- **Carpool Matching**: Find rides based on start/end locations and departure time
- **Multi-seat Booking**: Book more than one seat in a single booking
- **Bus Schedule Integration**: Access JSP bus routes and schedules stored in the database
- **Stop Management**: Comprehensive database of Skopje bus stops in geographic route order
- **Route Planning**: Multi-stop route support for drivers

### AI Assistant
- **Conversational Interface**: Chat-based assistant powered by Llama 3.3 70B
- **Ride Search & Booking**: Find and book carpool rides through natural conversation
- **Bus Schedule Lookup**: Ask for bus times between any two stops
- **FAQ Answering**: Categorised Q&A items covering booking, payment, safety, and more
- **Stop Disambiguation**: Partial stop names resolved automatically, multiple matches shown as a numbered list
- **Booking Confirmation Card**: Structured booking summary displayed after a successful booking

### User Experience
- **Responsive Design**: Bootstrap-powered mobile-friendly interface
- **Modern UI**: Clean, intuitive design with custom CSS styling
- **Profile Management**: Comprehensive user profiles with ride history and wallet balance
- **Safety Features**: Scam prevention education and safety guidelines

##  Project Structure

```
SkopjeTransit/
├── SkopjeTransit/              # Main Django project configuration
│   ├── settings.py             # Django settings and configuration
│   ├── urls.py                 # Main URL routing
│   ├── wsgi.py / asgi.py       # WSGI / ASGI configuration
├── accounts/                   # User authentication and profiles
│   ├── models.py               # Custom User model (is_driver/is_passenger) + Profile (balance)
│   ├── views.py                # Authentication and profile views
│   ├── forms.py                # User registration forms
│   ├── urls.py                 # Account-related URL patterns
│   ├── signals.py              # Auto-create Profile on user registration
│   ├── management/commands/
│   │   └── add_initial_balance.py
│   └── templates/
│       ├── login.html
│       ├── register.html
│       ├── profile.html
│       └── ride_history.html
├── rides/                      # Core ride management
│   ├── models.py               # Ride, Booking (seats), Stop (order), Bus,
│   │                           #   BusSchedule, Transaction, Review
│   ├── views.py                # Ride creation, booking, start/end, review views
│   ├── forms.py                # Ride and booking forms
│   ├── urls.py                 # Ride-related URL patterns
│   ├── management/commands/
│   │   ├── generate_bus_schedule.py   # Seed all JSP bus data into the DB
│   │   └── update_bus_data.py
│   └── templates/
│       ├── create_ride.html
│       └── book_ride.html
├── core/                       # Main application logic + AI assistant
│   ├── views.py                # Home page, search, and bus/stop data constants
│   ├── views_assistant.py      # AI assistant view with greeting/shortcut logic
│   ├── urls.py                 # Core + assistant URL patterns
│   ├── services/
│   │   ├── agent.py            # LLM agent: tool definitions, dispatch, run_agent()
│   │   └── transit.py          # DB helpers: stop lookup, carpool/bus search, booking
│   ├── data/
│   │   └── faq.json            # 24 FAQ items across 6 categories
│   └── templates/
│       ├── base.html           # Base template with navigation and page-wrapper
│       ├── home.html           # Home page with search form
│       ├── ride_results.html   # Search results with maps
│       ├── scam_safety.html    # Safety information page
│       └── core/
│           └── assistant.html  # AI assistant chat UI
├── static/
│   └── photos/                 # Application images and logo
├── scripts/
│   ├── setup_database.py       # Database initialisation helper
│   └── update_bus_data_script.py
├── requirements.txt            # Pinned Python dependencies
├── manage.py
└── db.sqlite3                  # SQLite database (development)
```

### Key Components

- **accounts/**: User authentication, profiles, role management, and wallet balance
- **rides/**: Ride creation, booking, start/end lifecycle, payments, and reviews
- **core/**: Home page, search, AI assistant view, and transit/agent services
- **core/services/**: Database-backed transit queries (`transit.py`) and LLM agent loop (`agent.py`)
- **core/data/faq.json**: FAQ knowledge base consumed by the assistant

##  Installation & Requirements

### Prerequisites

- **Python**: 3.10 or higher
- **An OpenRouter API key** (for the AI assistant) — sign up at https://openrouter.ai

### Install Dependencies

```bash
git clone <repository-url>
cd SkopjeTransit

python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Step-by-Step Setup

1. **Create a `.env` file** in the project root (next to `manage.py`):
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

2. **Run Database Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Seed Bus Data**
   ```bash
   python manage.py generate_bus_schedule
   ```

4. **Create Superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

6. **Access the Application**
   - Main app: `http://127.0.0.1:8000/`
   - AI assistant: `http://127.0.0.1:8000/assistant/`
   - Admin panel: `http://127.0.0.1:8000/admin/`

##  Configuration

All sensitive configuration is loaded from a `.env` file via `python-dotenv`. The two supported keys are:

| Variable | Purpose |
|---|---|
| `OPENROUTER_API_KEY` | Required for the AI assistant (Llama 3.3 via OpenRouter) |
| `GEMINI_API_KEY` | Reserved for future use |

If `OPENROUTER_API_KEY` is not set, the assistant view will still load but LLM calls will fail.

##  Usage

### User Registration and Login

1. Navigate to `/accounts/register/` and fill in your details
2. Log in at `/accounts/login/`
3. Use "Switch Role" in the navigation to toggle between driver and passenger modes

### For Drivers

1. **Create a Ride** — Switch to driver mode, click "Create Ride" (`/rides/create/`)
   - Set start and end locations, departure time, available seats, seat price, and optional intermediate stops
2. **Manage Rides** — View pending bookings in your profile; confirm and start rides
3. **Start / End Ride** — Mark rides as ongoing and complete them; payment is processed automatically on completion

### For Passengers

1. **Search for Rides** — Use the home page search form (start location, destination, date/time)
2. **Book a Ride** — Select a ride from results, choose your pickup stop and number of seats, confirm
3. **Manage Bookings** — View all bookings in your profile; submit reviews after completion

### Bus Schedule

1. Search results include matching JSP bus lines alongside carpool options
2. Interactive Leaflet map shows stops and bus routes
3. Or ask the AI assistant: "What buses go from Vlae to Centar?"

##  AI Assistant

The assistant lives at `/assistant/` and is powered by **Llama 3.3 70B** via OpenRouter.

### Capabilities

| What to ask | Example |
|---|---|
| Find a carpool | "Find me a ride from Aerodrom to City Park tomorrow at 5pm" |
| Book a carpool | After a ride is shown, "Book 2 seats" → confirm |
| Check bus schedule | "What buses run from Vlae to Centar?" |
| Browse the FAQ | "Do you have an FAQ?" |
| Ask a specific question | "How do I cancel a booking?" |

### How It Works

1. **Short-circuit layer** (`views_assistant.py`) — Greetings, goodbyes, and vague booking requests ("book me a ride") are handled with canned replies before reaching the LLM.
2. **LLM agent loop** (`core/services/agent.py`) — Sends the conversation to Llama 3.3 with four tool definitions: `search_rides`, `book_ride`, `get_bus_schedule`, `answer_faq`.
3. **Transit service** (`core/services/transit.py`) — Executes the actual database queries for stop lookup, carpool search, bus schedule lookup, and booking creation.
4. **Session history** — The last 30 messages are stored in the Django session so the conversation persists across page reloads.

### Tools Available to the Agent

| Tool | Description |
|---|---|
| `search_rides` | Find carpool rides; falls back to bus suggestions if none found |
| `book_ride` | Create a `Booking` record after user confirmation |
| `get_bus_schedule` | Find direct buses between two stops |
| `answer_faq` | Answer questions from `core/data/faq.json` using fuzzy matching |

##  Datasets / Static Data

### JSP Bus Data

Bus data is stored in the database and seeded via the `generate_bus_schedule` management command:

- **Bus Routes**: Multiple JSP lines (2, 4, 7, 15, 19, 22, 24, 60 and their return directions)
- **Bus Stops**: 50+ stops across Skopje with GPS coordinates (used for the interactive map)
- **Schedule Times**: Estimated arrival times (not real-time)
- **Stop Order**: Each stop has an `order` field preserving geographic route order

GPS coordinates for the map are defined in `core/views.py`:

```python
STOP_COORDINATES = {
    "Gjorce Petrov Polyclinic": (42.009960610861896, 21.362986632943255),
    # ...
}
```

### FAQ Knowledge Base

`core/data/faq.json` contains 24 Q&A pairs across six categories:

- Booking & Cancellations
- Payment & Pricing
- Safety
- For Drivers
- Bus Schedules
- Support

### Data Disclaimer

**Important:** JSP bus schedule data is static and estimated. For production use, integrate with real-time APIs from JSP or another transportation authority.

##  Contributors & Acknowledgments

This project was developed for the course **Human Computer Interaction and Design** (DNICK) at the Faculty of Computer Science and Engineering (FINKI), Ss. Cyril and Methodius University, Skopje, Macedonia.

### Development Team
- **Stefan Lazarevski**
- **Ana Marija Kraus**

### Mentor
- **Vlatko Spasev**
- **Ivan Kitanovski PhD**

### External Libraries & Frameworks
- **Django**: Web framework (https://djangoproject.com/)
- **Bootstrap**: CSS framework (https://getbootstrap.com/)
- **Leaflet**: Interactive maps (https://leafletjs.com/)
- **OpenStreetMap**: Map tiles (https://www.openstreetmap.org/)
- **OpenRouter / Llama 3.3**: AI inference (https://openrouter.ai/)
- **OpenAI Python SDK**: Used as the OpenRouter client

---
