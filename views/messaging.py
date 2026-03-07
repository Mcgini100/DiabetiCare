from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Message, User
from forms import MessageForm

messaging_bp = Blueprint('messaging', __name__)


@messaging_bp.route('/')
@login_required
def inbox():
    received = Message.query.filter_by(recipient_id=current_user.id)\
        .order_by(Message.created_at.desc()).limit(30).all()
    sent = Message.query.filter_by(sender_id=current_user.id)\
        .order_by(Message.created_at.desc()).limit(30).all()
    unread_count = Message.query.filter_by(recipient_id=current_user.id, read=False).count()
    return render_template('messaging/inbox.html', received=received, sent=sent, unread_count=unread_count)


@messaging_bp.route('/compose', methods=['GET', 'POST'])
@login_required
def compose():
    form = MessageForm()
    if form.validate_on_submit():
        recipient = User.query.filter_by(email=form.recipient_email.data.lower()).first()
        if not recipient:
            flash('Recipient not found.', 'warning')
        elif recipient.id == current_user.id:
            flash('You cannot message yourself.', 'warning')
        else:
            msg = Message(sender_id=current_user.id, recipient_id=recipient.id,
                         subject=form.subject.data, body=form.body.data)
            db.session.add(msg)
            db.session.commit()
            flash('Message sent!', 'success')
            return redirect(url_for('messaging.inbox'))
    return render_template('messaging/compose.html', form=form)


@messaging_bp.route('/read/<int:msg_id>')
@login_required
def read(msg_id):
    msg = Message.query.get_or_404(msg_id)
    if msg.recipient_id != current_user.id and msg.sender_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('messaging.inbox'))
    if msg.recipient_id == current_user.id and not msg.read:
        msg.read = True
        db.session.commit()
    return render_template('messaging/read.html', msg=msg)
