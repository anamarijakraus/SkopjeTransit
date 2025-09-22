#  SkopjeTransit - Smart Transportation App

A comprehensive Django-based transportation platform designed for Skopje, Macedonia, combining carpooling services with public bus schedules. The app enables users to switch between driver and passenger roles, book rides, and access real-time bus information with interactive maps.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation & Requirements](#installation--requirements)
- [Usage](#usage)
- [Datasets / Static Data](#datasets--static-data)
- [Contributors & Acknowledgments](#contributors--acknowledgments)

##  Project Overview

SkopjeTransit is a smart transportation solution that addresses urban mobility challenges in Skopje by providing:

- **Carpooling Platform**: Connect drivers with passengers for shared rides
- **Public Bus Integration**: Access to JSP's (Javen Skopski Prevoz) bus schedules and routes

The application serves as a bridge between private carpooling and public transportation, offering users flexible mobility options while promoting sustainable transportation practices.

##  Features

### Core Functionality
- **User Registration & Authentication**: Secure account creation with role-based access
- **Dual Role System**: Switch between driver and passenger modes
- **Ride Management**: Create, search, and book rides with custom routes
- **Real-time Status Tracking**: Monitor ride status (pending, confirmed, ongoing, completed)
- **Interactive Maps**: Leaflet integration for visual route planning
- **Payment Processing**: Digital wallet with balance management
- **Review & Rating System**: 5-star rating system for drivers from passengers

### Transportation Features
- **Carpool Matching**: Find rides based on start/end locations and departure time
- **Bus Schedule Integration**: Access JSP bus routes and schedules
- **Stop Management**: Comprehensive database of Skopje bus stops
- **Route Planning**: Multi-stop route support for drivers
- **Seat Management**: Track available seats and booking capacity

### User Experience
- **Responsive Design**: Bootstrap-powered mobile-friendly interface
- **Modern UI**: Clean, intuitive design with custom CSS styling
- **Profile Management**: Comprehensive user profiles with ride history
- **Safety Features**: Scam prevention education and safety guidelines

##  Project Structure

```
SkopjeTransit/
├── SkopjeTransit/              # Main Django project configuration
│   ├── __init__.py
│   ├── settings.py             # Django settings and configuration
│   ├── urls.py                 # Main URL routing
│   ├── wsgi.py                 # WSGI configuration
│   └── asgi.py                 # ASGI configuration
├── accounts/                   # User authentication and profiles
│   ├── models.py               # Custom User model and Profile
│   ├── views.py                # Authentication and profile views
│   ├── forms.py                # User registration forms
│   ├── urls.py                 # Account-related URL patterns
│   ├── admin.py                # Django admin configuration
│   ├── signals.py              # User profile creation signals
│   ├── templates/              # Account-related templates
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html
│   │   └── ride_history.html
│   └── migrations/             # Database migrations
├── rides/                      # Core ride management
│   ├── models.py               # Ride, Booking, Stop, Bus models
│   ├── views.py                # Ride creation and booking views
│   ├── forms.py                # Ride and booking forms
│   ├── urls.py                 # Ride-related URL patterns
│   ├── admin.py                # Django admin for rides
│   ├── templates/              # Ride-related templates
│   │   ├── create_ride.html
│   │   └── book_ride.html
│   ├── management/             # Custom Django commands
│   │   └── commands/
│   │       ├── generate_bus_schedule.py
│   │       └── update_bus_data.py
│   └── migrations/             # Database migrations
├── core/                       # Main application logic
│   ├── models.py               
│   ├── views.py                # Home page and search functionality
│   ├── urls.py                 # Core URL patterns
│   ├── admin.py                # Core admin configuration
│   └── templates/              # Main templates
│       ├── base.html           # Base template with navigation
│       ├── home.html           # Home page with search
│       ├── ride_results.html   # Search results with maps
│       └── scam_safety.html    # Safety information page
├── static/                     # Static files
│   └── photos/                 # Application images
│       ├── logo.png
│       ├── driver-community.jpg
│       ├── above_scam_image.png
│       ├── scam-safety.png
│       └── right_part_of_navbar.png
├── db.sqlite3                  # SQLite database (development)
├── manage.py                   # Django management script
├── setup_database.py           # Database initialization script
└── update_bus_data_script.py   # Bus data update utility
```

### Key Components

- **accounts/**: Handles user authentication, profiles, and role management
- **rides/**: Core functionality for ride creation, booking, and management
- **core/**: Main application logic, home page, and search functionality
- **templates/**: HTML templates with Bootstrap styling

##  Installation & Requirements

### Prerequisites

- **Python**: 3.8 or higher
- **Django**: 5.2.3

### Required Python Packages

```bash
Django==5.2.3
django-crispy-forms==2.0
Pillow==10.0.0
```

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd SkopjeTransit
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install Django==5.2.3
   pip install django-crispy-forms==2.0
   pip install Pillow==10.0.0
   ```

4. **Run Database Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Superuser (Optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Initialize Bus Data**
   ```bash
   python manage.py generate_bus_schedule
   ```

7. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Access the Application**
   - Open your browser and navigate to `http://127.0.0.1:8000/`
   - Admin panel available at `http://127.0.0.1:8000/admin/`


##  Usage

### User Registration and Login

1. **Register a New Account**
   - Navigate to `/accounts/register/`
   - Fill in username, email, and password
   - Account is created with passenger role by default

2. **Login**
   - Go to `/accounts/login/`
   - Enter credentials to access your account

3. **Switch Roles**
   - Use the "Switch Role" button in the navigation
   - Toggle between driver and passenger modes

### For Drivers

1. **Create a Ride**
   - Switch to driver role
   - Click "Create Ride" or navigate to `/rides/create/`
   - Fill in ride details:
     - Start and end locations
     - Departure time
     - Available seats
     - Seat price
     - Intermediate stops (optional)

2. **Manage Rides**
   - View current rides in your profile
   - Confirm pending bookings
   - Track ride status and earnings

### For Passengers

1. **Search for Rides**
   - Use the home page search form
   - Enter start location, destination, and departure time
   - View available rides and bus options

2. **Book a Ride**
   - Click on a ride from search results
   - Select pickup stop
   - Confirm booking

3. **Manage Bookings**
   - View confirmed, pending, and ongoing rides
   - Start and end rides
   - Submit reviews and ratings

### Bus Schedule Integration

1. **View Bus Routes**
   - Search results include JSP bus options
   - Interactive map shows bus stops and routes
   - Real-time schedule information

2. **Interactive Maps**
   - Leaflet-powered maps
   - Click on bus stops for route information
   - Visual representation of transportation options

##  Datasets / Static Data

### JSP Bus Data

The application includes hardcoded data for JSP (Javen Skopski Prevoz) buses:

- **Bus Routes**: 7 different bus lines (2, 4, 7, 15, 19, 22, 24, 60)
- **Bus Stops**: 50+ stops across Skopje with GPS coordinates
- **Schedule Times**: Estimated arrival times (not real-time)

### Static Data Location

Bus data is stored in `core/views.py`:

```python
STOP_COORDINATES = {
    "Gjorce Petrov Polyclinic": (42.009960610861896, 21.362986632943255),
    # ... more stops
}

BUS_STOPS = {
    '2': ["Gjorce Petrov Cinema", "Gjorce Petrov Old Market", ...],
    '4': ["Gjorce Petrov Cinema", "Gjorce Petrov Old Market", ...],
    # ... more routes
}
```

### Data Disclaimer

 **Important:** The JSP bus data is static and estimated. For production use, integrate with real-time APIs from JSP or other transportation authorities.


##  Contributors & Acknowledgments

This project was developed for the course **Human Computer Interaction and Design** (DNICK) at the Faculty of Computer Science and Engineering (FINKI), Ss. Cyril and Methodius University, Skopje, Macedonia.


### Development Team
- **Stefan Lazarevski**
- **Ana Marija Kraus**

### Mentor
- **Vlatko Spasev**

### External Libraries & Frameworks
- **Django**: Web framework (https://djangoproject.com/)
- **Bootstrap**: CSS framework (https://getbootstrap.com/)
- **Leaflet**: Interactive maps (https://leafletjs.com/)
- **OpenStreetMap**: Map tiles (https://www.openstreetmap.org/)

---

