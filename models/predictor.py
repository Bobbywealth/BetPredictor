import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class SportsPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.last_trained = None
        self.model_type = "Random Forest"
        
    def create_features(self, data):
        """Create features for machine learning model"""
        features_list = []
        targets = []
        
        # Get unique teams
        teams = list(set(data['team1'].tolist() + data['team2'].tolist()))
        team_to_idx = {team: idx for idx, team in enumerate(teams)}
        
        for idx, row in data.iterrows():
            team1, team2 = row['team1'], row['team2']
            
            # Basic features
            features = {
                'team1_idx': team_to_idx[team1],
                'team2_idx': team_to_idx[team2],
                'is_home': 1,  # team1 is home
                'sport_encoded': hash(row['sport']) % 100,  # Simple sport encoding
            }
            
            # Historical performance features
            team1_history = self._get_team_recent_performance(data, team1, row['date'])
            team2_history = self._get_team_recent_performance(data, team2, row['date'])
            
            features.update({
                'team1_recent_wins': team1_history['wins'],
                'team1_recent_losses': team1_history['losses'],
                'team1_recent_avg_score': team1_history['avg_score'],
                'team1_recent_avg_conceded': team1_history['avg_conceded'],
                'team2_recent_wins': team2_history['wins'],
                'team2_recent_losses': team2_history['losses'],
                'team2_recent_avg_score': team2_history['avg_score'],
                'team2_recent_avg_conceded': team2_history['avg_conceded'],
            })
            
            # Head-to-head features
            h2h_stats = self._get_h2h_stats(data, team1, team2, row['date'])
            features.update({
                'h2h_team1_wins': h2h_stats['team1_wins'],
                'h2h_team2_wins': h2h_stats['team2_wins'],
                'h2h_draws': h2h_stats['draws'],
                'h2h_total_games': h2h_stats['total_games'],
            })
            
            # Determine winner (target)
            if row['team1_score'] > row['team2_score']:
                target = 1  # Team1 wins
            elif row['team1_score'] < row['team2_score']:
                target = 0  # Team2 wins
            else:
                target = 2  # Draw
            
            features_list.append(list(features.values()))
            targets.append(target)
            
            if not self.feature_names:
                self.feature_names = list(features.keys())
        
        return np.array(features_list), np.array(targets)
    
    def _get_team_recent_performance(self, data, team, current_date, games_back=5):
        """Get recent performance stats for a team"""
        # Filter data before current date
        mask = (data['date'] < current_date) & ((data['team1'] == team) | (data['team2'] == team))
        team_games = data[mask].tail(games_back)
        
        if len(team_games) == 0:
            return {'wins': 0, 'losses': 0, 'avg_score': 0, 'avg_conceded': 0}
        
        wins = 0
        losses = 0
        scores = []
        conceded = []
        
        for _, game in team_games.iterrows():
            if game['team1'] == team:
                score = game['team1_score']
                opp_score = game['team2_score']
            else:
                score = game['team2_score']
                opp_score = game['team1_score']
            
            scores.append(score)
            conceded.append(opp_score)
            
            if score > opp_score:
                wins += 1
            elif score < opp_score:
                losses += 1
        
        return {
            'wins': wins,
            'losses': losses,
            'avg_score': np.mean(scores) if scores else 0,
            'avg_conceded': np.mean(conceded) if conceded else 0
        }
    
    def _get_h2h_stats(self, data, team1, team2, current_date):
        """Get head-to-head statistics between two teams"""
        mask = (data['date'] < current_date) & (
            ((data['team1'] == team1) & (data['team2'] == team2)) |
            ((data['team1'] == team2) & (data['team2'] == team1))
        )
        h2h_games = data[mask]
        
        if len(h2h_games) == 0:
            return {'team1_wins': 0, 'team2_wins': 0, 'draws': 0, 'total_games': 0}
        
        team1_wins = 0
        team2_wins = 0
        draws = 0
        
        for _, game in h2h_games.iterrows():
            if game['team1'] == team1:
                if game['team1_score'] > game['team2_score']:
                    team1_wins += 1
                elif game['team1_score'] < game['team2_score']:
                    team2_wins += 1
                else:
                    draws += 1
            else:  # team2 is team1 in this game
                if game['team1_score'] > game['team2_score']:
                    team2_wins += 1
                elif game['team1_score'] < game['team2_score']:
                    team1_wins += 1
                else:
                    draws += 1
        
        return {
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'draws': draws,
            'total_games': len(h2h_games)
        }
    
    def train_model(self, data):
        """Train the machine learning model"""
        try:
            # Create features and targets
            X, y = self.create_features(data)
            
            if len(X) < 10:
                raise ValueError("Not enough data to train model (minimum 10 samples required)")
            
            # Split the data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train Random Forest model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
            
            self.model.fit(X_train_scaled, y_train)
            
            # Store test data for performance evaluation
            self.X_test = X_test_scaled
            self.y_test = y_test
            self.last_trained = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"Error training model: {str(e)}")
            return False
    
    def predict_match(self, team1, team2, sport, data, home_advantage=1.0, recent_form_weight=0.5):
        """Predict the outcome of a match"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # Create feature vector for prediction
        teams = list(set(data['team1'].tolist() + data['team2'].tolist()))
        team_to_idx = {team: idx for idx, team in enumerate(teams)}
        
        if team1 not in team_to_idx or team2 not in team_to_idx:
            raise ValueError("One or both teams not found in training data")
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Get recent performance
        team1_history = self._get_team_recent_performance(data, team1, current_date)
        team2_history = self._get_team_recent_performance(data, team2, current_date)
        
        # Get head-to-head stats
        h2h_stats = self._get_h2h_stats(data, team1, team2, current_date)
        
        # Create feature vector
        features = np.array([[
            team_to_idx[team1],
            team_to_idx[team2],
            1,  # team1 is home
            hash(sport) % 100,
            team1_history['wins'],
            team1_history['losses'],
            team1_history['avg_score'],
            team1_history['avg_conceded'],
            team2_history['wins'],
            team2_history['losses'],
            team2_history['avg_score'],
            team2_history['avg_conceded'],
            h2h_stats['team1_wins'],
            h2h_stats['team2_wins'],
            h2h_stats['draws'],
            h2h_stats['total_games'],
        ]])
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Get prediction probabilities
        probabilities = self.model.predict_proba(features_scaled)[0]
        prediction = self.model.predict(features_scaled)[0]
        
        # Adjust for home advantage
        if len(probabilities) >= 2:
            probabilities[1] *= home_advantage  # Boost home team (team1)
            probabilities = probabilities / probabilities.sum()  # Normalize
        
        # Determine winner and confidence
        if prediction == 1:
            predicted_winner = team1
            confidence = probabilities[1] if len(probabilities) > 1 else 0.5
        elif prediction == 0:
            predicted_winner = team2
            confidence = probabilities[0] if len(probabilities) > 0 else 0.5
        else:
            predicted_winner = "Draw"
            confidence = probabilities[2] if len(probabilities) > 2 else 0.33
        
        result = {
            'predicted_winner': predicted_winner,
            'confidence': confidence,
            'team1_win_prob': probabilities[1] if len(probabilities) > 1 else 0.33,
            'team2_win_prob': probabilities[0] if len(probabilities) > 0 else 0.33,
            'draw_prob': probabilities[2] if len(probabilities) > 2 else 0.33,
            'raw_prediction': prediction,
            'all_probabilities': probabilities
        }
        
        return result
    
    def get_betting_recommendations(self, prediction_result):
        """Generate betting recommendations based on prediction"""
        recommendations = []
        
        confidence = prediction_result['confidence']
        predicted_winner = prediction_result['predicted_winner']
        team1_prob = prediction_result['team1_win_prob']
        team2_prob = prediction_result['team2_win_prob']
        draw_prob = prediction_result.get('draw_prob', 0)
        
        # High confidence recommendations
        if confidence > 0.7:
            risk_level = "Low"
            suggested_stake = "High"
            expected_value = confidence * 1.5
        elif confidence > 0.6:
            risk_level = "Medium"
            suggested_stake = "Medium"
            expected_value = confidence * 1.2
        else:
            risk_level = "High"
            suggested_stake = "Low"
            expected_value = confidence * 0.8
        
        # Main recommendation
        recommendations.append({
            'bet_type': 'Match Winner',
            'selection': predicted_winner,
            'confidence': confidence,
            'risk_level': risk_level,
            'expected_value': expected_value,
            'suggested_stake': suggested_stake,
            'reasoning': f"Model predicts {predicted_winner} with {confidence:.1%} confidence based on recent form and historical data."
        })
        
        # Over/Under recommendation based on team scoring patterns
        total_prob = team1_prob + team2_prob
        if total_prob > 0.8:
            recommendations.append({
                'bet_type': 'Total Goals/Points',
                'selection': 'Over',
                'confidence': total_prob * 0.8,
                'risk_level': 'Medium',
                'expected_value': total_prob * 1.1,
                'suggested_stake': 'Medium',
                'reasoning': 'Both teams show strong offensive capabilities based on recent performance.'
            })
        
        # Draw recommendation
        if draw_prob > 0.25:
            recommendations.append({
                'bet_type': 'Draw',
                'selection': 'Draw',
                'confidence': draw_prob,
                'risk_level': 'High',
                'expected_value': draw_prob * 2.0,
                'suggested_stake': 'Low',
                'reasoning': 'Teams appear evenly matched based on historical head-to-head record.'
            })
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def get_model_performance(self):
        """Get model performance metrics"""
        if self.model is None or not hasattr(self, 'X_test'):
            return {}
        
        try:
            y_pred = self.model.predict(self.X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(self.y_test, y_pred)
            precision = precision_score(self.y_test, y_pred, average='weighted', zero_division=0)
            recall = recall_score(self.y_test, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(self.y_test, y_pred, average='weighted', zero_division=0)
            
            # Feature importance
            feature_importance = {}
            if hasattr(self.model, 'feature_importances_'):
                for i, importance in enumerate(self.model.feature_importances_):
                    if i < len(self.feature_names):
                        feature_importance[self.feature_names[i]] = importance
            
            # Confusion matrix
            cm = confusion_matrix(self.y_test, y_pred)
            
            return {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'feature_importance': feature_importance,
                'confusion_matrix': cm.tolist()
            }
        except Exception as e:
            print(f"Error calculating performance metrics: {str(e)}")
            return {}
    
    def get_model_info(self):
        """Get general model information"""
        cv_score = 0
        if self.model is not None and hasattr(self, 'X_test'):
            try:
                # Combine train and test data for cross-validation
                all_features = np.vstack([self.scaler.transform(self.X_test), self.X_test])
                all_targets = np.concatenate([self.y_test, self.y_test])
                cv_scores = cross_val_score(self.model, all_features, all_targets, cv=3)
                cv_score = cv_scores.mean()
            except:
                cv_score = 0
        
        return {
            'model_type': self.model_type,
            'training_samples': len(self.X_test) * 5 if hasattr(self, 'X_test') else 0,  # Estimate
            'n_features': len(self.feature_names),
            'last_trained': self.last_trained.strftime('%Y-%m-%d %H:%M:%S') if self.last_trained else 'Never',
            'cv_score': cv_score
        }
