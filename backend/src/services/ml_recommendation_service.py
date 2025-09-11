"""
Machine Learning Recommendation Service for enhanced personalization.

This service implements ML models for better course recommendations,
A/B testing framework for personalization strategies, and feedback loops
to continuously improve recommendation accuracy.
"""

import logging
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
from sqlalchemy.orm import Session

from ..db.crud import analytics_crud
from ..db.models.db_analytics import (
    UserBehaviorData, LearningPattern, UserLearningProfile, EngagementMetrics,
    EventType, LearningStyleType, DifficultyLevel
)
from ..db.models.db_course import Course, Chapter
from ..utils.analytics_utils import generate_analytics_id

logger = logging.getLogger(__name__)


class MLRecommendationModel:
    """Base class for ML recommendation models."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        self.last_trained = None
        self.feature_columns = []
        
    def prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for ML model."""
        raise NotImplementedError
        
    def train(self, training_data: pd.DataFrame) -> Dict[str, float]:
        """Train the ML model."""
        raise NotImplementedError
        
    def predict(self, features: np.ndarray) -> np.ndarray:
        """Make predictions using the trained model."""
        if not self.is_trained:
            raise ValueError(f"Model {self.model_name} is not trained")
        return self.model.predict(features)
        
    def save_model(self, filepath: str):
        """Save the trained model to disk."""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_columns': self.feature_columns,
            'is_trained': self.is_trained,
            'last_trained': self.last_trained
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
            
    def load_model(self, filepath: str):
        """Load a trained model from disk."""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.label_encoder = model_data['label_encoder']
            self.feature_columns = model_data['feature_columns']
            self.is_trained = model_data['is_trained']
            self.last_trained = model_data['last_trained']
            
            logger.info(f"Loaded model {self.model_name} trained on {self.last_trained}")
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {str(e)}")
            self.is_trained = False


class CourseRecommendationModel(MLRecommendationModel):
    """ML model for course recommendations based on user behavior and preferences."""
    
    def __init__(self):
        super().__init__("course_recommendation")
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        
    def prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for course recommendation model."""
        feature_columns = [
            'user_completion_rate', 'user_engagement_score', 'user_avg_session_duration',
            'user_difficulty_level', 'user_learning_style_encoded', 'user_total_courses',
            'course_difficulty', 'course_avg_rating', 'course_completion_rate',
            'topic_similarity_score', 'user_topic_performance'
        ]
        
        self.feature_columns = feature_columns
        
        # Ensure all required columns exist
        for col in feature_columns:
            if col not in data.columns:
                data[col] = 0.0
        
        features = data[feature_columns].fillna(0)
        return self.scaler.fit_transform(features)
        
    def train(self, training_data: pd.DataFrame) -> Dict[str, float]:
        """Train the course recommendation model."""
        try:
            # Prepare features and target
            X = self.prepare_features(training_data)
            y = training_data['user_liked_course'].fillna(0).astype(int)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train model
            self.model.fit(X_train, y_train)
            
            # Evaluate
            train_predictions = self.model.predict(X_train)
            test_predictions = self.model.predict(X_test)
            
            train_accuracy = accuracy_score(y_train, train_predictions)
            test_accuracy = accuracy_score(y_test, test_predictions)
            
            self.is_trained = True
            self.last_trained = datetime.now(timezone.utc)
            
            logger.info(f"Trained {self.model_name} - Train Accuracy: {train_accuracy:.3f}, Test Accuracy: {test_accuracy:.3f}")
            
            return {
                'train_accuracy': train_accuracy,
                'test_accuracy': test_accuracy,
                'feature_importance': dict(zip(self.feature_columns, self.model.feature_importances_))
            }
            
        except Exception as e:
            logger.error(f"Error training {self.model_name}: {str(e)}")
            return {'error': str(e)}


class DifficultyPredictionModel(MLRecommendationModel):
    """ML model for predicting optimal content difficulty for users."""
    
    def __init__(self):
        super().__init__("difficulty_prediction")
        self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        
    def prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for difficulty prediction model."""
        feature_columns = [
            'user_completion_rate', 'user_engagement_score', 'user_avg_session_duration',
            'user_current_difficulty', 'user_challenge_preference', 'user_consistency_score',
            'content_base_difficulty', 'user_topic_familiarity', 'recent_performance_trend'
        ]
        
        self.feature_columns = feature_columns
        
        # Ensure all required columns exist
        for col in feature_columns:
            if col not in data.columns:
                data[col] = 0.5  # Default to medium difficulty/performance
        
        features = data[feature_columns].fillna(0.5)
        return self.scaler.fit_transform(features)
        
    def train(self, training_data: pd.DataFrame) -> Dict[str, float]:
        """Train the difficulty prediction model."""
        try:
            # Prepare features and target
            X = self.prepare_features(training_data)
            y = training_data['optimal_difficulty'].fillna(0.5)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model
            self.model.fit(X_train, y_train)
            
            # Evaluate
            train_predictions = self.model.predict(X_train)
            test_predictions = self.model.predict(X_test)
            
            train_mse = mean_squared_error(y_train, train_predictions)
            test_mse = mean_squared_error(y_test, test_predictions)
            
            self.is_trained = True
            self.last_trained = datetime.now(timezone.utc)
            
            logger.info(f"Trained {self.model_name} - Train MSE: {train_mse:.3f}, Test MSE: {test_mse:.3f}")
            
            return {
                'train_mse': train_mse,
                'test_mse': test_mse,
                'feature_importance': dict(zip(self.feature_columns, self.model.feature_importances_))
            }
            
        except Exception as e:
            logger.error(f"Error training {self.model_name}: {str(e)}")
            return {'error': str(e)}


