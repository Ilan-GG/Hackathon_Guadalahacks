# Satellite Viewer for Spatial Inspection 🌍

**Sponsored by HERE Technologies**

This repository contains a geospatial data validation system developed for HERE Technologies company during the **Guadalahacks Hackathon**. The project focuses on automating quality assurance for Points of Interest (POI) data by validating their positional accuracy and attributes against HERE’s street network and satellite imagery.

## 📌 Project Description

The project focuses on:
- **POI Validation**:
Applies a series of deterministic validation rules (e.g., distance from interpolated point, street name mismatches, side orientation issues) to automatically flag POIs with potential violations and assign explanatory scenarios.
- **Satellite Imagery Analysis**: Detecting structures around POIs to validate their existence using a Machine Learning Model
- **Data Classification**: Categorizing POIs into scenarios based on positional accuracy and naming consistency
- **Duplicate Detection**: Identifying and reporting duplicate POI entries.
- **Real-Time Feedback**: Generating files from analysis.

Key technologies used:
- Geospatial processing with Turf.js and GeoJSON
- Satellite imagery analysis with OpenCV
- Excel report generation
- HERE Maps API for tile fetching

## 🛠 Technologies Used

- **Core**: 
  - Node.js (JavaScript) 
  - Python (for image analysis)
- **Geospatial**: 
  - Turf.js 
  - GeoJSON 
  - Shapely (Python)
- **Image Processing**: 
  - OpenCV 
  - scipy.spatial
- **Data Handling**: 
  - Pandas (Python) 
  - XLSX (Excel export)
- **APIs**: 
  - HERE Maps API
    
  ## 🚀 Installation & Usage

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Ilan-GG/Hackathon_Guadalahacks.git
   cd Hackathon_Guadalahacks
2. **Install dependencies**:
   ```bash
   npm install turf xlsx
   pip install opencv-python scipy pandas geopandas
4. **Configure the API Keys**:
   Add your HERE Maps API key in satellite_imagery_tile_request.py
6. **Run the pipeline**:
   ```bash
   node classifyPOIs.js
   node data.js  

## 📊 Key Features
1. **POI Classification**

- **Scenario 1**: No POI in reality 
- **Scenario 2**: Incorrect POI position
- **Scenario 3**: Incorrect Multiply Digitised attribution
- **Scenario 4**: Valid POI

2. **Satellite Analysis**

- Detects structures on both sides of roads  
- Validates POI existence based on imagery  

3. **Duplicate Detection**

- Identifies POIs with identical coordinates/names  
- Exports duplicates to CSV  

## 📄 Sample Outputs

- `POI_Scenarios.xlsx`: Excel file with POIs categorized by scenario  
- `repeatedData_POI_4815075.csv`: List of duplicate POIs  
- `satellite_tile.png`: Marked-up satellite imagery with POI locations

**Team:**
- Ilan Gómez Guerrero
- María Guadalupe Soto Acosta
- Jimena Díaz Franco

**Created at Guadalahacks Hackathon**

