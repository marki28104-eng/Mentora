"""
Advanced Analytics Service for predictive analytics, cohort analysis, and real-time personalization.

This service implements advanced analytics features including:
- Predictive analytics for learning outcomes
- Cohort analysis for learning pattern identification
- Real-time personalization adjustments during learning sessions
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from ..db.crud import analytics_crud
from ..db.models.db_analytics import (
    UserBehaviorData, LearningPattern, UserLearningProfile, EngagementMetrics,
    EventType, LearningStyleType, DifficultyLevel
)
from ..db.models.db_course import Course, Chapter
from ..utils.analytics_utils import generate_analytics_id
from ..config.settings import (
    ANALYTICS_MIN_DATA_POINTS_FOR_TRAINING,
    ANALYTICS_ENABLE_REAL_TIME_PERSONALIZATION,
    ANALYTICS_ENABLE_PREDICTIVE_MODELS,
    ANALYTICS_ENABLE_COHORT_ANALYSIS
)

logger = logging.getLogger(__name__)


class PredictiveOutcome:
    """Container for predictive analytics results."""
    
    def __init__(
        self,
        user_id: str,
        prediction_type: str,
        predicted_value: float,
        confidence: float,
        factors: Dict[str, float],
        recommendations: List[str]
    ):
        self.user_id = user_id
        self.prediction_type = prediction_type
        self.predicted_value = predicted_value
        self.confidence = confidence
        self.factors = factors
        self.recommendations = recommendations
        self.created_at = datetime.now(timezone.utc)


class CohortAnalysis:
    """Container for cohort analysis results."""
    
    def __init__(
        self,
        cohort_name: str,
        cohort_size: int,
        time_period: str,
        retention_rates: Dict[str, float],
        engagement_trends: Dict[str, float],
        learning_patterns: Dict[str, Any],
        performance_metrics: Dict[str, float]
    ):
        self.cohort_name = cohort_name
        self.cohort_size = cohort_size
        self.time_period = time_period
        self.retention_rates = retention_rates
        self.engagement_trends = engagement_trends
        self.learning_patterns = learning_patterns
        self.performance_metrics = performance_metrics
        self.created_at = datetime.now(timezone.utc)


class RealTimePersonalization:
    """Container for real-time personalization adjustments."""
    
    def __init__(
        self,
        user_id: str,
        session_id: str,
        adjustments: Dict[str, Any],
        trigger_events: List[str],
        confidence: float
    ):
        self.user_id = user_id
        self.session_id = session_id
        self.adjustments = adjustments
        self.trigger_events = trigger_events
        self.confidence = confidence
        self.created_at = datetime.now(timezone.utc)


class PredictiveAnalyticsEngine:
    """Engine for predictive analytics on learning outcomes."""
    
    def __init__(self):
        self.completion_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.success_predictor = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.engagement_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    async def train_predictive_models(self, db: Session) -> Dict[str, Any]:
        """Train predictive models using historical data."""
        try:
            # Prepare training data
            training_data = await self._prepare_predictive_training_data(db)
            
            if len(training_data) < ANALYTICS_MIN_DATA_POINTS_FOR_TRAINING:
                logger.warning(f"Insufficient data for predictive model training (need {ANALYTICS_MIN_DATA_POINTS_FOR_TRAINING}, got {len(training_data)})")
                return {'error': 'Insufficient training data'}
            
            # Prepare features
            feature_columns = [
                'initial_engagement', 'session_frequency', 'avg_session_duration',
                'difficulty_preference', 'learning_style_encoded', 'time_of_day',
                'content_type_preference', 'social_learning_score', 'prior_knowledge'
            ]
            
            X = training_data[feature_columns].fillna(0)
            X_scaled = self.scaler.fit_transform(X)
            
            results = {}
            
            # Train completion predictor
            y_completion = training_data['completion_rate'].fillna(0)
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y_completion, test_size=0.2, random_state=42
            )
            
            self.completion_predictor.fit(X_train, y_train)
            completion_pred = self.completion_predictor.predict(X_test)
            completion_mse = mean_squared_error(y_test, completion_pred)
            
            results['completion_predictor'] = {
                'mse': completion_mse,
                'feature_importance': dict(zip(feature_columns, self.completion_predictor.feature_importances_))
            }
            
            # Train success predictor (binary classification)
            y_success = (training_data['completion_rate'] > 0.7).astype(int)
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y_success, test_size=0.2, random_state=42, stratify=y_success
            )
            
            self.success_predictor.fit(X_train, y_train)
            success_pred = self.success_predictor.predict(X_test)
            success_accuracy = accuracy_score(y_test, success_pred)
            
            results['success_predictor'] = {
                'accuracy': success_accuracy,
                'feature_importance': dict(zip(feature_columns, self.success_predictor.feature_importances_))
            }
            
            # Train engagement predictor
            y_engagement = training_data['final_engagement'].fillna(0.5)
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y_engagement, test_size=0.2, random_state=42
            )
            
            self.engagement_predictor.fit(X_train, y_train)
            engagement_pred = self.engagement_predictor.predict(X_test)
            engagement_mse = mean_squared_error(y_test, engagement_pred)
            
            results['engagement_predictor'] = {
                'mse': engagement_mse,
                'feature_importance': dict(zip(feature_columns, self.engagement_predictor.feature_importances_))
            }
            
            self.is_trained = True
            logger.info("Successfully trained predictive analytics models")
            
            return results
            
        except Exception as e:
            logger.error(f"Error training predictive models: {str(e)}")
            return {'error': str(e)}
    
    async def predict_learning_outcome(
        self, 
        db: Session, 
        user_id: str, 
        course_id: int
    ) -> Optional[PredictiveOutcome]:
        """Predict learning outcome for a user and course."""
        if not self.is_trained:
            logger.warning("Predictive models not trained")
            return None
        
        try:
            # Get user profile and recent behavior
            user_profile = analytics_crud.get_user_learning_profile(db, user_id)
            if not user_profile:
                return None
            
            # Prepare features for prediction
            features = self._prepare_prediction_features(db, user_profile, course_id)
            features_scaled = self.scaler.transform([features])
            
            # Make predictions
            completion_pred = self.completion_predictor.predict(features_scaled)[0]
            success_prob = self.success_predictor.predict_proba(features_scaled)[0][1]
            engagement_pred = self.engagement_predictor.predict(features_scaled)[0]
            
            # Calculate overall outcome score
            outcome_score = (completion_pred * 0.4 + success_prob * 0.4 + engagement_pred * 0.2)
            
            # Determine confidence based on model agreement
            confidence = 1.0 - np.std([completion_pred, success_prob, engagement_pred])
            
            # Identify key factors
            feature_names = [
                'initial_engagement', 'session_frequency', 'avg_session_duration',
                'difficulty_preference', 'learning_style_encoded', 'time_of_day',
                'content_type_preference', 'social_learning_score', 'prior_knowledge'
            ]
            
            # Get feature importance from completion predictor
            importance = self.completion_predictor.feature_importances_
            factors = dict(zip(feature_names, importance))
            
            # Generate recommendations based on predictions
            recommendations = self._generate_outcome_recommendations(
                completion_pred, success_prob, engagement_pred, factors
            )
            
            return PredictiveOutcome(
                user_id=user_id,
                prediction_type="learning_outcome",
                predicted_value=outcome_score,
                confidence=confidence,
                factors=factors,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error predicting learning outcome: {str(e)}")
            return None
    
    async def _prepare_predictive_training_data(self, db: Session) -> pd.DataFrame:
        """Prepare training data for predictive models."""
        # Get all user profiles with sufficient data
        user_profiles = analytics_crud.get_all_user_learning_profiles(db)
        
        training_data = []
        
        for profile in user_profiles:
            # Get user's behavior data from last 90 days
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=90)
            
            behavior_data = analytics_crud.get_user_behavior_data(
                db=db,
                user_id=profile.user_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if len(behavior_data) < 10:  # Need minimum data points
                continue
            
            # Calculate features from behavior data
            session_data = self._analyze_session_patterns(behavior_data)
            
            training_example = {
                'user_id': profile.user_id,
                'initial_engagement': session_data.get('initial_engagement', 0.5),
                'session_frequency': session_data.get('session_frequency', 1.0),
                'avg_session_duration': profile.average_session_duration or 30,
                'difficulty_preference': profile.challenge_preference,
                'learning_style_encoded': self._encode_learning_style(profile.learning_style),
                'time_of_day': session_data.get('preferred_time', 12),
                'content_type_preference': session_data.get('content_preference', 0.5),
                'social_learning_score': session_data.get('social_score', 0.0),
                'prior_knowledge': profile.current_difficulty_level,
                'completion_rate': profile.completion_rate,
                'final_engagement': profile.engagement_score
            }
            
            training_data.append(training_example)
        
        return pd.DataFrame(training_data)
    
    def _analyze_session_patterns(self, behavior_data: List[UserBehaviorData]) -> Dict[str, float]:
        """Analyze session patterns from behavior data."""
        if not behavior_data:
            return {}
        
        # Group by session
        sessions = {}
        for data in behavior_data:
            if data.session_id not in sessions:
                sessions[data.session_id] = []
            sessions[data.session_id].append(data)
        
        # Calculate session metrics
        session_durations = []
        engagement_scores = []
        time_preferences = []
        
        for session_id, session_events in sessions.items():
            if len(session_events) > 1:
                session_events.sort(key=lambda x: x.timestamp)
                duration = (session_events[-1].timestamp - session_events[0].timestamp).total_seconds() / 60
                session_durations.append(duration)
                
                # Calculate engagement for this session
                interactions = len([e for e in session_events if e.event_type == EventType.CONTENT_INTERACTION])
                engagement = min(1.0, interactions / len(session_events))
                engagement_scores.append(engagement)
                
                # Track time preference
                time_preferences.append(session_events[0].timestamp.hour)
        
        return {
            'initial_engagement': engagement_scores[0] if engagement_scores else 0.5,
            'session_frequency': len(sessions) / 30,  # sessions per day over 30 days
            'preferred_time': np.mean(time_preferences) if time_preferences else 12,
            'content_preference': 0.5,  # Would analyze content types
            'social_score': 0.0  # Would analyze social interactions
        }
    
    def _prepare_prediction_features(
        self, 
        db: Session, 
        user_profile: UserLearningProfile, 
        course_id: int
    ) -> List[float]:
        """Prepare features for prediction."""
        # Get recent behavior for initial engagement estimation
        recent_behavior = analytics_crud.get_user_behavior_data(
            db=db,
            user_id=user_profile.user_id,
            start_date=datetime.now(timezone.utc) - timedelta(days=7),
            end_date=datetime.now(timezone.utc),
            limit=100
        )
        
        session_patterns = self._analyze_session_patterns(recent_behavior)
        
        return [
            session_patterns.get('initial_engagement', user_profile.engagement_score),
            session_patterns.get('session_frequency', 1.0),
            user_profile.average_session_duration or 30,
            user_profile.challenge_preference,
            self._encode_learning_style(user_profile.learning_style),
            session_patterns.get('preferred_time', 12),
            session_patterns.get('content_preference', 0.5),
            session_patterns.get('social_score', 0.0),
            user_profile.current_difficulty_level
        ]
    
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
    
    def _generate_outcome_recommendations(
        self,
        completion_pred: float,
        success_prob: float,
        engagement_pred: float,
        factors: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations based on predictions."""
        recommendations = []
        
        if completion_pred < 0.5:
            recommendations.append("Consider breaking content into smaller chunks")
            recommendations.append("Provide additional support materials")
        
        if success_prob < 0.6:
            recommendations.append("Adjust difficulty level to match user capability")
            recommendations.append("Increase interactive elements")
        
        if engagement_pred < 0.5:
            recommendations.append("Add more visual or interactive content")
            recommendations.append("Implement gamification elements")
        
        # Factor-based recommendations
        top_factors = sorted(factors.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for factor, importance in top_factors:
            if factor == 'session_frequency' and importance > 0.2:
                recommendations.append("Encourage more frequent, shorter sessions")
            elif factor == 'difficulty_preference' and importance > 0.2:
                recommendations.append("Adjust content difficulty based on user preference")
        
        return recommendations[:5]  # Limit to top 5 recommendations


class CohortAnalysisEngine:
    """Engine for cohort analysis and learning pattern identification."""
    
    def __init__(self):
        pass
    
    async def analyze_user_cohorts(
        self, 
        db: Session, 
        cohort_type: str = "registration_month",
        time_period_days: int = 90
    ) -> List[CohortAnalysis]:
        """Analyze user cohorts based on specified criteria."""
        try:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=time_period_days)
            
            # Get all user profiles
            user_profiles = analytics_crud.get_all_user_learning_profiles(db)
            
            # Group users into cohorts
            cohorts = self._create_cohorts(user_profiles, cohort_type)
            
            cohort_analyses = []
            
            for cohort_name, cohort_users in cohorts.items():
                if len(cohort_users) < 5:  # Skip small cohorts
                    continue
                
                # Analyze cohort behavior
                cohort_analysis = await self._analyze_cohort_behavior(
                    db, cohort_name, cohort_users, start_date, end_date
                )
                
                cohort_analyses.append(cohort_analysis)
            
            logger.info(f"Analyzed {len(cohort_analyses)} cohorts")
            return cohort_analyses
            
        except Exception as e:
            logger.error(f"Error analyzing cohorts: {str(e)}")
            return []
    
    def _create_cohorts(
        self, 
        user_profiles: List[UserLearningProfile], 
        cohort_type: str
    ) -> Dict[str, List[UserLearningProfile]]:
        """Create cohorts based on specified criteria."""
        cohorts = {}
        
        for profile in user_profiles:
            if cohort_type == "registration_month":
                # Group by registration month (using created_at as proxy)
                cohort_key = profile.created_at.strftime("%Y-%m")
            elif cohort_type == "learning_style":
                # Group by learning style
                cohort_key = profile.learning_style.value
            elif cohort_type == "difficulty_level":
                # Group by preferred difficulty
                cohort_key = profile.preferred_difficulty.value
            elif cohort_type == "engagement_level":
                # Group by engagement level
                if profile.engagement_score >= 0.7:
                    cohort_key = "high_engagement"
                elif profile.engagement_score >= 0.4:
                    cohort_key = "medium_engagement"
                else:
                    cohort_key = "low_engagement"
            else:
                cohort_key = "default"
            
            if cohort_key not in cohorts:
                cohorts[cohort_key] = []
            cohorts[cohort_key].append(profile)
        
        return cohorts
    
    async def _analyze_cohort_behavior(
        self,
        db: Session,
        cohort_name: str,
        cohort_users: List[UserLearningProfile],
        start_date: datetime,
        end_date: datetime
    ) -> CohortAnalysis:
        """Analyze behavior patterns for a specific cohort."""
        
        # Calculate retention rates
        retention_rates = self._calculate_retention_rates(db, cohort_users, start_date, end_date)
        
        # Calculate engagement trends
        engagement_trends = self._calculate_engagement_trends(db, cohort_users, start_date, end_date)
        
        # Identify learning patterns
        learning_patterns = self._identify_cohort_learning_patterns(cohort_users)
        
        # Calculate performance metrics
        performance_metrics = self._calculate_cohort_performance(cohort_users)
        
        return CohortAnalysis(
            cohort_name=cohort_name,
            cohort_size=len(cohort_users),
            time_period=f"{start_date.date()} to {end_date.date()}",
            retention_rates=retention_rates,
            engagement_trends=engagement_trends,
            learning_patterns=learning_patterns,
            performance_metrics=performance_metrics
        )
    
    def _calculate_retention_rates(
        self,
        db: Session,
        cohort_users: List[UserLearningProfile],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """Calculate retention rates for cohort."""
        
        user_ids = [user.user_id for user in cohort_users]
        
        # Calculate weekly retention
        retention_rates = {}
        
        for week in range(1, 13):  # 12 weeks
            week_start = start_date + timedelta(weeks=week-1)
            week_end = week_start + timedelta(weeks=1)
            
            if week_end > end_date:
                break
            
            # Count active users in this week
            active_users = 0
            for user_id in user_ids:
                behavior_data = analytics_crud.get_user_behavior_data(
                    db=db,
                    user_id=user_id,
                    start_date=week_start,
                    end_date=week_end,
                    limit=1
                )
                if behavior_data:
                    active_users += 1
            
            retention_rate = active_users / len(user_ids) if user_ids else 0
            retention_rates[f"week_{week}"] = retention_rate
        
        return retention_rates
    
    def _calculate_engagement_trends(
        self,
        db: Session,
        cohort_users: List[UserLearningProfile],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """Calculate engagement trends for cohort."""
        
        user_ids = [user.user_id for user in cohort_users]
        
        # Calculate monthly engagement
        engagement_trends = {}
        
        current_date = start_date
        month_num = 1
        
        while current_date < end_date:
            month_end = min(current_date + timedelta(days=30), end_date)
            
            total_engagement = 0
            active_users = 0
            
            for user_id in user_ids:
                engagement_metrics = analytics_crud.get_engagement_metrics(
                    db=db,
                    user_id=user_id,
                    start_date=current_date,
                    end_date=month_end
                )
                
                if engagement_metrics:
                    avg_engagement = sum(m.engagement_score for m in engagement_metrics) / len(engagement_metrics)
                    total_engagement += avg_engagement
                    active_users += 1
            
            avg_cohort_engagement = total_engagement / active_users if active_users > 0 else 0
            engagement_trends[f"month_{month_num}"] = avg_cohort_engagement
            
            current_date = month_end
            month_num += 1
        
        return engagement_trends
    
    def _identify_cohort_learning_patterns(
        self, 
        cohort_users: List[UserLearningProfile]
    ) -> Dict[str, Any]:
        """Identify common learning patterns in cohort."""
        
        # Analyze learning styles distribution
        learning_styles = {}
        for user in cohort_users:
            style = user.learning_style.value
            learning_styles[style] = learning_styles.get(style, 0) + 1
        
        # Analyze difficulty preferences
        difficulty_prefs = {}
        for user in cohort_users:
            diff = user.preferred_difficulty.value
            difficulty_prefs[diff] = difficulty_prefs.get(diff, 0) + 1
        
        # Analyze session patterns
        session_durations = [user.average_session_duration for user in cohort_users if user.average_session_duration]
        avg_session_duration = np.mean(session_durations) if session_durations else 0
        
        # Analyze completion patterns
        completion_rates = [user.completion_rate for user in cohort_users]
        avg_completion_rate = np.mean(completion_rates)
        
        return {
            'learning_styles_distribution': learning_styles,
            'difficulty_preferences': difficulty_prefs,
            'avg_session_duration': avg_session_duration,
            'avg_completion_rate': avg_completion_rate,
            'cohort_characteristics': self._identify_cohort_characteristics(cohort_users)
        }
    
    def _calculate_cohort_performance(
        self, 
        cohort_users: List[UserLearningProfile]
    ) -> Dict[str, float]:
        """Calculate performance metrics for cohort."""
        
        completion_rates = [user.completion_rate for user in cohort_users]
        engagement_scores = [user.engagement_score for user in cohort_users]
        consistency_scores = [user.consistency_score for user in cohort_users]
        
        return {
            'avg_completion_rate': np.mean(completion_rates),
            'avg_engagement_score': np.mean(engagement_scores),
            'avg_consistency_score': np.mean(consistency_scores),
            'completion_rate_std': np.std(completion_rates),
            'engagement_score_std': np.std(engagement_scores),
            'high_performers_pct': len([r for r in completion_rates if r > 0.8]) / len(completion_rates),
            'low_performers_pct': len([r for r in completion_rates if r < 0.3]) / len(completion_rates)
        }
    
    def _identify_cohort_characteristics(
        self, 
        cohort_users: List[UserLearningProfile]
    ) -> List[str]:
        """Identify key characteristics of the cohort."""
        characteristics = []
        
        # Analyze engagement levels
        high_engagement = len([u for u in cohort_users if u.engagement_score > 0.7])
        if high_engagement / len(cohort_users) > 0.6:
            characteristics.append("High engagement cohort")
        
        # Analyze completion rates
        high_completion = len([u for u in cohort_users if u.completion_rate > 0.8])
        if high_completion / len(cohort_users) > 0.5:
            characteristics.append("High completion rate cohort")
        
        # Analyze learning styles
        visual_learners = len([u for u in cohort_users if u.learning_style == LearningStyleType.VISUAL])
        if visual_learners / len(cohort_users) > 0.5:
            characteristics.append("Predominantly visual learners")
        
        # Analyze difficulty preferences
        advanced_learners = len([u for u in cohort_users if u.preferred_difficulty == DifficultyLevel.ADVANCED])
        if advanced_learners / len(cohort_users) > 0.4:
            characteristics.append("Advanced difficulty preference")
        
        return characteristics


class RealTimePersonalizationEngine:
    """Engine for real-time personalization adjustments during learning sessions."""
    
    def __init__(self):
        self.session_data = {}  # Store real-time session data
        self.adjustment_thresholds = {
            'low_engagement': 0.3,
            'high_struggle': 0.7,
            'fast_progress': 0.8,
            'attention_drop': 0.4
        }
    
    async def monitor_learning_session(
        self,
        db: Session,
        user_id: str,
        session_id: str,
        event_data: Dict[str, Any]
    ) -> Optional[RealTimePersonalization]:
        """Monitor learning session and provide real-time adjustments."""
        try:
            # Update session data
            if session_id not in self.session_data:
                self.session_data[session_id] = {
                    'user_id': user_id,
                    'start_time': datetime.now(timezone.utc),
                    'events': [],
                    'current_engagement': 0.5,
                    'difficulty_level': 0.5,
                    'content_interactions': 0,
                    'time_on_content': 0,
                    'struggle_indicators': 0,
                    'success_indicators': 0
                }
            
            session = self.session_data[session_id]
            session['events'].append({
                'timestamp': datetime.now(timezone.utc),
                'event_type': event_data.get('event_type'),
                'data': event_data
            })
            
            # Analyze current session state
            session_analysis = self._analyze_current_session(session)
            
            # Determine if adjustments are needed
            adjustments = self._determine_real_time_adjustments(
                db, user_id, session_analysis
            )
            
            if adjustments['adjustments']:
                return RealTimePersonalization(
                    user_id=user_id,
                    session_id=session_id,
                    adjustments=adjustments['adjustments'],
                    trigger_events=adjustments['triggers'],
                    confidence=adjustments['confidence']
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error monitoring learning session: {str(e)}")
            return None
    
    def _analyze_current_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current session state for real-time insights."""
        
        events = session['events']
        if not events:
            return {}
        
        # Calculate session duration
        session_duration = (datetime.now(timezone.utc) - session['start_time']).total_seconds() / 60
        
        # Analyze recent events (last 5 minutes)
        recent_cutoff = datetime.now(timezone.utc) - timedelta(minutes=5)
        recent_events = [e for e in events if e['timestamp'] > recent_cutoff]
        
        # Calculate engagement indicators
        interaction_rate = len([e for e in recent_events if e['event_type'] == 'content_interaction']) / max(1, len(recent_events))
        
        # Calculate struggle indicators
        struggle_events = len([e for e in recent_events if e['event_type'] in ['help_request', 'retry_attempt', 'long_pause']])
        
        # Calculate success indicators
        success_events = len([e for e in recent_events if e['event_type'] in ['correct_answer', 'completion', 'progress']])
        
        # Calculate attention indicators
        attention_events = len([e for e in recent_events if e['event_type'] in ['scroll', 'click', 'focus']])
        attention_score = min(1.0, attention_events / 10)  # Normalize to 0-1
        
        return {
            'session_duration': session_duration,
            'recent_interaction_rate': interaction_rate,
            'struggle_indicators': struggle_events,
            'success_indicators': success_events,
            'attention_score': attention_score,
            'total_events': len(events),
            'recent_events_count': len(recent_events)
        }
    
    def _determine_real_time_adjustments(
        self,
        db: Session,
        user_id: str,
        session_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine what real-time adjustments to make."""
        
        adjustments = {}
        triggers = []
        confidence = 0.0
        
        # Get user profile for context
        user_profile = analytics_crud.get_user_learning_profile(db, user_id)
        
        # Check for low engagement
        if session_analysis.get('recent_interaction_rate', 0) < self.adjustment_thresholds['low_engagement']:
            adjustments['engagement_boost'] = {
                'add_interactive_elements': True,
                'show_progress_indicator': True,
                'suggest_break': session_analysis.get('session_duration', 0) > 45
            }
            triggers.append('low_engagement')
            confidence += 0.3
        
        # Check for struggle indicators
        if session_analysis.get('struggle_indicators', 0) >= self.adjustment_thresholds['high_struggle']:
            adjustments['difficulty_reduction'] = {
                'provide_hints': True,
                'simplify_content': True,
                'offer_alternative_explanation': True,
                'reduce_difficulty_by': 0.1
            }
            triggers.append('high_struggle')
            confidence += 0.4
        
        # Check for fast progress
        if (session_analysis.get('success_indicators', 0) >= self.adjustment_thresholds['fast_progress'] and
            session_analysis.get('recent_interaction_rate', 0) > 0.7):
            adjustments['difficulty_increase'] = {
                'increase_challenge': True,
                'add_bonus_content': True,
                'suggest_advanced_topics': True,
                'increase_difficulty_by': 0.1
            }
            triggers.append('fast_progress')
            confidence += 0.3
        
        # Check for attention drop
        if session_analysis.get('attention_score', 1.0) < self.adjustment_thresholds['attention_drop']:
            adjustments['attention_recovery'] = {
                'change_content_format': True,
                'add_multimedia': True,
                'suggest_short_break': True,
                'gamify_next_section': True
            }
            triggers.append('attention_drop')
            confidence += 0.2
        
        # Personalization based on user profile
        if user_profile:
            if user_profile.learning_style == LearningStyleType.VISUAL and 'engagement_boost' in adjustments:
                adjustments['engagement_boost']['add_visual_elements'] = True
                confidence += 0.1
            
            if user_profile.attention_span and user_profile.attention_span < 20:
                if session_analysis.get('session_duration', 0) > user_profile.attention_span:
                    adjustments['pacing_adjustment'] = {
                        'suggest_break': True,
                        'break_content_into_chunks': True
                    }
                    triggers.append('attention_span_exceeded')
                    confidence += 0.2
        
        return {
            'adjustments': adjustments,
            'triggers': triggers,
            'confidence': min(1.0, confidence)
        }
    
    def cleanup_old_sessions(self, hours_old: int = 24):
        """Clean up old session data to prevent memory leaks."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_old)
        
        sessions_to_remove = []
        for session_id, session_data in self.session_data.items():
            if session_data['start_time'] < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.session_data[session_id]
        
        if sessions_to_remove:
            logger.info(f"Cleaned up {len(sessions_to_remove)} old learning sessions")


class AdvancedAnalyticsService:
    """Main service for advanced analytics features."""
    
    def __init__(self):
        self.predictive_engine = PredictiveAnalyticsEngine()
        self.cohort_engine = CohortAnalysisEngine()
        self.realtime_engine = RealTimePersonalizationEngine()
    
    async def initialize_models(self, db: Session) -> Dict[str, Any]:
        """Initialize and train all advanced analytics models."""
        try:
            # Train predictive models
            predictive_results = await self.predictive_engine.train_predictive_models(db)
            
            logger.info("Advanced analytics models initialized")
            
            return {
                'predictive_models': predictive_results,
                'status': 'initialized'
            }
            
        except Exception as e:
            logger.error(f"Error initializing advanced analytics: {str(e)}")
            return {'error': str(e)}
    
    async def get_learning_outcome_prediction(
        self, 
        db: Session, 
        user_id: str, 
        course_id: int
    ) -> Optional[PredictiveOutcome]:
        """Get predictive analytics for learning outcomes."""
        if not ANALYTICS_ENABLE_PREDICTIVE_MODELS:
            logger.info("Predictive models are disabled in configuration")
            return None
        return await self.predictive_engine.predict_learning_outcome(db, user_id, course_id)
    
    async def analyze_cohorts(
        self, 
        db: Session, 
        cohort_type: str = "registration_month"
    ) -> List[CohortAnalysis]:
        """Perform cohort analysis for learning pattern identification."""
        if not ANALYTICS_ENABLE_COHORT_ANALYSIS:
            logger.info("Cohort analysis is disabled in configuration")
            return []
        return await self.cohort_engine.analyze_user_cohorts(db, cohort_type)
    
    async def process_real_time_event(
        self,
        db: Session,
        user_id: str,
        session_id: str,
        event_data: Dict[str, Any]
    ) -> Optional[RealTimePersonalization]:
        """Process real-time learning event and provide personalization adjustments."""
        if not ANALYTICS_ENABLE_REAL_TIME_PERSONALIZATION:
            logger.info("Real-time personalization is disabled in configuration")
            return None
        return await self.realtime_engine.monitor_learning_session(
            db, user_id, session_id, event_data
        )
    
    def cleanup_session_data(self):
        """Clean up old session data."""
        self.realtime_engine.cleanup_old_sessions()