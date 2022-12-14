from email import message
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, send_file
)

from app.auth import login_required
from app.db import get_db

bp = Blueprint('inbox', __name__, url_prefix='/inbox')

@bp.route("/getDB")
@login_required
def getDB():
    return send_file(current_app.config['DATABASE'], as_attachment=True)


@bp.route('/show')
@login_required
def show():
    print(g.user['id'])
    db = get_db()
    messages = db.execute(
        'SELECT m.subject, u.username, m.created, m.body FROM message m, user u where m.to_id = ? and u.id=?', (g.user['id'], g.user['id'])
    ).fetchall()
    

    return render_template('inbox/show.html', messages=messages)


@bp.route('/send', methods=('GET', 'POST'))
@login_required
def send():
    if request.method == 'POST':        
        from_id = g.user['id']
        to_username = request.form['to']
        subject = request.form['subject']
        body = request.form['body']
        print('llega send')
        print(to_username)
        db = get_db()
       
        if not to_username:
            flash('To field is required')
            return render_template('inbox/send.html')
        
        if not subject:
            flash('Subject field is required')
            return render_template('inbox/send.html')
        
        if not body:
            flash('Body field is required')
            return render_template('inbox/send.html')    
        
        error = None    
        userto = None 
        
        userto = db.execute( #query
            'SELECT * FROM user WHERE username = ?' , (to_username,)
        ).fetchone()
        
        if userto is None:
            error = 'Recipient does not exist'
     
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO message (from_id,to_id,subject,body) values(?,?,?,?)',
                (g.user['id'], userto['id'], subject, body)
            )
            db.commit()

            return redirect(url_for('inbox.show'))

    return render_template('inbox/send.html')