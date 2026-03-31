from django.shortcuts import render, get_object_or_404, redirect
from .models import Painting, Comments, Likes
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def gallery(request):
    """show all paintings in the gallery"""
    painting = Painting.objects.filter(is_active=True)

    return render(request, "gallery/gallery.html",{
        "painting": painting,
        "user": request.user
    })

@login_required
def uplode_painting(request):
    """"uplode painting function for admin only"""
    if not request.user.is_staff:
        return redirect("index")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        picture = request.FILES.get("painting")
        description = request.POST.get("description")

        if not title or not picture:
            messages.error(request, "العنوان والصورة مطلوبان")
            return redirect("uplode_painting")

        painting = Painting.objects.create(
            title=title,
            picture=picture,
            description=description
            )
        if painting:
            painting.save()
            messages.success(request, "تم رفع اللوحة بنجاح")
            return redirect("gallery")
        else:
            messages.error(request, "حدث خطأ في رفع اللوحة")
            return redirect("uplode_painting")

    return render(request, "gallery/uplode.html")

@login_required
def edit_painting(request, painting_id):
    """edit painting function for admin only"""
    if not request.user.is_staff:
        return redirect("index")

    painting = get_object_or_404(Painting, id=painting_id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        picture = request.FILES.get("painting")
        description = request.POST.get("description")

        if not title:
            messages.error(request, "العنوان مطلوب")
            return redirect("edit_painting", painting_id=painting.id)

        painting.title = title
        painting.description = description
        if picture:
            painting.picture = picture

        painting.save()
        messages.success(request, "تم تحديث اللوحة بنجاح")
        return redirect("gallery")

    return render(request, "gallery/edit.html", {
        "painting": painting
    })

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
    if request.method == "POST":
        painting = get_object_or_404(Painting, id=painting_id)
        comment = request.POST.get("comment", "").strip()

        if comment:
            comment = Comments.objects.create(
                user=request.user,
                painting=painting,
                comment=comment
                )
            messages.success(request, "تم اضافة التعليق بنجاح")
        else:
            messages.error(request, "التعليق لا يمكن ان يكون فارغ")

        return redirect("painting_detail", painting_id=painting_id)


@login_required
def add_like(request, painting_id):
    """"like and unlike function for paintings"""
    if request.method == "POST":
        painting = get_object_or_404(Painting, id=painting_id)
        user = request.user

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

    return render(request, "gallery/painting_detail.html", {
        "painting": painting,
        "comments": comments,
        "likes_count": likes.count()
    })

