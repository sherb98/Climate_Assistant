# Climate Assistant

## Overview of the Project
<a href="https://www.youtube.com/watch?v=B2lVwIztorY=Vid_1
" target="_blank"><img src="https://github.com/sherb98/Climate_Assistant/assets/96775603/dc5c8b29-9470-4753-a1c1-fcb42d230758"
alt="Climate Assistant Video" width="400" height="250" border="10" /></a>  
Click image above for video (https://www.youtube.com/watch?v=B2lVwIztorY)

Climate Assistant is a tool designed for use in the early stages of building design, catering to architects and individuals planning to build or renovate a property. Its user-friendly interface requires just three inputs: a weather file, the type of building (be it office or residential), and the orientation of windows (North, East, South, or West). Utilizing these inputs, Climate Assistant evaluates whether it is likely that air conditioning is needed. It also helps to identify the most effective climate-responsive measures to either negate the necessity of an A/C unit or to minimize its energy consumption. The program runs annual Energy Plus simulations in the background, employing the 'Predicted Mean Vote' (PMV) metric to assess if the building is too hot.

![image](https://github.com/sherb98/Climate_Assistant/assets/96775603/1b5e15ee-8f7d-4f85-8b51-b771e8540bbe)



## Dependencies 

### Python Libraries
Written in python 3.11
Libraries used:
- **flask**
  - `pip install flask`
- **pandas**
  - `pip install pandas`
- **pythermalcomfort**
  - `pip install pythermalcomfort`
- **matplotlib**
  - `pip install matplotlib`
- **eppy**
  - `pip install eppy`

### Installing EnergyPlus
Install EnergyPlus (Version 22.2) from: [EnergyPlus Downloads](https://energyplus.net/downloads)

![image](https://github.com/sherb98/Climate_Assistant/assets/96775603/7d43bb21-51a7-4f4e-bb5d-44309bc5679c)

### Set the idd File Variable
In `SimManagement.py`, set the `iddfile` variable to the path where the EnergyPlus IDD file is located, similar to below: 
```python
iddfile="C:\\EnergyPlusV22-2-0\\Energy+.idd"
```

## Running the Program

### Downloading EPW Weather Data
As shown in the Video, weather data has to be in the *.epw format can can be downloaded here: https://energyplus.net/weather

### Steps
It is important that the application is run in within the folder structure downloaded from the repository.
1. In VS Code open the project and in the terminal, type “python Climate_Assistant.py” and wait for the connection to be established.
2. In the browser type in the URL bar: http://localhost:3000/
3. Upload the epw weather file and set the other two variables.
4. Hit “submit”.
5. In VS code you should see the simulations running in the terminal in the browser, the http://localhost:3000/submit page is loading (this can take up to 2 minutes, if the simulation has not been conducted before; if the simulation has been conducted before (same epw file, building type and window orientation), the result should pop up right away).
6. Look at the results!
7. If you want to start over, just enter http://localhost:3000/ in the URL bar again.

## Folder/File Explanations
A quick overview of the projects folder structure:
- **Simulations**: This is the folder where the EnergyPlus Simulations are being run in, its contents are deleted after each run. Make sure none of the files in the folder are open when using the application.
- **static**: The png of the result bar chart is being saved here.
- **templates**: The HTML templates are located here.
- **Weather**: The epw files provided by the user are being saved into this folder.

- **Office_totalBaseline.idf**: This is the template that is used as the basis for all the office simulations. Profiles and internal heat gains are based on the SIA, Merkblatt 2024.
- **Residential_totalBaseline.idf**: This is the template that is used as the basis for all the residential simulations. Profiles and internal heat gains are based on the SIA, Merkblatt 2024.
