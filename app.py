from flask import Flask, render_template, request, redirect, url_for
from config import Config
from database.db import db
from database.models import Project, Sprint, UserStory  # Import Sprint and UserStory models
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Initialize SQLAlchemy and Flask-Migrate
db.init_app(app)
migrate = Migrate(app, db)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()


@app.route('/')
def button():
    return render_template('button.html')


@app.route('/new_project')
def new_project():
    return render_template('form.html')


@app.route('/create_project', methods=['POST'])
def create_project():
    try:
        # Extract project data from the form
        project_data = {
            'project_id': request.form['project_id'],
            'project_name': request.form['project_name'],
            'project_description': request.form['project_description'],
            'project_owner': request.form['project_owner'],
            'start_date': datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
            'end_date': datetime.strptime(request.form['end_date'], '%Y-%m-%d').date(),
            'revised_end_date': datetime.strptime(request.form.get('revised_end_date'), '%Y-%m-%d').date() if request.form.get('revised_end_date') else None,
            'status': request.form['status']
        }

        # Create and save the project
        project = Project(**project_data)
        db.session.add(project)
        db.session.commit()

        # Save sprints with IDs
        sprint_count = int(request.form.get('sprintCount', 0))
        for i in range(1, sprint_count + 1):
            sprint_id = request.form.get(f'sprint_{i}_id')
            sprint_start_date = request.form.get(f'sprint_{i}_start_date')
            sprint_end_date = request.form.get(f'sprint_{i}_end_date')

            if not sprint_id or not sprint_start_date or not sprint_end_date:
                raise ValueError(f"Missing data for Sprint {i}")

            sprint = Sprint(
                sprint_id=sprint_id,
                start_date=datetime.strptime(sprint_start_date, '%Y-%m-%d').date(),
                end_date=datetime.strptime(sprint_end_date, '%Y-%m-%d').date(),
                project_id=project.project_id
            )
            db.session.add(sprint)

        # Save user stories with IDs
        user_story_count = int(request.form.get('user_stories', 0))
        for i in range(1, user_story_count + 1):
            story_id = request.form.get(f'story_{i}_id')
            story_title = request.form.get(f'story_{i}_title')
            story_efforts = request.form.get(f'story_{i}_efforts')

            if not story_id or not story_title:
                raise ValueError(f"Missing data for User Story {i}")

            user_story = UserStory(
                story_id=story_id,
                title=story_title,
                efforts=int(story_efforts) if story_efforts else None,
                project_id=project.project_id
            )
            db.session.add(user_story)

        # Commit all changes
        db.session.commit()

        return redirect(url_for('new_project'))

    except ValueError as ve:
        db.session.rollback()
        return f"Validation error: {ve}", 400
    except Exception as e:
        db.session.rollback()
        return f"An error occurred: {e}", 400


@app.route('/view_projects')
def view_projects():
    # Fetch all projects with their associated sprints and user stories
    projects = Project.query.all()
    return render_template('view_projects.html', projects=projects)


if __name__ == '__main__':
    app.run(debug=True)
