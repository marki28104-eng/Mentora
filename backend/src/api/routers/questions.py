from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from ...db.database import get_db
from ..schemas.questions import QuestionResponse
from ...db.crud import questions_crud
from ...db.models.db_course import Chapter, PracticeQuestion
from ...db.models.db_user import User
from ...utils.auth import get_current_active_user
from ...services.course_service import verify_course_ownership
from ...services.adaptive_assessment_service import AdaptiveAssessmentService
from .courses import agent_service



router = APIRouter(
    prefix="/chapters",
    tags=["chapters"],
    responses={404: {"description": "Not found"}},
)

# Initialize adaptive assessment service
adaptive_assessment_service = AdaptiveAssessmentService()

def get_practice_questions(questions: List[PracticeQuestion]) -> List[QuestionResponse]:
    """
    Helper function to convert list of PracticeQuestion objects to list of QuestionResponse objects.
    """
    return [
        QuestionResponse(
            id=q.id,
            type=q.type,
            question=q.question,
            answer_a=q.answer_a,
            answer_b=q.answer_b,
            answer_c=q.answer_c,
            answer_d=q.answer_d,
            correct_answer=q.correct_answer,
            explanation=q.explanation,
            users_answer=q.users_answer,
            points_received=q.points_received,
            feedback=q.feedback
        ) for q in questions
    ]


