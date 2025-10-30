# Q-Line: Smart Queue & Appointment System

Q-Line is a dynamic, web-based smart queue and appointment management system designed to eliminate physical waiting lines and streamline the scheduling process for various services. The platform allows end-users to search for services by type and location, view available branches, and book specific time slots online with ease.

This project is containerized with Docker and ready for cloud deployment.

## Key Features

### For Users (Customers)
* **User Authentication**: Secure sign-up and login functionality.
* **Dynamic Service Search**: Find services by type (Clinic, Salon, etc.) and location.
* **Multi-Step Booking**: A seamless flow from selecting a branch to choosing a specific, auto-generated time slot.
* **Real-Time Availability**: View available (green) and booked (red) slots to prevent double-booking.
* **Appointment Management**: View active appointments and a complete history of past (completed/missed) bookings.

### For Staff (Service Providers)
* **Business Registration**: A two-step process to register a new service branch.
* **Staff Dashboard**: An at-a-glance view of today's, upcoming, completed, and missed appointments.
* **Live Queue Management**: Actions to `Serve`, `Skip`, and `Delete` appointments in real-time.
* **Schedule Control**: Manage working hours, add/edit/delete time slot groups, and set holidays.
* **Notifications**: Get notified about new bookings and status changes.

## Technology Stack

* **Backend**: Python, Django
* **Frontend**: HTML, CSS, JavaScript
* **Database**: SQLite 3 (for development)
* **UI Framework**: Bootstrap
* **Deployment**: Docker, Gunicorn, WhiteNoise, Terraform, Google Cloud Platform (GCP)

## Setup & Installation

There are two ways to run this project. The recommended method is using Docker.

### Recommended Setup (Docker)

This is the simplest way to run the application as it's intended for production.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Nithin050/Q-Line.git](https://github.com/Nithin050/Q-Line.git)
    cd Q-Line/qline
    ```
2.  **Ensure Docker Desktop is running.**

3.  **Build the Docker image:**
    ```bash
    docker build -t q-line-app .
    ```
4.  **Run the container:**
    ```bash
    docker run -p 8000:8000 q-line-app
    ```
5.  The application will be available at `http://localhost:8000/main/`.

### Manual/Legacy Setup (For Development)

This method is for running the app without Docker, using a local Python environment.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Nithin050/Q-Line.git](https://github.com/Nithin050/Q-Line.git)
    ```
2.  **Navigate to the project directory:**
    ```bash
    cd Q-Line/qline
    ```
3.  **Create and activate a virtual environment:**
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows, use env\Scripts\activate
    ```
4.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Apply the database migrations:**
    ```bash
    python manage.py migrate
    ```
6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
The application will be available at `http://127.0.0.1:8000/main/`.

## Screenshots

**User Dashboard**
![User Dashboard](user_dashboard.png)

**Booking Page**
![Booking Page](booking_page.png)

**Staff Dashboard**
![Staff Dashboard](staff_dashboard.png)
