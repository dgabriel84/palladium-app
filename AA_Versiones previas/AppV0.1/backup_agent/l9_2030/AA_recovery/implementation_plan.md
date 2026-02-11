# Implementation Plan - Hotel Cancellation Prediction App

Create a Streamlit application that predicts the probability of hotel reservation cancellation using the pre-trained LightGBM model.

## User Review Required

> [!IMPORTANT]
> The application will point directly to the model file at `/Users/gabi/Library/CloudStorage/GoogleDrive-dgabriel84@gmail.com/.shortcut-targets-by-id/1MHQ8E-8B1PFz3EgbmBRY7WLo5AhTV1mF/TFM_Palladium_Team/04_models/lightgbm_FINAL20260206_142533/lightgbm.joblib`. Ensure this path remains accessible.

## Proposed Changes

### Logic Layer
#### [NEW] [utils.py](file:///Users/gabi/.gemini/antigravity/scratch/palladium_predict/utils.py)
- Port the `get_features` function from `funcion_producion.py`.
- Include necessary helper functions (`get_ADR`, `get_REV_PAX`, etc.).
- Add model loading logic using `joblib`.

### UI Layer
#### [NEW] [app.py](file:///Users/gabi/.gemini/antigravity/scratch/palladium_predict/app.py)
- **Inputs**:
    - Date pickers for `LLEGADA`, `FECHA_TOMA`.
    - Numeric inputs for `NOCHES`, `PAX`, `ADULTOS`, `VALOR_RESERVA`.
    - Text/Select inputs for `CLIENTE`, `FIDELIDAD`, `PAIS`, `SEGMENTO`, `FUENTE_NEGOCIO`, `NOMBRE_HOTEL`, `NOMBRE_HABITACION`.
- **Processing**:
    - Call `utils.get_features` with user inputs.
    - Convert categorical colums to `category` dtype as per notebook.
    - Select features listed in `metrics.json`.
- **Output**:
    - Display cancellation probability.

## Verification Plan

### Manual Verification
- Run the app using `streamlit run app.py`.
- Input the sample values from the notebook (Cell 31) and verify if the prediction outcome matches (or is reasonable).
    - Example: LLEGADA='2026-06-01', NOCHES=15, PAX=2, ADULTOS=2, VALOR_RESERVA=11088.0, etc.
- Verify that finding the model file works.