@router.get("/{course_id}/chapters/{chapter_id}")
async def get_questions_by_chapter_id(
        course_id: int,
        chapter_id: int,
        adaptive: bool = True,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Get questions for a chapter with optional adaptive difficulty adjustment.
    """
    course = await verify_course_ownership(course_id, str(current_user.id), db)
    # Find the specific chapter
    chapter = (db.query(Chapter)
               .filter(Chapter.id == chapter_id, Chapter.course_id == course_id)
               .first())

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found in this course"
        )
    if not chapter.questions:
        return {"questions": [], "adaptive": False}

    if adaptive:
        # Create adaptive assessment session
        assessment_session = await adaptive_assessment_service.create_adaptive_assessment(
            db=db,
            user_id=str(current_user.id),
            chapter_id=chapter_id,
            assessment_type="practice"
        )
        
        if assessment_session:
            # Get all adaptive questions
            adaptive_questions = []
            for i in range(len(assessment_session.questions)):
                question_data = await adaptive_assessment_service.get_next_question(
                    db=db,
                    session=assessment_session
                )
                if question_data:
                    adaptive_questions.append(question_data)
            
            return {
                "questions": adaptive_questions,
                "adaptive": True,
                "session_id": assessment_session.session_id,
                "difficulty_adjustments": assessment_session.difficulty_adjustments
            }
    
    # Fallback to standard questions
    return {
        "questions": get_practice_questions(chapter.questions),
        "adaptive": False
    }

@router.get("/{course_id}/chapters/{chapter_id}/{question_id}/save", response_model=QuestionResponse)
async def save_answer(
        course_id: int,
        chapter_id: int,
        question_id: int,
        users_answer: str,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """ Save a user's answer to a question. Also saves user answer plus feedback in the database. """
    course = await verify_course_ownership(course_id, str(current_user.id), db)

    # Find the question first
    question = (db.query(PracticeQuestion)
                .filter(PracticeQuestion.id == question_id)
                .first())

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # Update question in db
    questions_crud.update_question(
        db,
        question_id,
        users_answer=users_answer
    )

    # Refresh question from db to get updated data
    db.refresh(question)

    # Return the updated question as QuestionResponse
    return QuestionResponse(
        id=question.id,
        type=question.type,
        question=question.question,
        answer_a=question.answer_a,
        answer_b=question.answer_b,
        answer_c=question.answer_c,
        answer_d=question.answer_d,
        correct_answer=question.correct_answer,
        explanation=question.explanation,
        users_answer=question.users_answer,
        points_received=question.points_received,
        feedback=question.feedback
    )

@router.get("/{course_id}/chapters/{chapter_id}/{question_id}/feedback", response_model=QuestionResponse)
async def get_feedback(
    course_id: int,
    chapter_id: int,
    question_id: int,
    users_answer: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """ Get feedback on an open text question. Also saves user answer plus feedback in the database. """
    course = await verify_course_ownership(course_id, str(current_user.id), db)

    # Find the question
    question = (db.query(PracticeQuestion)
                .filter(question_id == PracticeQuestion.id)
                .first())

    # Get feedback from grader
    points, feedback = await agent_service.grade_question(
        user_id=current_user.id,
        course_id=course_id,
        question=question.question,
        correct_answer=question.correct_answer,
        users_answer=users_answer,
        chapter_id=chapter_id,
        db=db
    )

    # Update question in db
    questions_crud.update_question(
        db,
        question_id,
        users_answer=users_answer,
        points_received=points,
        feedback=feedback,
    )

    return QuestionResponse(
        id=question_id,
        type=question.type,
        question=question.question,
        answer_a=question.answer_a,
        answer_b=question.answer_b,
        answer_c=question.answer_c,
        answer_d=question.answer_d,
        correct_answer=question.correct_answer,
        explanation=question.explanation,
        users_answer=question.users_answer,
        points_received=question.points_received,
        feedback=question.feedback
    )


# -------- ADAPTIVE ASSESSMENT ENDPOINTS ----------

@router.post("/{course_id}/chapters/{chapter_id}/adaptive-assessment")
async def create_adaptive_assessment(
        course_id: int,
        chapter_id: int,
        assessment_type: str = "practice",
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Create a new adaptive assessment session for a chapter.
    """
    await verify_course_ownership(course_id, str(current_user.id), db)
    
    assessment_session = await adaptive_assessment_service.create_adaptive_assessment(
        db=db,
        user_id=str(current_user.id),
        chapter_id=chapter_id,
        assessment_type=assessment_type
    )
    
    if not assessment_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No questions available for adaptive assessment"
        )
    
    return {
        "session_id": assessment_session.session_id,
        "chapter_id": chapter_id,
        "total_questions": len(assessment_session.questions),
        "difficulty_adjustments": assessment_session.difficulty_adjustments,
        "adaptive_features": assessment_session.real_time_adaptation
    }


@router.get("/adaptive-sessions/{session_id}/next-question")
async def get_next_adaptive_question(
        session_id: str,
        previous_answer: Optional[Dict[str, Any]] = None,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Get the next question in an adaptive assessment session.
    """
    # Note: In a real implementation, you'd store and retrieve sessions
    # For now, we'll create a simple response structure
    
    # This would typically retrieve the session from storage
    # For demonstration, we'll return a structured response
    
    return {
        "message": "Adaptive question endpoint - session storage needed for full implementation",
        "session_id": session_id,
        "note": "This endpoint requires session storage implementation"
    }


@router.post("/{course_id}/chapters/{chapter_id}/supplementary-practice")
async def get_supplementary_practice(
        course_id: int,
        chapter_id: int,
        struggling_topics: List[str],
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Get supplementary practice recommendations for struggling topics.
    """
    await verify_course_ownership(course_id, str(current_user.id), db)
    
    recommendations = await adaptive_assessment_service.get_supplementary_practice(
        db=db,
        user_id=str(current_user.id),
        chapter_id=chapter_id,
        struggling_topics=struggling_topics
    )
    
    return {
        "chapter_id": chapter_id,
        "struggling_topics": struggling_topics,
        "recommendations": recommendations,
        "total_recommendations": len(recommendations)
    }


@router.post("/{course_id}/chapters/{chapter_id}/assessment-feedback")
async def submit_assessment_feedback(
        course_id: int,
        chapter_id: int,
        question_id: int,
        user_answer: str,
        time_taken: int,
        session_id: Optional[str] = None,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Submit assessment feedback for real-time difficulty adjustment.
    """
    await verify_course_ownership(course_id, str(current_user.id), db)
    
    # Get the question to check correctness
    question = questions_crud.get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Determine if answer is correct
    is_correct = False
    if question.type == "MC":
        is_correct = user_answer.strip().upper() == question.correct_answer.strip().upper()
    elif question.type == "OT":
        # For open text, we'd need more sophisticated checking
        # For now, we'll use a simple similarity check
        is_correct = user_answer.lower().strip() in question.correct_answer.lower()
    
    # Save the answer
    questions_crud.update_question(
        db,
        question_id,
        users_answer=user_answer
    )
    
    # Prepare feedback response
    feedback_response = {
        "question_id": question_id,
        "is_correct": is_correct,
        "correct_answer": question.correct_answer,
        "explanation": question.explanation,
        "time_taken": time_taken,
        "performance_feedback": {
            "accuracy": "correct" if is_correct else "incorrect",
            "time_efficiency": "good" if time_taken < 120 else "could_improve",
            "next_difficulty": "maintain" if is_correct else "reduce"
        }
    }
    
    # If part of an adaptive session, this would trigger real-time adjustments
    if session_id:
        feedback_response["session_id"] = session_id
        feedback_response["adaptive_adjustments"] = {
            "difficulty_change": -0.1 if not is_correct else 0.05,
            "time_adjustment": 1.2 if not is_correct else 0.9,
            "support_level": "increased" if not is_correct else "maintained"
        }
    
    return feedback_response



