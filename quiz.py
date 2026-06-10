from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from models import db, Quiz, Question, Score
from datetime import datetime

quiz = Blueprint('quiz', __name__)


@quiz.route('/dashboard')
@login_required
def dashboard():
    all_quizzes = Quiz.query.order_by(Quiz.created_at.desc()).all()
    my_scores = Score.query.filter_by(user_id=current_user.id).all()
    attempted_quiz_ids = [s.quiz_id for s in my_scores]
    return render_template('dashboard.html',
                           quizzes=all_quizzes,
                           attempted_quiz_ids=attempted_quiz_ids)


@quiz.route('/create', methods=['GET', 'POST'])
@login_required
def create_quiz():
    if request.method == 'POST':
        title = request.form.get('title').strip()
        topic = request.form.get('topic').strip()

        if not title or not topic:
            flash('Title and topic are required.', 'error')
            return redirect(url_for('quiz.create_quiz'))

        new_quiz = Quiz(
            title=title,
            topic=topic,
            created_by=current_user.id
        )
        db.session.add(new_quiz)
        db.session.commit()

        return redirect(url_for('quiz.add_questions', quiz_id=new_quiz.id))

    return render_template('create_quiz.html')


@quiz.route('/quiz/<int:quiz_id>/add-questions', methods=['GET', 'POST'])
@login_required
def add_questions(quiz_id):
    current_quiz = Quiz.query.get_or_404(quiz_id)

    if current_quiz.created_by != current_user.id:
        flash('You can only add questions to your own quizzes.', 'error')
        return redirect(url_for('quiz.dashboard'))

    if request.method == 'POST':
        question_text = request.form.get('question_text').strip()
        option_a = request.form.get('option_a').strip()
        option_b = request.form.get('option_b').strip()
        option_c = request.form.get('option_c').strip()
        option_d = request.form.get('option_d').strip()
        correct_answer = request.form.get('correct_answer')

        new_question = Question(
            quiz_id=quiz_id,
            question_text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct_answer
        )
        db.session.add(new_question)
        db.session.commit()

        flash('Question added!', 'success')
        return redirect(url_for('quiz.add_questions', quiz_id=quiz_id))

    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('add_questions.html',
                           quiz=current_quiz,
                           questions=questions)


@quiz.route('/quiz/<int:quiz_id>/attempt')
@login_required
def attempt_quiz(quiz_id):
    current_quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if not questions:
        flash('This quiz has no questions yet.', 'error')
        return redirect(url_for('quiz.dashboard'))

    return render_template('attempt_quiz.html',
                           quiz=current_quiz,
                           questions=questions)


@quiz.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    current_quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    score = 0
    total = len(questions)

    for question in questions:
        selected = request.form.get(f'question_{question.id}')
        if selected and selected == question.correct_answer:
            score += 1

    # Save score
    new_score = Score(
        user_id=current_user.id,
        quiz_id=quiz_id,
        score=score,
        total=total
    )
    db.session.add(new_score)
    db.session.commit()

    return redirect(url_for('quiz.result', quiz_id=quiz_id, score=score, total=total))


@quiz.route('/quiz/<int:quiz_id>/result')
@login_required
def result(quiz_id):
    current_quiz = Quiz.query.get_or_404(quiz_id)
    score = request.args.get('score', 0, type=int)
    total = request.args.get('total', 0, type=int)
    percent = round((score / total) * 100) if total > 0 else 0

    return render_template('result.html',
                           quiz=current_quiz,
                           score=score,
                           total=total,
                           percent=percent)


@quiz.route('/history')
@login_required
def history():
    scores = Score.query.filter_by(user_id=current_user.id)\
             .order_by(Score.attempted_at.desc()).all()
    return render_template('history.html', scores=scores)


@quiz.route('/analytics')
@login_required
def analytics():
    scores = Score.query.filter_by(user_id=current_user.id).all()

    # Topic wise performance
    topic_data = {}
    for s in scores:
        topic = s.quiz.topic
        if topic not in topic_data:
            topic_data[topic] = {'total_score': 0, 'total_questions': 0, 'attempts': 0}
        topic_data[topic]['total_score'] += s.score
        topic_data[topic]['total_questions'] += s.total
        topic_data[topic]['attempts'] += 1

    # Calculate percentage per topic
    topic_performance = []
    weak_topics = []

    for topic, data in topic_data.items():
        percent = round((data['total_score'] / data['total_questions']) * 100)
        topic_performance.append({
            'topic': topic,
            'percent': percent,
            'attempts': data['attempts']
        })
        if percent < 50:
            weak_topics.append(topic)

    return render_template('analytics.html',
                           topic_performance=topic_performance,
                           weak_topics=weak_topics)