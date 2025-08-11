"""
Confidence Calibration System for Sports Betting AI
Maps AI confidence levels to actual win rates and applies governance
"""

import streamlit as st
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json
import math

class ConfidenceCalibrator:
    """
    Confidence calibration system that ensures AI confidence matches actual performance
    If AI says 75% confidence, it should win 75% of the time
    """
    
    def __init__(self):
        # Confidence bins for calibration (50-55%, 55-60%, etc.)
        self.confidence_bins = [
            (0.50, 0.55), (0.55, 0.60), (0.60, 0.65), (0.65, 0.70),
            (0.70, 0.75), (0.75, 0.80), (0.80, 0.85), (0.85, 0.90), (0.90, 0.95)
        ]
        
        # Historical performance tracking
        self.calibration_data = self._load_calibration_data()
        
        # Confidence governance rules
        self.max_confidence_allowed = 0.90  # Cap overconfidence
        self.min_sample_size = 10  # Need 10+ predictions to calibrate
        self.recency_weight = 0.7  # Weight recent performance more heavily

    def calibrate_confidence(self, raw_confidence: float, prediction_context: Dict) -> Dict:
        """
        Calibrate AI confidence based on historical performance
        
        Args:
            raw_confidence: Original AI confidence (0.0-1.0)
            prediction_context: Game context (sport, model_type, etc.)
            
        Returns:
            Dict with calibrated confidence and calibration info
        """
        
        try:
            # Step 1: Apply basic governance
            governed_confidence = self._apply_confidence_governance(raw_confidence, prediction_context)
            
            # Step 2: Get historical calibration for this confidence range
            calibration_adjustment = self._get_calibration_adjustment(governed_confidence, prediction_context)
            
            # Step 3: Apply calibration adjustment
            calibrated_confidence = self._apply_calibration_adjustment(
                governed_confidence, calibration_adjustment
            )
            
            # Step 4: Calculate reliability score
            reliability_score = self._calculate_reliability_score(calibrated_confidence, prediction_context)
            
            # Step 5: Get recommendation tier based on calibrated confidence
            recommendation_tier = self._get_calibrated_recommendation_tier(calibrated_confidence, reliability_score)
            
            return {
                'raw_confidence': raw_confidence,
                'governed_confidence': governed_confidence,
                'calibrated_confidence': calibrated_confidence,
                'calibration_adjustment': calibration_adjustment,
                'reliability_score': reliability_score,
                'recommendation_tier': recommendation_tier,
                'confidence_explanation': self._generate_confidence_explanation(
                    raw_confidence, calibrated_confidence, calibration_adjustment
                ),
                'calibration_quality': self._assess_calibration_quality(prediction_context)
            }
            
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.write(f"Debug: Confidence calibration error: {e}")
            
            # Fallback to conservative calibration
            return self._conservative_fallback(raw_confidence)

    def _apply_confidence_governance(self, confidence: float, context: Dict) -> float:
        """Apply governance rules to prevent overconfidence"""
        
        sport = context.get('sport', 'Unknown').upper()
        model_type = context.get('model_type', 'Generic')
        data_quality = context.get('data_quality_score', 0.5)
        
        # Start with raw confidence
        governed = confidence
        
        # Rule 1: Cap maximum confidence
        governed = min(governed, self.max_confidence_allowed)
        
        # Rule 2: Reduce confidence for low data quality
        if data_quality < 0.6:
            governed *= 0.95  # 5% reduction for poor data
        elif data_quality < 0.4:
            governed *= 0.90  # 10% reduction for very poor data
        
        # Rule 3: Sport-specific confidence limits
        sport_caps = {
            'MLB': 0.85,  # Baseball has high variance
            'NHL': 0.80,  # Hockey has high variance
            'NBA': 0.88,  # Basketball more predictable
            'NFL': 0.87,  # Football moderate variance
            'NCAAF': 0.75, # College football very high variance
            'NCAAB': 0.80  # College basketball high variance
        }
        
        sport_cap = sport_caps.get(sport, 0.85)
        governed = min(governed, sport_cap)
        
        # Rule 4: Model-specific adjustments
        if 'Generic' in model_type:
            governed *= 0.92  # Reduce confidence for generic models
        
        # Rule 5: Minimum confidence floor
        governed = max(governed, 0.51)  # Never go below slight edge
        
        return governed

    def _get_calibration_adjustment(self, confidence: float, context: Dict) -> float:
        """Get calibration adjustment based on historical performance"""
        
        sport = context.get('sport', 'Unknown').upper()
        
        # Find the appropriate confidence bin
        confidence_bin = self._get_confidence_bin(confidence)
        
        if not confidence_bin:
            return 0.0  # No adjustment if bin not found
        
        # Get historical data for this bin and sport
        historical_data = self.calibration_data.get(sport, {}).get(f"{confidence_bin[0]:.2f}-{confidence_bin[1]:.2f}", {})
        
        if not historical_data or historical_data.get('count', 0) < self.min_sample_size:
            # Not enough data for calibration - use conservative adjustment
            return self._conservative_adjustment(confidence)
        
        # Calculate calibration adjustment
        predicted_win_rate = (confidence_bin[0] + confidence_bin[1]) / 2  # Bin midpoint
        actual_win_rate = historical_data.get('win_rate', predicted_win_rate)
        
        # Adjustment factor (how much to shift confidence)
        calibration_error = actual_win_rate - predicted_win_rate
        adjustment = calibration_error * 0.5  # Apply 50% of the error correction
        
        # Cap adjustment to prevent wild swings
        adjustment = max(-0.10, min(0.10, adjustment))
        
        return adjustment

    def _apply_calibration_adjustment(self, confidence: float, adjustment: float) -> float:
        """Apply calibration adjustment while maintaining bounds"""
        
        calibrated = confidence + adjustment
        
        # Ensure we stay within reasonable bounds
        calibrated = max(0.51, min(0.90, calibrated))
        
        return calibrated

    def _calculate_reliability_score(self, confidence: float, context: Dict) -> float:
        """Calculate how reliable this confidence level is (0-1)"""
        
        sport = context.get('sport', 'Unknown').upper()
        data_quality = context.get('data_quality_score', 0.5)
        
        # Base reliability from confidence level
        if confidence >= 0.80:
            base_reliability = 0.9
        elif confidence >= 0.70:
            base_reliability = 0.8
        elif confidence >= 0.60:
            base_reliability = 0.7
        else:
            base_reliability = 0.6
        
        # Adjust for data quality
        data_adjustment = (data_quality - 0.5) * 0.2  # -0.1 to +0.1 adjustment
        
        # Adjust for sport predictability
        sport_reliability = {
            'NBA': 0.05,   # More predictable
            'NFL': 0.0,    # Baseline
            'MLB': -0.05,  # Less predictable
            'NHL': -0.05,  # Less predictable
            'NCAAF': -0.10, # Much less predictable
            'NCAAB': -0.08  # Less predictable
        }
        
        sport_adjustment = sport_reliability.get(sport, 0.0)
        
        # Calculate final reliability
        reliability = base_reliability + data_adjustment + sport_adjustment
        
        return max(0.3, min(1.0, reliability))

    def _get_calibrated_recommendation_tier(self, confidence: float, reliability: float) -> str:
        """Get betting recommendation tier based on calibrated confidence and reliability"""
        
        # Effective confidence = confidence * reliability
        effective_confidence = confidence * reliability
        
        if effective_confidence >= 0.75 and confidence >= 0.80:
            return "PREMIUM_PLAY"      # 3-5 units
        elif effective_confidence >= 0.65 and confidence >= 0.70:
            return "STRONG_PLAY"       # 2-3 units
        elif effective_confidence >= 0.55 and confidence >= 0.60:
            return "MODERATE_PLAY"     # 1-2 units
        elif effective_confidence >= 0.52 and confidence >= 0.55:
            return "LEAN_PLAY"         # 0.5-1 unit
        else:
            return "NO_PLAY"           # Pass

    def _generate_confidence_explanation(self, raw: float, calibrated: float, adjustment: float) -> str:
        """Generate human-readable explanation of confidence calibration"""
        
        if abs(adjustment) < 0.01:
            return f"Confidence well-calibrated at {calibrated:.1%}"
        elif adjustment > 0:
            return f"Confidence boosted from {raw:.1%} to {calibrated:.1%} (strong recent performance)"
        else:
            return f"Confidence reduced from {raw:.1%} to {calibrated:.1%} (conservative adjustment)"

    def _assess_calibration_quality(self, context: Dict) -> str:
        """Assess the quality of calibration data available"""
        
        sport = context.get('sport', 'Unknown').upper()
        sport_data = self.calibration_data.get(sport, {})
        
        total_predictions = sum(bin_data.get('count', 0) for bin_data in sport_data.values())
        
        if total_predictions >= 100:
            return "High"
        elif total_predictions >= 50:
            return "Medium"
        elif total_predictions >= 20:
            return "Low"
        else:
            return "Insufficient"

    def _get_confidence_bin(self, confidence: float) -> Optional[Tuple[float, float]]:
        """Get the appropriate confidence bin for a confidence level"""
        
        for bin_start, bin_end in self.confidence_bins:
            if bin_start <= confidence < bin_end:
                return (bin_start, bin_end)
        
        # Handle edge case for very high confidence
        if confidence >= 0.90:
            return (0.90, 0.95)
        
        return None

    def _conservative_adjustment(self, confidence: float) -> float:
        """Conservative adjustment when insufficient calibration data"""
        
        # Slightly reduce confidence for high values (overconfidence bias)
        if confidence >= 0.80:
            return -0.03  # 3% reduction
        elif confidence >= 0.70:
            return -0.02  # 2% reduction
        elif confidence >= 0.60:
            return -0.01  # 1% reduction
        else:
            return 0.0   # No adjustment for moderate confidence

    def _conservative_fallback(self, raw_confidence: float) -> Dict:
        """Conservative fallback when calibration fails"""
        
        # Apply basic governance
        calibrated = min(raw_confidence * 0.95, 0.85)  # 5% reduction, cap at 85%
        
        return {
            'raw_confidence': raw_confidence,
            'governed_confidence': calibrated,
            'calibrated_confidence': calibrated,
            'calibration_adjustment': calibrated - raw_confidence,
            'reliability_score': 0.6,
            'recommendation_tier': 'MODERATE_PLAY',
            'confidence_explanation': 'Conservative calibration applied (insufficient data)',
            'calibration_quality': 'Insufficient'
        }

    def _load_calibration_data(self) -> Dict:
        """Load historical calibration data (placeholder - would load from database)"""
        
        # Placeholder calibration data based on typical sports betting performance
        # In production, this would load from database of actual predictions vs results
        
        return {
            'NBA': {
                '0.50-0.55': {'count': 45, 'wins': 24, 'win_rate': 0.533},
                '0.55-0.60': {'count': 38, 'wins': 21, 'win_rate': 0.553},
                '0.60-0.65': {'count': 42, 'wins': 26, 'win_rate': 0.619},
                '0.65-0.70': {'count': 35, 'wins': 23, 'win_rate': 0.657},
                '0.70-0.75': {'count': 28, 'wins': 20, 'win_rate': 0.714},
                '0.75-0.80': {'count': 22, 'wins': 17, 'win_rate': 0.773},
                '0.80-0.85': {'count': 15, 'wins': 12, 'win_rate': 0.800},
            },
            'NFL': {
                '0.50-0.55': {'count': 32, 'wins': 16, 'win_rate': 0.500},
                '0.55-0.60': {'count': 28, 'wins': 15, 'win_rate': 0.536},
                '0.60-0.65': {'count': 25, 'wins': 15, 'win_rate': 0.600},
                '0.65-0.70': {'count': 20, 'wins': 13, 'win_rate': 0.650},
                '0.70-0.75': {'count': 18, 'wins': 13, 'win_rate': 0.722},
                '0.75-0.80': {'count': 12, 'wins': 9, 'win_rate': 0.750},
            },
            'MLB': {
                '0.50-0.55': {'count': 55, 'wins': 27, 'win_rate': 0.491},
                '0.55-0.60': {'count': 48, 'wins': 26, 'win_rate': 0.542},
                '0.60-0.65': {'count': 40, 'wins': 24, 'win_rate': 0.600},
                '0.65-0.70': {'count': 30, 'wins': 19, 'win_rate': 0.633},
                '0.70-0.75': {'count': 25, 'wins': 17, 'win_rate': 0.680},
                '0.75-0.80': {'count': 18, 'wins': 13, 'win_rate': 0.722},
            }
        }

    def update_calibration_data(self, prediction_result: Dict):
        """Update calibration data with new prediction result"""
        
        # This would update the database with actual results
        # For now, this is a placeholder for the interface
        
        sport = prediction_result.get('sport', 'Unknown').upper()
        confidence = prediction_result.get('confidence', 0.5)
        won = prediction_result.get('won', False)
        
        # In production, this would:
        # 1. Find the appropriate confidence bin
        # 2. Update count and win rate in database
        # 3. Trigger recalibration if needed
        
        if st.session_state.get('debug_mode', False):
            st.write(f"Debug: Would update calibration data - {sport}, {confidence:.3f}, {'Win' if won else 'Loss'}")

    def get_calibration_report(self) -> Dict:
        """Generate calibration report showing model performance"""
        
        report = {
            'overall_calibration': 'Good',
            'sports_breakdown': {},
            'recommendations': []
        }
        
        for sport, sport_data in self.calibration_data.items():
            total_predictions = sum(bin_data.get('count', 0) for bin_data in sport_data.values())
            total_wins = sum(bin_data.get('wins', 0) for bin_data in sport_data.values())
            
            if total_predictions > 0:
                overall_accuracy = total_wins / total_predictions
                
                # Calculate calibration error
                calibration_error = 0
                weighted_predictions = 0
                
                for bin_range, bin_data in sport_data.items():
                    if bin_data.get('count', 0) >= 5:  # Minimum sample size
                        bin_start, bin_end = map(float, bin_range.split('-'))
                        expected_rate = (bin_start + bin_end) / 2
                        actual_rate = bin_data.get('win_rate', expected_rate)
                        
                        error = abs(actual_rate - expected_rate)
                        weight = bin_data.get('count', 0)
                        
                        calibration_error += error * weight
                        weighted_predictions += weight
                
                if weighted_predictions > 0:
                    avg_calibration_error = calibration_error / weighted_predictions
                else:
                    avg_calibration_error = 0
                
                report['sports_breakdown'][sport] = {
                    'total_predictions': total_predictions,
                    'accuracy': overall_accuracy,
                    'calibration_error': avg_calibration_error,
                    'calibration_quality': 'Good' if avg_calibration_error < 0.05 else 'Needs Improvement'
                }
        
        return report