class UserClusteringModel(MLRecommendationModel):
    """ML model for clustering users based on learning patterns."""
    
    def __init__(self, n_clusters: int = 5):
        super().__init__("user_clustering")
        self.model = KMeans(n_clusters=n_clusters, random_state=42)
        self.n_clusters = n_clusters
        
    def prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for user clustering model."""
        feature_columns = [
            'completion_rate', 'engagement_score', 'avg_session_duration',
            'challenge_preference', 'consistency_score', 'learning_style_encoded',
            'preferred_difficulty_encoded', 'total_learning_time'
        ]
        
        self.feature_columns = feature_columns
        
        # Ensure all required columns exist
        for col in feature_columns:
            if col not in data.columns:
                data[col] = 0.0
        
        features = data[feature_columns].fillna(0)
        return self.scaler.fit_transform(features)
        
    def train(self, training_data: pd.DataFrame) -> Dict[str, float]:
        """Train the user clustering model."""
        try:
            # Prepare features
            X = self.prepare_features(training_data)
            
            # Train model
            self.model.fit(X)
            
            # Evaluate using inertia (within-cluster sum of squares)
            inertia = self.model.inertia_
            
            self.is_trained = True
            self.last_trained = datetime.now(timezone.utc)
            
            logger.info(f"Trained {self.model_name} with {self.n_clusters} clusters - Inertia: {inertia:.3f}")
            
            return {
                'inertia': inertia,
                'n_clusters': self.n_clusters,
                'cluster_centers': self.model.cluster_centers_.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error training {self.model_name}: {str(e)}")
            return {'error': str(e)}
            
    def predict_cluster(self, features: np.ndarray) -> int:
        """Predict cluster for given features."""
        if not self.is_trained:
            raise ValueError(f"Model {self.model_name} is not trained")
        return self.model.predict(features)[0]


class ABTestingFramework:
    """A/B testing framework for personalization strategies."""
    
    def __init__(self):
        self.active_tests = {}
        self.test_results = {}
        
    def create_ab_test(
        self,
        test_name: str,
        variants: List[str],
        traffic_split: List[float],
        success_metric: str,
        duration_days: int = 14
    ) -> Dict[str, Any]:
        """Create a new A/B test for personalization strategies."""
        
        if len(variants) != len(traffic_split):
            raise ValueError("Number of variants must match traffic split")
        
        if abs(sum(traffic_split) - 1.0) > 0.001:
            raise ValueError("Traffic split must sum to 1.0")
        
        test_config = {
            'test_name': test_name,
            'variants': variants,
            'traffic_split': traffic_split,
            'success_metric': success_metric,
            'start_date': datetime.now(timezone.utc),
            'end_date': datetime.now(timezone.utc) + timedelta(days=duration_days),
            'status': 'active',
            'user_assignments': {},
            'results': {variant: {'users': 0, 'conversions': 0, 'metric_sum': 0.0} for variant in variants}
        }
        
        self.active_tests[test_name] = test_config
        logger.info(f"Created A/B test '{test_name}' with variants {variants}")
        
        return test_config
        
    def assign_user_to_variant(self, test_name: str, user_id: str) -> Optional[str]:
        """Assign a user to a test variant."""
        
        if test_name not in self.active_tests:
            return None
            
        test = self.active_tests[test_name]
        
        # Check if test is still active
        if datetime.now(timezone.utc) > test['end_date']:
            test['status'] = 'completed'
            return None
            
        # Check if user is already assigned
        if user_id in test['user_assignments']:
            return test['user_assignments'][user_id]
        
        # Assign user based on hash and traffic split
        user_hash = hash(user_id + test_name) % 1000 / 1000.0
        
        cumulative_split = 0.0
        for i, (variant, split) in enumerate(zip(test['variants'], test['traffic_split'])):
            cumulative_split += split
            if user_hash <= cumulative_split:
                test['user_assignments'][user_id] = variant
                test['results'][variant]['users'] += 1
                logger.debug(f"Assigned user {user_id} to variant '{variant}' in test '{test_name}'")
                return variant
                
        # Fallback to first variant
        variant = test['variants'][0]
        test['user_assignments'][user_id] = variant
        test['results'][variant]['users'] += 1
        return variant
        
    def record_conversion(self, test_name: str, user_id: str, metric_value: float = 1.0):
        """Record a conversion event for A/B test analysis."""
        
        if test_name not in self.active_tests:
            return
            
        test = self.active_tests[test_name]
        
        if user_id not in test['user_assignments']:
            return
            
        variant = test['user_assignments'][user_id]
        test['results'][variant]['conversions'] += 1
        test['results'][variant]['metric_sum'] += metric_value
        
        logger.debug(f"Recorded conversion for user {user_id} in variant '{variant}' of test '{test_name}'")
        
    def get_test_results(self, test_name: str) -> Optional[Dict[str, Any]]:
        """Get current results for an A/B test."""
        
        if test_name not in self.active_tests:
            return None
            
        test = self.active_tests[test_name]
        results = {}
        
        for variant in test['variants']:
            variant_data = test['results'][variant]
            users = variant_data['users']
            conversions = variant_data['conversions']
            
            conversion_rate = conversions / users if users > 0 else 0.0
            avg_metric = variant_data['metric_sum'] / users if users > 0 else 0.0
            
            results[variant] = {
                'users': users,
                'conversions': conversions,
                'conversion_rate': conversion_rate,
                'avg_metric_value': avg_metric
            }
        
        # Calculate statistical significance (simplified)
        if len(test['variants']) == 2:
            control_rate = results[test['variants'][0]]['conversion_rate']
            treatment_rate = results[test['variants'][1]]['conversion_rate']
            
            # Simple z-test approximation
            control_users = results[test['variants'][0]]['users']
            treatment_users = results[test['variants'][1]]['users']
            
            if control_users > 30 and treatment_users > 30:
                pooled_rate = (results[test['variants'][0]]['conversions'] + 
                              results[test['variants'][1]]['conversions']) / (control_users + treatment_users)
                
                se = np.sqrt(pooled_rate * (1 - pooled_rate) * (1/control_users + 1/treatment_users))
                
                if se > 0:
                    z_score = abs(treatment_rate - control_rate) / se
                    # Approximate p-value (two-tailed)
                    p_value = 2 * (1 - 0.5 * (1 + np.sign(z_score) * np.sqrt(1 - np.exp(-2 * z_score**2 / np.pi))))
                    
                    results['statistical_analysis'] = {
                        'z_score': z_score,
                        'p_value': p_value,
                        'significant': p_value < 0.05,
                        'lift': (treatment_rate - control_rate) / control_rate if control_rate > 0 else 0
                    }
        
        return {
            'test_config': test,
            'results': results,
            'status': test['status']
        }


class FeedbackLoop:
    """Feedback loop system to improve recommendation accuracy."""
    
    def __init__(self):
        self.feedback_data = []
        
    def collect_implicit_feedback(
        self,
        user_id: str,
        recommendation_id: str,
        action: str,
        context: Dict[str, Any]
    ):
        """Collect implicit feedback from user actions."""
        
        feedback = {
            'user_id': user_id,
            'recommendation_id': recommendation_id,
            'action': action,  # 'click', 'view', 'complete', 'skip', 'rate'
            'context': context,
            'timestamp': datetime.now(timezone.utc),
            'feedback_type': 'implicit'
        }
        
        self.feedback_data.append(feedback)
        logger.debug(f"Collected implicit feedback: {action} for recommendation {recommendation_id}")
        
    def collect_explicit_feedback(
        self,
        user_id: str,
        recommendation_id: str,
        rating: float,
        context: Dict[str, Any]
    ):
        """Collect explicit feedback from user ratings."""
        
        feedback = {
            'user_id': user_id,
            'recommendation_id': recommendation_id,
            'rating': rating,
            'context': context,
            'timestamp': datetime.now(timezone.utc),
            'feedback_type': 'explicit'
        }
        
        self.feedback_data.append(feedback)
        logger.debug(f"Collected explicit feedback: rating {rating} for recommendation {recommendation_id}")
        
    def calculate_recommendation_quality_score(self, recommendation_id: str) -> float:
        """Calculate quality score for a recommendation based on feedback."""
        
        relevant_feedback = [f for f in self.feedback_data if f['recommendation_id'] == recommendation_id]
        
        if not relevant_feedback:
            return 0.5  # Default neutral score
        
        score = 0.0
        weight_sum = 0.0
        
        for feedback in relevant_feedback:
            if feedback['feedback_type'] == 'explicit':
                # Direct rating feedback
                score += feedback['rating'] * 1.0
                weight_sum += 1.0
            elif feedback['feedback_type'] == 'implicit':
                # Infer satisfaction from actions
                action_scores = {
                    'click': 0.6,
                    'view': 0.5,
                    'complete': 0.9,
                    'skip': 0.2,
                    'rate': 0.7
                }
                action_score = action_scores.get(feedback['action'], 0.5)
                score += action_score * 0.5  # Lower weight for implicit feedback
                weight_sum += 0.5
        
        return score / weight_sum if weight_sum > 0 else 0.5
        
    def get_model_performance_metrics(self) -> Dict[str, float]:
        """Calculate overall model performance metrics from feedback."""
        
        if not self.feedback_data:
            return {}
        
        # Group feedback by recommendation
        recommendation_scores = {}
        for feedback in self.feedback_data:
            rec_id = feedback['recommendation_id']
            if rec_id not in recommendation_scores:
                recommendation_scores[rec_id] = self.calculate_recommendation_quality_score(rec_id)
        
        scores = list(recommendation_scores.values())
        
        return {
            'avg_recommendation_score': np.mean(scores),
            'recommendation_score_std': np.std(scores),
            'total_recommendations': len(recommendation_scores),
            'total_feedback_events': len(self.feedback_data),
            'high_quality_recommendations': len([s for s in scores if s > 0.7]),
            'low_quality_recommendations': len([s for s in scores if s < 0.3])
        }


class MLRecommendationService:
    """Main service for ML-based recommendations and A/B testing."""
    
    def __init__(self):
        self.course_model = CourseRecommendationModel()
        self.difficulty_model = DifficultyPredictionModel()
        self.clustering_model = UserClusteringModel()
        self.ab_testing = ABTestingFramework()
        self.feedback_loop = FeedbackLoop()
        
    async def train_models(self, db: Session) -> Dict[str, Any]:
        """Train all ML models using available data."""
        
        try:
            # Prepare training data
            training_data = await self._prepare_training_data(db)
            
            if training_data.empty:
                logger.warning("No training data available for ML models")
                return {'error': 'No training data available'}
            
            results = {}
            
            # Train course recommendation model
            if len(training_data) > 50:  # Minimum data requirement
                course_results = self.course_model.train(training_data)
                results['course_recommendation'] = course_results
                
                # Train difficulty prediction model
                difficulty_results = self.difficulty_model.train(training_data)
                results['difficulty_prediction'] = difficulty_results
                
                # Train user clustering model
                user_data = training_data.drop_duplicates(subset=['user_id'])
                if len(user_data) > 10:
                    clustering_results = self.clustering_model.train(user_data)
                    results['user_clustering'] = clustering_results
            
            logger.info(f"Trained ML models with {len(training_data)} data points")
            return results
            
        except Exception as e:
            logger.error(f"Error training ML models: {str(e)}")
            return {'error': str(e)}
            
    async def get_ml_recommendations(
        self,
        db: Session,
        user_id: str,
        course_candidates: List[Course],
        max_recommendations: int = 5
    ) -> List[Dict[str, Any]]:
        """Get ML-based course recommendations for a user."""
        
        try:
            if not self.course_model.is_trained:
                logger.warning("Course recommendation model not trained, falling back to rule-based")
                return []
            
            # Get user profile and behavior data
            user_profile = analytics_crud.get_user_learning_profile(db, user_id)
            if not user_profile:
                return []
            
            recommendations = []
            
            for course in course_candidates:
                # Prepare features for this user-course pair
                features = self._prepare_recommendation_features(user_profile, course)
                
                # Get ML prediction
                prediction_prob = self.course_model.model.predict_proba([features])[0][1]  # Probability of positive class
                
                # Get optimal difficulty prediction
                difficulty_features = self._prepare_difficulty_features(user_profile, course)
                optimal_difficulty = self.difficulty_model.predict([difficulty_features])[0]
                
                # Get user cluster for additional insights
                user_features = self._prepare_user_features(user_profile)
                user_cluster = self.clustering_model.predict_cluster([user_features])
                
                recommendation = {
                    'course_id': course.id,
                    'title': course.title,
                    'ml_score': float(prediction_prob),
                    'optimal_difficulty': float(optimal_difficulty),
                    'user_cluster': int(user_cluster),
                    'confidence': float(prediction_prob),
                    'reason': f"ML model prediction (cluster {user_cluster})"
                }
                
                recommendations.append(recommendation)
            
            # Sort by ML score and return top recommendations
            recommendations.sort(key=lambda x: x['ml_score'], reverse=True)
            return recommendations[:max_recommendations]
            
        except Exception as e:
            logger.error(f"Error getting ML recommendations: {str(e)}")
            return []
            
    async def _prepare_training_data(self, db: Session) -> pd.DataFrame:
        """Prepare training data for ML models."""
        
        # Get all user profiles
        user_profiles = analytics_crud.get_all_user_learning_profiles(db)
        
        training_data = []
        
        for profile in user_profiles:
            # Get user's course interactions
            behavior_data = analytics_crud.get_user_behavior_data(
                db=db,
                user_id=profile.user_id,
                start_date=datetime.now(timezone.utc) - timedelta(days=90),
                end_date=datetime.now(timezone.utc)
            )
            
            # Extract course interactions
            course_interactions = {}
            for data in behavior_data:
                if data.course_id:
                    if data.course_id not in course_interactions:
                        course_interactions[data.course_id] = {
                            'views': 0, 'completions': 0, 'time_spent': 0
                        }
                    
                    if data.event_type == EventType.PAGE_VIEW:
                        course_interactions[data.course_id]['views'] += 1
                    elif data.event_type == EventType.COURSE_COMPLETE:
                        course_interactions[data.course_id]['completions'] += 1
                    
                    if data.duration_seconds:
                        course_interactions[data.course_id]['time_spent'] += data.duration_seconds
            
            # Create training examples
            for course_id, interaction in course_interactions.items():
                # Determine if user "liked" the course (implicit feedback)
                user_liked = (
                    interaction['completions'] > 0 or 
                    interaction['time_spent'] > 300 or  # 5+ minutes
                    interaction['views'] > 3
                )
                
                training_example = {
                    'user_id': profile.user_id,
                    'course_id': course_id,
                    'user_completion_rate': profile.completion_rate,
                    'user_engagement_score': profile.engagement_score,
                    'user_avg_session_duration': profile.average_session_duration or 30,
                    'user_difficulty_level': profile.current_difficulty_level,
                    'user_learning_style_encoded': self._encode_learning_style(profile.learning_style),
                    'user_total_courses': profile.courses_completed,
                    'user_challenge_preference': profile.challenge_preference,
                    'user_consistency_score': profile.consistency_score,
                    'course_difficulty': 0.5,  # Default, would come from course metadata
                    'course_avg_rating': 4.0,  # Default, would come from course ratings
                    'course_completion_rate': 0.7,  # Default, would be calculated
                    'topic_similarity_score': 0.5,  # Would be calculated using NLP
                    'user_topic_performance': 0.5,  # Would be calculated from user's topic history
                    'user_liked_course': int(user_liked),
                    'optimal_difficulty': min(1.0, profile.current_difficulty_level + 0.1),  # Slightly higher than current
                    'completion_rate': profile.completion_rate,
                    'engagement_score': profile.engagement_score,
                    'avg_session_duration': profile.average_session_duration or 30,
                    'challenge_preference': profile.challenge_preference,
                    'consistency_score': profile.consistency_score,
                    'learning_style_encoded': self._encode_learning_style(profile.learning_style),
                    'preferred_difficulty_encoded': self._encode_difficulty(profile.preferred_difficulty),
                    'total_learning_time': profile.total_learning_time or 0
                }
                
                training_data.append(training_example)
        
        return pd.DataFrame(training_data)
        
    def _prepare_recommendation_features(self, user_profile: UserLearningProfile, course: Course) -> np.ndarray:
        """Prepare features for course recommendation prediction."""
        
        features = [
            user_profile.completion_rate,
            user_profile.engagement_score,
            user_profile.average_session_duration or 30,
            user_profile.current_difficulty_level,
            self._encode_learning_style(user_profile.learning_style),
            user_profile.courses_completed,
            0.5,  # course_difficulty (default)
            4.0,  # course_avg_rating (default)
            0.7,  # course_completion_rate (default)
            0.5,  # topic_similarity_score (would be calculated)
            0.5   # user_topic_performance (would be calculated)
        ]
        
        return self.course_model.scaler.transform([features])[0]
        
    def _prepare_difficulty_features(self, user_profile: UserLearningProfile, course: Course) -> np.ndarray:
        """Prepare features for difficulty prediction."""
        
        features = [
            user_profile.completion_rate,
            user_profile.engagement_score,
            user_profile.average_session_duration or 30,
            user_profile.current_difficulty_level,
            user_profile.challenge_preference,
            user_profile.consistency_score,
            0.5,  # content_base_difficulty (default)
            0.5,  # user_topic_familiarity (would be calculated)
            0.0   # recent_performance_trend (would be calculated)
        ]
        
        return self.difficulty_model.scaler.transform([features])[0]
        
    def _prepare_user_features(self, user_profile: UserLearningProfile) -> np.ndarray:
        """Prepare features for user clustering."""
        
        features = [
            user_profile.completion_rate,
            user_profile.engagement_score,
            user_profile.average_session_duration or 30,
            user_profile.challenge_preference,
            user_profile.consistency_score,
            self._encode_learning_style(user_profile.learning_style),
            self._encode_difficulty(user_profile.preferred_difficulty),
            user_profile.total_learning_time or 0
        ]
        
        return self.clustering_model.scaler.transform([features])[0]
        
    def _encode_learning_style(self, learning_style: LearningStyleType) -> float:
        """Encode learning style as numeric value."""
        encoding = {
            LearningStyleType.VISUAL: 0.0,
            LearningStyleType.AUDITORY: 0.25,
            LearningStyleType.KINESTHETIC: 0.5,
            LearningStyleType.READING: 0.75,
            LearningStyleType.MIXED: 0.5,
            LearningStyleType.UNKNOWN: 0.5
        }
        return encoding.get(learning_style, 0.5)
        
    def _encode_difficulty(self, difficulty: DifficultyLevel) -> float:
        """Encode difficulty level as numeric value."""
        encoding = {
            DifficultyLevel.BEGINNER: 0.0,
            DifficultyLevel.INTERMEDIATE: 0.5,
            DifficultyLevel.ADVANCED: 1.0
        }
        return encoding.get(difficulty, 0.5)