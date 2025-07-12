from flask import Blueprint, render_template, request, redirect, url_for
from app.services.queue_service import get_job_queue, edit_job as edit_job_service, delete_job, add_job

queue_bp = Blueprint('queue', __name__)

@queue_bp.route('/queue')
def queue_page():
    jobs = get_job_queue()
    return render_template('queue.html', jobs=jobs)

@queue_bp.route('/queue/edit/<job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    if request.method == 'POST':
        new_priority = request.form.get('priority')
        new_name = request.form.get('name')
        edit_job_service(job_id, new_priority, new_name)
        return redirect(url_for('queue.queue_page'))
    jobs = get_job_queue()
    job = next((j for j in jobs if str(j.id) == str(job_id) or str(j.id) == job_id), None)
    if job:
        job.name = job.id  # Set name to Job ID for editing
    return render_template('edit_job.html', job=job)

@queue_bp.route('/queue/delete/<job_id>', methods=['POST'])
def delete_job_route(job_id):
    delete_job(job_id)
    return redirect(url_for('queue.queue_page'))

@queue_bp.route('/queue/add', methods=['GET', 'POST'])
def add_job_route():
    if request.method == 'POST':
        name = request.form.get('name')
        priority = request.form.get('priority')
        add_job(name, priority)
        return redirect(url_for('queue.queue_page'))
    return render_template('add_job.html')
