from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import PaintingForm, CommentForm
from workshop.views import send_email
from .models import Painting, Comments, Likes
from accounts.models import Profile


def gallery(request):
    return render(
        request,
        "gallery/gallery.html",
    )


@login_required
def uplode_painting(request):
    """ "uplode painting function for admin only"""
    if not request.user.is_staff:
        return redirect("gallery:gallery")

    if request.method == "POST":
        form = PaintingForm(request.POST, request.FILES)

        if not form.is_valid():
            messages.error(request, "العنوان والصورة مطلوبان")
            return redirect("gallery:uplode_painting")

        painting = form.save()

        users = Profile.objects.filter(notifications=True).select_related("user")

        for user in users:

            subject = f"لوحة جديدة في المعرض: {painting.title}"

            message = f""" مرحباً {user.user.username}!

            تم إضافة لوحة جديدة بعنوان  "{painting.title}" إلى معرضنا الفني. 

            يمكنك زيارة المعرض الآن لمشاهدة اللوحة الجديدة وترك رايك عليها:
            http://arwa-art.onrender.com/gallery/{painting.id}/

            مع خالص التحية,
            منصة اروى الفنية
            """

            send_email(subject, message, [user.user.email])

        messages.success(request, "تم رفع اللوحة بنجاح")
        return redirect("gallery:gallery")

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
    if not request.user.is_staff:
        return redirect("gallery:gallery")

    painting = get_object_or_404(Painting, id=painting_id)

    if request.method == "POST":
        form = PaintingForm(request.POST, request.FILES, instance=painting)
        new_picture = request.FILES.get("picture")

        if form.is_valid():
            painting = form.save(commit=False)

            if new_picture:
                painting.picture = new_picture

            painting.save()
            messages.success(request, "تم تحديث اللوحة بنجاح")
            return redirect("gallery:gallery")

        return render(
            request,
            "gallery/edit.html",
            {
                "painting": painting,
                "form": form,
            },
        )
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
    """Delete (archive) painting """
    if not request.user.is_staff:
        return redirect("gallery:gallery")

    painting = Painting.objects.get(id=painting_id)
    painting.is_active = False
    painting.save()

    messages.success(request, "تم حذف اللوحة بنجاح")
    return redirect("gallery:gallery")


@login_required
def add_comment(request, painting_id):
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

    return redirect("gallery:painting_detail", painting_id=painting_id)


@login_required
def add_like(request, painting_id):
    """ "like and unlike function for paintings"""
    painting = get_object_or_404(Painting, id=painting_id)
    user = request.user

    if request.method == "POST":
        like = Likes.objects.filter(user=user, painting=painting)

        if like.exists():
            # unlike
            like.delete()
        else:
            # like
            Likes.objects.create(user=user, painting=painting)

    return redirect("gallery:painting_detail", painting_id=painting.id)


def painting_detail(request, painting_id):
    """ "show the details of the painting"""
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
            "user_liked": user_liked,
        },
    )
