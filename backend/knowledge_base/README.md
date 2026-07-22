# Kisan Mitra: Agricultural Knowledge Base Architecture & Extension Guide

This directory (`backend/knowledge_base/`) contains the structured, modular agricultural knowledge datasets used to fuel Kisan Mitra's local RAG (Retrieval-Augmented Generation) system.

---

## 1. Directory Structure

```
backend/knowledge_base/
├── README.md                          # Documentation & dataset extension manual
├── crop_profiles.json                 # Crop profiles (22+ crops, seasons, soil, NPK, harvest)
├── soil_knowledge.json                # Soil types, characteristics, pH, water retention
├── fertilizer_knowledge.json          # Fertilizer compositions, dosages, split applications
├── irrigation_knowledge.json          # Drip, sprinkler, AWD, furrow irrigation guides
├── weather_advisory.json              # Heatwave, cold wave, heavy rain, drought advisories
├── pest_disease_knowledge.json        # Fungal/pest symptoms, prevention, treatments
├── government_schemes.json            # PM-KISAN, PMFBY, KCC, Soil Health Card summaries
├── market_knowledge.json              # MSP, e-NAM, post-harvest storage & selling advice
└── faq_dataset.json                   # Question-Answer pairs for crop, soil, organic farming
```

---

## 2. Standard Record Schema

Every record across all JSON datasets adheres to a strict, standardized schema:

```json
{
  "id": "unique_string_identifier",
  "category": "crop_profiles | soil_knowledge | fertilizer_knowledge | irrigation_knowledge | weather_advisory | pest_disease_knowledge | government_schemes | market_knowledge | faq",
  "title": "Clear descriptive title",
  "content": "Detailed, high-quality, structured text content...",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "related_crops": ["crop_name_1", "crop_name_2"],
  "language": "en",
  "source": "ICAR / Ministry of Agriculture / IMD / Agronomic Guidelines"
}
```

---

## 3. How to Add New Datasets Without Changing Code

The RAG index builder dynamically scans all `.json` files inside `backend/knowledge_base/`:

1. **Adding New Entries to Existing Files**:
   - Simply append new JSON objects into the corresponding category file (e.g. `crop_profiles.json` or `faq_dataset.json`).
   - Ensure the `id` is unique and the required schema fields (`id`, `category`, `title`, `content`, `keywords`, `related_crops`, `language`, `source`) are populated.

2. **Adding Entirely New Categories**:
   - Create a new `.json` file inside `backend/knowledge_base/` (e.g. `organic_farming_knowledge.json`).
   - Format the file as a JSON array of record objects following the schema.
   - The RAG ingestion script automatically discovers and indexes all JSON files in the `backend/knowledge_base/` folder without any code changes.
