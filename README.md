# UK Road Accident Severity Prediction

A machine learning project that classifies road collision severity using Department for Transport STATS19 data.

The project covers data preparation, exploratory analysis, feature engineering, model evaluation and an interactive application built with FastAPI and Streamlit.

Docker Compose runs the application locally and provides the configuration for deployment on AWS EC2.

## Live Demo

[Open the application](http://13.42.73.85:8501)

Hosted on AWS EC2 using Docker Compose.

## Application

The interface accepts collision details, road conditions, vehicle information and casualty ages.

It returns:

- Predicted severity: Fatal, Serious or Slight.
- Model probabilities for each severity class.

Optional inputs can be left blank. The saved preprocessing pipeline handles missing values before prediction.

The application classifies severity from supplied collision information. It does not estimate the probability of a collision occurring.

## Technology Stack

- Python 3.11
- pandas and NumPy
- scikit-learn
- FastAPI and Uvicorn
- Streamlit
- Docker and Docker Compose
- GitHub Actions

## Data

The project uses the public STATS19 collision, vehicle and casualty datasets for Great Britain.

Records were filtered to collisions from 2010 through 2024:

| Dataset | Selected records |
|---|---:|
| Collisions | 1,886,746 |
| Vehicles | 3,400,657 |
| Casualties | 2,479,311 |

Vehicle and casualty information was aggregated before merging, producing one row per collision.

Data source: [Department for Transport — Road safety open data](https://www.gov.uk/government/statistical-data-sets/road-safety-open-data)

The large CSV files are excluded from Git. The notebooks contain the preparation and training workflow.

## Project Structure

```text
.
├── .github/
│   └── workflows/
│       └── ci.yml
├── api/
│   └── main.py
├── app/
│   └── streamlit_app.py
├── models/
│   └── production_pipeline.joblib
├── notebooks/
│   ├── 01_collision_data_preparation.ipynb
│   ├── 02_vehicle_data_preparation.ipynb
│   ├── 03_casualty_data_preparation.ipynb
│   ├── 04_data_integration_eda.ipynb
│   └── 05_model_training.ipynb
├── .dockerignore
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── LICENSE
└── README.md
```

## Machine Learning Workflow

1. Prepare the collision, vehicle and casualty datasets.
2. Remove redundant identifiers and severity-related predictors.
3. Convert missing age and engine-capacity codes to missing values.
4. Aggregate vehicle and casualty information at collision level.
5. Create temporal features and explore the integrated dataset.
6. Separate training, validation and test data using stratified splits.
7. Fit imputation, scaling and categorical encoding using training data only.
8. Compare Logistic Regression, Decision Tree and Random Forest.
9. Select a model using validation results and its serialized size.

The notebooks were developed in Google Colab. Their file paths refer to the project folder in Google Drive.

To reproduce the workflow, place the three source CSV files in
`MyDrive/UK-Accident-Prediction` and run notebooks 01–05 in order.

## Selected Model

Random Forest Classifier:

| Parameter | Value |
|---|---|
| Training sample | 400,000 collisions |
| Number of trees | 100 |
| Maximum depth | 20 |
| Minimum samples per leaf | 10 |
| Class weighting | `balanced_subsample` |
| Random seed | 42 |

Preprocessing and classification are exported together in
`production_pipeline.joblib`.

The compressed pipeline occupies approximately **26.37 MiB**.

## Results

| Metric | Validation | Test |
|---|---:|---:|
| Accuracy | 0.6439 | 0.6448 |
| Macro F1 | 0.4109 | 0.4133 |

Test results by severity:

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| Fatal | 0.056 | 0.480 | 0.101 |
| Serious | 0.298 | 0.463 | 0.362 |
| Slight | 0.895 | 0.685 | 0.776 |

Approximately 81.63% of collisions belong to the Slight class. Accuracy is therefore reported alongside Macro F1 and per-class metrics.

The test set was inspected across multiple development iterations. These test results should not be interpreted as a completely untouched final benchmark.

## Run Locally

Use Python 3.11 and a virtual environment.

```bash
python3.11 -m venv .venv
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Start the API from the project root:

```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

In a second terminal, activate the same environment and start Streamlit:

```bash
python -m streamlit run app/streamlit_app.py
```

Open:

- Application: http://localhost:8501
- API health: http://localhost:8000/health
- API documentation: http://localhost:8000/docs

## Run with Docker

With Docker running, execute from the project root:

```bash
docker compose up --build -d
```

Open http://localhost:8501.

Check service status:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs --tail=50
```

Stop the application:

```bash
docker compose down
```

The containers share one image. Streamlit sends requests to FastAPI using:

```text
API_URL=http://api:8000/predict
```

The model is loaded by the API only. Training data and notebooks are excluded from the Docker image.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check API availability |
| POST | `/predict` | Predict severity and return class probabilities |

The prediction request contains a `features` dictionary matching the pipeline's input columns. Missing values are represented as JSON `null`.

The API rejects missing or unexpected feature names.

## Continuous Integration

GitHub Actions runs on pushes and pull requests targeting `main`.

The workflow checks:

- Dependency installation.
- Python syntax.
- Pipeline loading and prediction.
- Probability output validity.
- Docker Compose configuration.
- Docker image construction.

These checks verify application compatibility, not model predictive quality.

## Deployment Resources

A local Docker measurement showed approximately:

| Service | Observed memory |
|---|---:|
| FastAPI | 244.2 MiB |
| Streamlit | 54.24 MiB |
| Total | 298.44 MiB |

The Docker image occupied approximately 1.19 GB on disk.

These are local measurements, not peak memory guarantees. Resource usage must also be checked on the deployed EC2 instance.

## Limitations

- Precision for Fatal collisions remains low.
- Class weighting improves minority-class recall at the expense of accuracy.
- Blank inputs are imputed and can reduce the information available for prediction.
- Unusually high vehicle ages and engine capacities were retained without a verified correction rule.
- Random splits do not demonstrate performance on future years.
- Model probabilities have not been calibrated.
- The application is a portfolio demonstration, not an operational safety or emergency-response system.

## License

Project code is released under the MIT License. See `LICENSE`.

The source dataset retains its own licensing terms, documented on the Department for Transport data page.

## Author
Mauricio Mazuera

LinkedIn: "https://www.linkedin.com/in/mauricio-mazuera-a0a7a933b/"

GitHub: "https://github.com/hmmazuera/UK_accident_prediction"

