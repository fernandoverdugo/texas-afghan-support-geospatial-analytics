# Texas Afghan Support Program — Geospatial Analytics

An end-to-end Python data-science project exploring the geographic distribution of program participation, rental assistance, and financial-wellness engagement across five Texas metropolitan areas using synthetic ZIP-level data.

The project combines **data validation, exploratory analysis, geospatial visualization, and reproducible reporting** to turn program-administration data into an interactive analytical product.

[**View the live interactive map**](https://fernandoverdugo.github.io/texas-afghan-support-geospatial-analytics/)  
[**View the rendered analysis notebook**](notebooks/01_exploratory_analysis.ipynb)

> **Portfolio dataset:** All program values are synthetic and intentionally perturbed. The project demonstrates analytical methods and software workflow rather than reporting operational results.

## Project objectives

This project answers several practical program-analysis questions:

- Where are participating households and individuals geographically concentrated?
- Which ZIP codes account for the largest rental-assistance totals?
- How does program volume differ across metropolitan areas?
- How concentrated is rental assistance across ZIP codes?
- How do enrollment, assistance, and Financial Wellness attendance change month to month?
- What relationships exist among households, participants, assistance, and service engagement?

## Key findings

These findings describe the **synthetic portfolio dataset**:

- **Houston** has the largest aggregate rental-assistance volume at approximately **$4.21M**.
- The **10 highest-assistance ZIP codes account for 57.6%** of total rental assistance, showing substantial geographic concentration.
- Statewide synthetic rental assistance increases **44.3% from July to August**, then changes **-1.6% from August to September**.
- Financial Wellness attendance increases **14.4% in August** and then decreases **72.1% in September**, illustrating why monthly context matters alongside cumulative program measures.

## Portfolio highlights

- **192 ZIP-code geographies** across Austin, Dallas, Fort Worth, Houston, and San Antonio
- Interactive choropleth layers for households, participants, rental assistance, and Financial Wellness Course attendance
- Detailed ZIP-level hover tooltips with monthly enrollment, rental assistance, Financial Wellness attendance, and month-over-month percentage changes
- Click/tap ZIP detail cards for touch-device accessibility
- Built-in Map Guide explaining quantile colors, MoM labels, metric definitions, and optional overlays
- Dynamic quantile legend, ZIP-code search, metro-area quick navigation, and fullscreen viewing
- Optional participant heat map and Top-10 rental-assistance ZIP overlays
- Executed exploratory-analysis notebook with descriptive, temporal, normalized, and correlation analysis
- Automated data-quality tests and GitHub Actions continuous integration
- Reproducible Python pipeline for generated tables, charts, and the interactive map

## Skills demonstrated

`Python` · `pandas` · `NumPy` · `Folium` · `Leaflet` · `GeoJSON` · `Matplotlib` · `Jupyter` · `pytest` · `GitHub Actions` · `EDA` · `data validation` · `geospatial analytics`

## Repository structure

```text
.
├── .github/workflows/quality-checks.yml
├── data/
│   ├── asp_zip_metrics.csv
│   ├── geometry/
│   │   └── asp_zip_geometries_part_*.geojson
│   └── README.md
├── notebooks/
│   └── 01_exploratory_analysis.ipynb
├── scripts/
│   ├── analyze.py
│   ├── build_map.py
│   └── run_pipeline.py
├── tests/
│   └── test_data_quality.py
├── LICENSE
├── requirements.txt
└── README.md
```

## Analytical workflow

```text
ZIP-level CSV + GeoJSON
          ↓
   data validation
          ↓
 exploratory analysis
          ↓
 summary tables + charts
          ↓
 interactive Folium map
          ↓
     GitHub Pages
```

### Data validation

Automated tests verify schema, ZIP uniqueness, expected metro areas, nonnegative measures, cumulative-enrollment logic, monthly-to-total rental-assistance reconciliation, FWC consistency, derived rates, and Top-10 flags.

### Exploratory data analysis

[**Open the rendered Jupyter notebook**](notebooks/01_exploratory_analysis.ipynb)

The notebook is fully executed in the repository, so GitHub displays the analytical tables and visualizations without requiring the reader to run the code first. It examines:

- descriptive statistics and data-quality checks
- metro-area comparisons
- ZIP-level distributions and concentration
- monthly enrollment, rental assistance, and Financial Wellness attendance
- month-over-month percentage changes
- ZIP-level growth and decline
- normalized measures such as rental assistance per household
- correlations among aggregate program measures
- key findings and analytical limitations

### Geospatial visualization

The Folium application provides switchable choropleth layers for total households, total participants, total rental assistance, and Financial Wellness attendance. It includes ZIP search, metro navigation, viewport-aware detail cards, click/tap details, a participant heat map, Top-10 markers, a dynamic legend, and a Map Guide.

## Reproduce the project

The repository targets **Python 3.15** and pins the tested dependency set in `requirements.txt`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the data-quality tests:

```bash
python -m pytest -q
```

Regenerate summary tables, charts, and the interactive map:

```bash
python scripts/run_pipeline.py
```

Open the exploratory notebook locally:

```bash
jupyter lab notebooks/01_exploratory_analysis.ipynb
```

Preview the map locally:

```bash
python -m http.server 8000 --directory docs
```

Then open `http://localhost:8000`.

## Data-science approach

The project is intentionally focused on **descriptive and exploratory analytics** rather than adding a predictive model where one is not methodologically necessary. The analysis uses grouped aggregation, distribution analysis, quantile-based geographic classification, concentration analysis, correlation, normalized measures, and month-over-month comparison.

Associations are treated as descriptive rather than causal.

## Data

The repository uses synthetic ZIP-code-level portfolio data modeled on program-administration scenarios. No client-level or personally identifiable information is included. See [`data/README.md`](data/README.md) for the complete data dictionary and interpretation notes.

## GitHub Pages

The interactive map is generated automatically through GitHub Actions. Each workflow run validates the data, rebuilds the analytical outputs and Folium application, and deploys the resulting site to GitHub Pages.

[**View the live interactive map**](https://fernandoverdugo.github.io/texas-afghan-support-geospatial-analytics/)

## License

Code in this repository is available under the [MIT License](LICENSE).