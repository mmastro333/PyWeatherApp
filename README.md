# Weather Application

A modern desktop weather assistant built with Python's `customtkinter` and valid requests to Open-Meteo. It features dynamic weather icons, system tray support, auto-refresh, and a sidebar for managing saved cities.

![Screenshot](screenshot.png)

_System Tray View:_
![Tray Screenshot](tray_screenshot.png)
*The application minimizes to the system tray, showing the current temperature and providing detailed info on hover.*

## Features

- **Icon Visualization**: Displays custom weather icons (e.g., sunny, rainy, cloudy) based on real-time conditions.
- **System Tray Support**: Minimizes to the system tray with a dynamic icon showing the current temperature. Hovering over the icon text shows the full city name and conditions.
- **Hourly Auto-Refresh**: Automatically updates weather data in the background every hour (with a random 0-30 minute delay to prevent API congestion).
- **City Management**:
  - **Sidebar List**: Save your favorite cities for quick access.
  - **Click-to-Load**: Instantly check the weather by clicking a saved city.
  - **Easy Removal**: Remove cities from your list with a single click of the "Remove" button.
- **Smart Geocoding**:
  - **Resolved Names**: Automatically updates your input (e.g., "detroit") to the full API-resolved name (e.g., "Detroit, Michigan").
  - **Smart Startup**: The app remembers your last "Saved" city as the default startup location. Merely checking weather does not change your default.
- **Persistent Configuration**: Your saved cities and settings are stored safely in your `%APPDATA%` folder, preserving them across updates and restarts.

## Installation

You can run the application directly from source or compile it into a portable Windows executable/installer.

### Method 1: Windows Installer (Recommended)

This method creates a standard `.exe` installer that can be set to **run automatically when Windows starts**.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/mmastro333/PyWeatherApp.git
    cd PyWeatherApp
    ```
2.  **Build the Executable**:
    -   Double-click the `build_exe.bat` file in the project folder.
    -   This uses `PyInstaller` to create a standalone file in the `dist` folder.
3.  **Generate the Installer**:
    -   Download [Inno Setup](https://jrsoftware.org/isdl.php).
    -   Open `setup_script.iss` with Inno Setup.
    -   Click **Run** (or press F9).
    -   This will generate `Output\PyWeatherApp_Setup_v2.0.exe`.
4.  **Install**:
    -   Run the generated setup file.
    -   Optionally check "Automatically start PyWeatherApp when Windows starts".

### Method 2: Run from Source (Developer)

1.  **Install Python 3.9+**.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the application**:
    ```bash
    python weather.py
    ```

## Usage

1.  **Check Weather**:
    -   Type a city name (e.g., `London` or `Paris, TX`) in the input box.
    -   Click **Check Weather**.
2.  **Manage Cities**:
    -   **Save**: Click **Save City** to store the current location in your sidebar and set it as your default startup city.
    -   **Load**: Click any city name in the sidebar.
    -   **Remove**: Click the red **Remove** button next to a city.
3.  **Minimize to Tray**:
    -   Click the **X** (close) button on the window. The app will keep running in the tray.
    -   **Right-click** the tray icon to **Open** the window or **Quit**.

## Project Structure

-   `weather.py`: Main application logic (GUI, API calls, Tray, Background Threads).
-   `weather_images/`: Directory containing dynamic weather icons.
-   `config.json`: Stored in `%APPDATA%\PyWeatherApp\` (User preferences).
-   `setup_script.iss`: Inno Setup script for creating the Windows installer.
-   `build_exe.bat`: Utility script to compile the Python code to an executable.

## Credits

This application was originally architected and hand-encoded by **Michael Mastrogiacomo**. It has since been expanded and "vibe coded" with the assistance of **Google's AntiGravity**, blending human engineering with advanced agentic AI capabilities.
