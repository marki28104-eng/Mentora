# Umami Analytics Integration

This document describes the Umami analytics integration for privacy-compliant user behavior tracking in Mentora.

## Overview

Umami is a privacy-focused analytics platform that provides insights without compromising user privacy. It doesn't use cookies and is GDPR compliant by default.

## Components

### 1. UmamiTracker Component

The main component that loads the Umami tracking script and provides tracking functionality.

**Location:** `frontend/src/components/UmamiTracker.jsx`

**Features:**
- Automatic page view tracking
- Custom event tracking
- Privacy-compliant (no cookies)
- TypeScript support

**Usage:**
```jsx
import UmamiTracker, { useUmamiTracker } from './components/UmamiTracker';

// In your app
<UmamiTracker 
  websiteId="your-website-id"
  src="https://analytics.umami.is/script.js"
  domains={['localhost', 'mentora.app']}
/>

// In components
const { trackEvent, trackPageView, isLoaded } = useUmamiTracker();
```

### 2. LearningTracker Component

A specialized wrapper that provides learning-specific tracking methods.

**Location:** `frontend/src/components/LearningTracker.jsx`

**Features:**
- Course interaction tracking
- Assessment completion tracking
- Learning behavior analysis
- Time spent tracking

**Usage:**
```jsx
import LearningTracker from './components/LearningTracker';

<LearningTracker>
  {(trackingMethods) => (
    <YourComponent 
      onCourseView={(id, name) => trackingMethods.trackCourseView(id, name)}
      onQuizComplete={(courseId, chapterId, score, time) => 
        trackingMethods.trackQuizComplete(courseId, chapterId, score, time)
      }
    />
  )}
</LearningTracker>
```

## Setup Instructions

### 1. Self-Hosted Umami Server

Run the setup script to start a local Umami server:

```bash
./setup-umami.sh
```

This will:
- Start Umami and PostgreSQL containers
- Generate secure configuration
- Provide access to the dashboard at http://localhost:3001

### 2. Environment Configuration

Update `frontend/.env` with your Umami configuration:

```env
VITE_UMAMI_WEBSITE_ID=your-website-id-here
VITE_UMAMI_SRC=http://localhost:3001/script.js
VITE_UMAMI_DOMAINS=localhost,mentora.app
```

### 3. Create Website in Umami

1. Login to Umami dashboard (http://localhost:3001)
2. Default credentials: admin / umami
3. Create a new website
4. Copy the website ID to your .env file

## Tracked Events

### Automatic Events
- Page views (all routes)
- Learning session starts
- Navigation between pages

### Learning-Specific Events
- `course_view` - When a user views a course
- `chapter_start` - When a user starts a chapter
- `chapter_complete` - When a user completes a chapter
- `quiz_start` - When a user starts a quiz
- `quiz_complete` - When a user completes a quiz
- `quiz_answer` - Individual quiz answers
- `content_interaction` - Interactions with course content
- `time_spent` - Time spent on different content types
- `difficulty_change` - When user changes difficulty settings
- `search_query` - Search interactions
- `course_creation` - When users create new courses

### Event Data Structure

Events include contextual data such as:
- Course and chapter IDs
- User type (premium/free)
- Content types
- Performance metrics
- Timestamps

## Privacy Compliance

### GDPR Compliance
- No cookies used
- No personal identifiers stored
- Data anonymization by default
- User consent management ready

### Data Collection
- Only behavioral data collected
- No PII (Personally Identifiable Information)
- Aggregated analytics only
- User-controlled data deletion

## Integration Points

### Frontend Integration
The tracking is integrated at the App level and provides:
- Automatic page view tracking
- Learning-specific event tracking
- Real-time analytics data collection

#### Implemented Tracking Events

**Course Interactions:**
- `course_view` - Tracked in CourseView.jsx when course is loaded
- `chapter_start` - Tracked when user navigates to a chapter
- `chapter_view` - Tracked in ChapterView.jsx when chapter is loaded

**Content Interactions:**
- `content_interaction` - Tracked when users switch tabs in chapters
- `quiz_start` - Tracked when quiz questions are loaded
- `quiz_answer` - Tracked when users answer quiz questions

**User Actions:**
- `course_creation` - Tracked when users create new courses
- `dashboard_view` - Tracked when users visit the dashboard

**Navigation:**
- Automatic page view tracking on route changes
- Learning session start tracking

### Backend Integration (Future)
Planned backend integration will include:
- Analytics data processing service
- Learning pattern analysis
- Personalization engine
- Recommendation system

## Development

### Testing
Use the example component to test tracking:
```jsx
import UmamiTrackingExample from './components/examples/UmamiTrackingExample';
```

### Debugging
Check browser console for tracking events and Umami status.

### Production Deployment
For production, replace the local Umami server with:
- Umami Cloud (https://umami.is)
- Self-hosted Umami on your infrastructure
- Update VITE_UMAMI_SRC accordingly

## Requirements Fulfilled

This implementation addresses the following requirements:

- **4.1**: Privacy-compliant analytics without cookies or personal identifiers
- **4.2**: GDPR compliance and user privacy protection
- **1.1-1.3**: User interaction and learning pattern tracking
- **5.1-5.4**: Foundation for learning analytics and progress visualization

## Next Steps

1. Complete backend analytics processing service
2. Implement personalization engine
3. Add learning pattern analysis
4. Create analytics dashboard for users
5. Implement A/B testing framework