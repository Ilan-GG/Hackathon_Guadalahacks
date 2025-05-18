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
