from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import ForumPost, ForumReply
from forms import PostForm, ReplyForm

community_bp = Blueprint('community', __name__)


@community_bp.route('/')
@login_required
def forums():
    category = request.args.get('category', '')
    query = ForumPost.query
    if category:
        query = query.filter_by(category=category)
    posts = query.order_by(ForumPost.pinned.desc(), ForumPost.created_at.desc()).limit(30).all()
    return render_template('community/forums.html', posts=posts, category=category)


@community_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def thread(post_id):
    post = ForumPost.query.get_or_404(post_id)
    form = ReplyForm()
    if form.validate_on_submit():
        reply = ForumReply(post_id=post.id, user_id=current_user.id, body=form.body.data)
        db.session.add(reply)
        db.session.commit()
        flash('Reply posted!', 'success')
        return redirect(url_for('community.thread', post_id=post.id))
    replies = ForumReply.query.filter_by(post_id=post.id).order_by(ForumReply.created_at.asc()).all()
    return render_template('community/thread.html', post=post, replies=replies, form=form)


@community_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = ForumPost(user_id=current_user.id, title=form.title.data,
                        body=form.body.data, category=form.category.data)
        db.session.add(post)
        db.session.commit()
        flash('Post created!', 'success')
        return redirect(url_for('community.thread', post_id=post.id))
    return render_template('community/new_post.html', form=form)


@community_bp.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('community.forums'))
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'info')
    return redirect(url_for('community.forums'))
