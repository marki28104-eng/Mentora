/**
 * Dashboard Service for personalized dashboard API calls
 */

import { apiWithCookies } from './baseApi';

class DashboardService {
  /**
   * Get comprehensive personalized dashboard data
   */
  async getPersonalizedDashboard() {
    try {
      const response = await apiWithCookies.get('/dashboard/personalized');
      return response.data;
    } catch (error) {
      console.error('Error fetching personalized dashboard:', error);
      throw error;
    }
  }

  /**
   * Get personalized learning path recommendations
   */
  async getLearningPathRecommendations(courseId = null, maxRecommendations = 5) {
    try {
      const params = new URLSearchParams();
      if (courseId) params.append('course_id', courseId);
      params.append('max_recommendations', maxRecommendations);

      const response = await apiWithCookies.get(`/dashboard/recommendations/learning-path?${params}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching learning path recommendations:', error);
      throw error;
    }
  }

  /**
   * Get adaptive content suggestions for struggling areas
   */
  async getAdaptiveContentSuggestions(strugglingAreas, maxSuggestions = 10) {
    try {
      const response = await apiWithCookies.post('/dashboard/suggestions/adaptive-content', {
        struggling_areas: strugglingAreas,
        max_suggestions: maxSuggestions
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching adaptive content suggestions:', error);
      throw error;
    }
  }

  /**
   * Get learning progress insights
   */
  async getLearningProgressInsights() {
    try {
      const response = await apiWithCookies.get('/dashboard/insights/learning-progress');
      return response.data;
    } catch (error) {
      console.error('Error fetching learning progress insights:', error);
      throw error;
    }
  }

  /**
   * Get next learning actions
   */
  async getNextLearningActions() {
    try {
      const response = await apiWithCookies.get('/dashboard/actions/next-steps');
      return response.data;
    } catch (error) {
      console.error('Error fetching next learning actions:', error);
      throw error;
    }
  }

  /**
   * Get learning style information
   */
  async getLearningStyleInfo() {
    try {
      const response = await apiWithCookies.get('/dashboard/profile/learning-style');
      return response.data;
    } catch (error) {
      console.error('Error fetching learning style info:', error);
      throw error;
    }
  }

  /**
   * Get personalized metrics
   */
  async getPersonalizedMetrics() {
    try {
      const response = await apiWithCookies.get('/dashboard/metrics/personalized');
      return response.data;
    } catch (error) {
      console.error('Error fetching personalized metrics:', error);
      throw error;
    }
  }
}

const dashboardService = new DashboardService();
export default dashboardService;