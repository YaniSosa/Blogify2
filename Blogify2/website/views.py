from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db
views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)

#user post creation 
@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')

        if not text:
            flash('Post cannot be empty', category='error')
        else:
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('create_post.html', user=current_user)

#post deletion by user
@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    #checks if there is a post with the id
    post = Post.query.filter_by(id=id).first()

    #checks if post doesnt exist
    if not post:
        flash("Post does not exist.", category='error')
    #checks if current user is the owner of the post
    elif current_user.id != post.id:
        flash('You do not have permission to delete this post.', category='error')
    #deletes post if is owned by user and if post exists
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.home'))


#brings to user's profile to show their post
@views.route("/posts/<username>")
@login_required
def posts(username):
    #checks if user exists
    user = User.query.filter_by(username=username).first()

    #error if user does not exist
    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    #gets post of existing user
    posts = user.posts
    return render_template("posts.html", user=current_user, posts=posts, username=username)


@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    #grab text from post request
    text = request.form.get('text')

    #error if empty
    if not text:
        flash('Comment cannot be empty.', category='error')
    #creates comment
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('views.home'))

#delete comments
@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    #ensures comment exists and belongs to the user
    comment = Comment.query.filter_by(id=comment_id).first()

    #error if comment does not exist
    if not comment:
        flash('Comment does not exist.', category='error')
    #if user is not the author of the comment - no permission to delete
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    #delete comment
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))

#like posts
@views.route("/like-post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    #ensures post exists
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(
        author=current_user.id, post_id=post_id).first()
    
    #error if post does not exist
    if not post:
        return jsonify({'error': 'Post does not exist.'}, 400)
    #if like exists, delete like
    elif like:
        db.session.delete(like)
        db.session.commit()
    #if there is no like, add like
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})