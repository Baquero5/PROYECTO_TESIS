"""
ML Service - Motor de predicción de demanda
Carga modelos entrenados (.pkl) y genera predicciones
"""
import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional, List
from datetime import datetime, timedelta
from app.core.config import get_settings


class MLService:
    def __init__(self):
        settings = get_settings()
        backend_dir = Path(__file__).resolve().parent.parent.parent
        self.models_path = backend_dir / settings.MODELS_PATH
        self.confidence_level = settings.PREDICTION_CONFIDENCE_LEVEL
        os.makedirs(self.models_path, exist_ok=True)

    def load_model(self, filename: str):
        """Carga un modelo entrenado desde disco."""
        path = os.path.join(self.models_path, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Modelo no encontrado: {path}")
        return joblib.load(path)

    def get_feature_columns(self) -> List[str]:
        """Retorna las columnas de features esperadas por el modelo."""
        return [
            "price", "is_available",
            "dayofweek", "day", "weekofyear", "month", "year",
            "is_month_start", "is_month_end", "is_weekend", "has_event",
            "snap_CA", "snap_TX", "snap_WI",
            "lag_1", "lag_7", "lag_14", "lag_28",
            "rolling_mean_7", "rolling_mean_14", "rolling_mean_28",
            "rolling_std_7", "rolling_std_14", "rolling_std_28",
            "price_change_1", "price_ratio_7", "promo_proxy",
        ]

    def prepare_features_from_history(self, historial_ventas: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara features a partir del historial de ventas de un producto.
        historial_ventas debe tener columnas: fecha_venta, cantidad, precio_unitario
        """
        df = historial_ventas.copy()
        df["date"] = pd.to_datetime(df["fecha_venta"])
        df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0).astype(float)
        df["precio_unitario"] = pd.to_numeric(df["precio_unitario"], errors="coerce").fillna(0.0).astype(float)
        df = df.sort_values("date").reset_index(drop=True)

        # Features de calendario
        df["dayofweek"] = df["date"].dt.dayofweek
        df["day"] = df["date"].dt.day
        df["weekofyear"] = df["date"].dt.isocalendar().week.astype(int)
        df["month"] = df["date"].dt.month
        df["year"] = df["date"].dt.year
        df["is_month_start"] = df["date"].dt.is_month_start.astype(int)
        df["is_month_end"] = df["date"].dt.is_month_end.astype(int)
        df["is_weekend"] = (df["dayofweek"] >= 5).astype(int)

        # Lags
        df["lag_1"] = df["cantidad"].shift(1)
        df["lag_7"] = df["cantidad"].shift(7)
        df["lag_14"] = df["cantidad"].shift(14)
        df["lag_28"] = df["cantidad"].shift(28)

        # Rolling statistics
        for window in [7, 14, 28]:
            df[f"rolling_mean_{window}"] = df["cantidad"].rolling(window=window).mean()
            df[f"rolling_std_{window}"] = df["cantidad"].rolling(window=window).std()

        # Price features
        df["price"] = df["precio_unitario"]
        df["price_change_1"] = df["price"].pct_change(1).fillna(0)
        df["price_ratio_7"] = df["price"].rolling(7).mean().fillna(df["price"])
        df["promo_proxy"] = (df["price"] < df["price"].rolling(7).mean()).astype(int)

        # Otros
        df["is_available"] = 1
        df["has_event"] = 0
        df["snap_CA"] = 0
        df["snap_TX"] = 0
        df["snap_WI"] = 0

        # Eliminar filas con NaN
        df = df.dropna()

        return df

    def predict_demand(
        self,
        model,
        historial_df: pd.DataFrame,
        horizonte: int = 30
    ) -> List[dict]:
        """
        Genera predicciones de demanda para los próximos N días.
        Retorna lista de diccionarios con fecha, demanda estimada, confianza_min, confianza_max.
        """
        feature_cols = self.get_feature_columns()
        predicciones = []

        # Calcular std de residuos para intervalos de confianza
        predictions_train = model.predict(historial_df[feature_cols].astype(float))
        residuals = historial_df["cantidad"].values - predictions_train
        residual_std = np.std(residuals)

        # Z-score basado en el nivel de confianza configurado
        from scipy import stats
        alpha = 1 - self.confidence_level
        z_score = stats.norm.ppf(1 - alpha / 2)

        # Buffer de historial para actualizar lags correctamente
        cantidades = list(historial_df["cantidad"].values[-28:])
        last_row = historial_df.iloc[-1:].copy()
        last_price = float(last_row["price"].values[0])

        for day in range(1, horizonte + 1):
            features_input = last_row[feature_cols].values.astype(float)
            features_df = pd.DataFrame(features_input, columns=feature_cols)

            pred = model.predict(features_df)[0]
            pred = max(0, round(float(pred)))

            # Intervalo de confianza que se amplía con el horizonte
            horizon_factor = np.sqrt(day)
            conf_min = max(0, round(pred - z_score * residual_std * horizon_factor))
            conf_max = round(pred + z_score * residual_std * horizon_factor)

            new_date = pd.to_datetime(last_row["date"].values[0]) + timedelta(days=1)

            predicciones.append({
                "fecha": new_date.strftime("%Y-%m-%d"),
                "demanda_estimada": pred,
                "confianza_min": conf_min,
                "confianza_max": conf_max,
            })

            # Agregar predicción al buffer de historial
            cantidades.append(pred)
            if len(cantidades) > 28:
                cantidades.pop(0)

            # Actualizar last_row para siguiente predicción
            last_row["date"] = new_date
            last_row["cantidad"] = pred

            # Actualizar lags correctamente desde el buffer
            last_row["lag_1"] = cantidades[-1]
            last_row["lag_7"] = cantidades[-7] if len(cantidades) >= 7 else cantidades[0]
            last_row["lag_14"] = cantidades[-14] if len(cantidades) >= 14 else cantidades[0]
            last_row["lag_28"] = cantidades[-28] if len(cantidades) >= 28 else cantidades[0]

            # Actualizar rolling statistics desde el buffer
            for window in [7, 14, 28]:
                if len(cantidades) >= window:
                    window_data = cantidades[-window:]
                    last_row[f"rolling_mean_{window}"] = np.mean(window_data)
                    last_row[f"rolling_std_{window}"] = np.std(window_data) if len(window_data) > 1 else 0

            # Mantener precio y features estáticas
            last_row["price"] = last_price

        return predicciones

    def save_model(self, model, filename: str) -> str:
        """Guarda un modelo entrenado en disco."""
        path = os.path.join(self.models_path, filename)
        joblib.dump(model, path)
        return path

    def list_models(self) -> List[str]:
        """Lista los archivos de modelo disponibles."""
        if not os.path.exists(self.models_path):
            return []
        return [f for f in os.listdir(self.models_path) if f.endswith((".pkl", ".joblib"))]


ml_service = MLService()
