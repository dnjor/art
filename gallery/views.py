from django.shortcuts import render
from .models import Painting, Comments, Likes
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def gallery(request):
    painting = Painting.objects.all()
    return render(request, "gallery/gallery.html",{
        "painting": painting,
        "user": request.user
    })

@login_required
def uplode_painting(request):
    if not request.user.is_staff:
        return redirect("index")

    if request.method == "POST":
        title = request.POST.get("title")
        picture = request.FILES.get("painting")
        description = request.POST.get("description")
        painting = Painting.objects.create(title=title, picture=picture, description=description)
        if painting:
            painting.save()
            return redirect("gallery")
        else:
            return render(request, "gallery/uplode.html",{
                "message": "حدث هطأ في رفع اللوحة"
            })
    return render(request, "gallery/uplode.html")

#add edit and delete functions for paintings
#add the comments and likes functions for paintings

