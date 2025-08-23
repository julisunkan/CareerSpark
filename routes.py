import os
import zipfile
from flask import render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from app import app
from models import resume_history
from utils.text_extractor import extract_text_from_file
from utils.nlp_analyzer import analyze_resume_vs_job
from utils.grammar_checker import check_grammar
from utils.resume_generator import generate_resume_formats
from utils.scoring import calculate_resume_score

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/offline')
def offline():
    """Offline page for PWA"""
    return render_template('offline.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    
    job_description = request.form.get('job_description', '').strip()
    
    if not job_description:
        flash('Job description is required', 'error')
        return redirect(request.url)
    
    # Check if file was uploaded
    file = request.files.get('resume_file')
    has_file = (file is not None and 
                hasattr(file, 'filename') and 
                file.filename is not None and 
                file.filename != '')
    
    if has_file and file is not None and file.filename is not None and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Extract text from uploaded file
            resume_text = extract_text_from_file(filepath)
            
            if not resume_text.strip():
                flash('Could not extract text from the uploaded file. Please check the file format.', 'error')
                os.remove(filepath)
                return redirect(request.url)
            
            # Analyze resume vs job description with timeout protection
            try:
                analysis = analyze_resume_vs_job(resume_text, job_description)
            except Exception as e:
                flash(f'Error analyzing resume: {str(e)}', 'error')
                os.remove(filepath)
                return redirect(request.url)
            
            # Check grammar with timeout protection
            try:
                grammar_results = check_grammar(resume_text)
            except Exception as e:
                # Use fallback grammar results if service fails
                grammar_results = {
                    'issues': [],
                    'issue_count': 0,
                    'suggestions': ['Grammar checking temporarily unavailable'],
                    'score': 90.0
                }
            
            # Calculate score
            score = calculate_resume_score(analysis, grammar_results)
            
            # Generate optimized resume formats
            optimized_resumes = generate_resume_formats(resume_text, job_description, analysis)
            
            # Save to history
            resume_data = {
                'original_filename': filename,
                'original_text': resume_text,
                'job_description': job_description,
                'analysis': analysis,
                'score': score,
                'suggestions': {
                    'grammar': grammar_results,
                    'keywords': analysis.get('missing_keywords', []),
                    'improvements': analysis.get('suggestions', [])
                },
                'optimized_resumes': optimized_resumes
            }
            
            resume_id = resume_history.save_resume(resume_data)
            
            # Clean up uploaded file
            os.remove(filepath)
            
            return redirect(url_for('analyze', resume_id=resume_id))
            
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
            if os.path.exists(filepath):
                os.remove(filepath)
            return redirect(request.url)
    elif has_file:
        flash('Invalid file type. Please upload PDF, DOCX, or TXT files only.', 'error')
        return redirect(request.url)
    else:
        # No file uploaded - generate resume from job description
        try:
            from utils.resume_generator_from_job import generate_resume_from_job_description
            
            # Generate new resume from job description
            resume_text = generate_resume_from_job_description(job_description)
            
            # Analyze the generated resume vs job description with timeout protection
            try:
                analysis = analyze_resume_vs_job(resume_text, job_description)
            except Exception as e:
                flash(f'Error analyzing generated resume: {str(e)}', 'error')
                return redirect(request.url)
            
            # Check grammar on generated content with timeout protection
            try:
                grammar_results = check_grammar(resume_text)
            except Exception as e:
                # Use fallback grammar results
                grammar_results = {
                    'issues': [],
                    'issue_count': 0,
                    'suggestions': ['Grammar checking temporarily unavailable'],
                    'score': 90.0
                }
            
            # Calculate score
            score = calculate_resume_score(analysis, grammar_results)
            
            # Generate optimized resume formats
            optimized_resumes = generate_resume_formats(resume_text, job_description, analysis)
            
            # Save to history
            resume_data = {
                'original_filename': 'generated_resume.txt',
                'original_text': resume_text,
                'job_description': job_description,
                'analysis': analysis,
                'score': score,
                'suggestions': {
                    'grammar': grammar_results,
                    'keywords': analysis.get('missing_keywords', []),
                    'improvements': analysis.get('suggestions', [])
                },
                'optimized_resumes': optimized_resumes,
                'is_generated': True  # Flag to indicate this was generated
            }
            
            resume_id = resume_history.save_resume(resume_data)
            
            return redirect(url_for('analyze', resume_id=resume_id))
            
        except Exception as e:
            flash(f'Error generating resume: {str(e)}', 'error')
            return redirect(request.url)

@app.route('/analyze/<resume_id>')
def analyze(resume_id):
    resume_data = resume_history.load_by_id(resume_id)
    if not resume_data:
        flash('Resume not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('analyze.html', resume=resume_data)

@app.route('/preview/<resume_id>/<format_type>')
def preview(resume_id, format_type):
    resume_data = resume_history.load_by_id(resume_id)
    if not resume_data:
        flash('Resume not found', 'error')
        return redirect(url_for('index'))
    
    if format_type not in ['chronological', 'functional', 'combination', 'targeted']:
        flash('Invalid format type', 'error')
        return redirect(url_for('analyze', resume_id=resume_id))
    
    optimized_resume = resume_data['optimized_resumes'].get(format_type, {})
    
    return render_template('preview.html', 
                         resume=resume_data, 
                         format_type=format_type,
                         optimized_resume=optimized_resume)

@app.route('/download/<resume_id>/<format_type>/<file_format>')
def download(resume_id, format_type, file_format):
    resume_data = resume_history.load_by_id(resume_id)
    if not resume_data:
        flash('Resume not found', 'error')
        return redirect(url_for('index'))
    
    try:
        from utils.resume_generator import generate_downloadable_resume
        
        filename = generate_downloadable_resume(
            resume_data, format_type, file_format, app.config['DOWNLOAD_FOLDER']
        )
        
        # Get original filename for better download experience
        original_name = resume_data.get('original_filename', 'resume')
        base_name = os.path.splitext(original_name)[0]
        download_name = f'{base_name}_{format_type}.{file_format}'
        
        # Set proper MIME type
        mimetype = 'application/pdf' if file_format == 'pdf' else 'text/plain'
        
        # Use send_file with proper server-side download configuration
        response = send_file(
            filename, 
            as_attachment=True, 
            download_name=download_name,
            mimetype=mimetype
        )
        
        # Clean up file after sending (in a background task or delayed cleanup)
        @response.call_on_close
        def cleanup_file():
            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except Exception:
                pass  # Log error in production
        
        return response
        
    except Exception as e:
        flash(f'Error generating download: {str(e)}', 'error')
        return redirect(url_for('preview', resume_id=resume_id, format_type=format_type))

@app.route('/download_all/<resume_id>')
def download_all(resume_id):
    resume_data = resume_history.load_by_id(resume_id)
    if not resume_data:
        flash('Resume not found', 'error')
        return redirect(url_for('index'))
    
    try:
        from utils.resume_generator import generate_downloadable_resume
        
        # Get original filename for better naming
        original_name = resume_data.get('original_filename', 'resume')
        base_name = os.path.splitext(original_name)[0]
        zip_filename = os.path.join(app.config['DOWNLOAD_FOLDER'], f'{base_name}_all_formats_{resume_id}.zip')
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for format_type in ['chronological', 'functional', 'combination', 'targeted']:
                for file_format in ['pdf', 'txt']:
                    try:
                        filename = generate_downloadable_resume(
                            resume_data, format_type, file_format, app.config['DOWNLOAD_FOLDER']
                        )
                        # Use better names in ZIP file
                        archive_name = f'{base_name}_{format_type}.{file_format}'
                        zipf.write(filename, archive_name)
                        os.remove(filename)  # Clean up individual files
                    except Exception as e:
                        app.logger.warning(f'Failed to generate {format_type} {file_format}: {str(e)}')
        
        # Ensure ZIP file was created and has content
        if not os.path.exists(zip_filename) or os.path.getsize(zip_filename) == 0:
            raise Exception('Failed to create ZIP file with resume formats')
        
        download_name = f'{base_name}_all_formats.zip'
        response = send_file(
            zip_filename, 
            as_attachment=True, 
            download_name=download_name,
            mimetype='application/zip'
        )
        
        # Clean up ZIP file after sending
        @response.call_on_close
        def cleanup_zip():
            try:
                if os.path.exists(zip_filename):
                    os.remove(zip_filename)
            except Exception:
                pass  # Log error in production
        
        return response
        
    except Exception as e:
        flash(f'Error generating ZIP file: {str(e)}', 'error')
        return redirect(url_for('analyze', resume_id=resume_id))

# PWA API endpoints for offline functionality
@app.route('/api/status')
def api_status():
    """API endpoint to check service status"""
    return jsonify({'status': 'online', 'timestamp': '2025-08-23T18:25:00Z'})

@app.route('/api/cleanup', methods=['POST'])
def manual_cleanup():
    """Manual cleanup endpoint for maintenance"""
    try:
        from utils.cleanup import manual_cleanup_now
        results = manual_cleanup_now()
        return jsonify({
            'success': True,
            'message': 'Cleanup completed successfully',
            'results': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Cleanup failed: {str(e)}'
        }), 500

@app.errorhandler(413)
def too_large(e):
    flash('File is too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('upload'))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500