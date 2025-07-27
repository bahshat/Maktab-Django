# Project: fees_manager

## Overview
This is a Django-based fees management application designed primarily for mobile use. It allows for student admission, tracking of fees (pending and due soon), and provides a dashboard with analytics. The UI is optimized for mobile devices with a dark theme, vibrant accents, and a fixed bottom navigation bar.

## Project Structure
- **Project Name:** `fees_manager`
- **App Name:** `students`

## Database Details (`students/models.py`)
The application uses a single model: `Student`.
- **`Student` Model Fields:**
    - `roll_number`: `SmallAutoField` (Primary Key, Auto-incrementing). This field is automatically generated upon admission and is not user-editable.
    - `name`: `CharField` (max_length=100) - Student's full name.
    - `phone_number`: `BigIntegerField` - Student's contact phone number.
    - `student_class`: `SmallIntegerField` - Student's class (e.g., 1-12).
    - `address`: `CharField` (max_length=255, blank=True) - Student's residential address.
    - `paid_till_date`: `DateField` (null=True, blank=True) - The date until which the student's fees are paid. If `None` or in the past, fees are considered pending.
    - `fees_period`: `CharField` (max_length=20, choices, default='quarterly') - Defines the billing cycle for the student's fees.
        - Choices: 'monthly', 'quarterly', 'half_yearly', 'yearly'.
        - Default: 'quarterly'.

## Routes (URLs)

### `fees_manager/urls.py`
- `path('admin/', admin.site.urls)`: Django admin interface.
- `path('', include('students.urls'))`: Includes all URLs from the `students` app at the root path.

### `students/urls.py`
- `path('search/', views.search_student, name='search_student')`: Main entry point for searching students by roll number.
- `path('admission/', views.add_student, name='add_student')`: Page for admitting new students. (Note: URL changed from 'add/' to 'admission/').
- `path('student/<int:roll_number>/', views.student_detail, name='student_detail')`: Displays and allows updates to a specific student's details.
- `path('pending/', views.pending_fees_list, name='pending_fees_list')`: Lists students with overdue fees.
- `path('due_soon/', views.due_soon_fees_list, name='due_soon_fees_list')`: Lists students whose fees are due within the next 7 days.
- `path('dashboard/', views.dashboard, name='dashboard')`: Provides analytics and a fees status distribution chart.

## Views (`students/views.py`)

- **`MONTHLY_FEE = 400`**: A constant defining the base monthly fee for all students.
- **`calculate_pending_periods(student, current_date)`**:
    - **Purpose:** Calculates the number of pending fee periods for a given student up to `current_date`.
    - **Logic:**
        - If `paid_till_date` is `None`, fees are pending from January 1st of the `current_date`'s year.
        - If `paid_till_date` is in the past, pending periods are calculated from that date up to `current_date`.
        - If `paid_till_date` is today or in the future, 0 pending periods are returned.
        - Uses ceiling division to count partial periods as full pending periods based on `fees_period` (monthly, quarterly, half-yearly, yearly).
    - **Returns:** `(pending_periods, months_per_period)` tuple.

- **`search_student(request)`**:
    - Handles GET/POST requests for searching students by `roll_number`.
    - Uses `SearchForm` for input validation.
    - Redirects to `student_detail` if found, otherwise displays "Student not found." message.

- **`add_student(request)`**:
    - Handles GET/POST requests for admitting new students.
    - Uses `StudentForm` for data input.
    - `roll_number` is automatically assigned by the database.

- **`student_detail(request, roll_number)`**:
    - Displays a student's details.
    - Allows updating `paid_till_date` via a POST request.

- **`pending_fees_list(request)`**:
    - Filters students where `paid_till_date` is in the past or `None`.
    - Iterates through these students, calls `calculate_pending_periods` to determine `pending_periods` and `pending_amount`.
    - Passes a list of dictionaries (containing student object, pending amount, pending periods) to the template.
    - Includes a WhatsApp button for each student with a pre-filled message detailing pending fees.

- **`due_soon_fees_list(request)`**:
    - Filters students whose `paid_till_date` is today or within the next 7 days.
    - Passes these students to the template.
    - Includes a WhatsApp button for each student with a pre-filled message about upcoming due fees.

- **`dashboard(request)`**:
    - Calculates `total_students`, `pending_students_count`, `due_soon_students_count`, and `paid_up_students_count`.
    - Prepares data for a Chart.js donut chart to visualize fees status distribution.

## Forms (`students/forms.py`)

- **`StudentForm`**:
    - A `ModelForm` for the `Student` model.
    - `roll_number` is `excluded` as it's auto-generated.
    - `paid_till_date` uses a `DateInput` widget with `type='date'` for a calendar picker.

- **`SearchForm`**:
    - A simple `Form` with a single `IntegerField` for `roll_number` input.

## Templates (`students/templates/students/`)
All templates follow a consistent dark theme inspired by the Behance design, with Roboto font, Font Awesome icons, rounded corners, and a fixed bottom navigation bar.

- **`search_student.html`**: Search input for roll number, links to other sections.
- **`add_student.html`**: Form for new student admission.
- **`student_detail.html`**: Displays student info, form to update `paid_till_date`.
- **`pending_fees_list.html`**: Lists pending students with calculated fees and WhatsApp buttons.
- **`due_soon_fees_list.html`**: Lists students with fees due soon and WhatsApp buttons.
- **`dashboard.html`**: Displays analytics cards in a 2x2 grid and a Chart.js donut chart for fees status distribution.

## Key Configurations (`fees_manager/settings.py`)
- **`ALLOWED_HOSTS = ['*']`**: Set for development/local network testing. **MUST be changed for production.**
- **`TIME_ZONE = 'Asia/Kolkata'`**: Configures Django to use India Standard Time for all timezone-aware operations.
- **`USE_TZ = True`**: Enables Django's timezone support.
- **Database:** Uses default SQLite.

## How to Run the Application

1.  **Navigate to the project root directory:**
    ```bash
    cd /home/rais/Desktop/Maktab-Django
    ```
2.  **Ensure virtual environment is set up and Django is installed:**
    ```bash
    python -m venv venv
    ./venv/bin/python -m pip install django
    ```
3.  **Apply database migrations:**
    ```bash
    ./venv/bin/python manage.py makemigrations
    ./venv/bin/python manage.py migrate
    ```
4.  **Populate with sample data (optional, but recommended for testing):**
    ```bash
    ./venv/bin/python manage.py populate_students
    ```
5.  **Run the development server (for access on the same network):**
    ```bash
    ./venv/bin/python manage.py runserver 0.0.0.0:8000
    ```
    - To access from other devices on the same network, find your computer's IP address (e.g., `ip a` on Linux/macOS, `ipconfig` on Windows) and navigate to `http://YOUR_IP_ADDRESS:8000/` in your browser.

## Debugging Notes
- If Chart.js text (legend, title) on the Dashboard is black, it's likely a browser caching issue. Clear your browser's cache thoroughly.
- If `paid_till_date` logic seems off, verify your system's date and time, and ensure `TIME_ZONE` is correctly set in `settings.py`. Re-running `populate_students` after changing timezone settings is recommended.
