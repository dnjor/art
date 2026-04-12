from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import PaintingForm, CommentForm
from workshop.views import send_email
from .models import Painting, Comments, Likes
from accounts.models import Profile

def gallery(request):
    """show all paintings in the gallery"""
    painting = Painting.objects.filter(is_active=True)

    return render(
        request,
        "gallery/gallery.html",
        {
            "painting": painting,
            "user": request.user
        }
    )

@login_required
def uplode_painting(request):
    """"uplode painting function for admin only"""
    if not request.user.is_staff:
        return redirect("index")

    if request.method == "POST":
        form = PaintingForm(request.POST, request.FILES)

        if not form.is_valid():
            messages.error(request, "العنوان والصورة مطلوبان")
            return redirect("uplode_painting")

        painting = form.save()

        users = Profile.objects.filter(notifications=True).select_related('user')

        subject = f"لوحة جديدة في المعرض: {painting.title}"

        message = f""" مرحباً {users.first().user.username}!

        تم إضافة لوحة جديدة بعنوان  "{painting.title}" إلى معرضنا الفني. 

        يمكنك زيارة المعرض الآن لمشاهدة اللوحة الجديدة وترك رايك عليها:
        http://arwa-art.onrender.com/gallery/{painting.id}/

        مع خالص التحية,
        منصة اروى الفنية
        """

        send_email(
            subject,
            message,
            [user.user.email for user in users]
        )
        messages.success(request, "تم رفع اللوحة بنجاح")
        return redirect("gallery")

    form = PaintingForm()
    return render(
        request,
        "gallery/uplode.html",
        {
            "form": form
        }
    )

@login_required
def edit_painting(request, painting_id):
    """edit painting function for admin only"""
    if not request.user.is_staff:
        return redirect("index")

    painting = get_object_or_404(Painting, id=painting_id)

    if request.method == "POST":
        form = PaintingForm(request.POST, request.FILES, instance=painting)

        if not form.is_valid():
            messages.error(request, "العنوان مطلوب")
            return redirect("edit_painting", painting_id=painting_id)

        form.save()
        messages.success(request, "تم تحديث اللوحة بنجاح")
        return redirect("gallery")

    form = PaintingForm(instance=painting)
    return render(
        request,
        "gallery/edit.html",
        {
            "form": form,
            "painting": painting
        }
    )

@login_required
def delete_painting(request, painting_id):
    """Delete (archive) painting — admin only."""
    if not request.user.is_staff:
        return redirect("index")

    painting = Painting.objects.get(id=painting_id)
    painting.is_active = False
    painting.save()

    messages.success(request, "تم حذف اللوحة بنجاح")
    return redirect("gallery")


@login_required
def add_comment(request, painting_id):
    """add comment function for paintings"""
    painting = get_object_or_404(Painting, id=painting_id)

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.painting = painting
            comment.save()
            messages.success(request, "تم إضافة التعليق بنجاح")
        else:
            messages.error(request, "التعليق لا يمكن ان يكون فارغ")

    return redirect("painting_detail", painting_id=painting_id)


@login_required
def add_like(request, painting_id):
    """"like and unlike function for paintings"""
    painting = get_object_or_404(Painting, id=painting_id)
    user = request.user

    if request.method == "POST":
        like = Likes.objects.filter(user=user, painting=painting)

        if like.exists():
            #unlike
            like.delete()
        else:
            #like
            Likes.objects.create(user=user, painting=painting)

    return redirect("painting_detail", painting_id=painting.id)


def painting_detail(request, painting_id):
    """"show the details of the painting"""
    painting = get_object_or_404(Painting, id=painting_id)
    likes = Likes.objects.filter(painting=painting)
    comments = Comments.objects.filter(painting=painting).order_by("-created_at")

    user_liked = False

    if request.user.is_authenticated:
        user_liked = likes.filter(user=request.user).exists()

    return render(
        request,
        "gallery/painting_detail.html", 
        {
            "painting": painting,
            "comments": comments,
            "likes_count": likes.count(),
            "comments_count": comments.count(),
            "user_liked": user_liked
        }
    )

