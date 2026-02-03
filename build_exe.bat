@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building PyWeatherApp.exe...
python -m PyInstaller --noconsole --onefile --add-data "weather_images;weather_images" --name "PyWeatherApp" weather.py

echo.
echo Build complete! Check the 'dist' folder for PyWeatherApp.exe.
echo Now you can use Inno Setup to compile 'setup_script.iss'.
pause
