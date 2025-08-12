"""
🎯 Reliability Curves & Overconfidence Correction
Advanced calibration system that shrinks overconfident predictions
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import streamlit as st

class ReliabilityCurveCalibrator:
    """Advanced reliability curve system to shrink overconfident picks"""
    
    def __init__(self):
        self.calibration_data = self._load_calibration_history()
        self.reliability_curve = self._build_reliability_curve()
        
    def _load_calibration_history(self) -> pd.DataFrame:
        """Load historical prediction vs outcome data for calibration"""
        
        # Try to load from database
        try:
            from app import init_supabase
            supabase = init_supabase()
            
            if supabase:
                # Get last 1000 completed predictions for calibration
                result = supabase.table('predictions')\
                    .select('confidence, was_correct, sport, created_at')\
                    .eq('bet_status', 'completed')\
                    .not_.is_('was_correct', 'null')\
                    .order('created_at', desc=True)\
                    .limit(1000)\
                    .execute()
                
                if result.data:
                    df = pd.DataFrame(result.data)
                    df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce')
                    df['was_correct'] = df['was_correct'].astype(bool)
                    return df
                    
        except Exception as e:
            st.warning(f"⚠️ Could not load calibration history: {e}")
        
        # Fallback: Generate synthetic calibration data based on typical overconfidence patterns
        return self._generate_synthetic_calibration_data()
    
    def _generate_synthetic_calibration_data(self) -> pd.DataFrame:
        """Generate realistic overconfidence patterns for calibration"""
        
        np.random.seed(42)  # Reproducible
        n_samples = 1000
        
        # Simulate typical AI overconfidence pattern
        raw_confidences = np.random.beta(2, 2, n_samples)  # U-shaped distribution
        
        # Apply overconfidence bias - AI tends to be overconfident at high levels
        calibrated_success_rates = []
        
        for conf in raw_confidences:
            if conf >= 0.9:
                # Very high confidence predictions are often overconfident
                actual_rate = conf * 0.85 + np.random.normal(0, 0.05)
            elif conf >= 0.8:
                # High confidence has moderate overconfidence
                actual_rate = conf * 0.9 + np.random.normal(0, 0.04)
            elif conf >= 0.7:
                # Medium-high confidence is fairly well calibrated
                actual_rate = conf * 0.95 + np.random.normal(0, 0.03)
            elif conf >= 0.6:
                # Medium confidence is slightly underconfident
                actual_rate = conf * 1.02 + np.random.normal(0, 0.03)
            else:
                # Low confidence is often underconfident
                actual_rate = conf * 1.1 + np.random.normal(0, 0.05)
            
            # Clamp to valid probability range
            actual_rate = max(0.1, min(0.95, actual_rate))
            calibrated_success_rates.append(actual_rate)
        
        # Generate outcomes based on calibrated rates
        outcomes = [np.random.random() < rate for rate in calibrated_success_rates]
        
        return pd.DataFrame({
            'confidence': raw_confidences,
            'was_correct': outcomes,
            'sport': np.random.choice(['NFL', 'NBA', 'MLB', 'NHL'], n_samples),
            'created_at': [datetime.now() - timedelta(days=np.random.randint(0, 365)) for _ in range(n_samples)]
        })
    
    def _build_reliability_curve(self) -> Dict[str, float]:
        """Build reliability curve mapping predicted confidence to actual accuracy"""
        
        if self.calibration_data.empty:
            return {}
        
        # Create confidence bins
        bins = np.linspace(0.5, 1.0, 11)  # 50% to 100% in 5% increments
        bin_centers = (bins[:-1] + bins[1:]) / 2
        
        reliability_curve = {}
        
        for i, (bin_start, bin_end) in enumerate(zip(bins[:-1], bins[1:])):
            # Get predictions in this confidence bin
            mask = (self.calibration_data['confidence'] >= bin_start) & \
                   (self.calibration_data['confidence'] < bin_end)
            
            bin_data = self.calibration_data[mask]
            
            if len(bin_data) > 0:
                actual_accuracy = bin_data['was_correct'].mean()
                predicted_confidence = bin_centers[i]
                
                reliability_curve[predicted_confidence] = actual_accuracy
            else:
                # No data in this bin - use interpolation
                reliability_curve[bin_centers[i]] = bin_centers[i]
        
        return reliability_curve
    
    def calibrate_confidence(self, raw_confidence: float, sport: str = None, 
                           context: Dict = None) -> Dict:
        """Apply reliability curve calibration to shrink overconfident picks"""
        
        # Ensure confidence is in valid range
        raw_confidence = max(0.5, min(0.99, raw_confidence))
        
        # Find the closest calibration point
        calibrated_confidence = self._interpolate_reliability_curve(raw_confidence)
        
        # Apply sport-specific adjustments
        sport_adjustment = self._get_sport_adjustment(sport)
        calibrated_confidence *= sport_adjustment
        
        # Apply overconfidence shrinkage
        shrinkage_factor = self._calculate_shrinkage_factor(raw_confidence)
        final_confidence = self._apply_shrinkage(calibrated_confidence, raw_confidence, shrinkage_factor)
        
        # Calculate reliability metrics
        reliability_score = self._calculate_reliability_score(final_confidence, raw_confidence)
        overconfidence_penalty = max(0, raw_confidence - final_confidence)
        
        return {
            'raw_confidence': raw_confidence,
            'calibrated_confidence': final_confidence,
            'reliability_score': reliability_score,
            'overconfidence_penalty': overconfidence_penalty,
            'shrinkage_applied': shrinkage_factor,
            'sport_adjustment': sport_adjustment,
            'calibration_quality': self._assess_calibration_quality(final_confidence),
            'recommendation_tier': self._get_recommendation_tier(final_confidence, reliability_score)
        }
    
    def _interpolate_reliability_curve(self, confidence: float) -> float:
        """Interpolate the reliability curve for given confidence level"""
        
        if not self.reliability_curve:
            return confidence  # No calibration data available
        
        # Find surrounding points for interpolation
        conf_points = sorted(self.reliability_curve.keys())
        
        if confidence <= conf_points[0]:
            return self.reliability_curve[conf_points[0]]
        elif confidence >= conf_points[-1]:
            return self.reliability_curve[conf_points[-1]]
        
        # Linear interpolation between surrounding points
        for i in range(len(conf_points) - 1):
            if conf_points[i] <= confidence <= conf_points[i + 1]:
                x1, x2 = conf_points[i], conf_points[i + 1]
                y1, y2 = self.reliability_curve[x1], self.reliability_curve[x2]
                
                # Linear interpolation
                weight = (confidence - x1) / (x2 - x1)
                return y1 + weight * (y2 - y1)
        
        return confidence  # Fallback
    
    def _get_sport_adjustment(self, sport: str) -> float:
        """Sport-specific reliability adjustments based on predictability"""
        
        sport_factors = {
            'NFL': 0.95,    # Slightly less predictable due to parity
            'NBA': 1.02,    # More predictable with star players
            'MLB': 0.90,    # Highly variable, lots of randomness
            'NHL': 0.93,    # Moderate predictability
            'NCAAF': 0.88,  # College football very unpredictable
            'NCAAB': 0.85,  # March Madness chaos
            'Tennis': 1.05, # Individual sports more predictable
            'WNBA': 0.98    # Smaller sample size
        }
        
        return sport_factors.get(sport, 0.95)  # Default conservative
    
    def _calculate_shrinkage_factor(self, raw_confidence: float) -> float:
        """Calculate how much to shrink overconfident predictions"""
        
        if raw_confidence >= 0.95:
            return 0.25  # Heavy shrinkage for extreme confidence
        elif raw_confidence >= 0.90:
            return 0.20  # Strong shrinkage for very high confidence
        elif raw_confidence >= 0.85:
            return 0.15  # Moderate shrinkage for high confidence
        elif raw_confidence >= 0.80:
            return 0.10  # Light shrinkage for medium-high confidence
        else:
            return 0.05  # Minimal shrinkage for moderate confidence
    
    def _apply_shrinkage(self, calibrated_conf: float, raw_conf: float, 
                        shrinkage: float) -> float:
        """Apply shrinkage toward the mean (typically ~0.65 for sports)"""
        
        mean_baseline = 0.65  # Historical sports betting baseline
        
        # Shrink toward the mean
        shrunk_confidence = calibrated_conf * (1 - shrinkage) + mean_baseline * shrinkage
        
        # Ensure we don't shrink below the raw confidence if it was already conservative
        if raw_conf < calibrated_conf:
            return max(raw_conf, shrunk_confidence)
        
        return shrunk_confidence
    
    def _calculate_reliability_score(self, final_conf: float, raw_conf: float) -> float:
        """Calculate reliability score based on calibration adjustments"""
        
        # Higher score for less adjustment needed
        adjustment_magnitude = abs(final_conf - raw_conf)
        reliability = 1.0 - (adjustment_magnitude * 2)  # Scale to 0-1
        
        return max(0.1, min(1.0, reliability))
    
    def _assess_calibration_quality(self, confidence: float) -> str:
        """Assess the quality of calibration"""
        
        if confidence >= 0.85:
            return "High"
        elif confidence >= 0.75:
            return "Medium"
        elif confidence >= 0.65:
            return "Fair"
        else:
            return "Low"
    
    def _get_recommendation_tier(self, confidence: float, reliability: float) -> str:
        """Get recommendation tier based on calibrated confidence and reliability"""
        
        # Combine confidence and reliability for tier
        composite_score = (confidence * 0.7) + (reliability * 0.3)
        
        if composite_score >= 0.90:
            return "PREMIUM_PLAY"
        elif composite_score >= 0.82:
            return "STRONG_PLAY"
        elif composite_score >= 0.75:
            return "MODERATE_PLAY"
        elif composite_score >= 0.65:
            return "LEAN_PLAY"
        else:
            return "NO_PLAY"
    
    def get_calibration_stats(self) -> Dict:
        """Get statistics about the calibration system"""
        
        if self.calibration_data.empty:
            return {"status": "No calibration data available"}
        
        total_predictions = len(self.calibration_data)
        overall_accuracy = self.calibration_data['was_correct'].mean()
        
        # Analyze overconfidence by bins
        high_conf_mask = self.calibration_data['confidence'] >= 0.85
        high_conf_data = self.calibration_data[high_conf_mask]
        
        high_conf_accuracy = high_conf_data['was_correct'].mean() if len(high_conf_data) > 0 else 0
        high_conf_predicted = high_conf_data['confidence'].mean() if len(high_conf_data) > 0 else 0
        
        overconfidence_gap = high_conf_predicted - high_conf_accuracy
        
        return {
            'total_predictions': total_predictions,
            'overall_accuracy': overall_accuracy,
            'high_confidence_predictions': len(high_conf_data),
            'high_confidence_accuracy': high_conf_accuracy,
            'high_confidence_predicted': high_conf_predicted,
            'overconfidence_gap': overconfidence_gap,
            'calibration_curve_points': len(self.reliability_curve),
            'last_updated': datetime.now().isoformat()
        }
