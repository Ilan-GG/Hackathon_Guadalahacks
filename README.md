# Hackathon Guadalahacks Project 🌍

This repository contains a geospatial data processing pipeline for Points of Interest (POI) validation and classification, developed during the **Guadalahacks Hackathon**. The system validates POI locations against street networks using satellite imagery and geometric analysis.

## 📌 Project Description

The project focuses on:
- **POI Validation**: Checking POI positions against street geometries using percentage-based references
- **Satellite Imagery Analysis**: Detecting structures around POIs to validate their existence
- **Data Classification**: Categorizing POIs into scenarios based on positional accuracy and naming consistency
- **Duplicate Detection**: Identifying and reporting duplicate POI entries

Key technologies used:
- Geospatial processing with Turf.js and GeoJSON
- Satellite imagery analysis with OpenCV
- Excel report generation
- HERE Maps API for tile fetching

## 🛠 Technologies Used

- **Core**: 
  - Node.js (JavaScript/TypeScript) 
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
   npm install @turf/turf xlsx
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
- **Additional solution**: Export duplicates POI's

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

