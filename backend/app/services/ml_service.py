"""
ML Service - Motor de predicción de demanda v3
Carga modelos entrenados (.pkl) y genera predicciones
Soporta: XGBoost v2, LightGBM v2, Ensemble ponderado (XGBoost + LightGBM)
"""
import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional, List, Dict
from datetime import datetime, timedelta
from app.core.config import get_settings


class MLService:
    def __init__(self):
        settings = get_settings()
        backend_dir = Path(__file__).resolve().parent.parent.parent
        self.models_path = backend_dir / settings.MODELS_PATH
        self.confidence_level = settings.PREDICTION_CONFIDENCE_LEVEL
        os.makedirs(self.models_path, exist_ok=True)
        self._xgb_model = None
        self._lgb_model = None
        self._ensemble_weights = None

    def load_model(self, filename: str):
        """Carga un modelo entrenado desde disco."""
        path = os.path.join(self.models_path, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Modelo no encontrado: {path}")
        return joblib.load(path)

    def load_ensemble(self) -> Tuple[object, object, Dict[str, float]]:
        """
        Carga el ensemble v2 (XGBoost + LightGBM) con sus pesos.
        Retorna: (xgb_model, lgb_model, weights)
        """
        if self._xgb_model is not None and self._lgb_model is not None:
            return self._xgb_model, self._lgb_model, self._ensemble_weights

        ensemble_path = os.path.join(self.models_path, "ensemble_v2.pkl")
        if not os.path.exists(ensemble_path):
            raise FileNotFoundError(f"Ensemble no encontrado: {ensemble_path}")

        ensemble_data = self.load_model("ensemble_v2.pkl")
        
        xgb_file = ensemble_data.get("xgb_model_file", "xgboost_v2_model.pkl")
        lgb_file = ensemble_data.get("lgb_model_file", "lightgbm_v2_model.pkl")
        
        self._xgb_model = self.load_model(xgb_file)
        self._lgb_model = self.load_model(lgb_file)
        self._ensemble_weights = {
            "xgboost": ensemble_data.get("xgb_weight", 0.5),
            "lightgbm": ensemble_data.get("lgb_weight", 0.5),
        }
        
        return self._xgb_model, self._lgb_model, self._ensemble_weights

    def get_v2_feature_columns(self) -> List[str]:
        """
        Features del modelo v2 - 19 variables.
        Estas features son las que el modelo espera durante la predicción.
        """
        return [
            "price", "dayofweek", "month", "is_month_end",
            "lag_1", "lag_7", "lag_14", "lag_28",
            "rolling_mean_7", "rolling_mean_14", "rolling_mean_28",
            "rolling_std_7", "rolling_std_28",
            "price_change_1",
            "is_holiday", "month_sin", "dayofweek_sin",
            "rolling_max_28", "rolling_min_28",
        ]

    def get_feature_columns(self) -> List[str]:
        """Retorna las columnas de features esperadas por el modelo."""
        return self.get_v2_feature_columns()

    def _calc_easter_sunday(self, year: int) -> datetime:
        """Calcula el domingo de Pascua para un año dado (algoritmo de Meeus/Jones/Butcher)."""
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        return datetime(year, month, day)

    def _get_ecuador_holidays(self, year: int) -> List[str]:
        """
        Genera la lista de festivos de Ecuador para un año dado.
        Incluye festivos fijos y móviles (Carnaval, Viernes Santo).
        """
        easter = self._calc_easter_sunday(year)

        # Festivos fijos
        fixed = [
            f"{year}-01-01",  # Año Nuevo
            f"{year}-05-01",  # Día del Trabajo
            f"{year}-05-24",  # Batalla de Pichincha
            f"{year}-08-10",  # Independencia de Guayaquil
            f"{year}-10-09",  # Primer Grito de Independencia
            f"{year}-11-02",  # Día de los Difuntos
            f"{year}-11-03",  # Independencia de Cuenca
            f"{year}-12-25",  # Navidad
        ]

        # Festivos móviles (basados en Pascua)
        carnaval_lunes = easter - timedelta(days=48)
        carnaval_martes = easter - timedelta(days=47)
        viernes_santo = easter - timedelta(days=2)

        variable = [
            carnaval_lunes.strftime("%Y-%m-%d"),
            carnaval_martes.strftime("%Y-%m-%d"),
            viernes_santo.strftime("%Y-%m-%d"),
        ]

        return fixed + variable

    def add_v2_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Agrega features v2 al dataframe.
        Incluye: festivos Ecuador, estacionalidad, tendencia, payday.
        """
        # Estación del año
        if "season" not in df.columns:
            df["season"] = df["date"].dt.month.map({
                1: 0, 2: 0, 3: 1, 4: 1, 5: 1, 6: 2,
                7: 2, 8: 2, 9: 3, 10: 3, 11: 3, 12: 0
            })

        # Festivos de Ecuador (generados dinámicamente por año)
        all_holidays = []
        for y in range(df["date"].dt.year.min(), df["date"].dt.year.max() + 1):
            all_holidays.extend(self._get_ecuador_holidays(y))

        if "is_holiday" not in df.columns:
            df["is_holiday"] = df["date"].dt.strftime("%Y-%m-%d").isin(all_holidays).astype(int)

        # Payday: día 15 y fin de mes
        if "is_payday" not in df.columns:
            df["is_payday"] = ((df["date"].dt.day == 15) | (df["date"].dt.is_month_end)).astype(int)

        # Componentes cíclicos
        if "month_sin" not in df.columns:
            df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
            df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
            df["dayofweek_sin"] = np.sin(2 * np.pi * df["dayofweek"] / 7)
            df["dayofweek_cos"] = np.cos(2 * np.pi * df["dayofweek"] / 7)

        # Tendencia temporal
        if "trend" not in df.columns:
            df["trend"] = (df["date"] - df["date"].min()).dt.days

        # Rolling max/min
        if "rolling_max_28" not in df.columns:
            df["rolling_max_28"] = df["cantidad"].rolling(28, min_periods=1).max()
            df["rolling_min_28"] = df["cantidad"].rolling(28, min_periods=1).min()

        return df

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

        # Rolling statistics (expanding: solo usa datos estrictamente pasados)
        for window in [7, 14, 28]:
            df[f"rolling_mean_{window}"] = df["cantidad"].rolling(window=window, min_periods=1).mean()
            df[f"rolling_std_{window}"] = df["cantidad"].rolling(window=window, min_periods=1).std().fillna(0)

        # Price features
        df["price"] = df["precio_unitario"]
        df["price_change_1"] = df["price"].pct_change(1).fillna(0)
        df["price_ratio_7"] = df["price"].rolling(7, min_periods=1).mean().fillna(df["price"])
        df["promo_proxy"] = (df["price"] < df["price"].rolling(7, min_periods=1).mean()).astype(int)

        # Otros
        df["is_available"] = 1
        df["has_event"] = 0
        df["snap_CA"] = 0
        df["snap_TX"] = 0
        df["snap_WI"] = 0

        # Features v2
        df = self.add_v2_features(df)

        # Eliminar filas con NaN
        df = df.dropna()

        return df

    def predict_demand(
        self,
        model,
        historial_df: pd.DataFrame,
        horizonte: int = 30,
        use_ensemble: bool = False,
    ) -> List[dict]:
        """
        Genera predicciones de demanda para los próximos N días.
        
        Args:
            model: Modelo individual (se ignora si use_ensemble=True)
            historial_df: DataFrame con historial de ventas y features
            horizonte: Número de días a predecir
            use_ensemble: Si True, usa ensemble XGBoost + LightGBM
        
        Retorna lista de diccionarios con fecha, demanda estimada, confianza_min, confianza_max.
        """
        feature_cols = self.get_feature_columns()
        predicciones = []

        # Verificar que las features existan
        missing = [f for f in feature_cols if f not in historial_df.columns]
        if missing:
            raise ValueError(f"Features faltantes: {missing}")

        # Cargar ensemble si se solicita
        xgb_model, lgb_model, weights = None, None, None
        if use_ensemble:
            try:
                xgb_model, lgb_model, weights = self.load_ensemble()
            except FileNotFoundError:
                use_ensemble = False

        # Calcular std de residuos para intervalos de confianza
        if use_ensemble:
            xgb_pred_train = xgb_model.predict(historial_df[feature_cols].astype(float))
            lgb_pred_train = lgb_model.predict(historial_df[feature_cols].astype(float))
            predictions_train = (
                weights["xgboost"] * xgb_pred_train +
                weights["lightgbm"] * lgb_pred_train
            )
        else:
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

        # Proyección de precio: usar promedio y desviación de los últimos 7 días
        historial_precios = historial_df["price"].values
        precio_promedio_7d = float(np.mean(historial_precios[-7:]))
        precio_std_7d = float(np.std(historial_precios[-7:]))

        for day in range(1, horizonte + 1):
            features_input = last_row[feature_cols].values.astype(float)
            features_df = pd.DataFrame(features_input, columns=feature_cols)

            # Predicción: ensemble o modelo individual
            if use_ensemble and xgb_model is not None and lgb_model is not None:
                xgb_pred = xgb_model.predict(features_df)[0]
                lgb_pred = lgb_model.predict(features_df)[0]
                pred = weights["xgboost"] * xgb_pred + weights["lightgbm"] * lgb_pred
            else:
                pred = model.predict(features_df)[0]
            
            pred = max(0, round(float(pred)))

            # Suavizado exponencial: mezclar predicción con media ponderada
            # de los últimos 7 valores del buffer para reducir acumulación de errores
            if len(cantidades) >= 7:
                ventana = cantidades[-7:]
                pesos = np.exp(np.linspace(-1, 0, 7))
                pesos = pesos / pesos.sum()
                suavizado = np.average(ventana, weights=pesos)
                pred = int(0.8 * pred + 0.2 * suavizado)
                pred = max(0, pred)

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

            # Actualizar features v2
            if "rolling_max_28" in feature_cols:
                last_row["rolling_max_28"] = max(cantidades) if cantidades else 0
                last_row["rolling_min_28"] = min(cantidades) if cantidades else 0

            if "month_sin" in feature_cols:
                new_month = new_date.month
                last_row["month_sin"] = np.sin(2 * np.pi * new_month / 12)
                last_row["month_cos"] = np.cos(2 * np.pi * new_month / 12)
                last_row["dayofweek_sin"] = np.sin(2 * np.pi * new_date.weekday() / 7)
                last_row["dayofweek_cos"] = np.cos(2 * np.pi * new_date.weekday() / 7)

            if "is_holiday" in feature_cols:
                ecuador_holidays = self._get_ecuador_holidays(new_date.year)
                last_row["is_holiday"] = int(new_date.strftime("%Y-%m-%d") in ecuador_holidays)

            # Proyectar precio con variación histórica (si hay variabilidad)
            if precio_std_7d > 0:
                variacion = np.random.normal(0, precio_std_7d * 0.1)
                new_price = max(0, round(precio_promedio_7d + variacion, 2))
            else:
                new_price = precio_promedio_7d

            # Actualizar price_change_1 (% cambio vs precio anterior)
            if last_row["price"].values[0] > 0:
                last_row["price_change_1"] = (new_price - last_row["price"].values[0]) / last_row["price"].values[0]
            else:
                last_row["price_change_1"] = 0.0
            last_row["price"] = new_price

        return predicciones

    def get_available_models(self) -> Dict[str, str]:
        """Retorna modelos disponibles con sus archivos."""
        models = {}
        ml_models_dir = self.models_path
        if os.path.exists(ml_models_dir):
            # Primero verificar si existe ensemble
            if os.path.exists(os.path.join(ml_models_dir, "ensemble_v2.pkl")):
                models["ensemble_v2"] = "ensemble_v2.pkl"
            
            for f in os.listdir(ml_models_dir):
                if f.endswith(".pkl"):
                    if "xgboost_v2" in f:
                        models["xgboost_v2"] = f
                    elif "lightgbm_v2" in f:
                        models["lightgbm_v2"] = f
                    elif "xgboost" in f and "v2" not in f:
                        models["xgboost_v1"] = f
                    elif "lightgbm" in f and "v2" not in f:
                        models["lightgbm_v1"] = f
        return models

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
