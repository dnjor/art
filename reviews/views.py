from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from pathlib import Path
from json import loads
import base64

from .models import Review

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


@login_required
def reviews_list(request):
    if not request.user.is_staff:
        return redirect("accounts:index")

    if request.method == "POST":
        review_id = request.POST.get("review_id")
        status = request.POST.get("status")

        if not status or not review_id:
            messages.error(request, "حدث خطاء في تحديث حالة التقييم")
            return redirect("reviews:reviews_list")

        review = get_object_or_404(Review, id=review_id)
        review.status = status
        review.save()

        messages.success(request, "تم تحديث حالة التقييم بنجاح")
        return redirect("reviews:reviews_list")

    reviews = Review.objects.all()

    for review in reviews:
        review.star_range = range(max(int(review.average or 0), 0))

    return render(request, "reviews/reviews_list.html", {"reviews": reviews})


@staff_member_required
@login_required
def sync_review_from_sheet(request):
    """when the admin want to update the new reviews"""
    import_reviews_from_sheet()
    messages.success(request, "تم تحديث التقيمات")
    return redirect("reviews:reviews_list")


def get_google_credentials():
    # First: try JSON from environment (best for Render)

    if settings.GOOGLE_SHEETS_CREDENTIALS_JSON:

        return Credentials.from_service_account_info(

            loads(settings.GOOGLE_SHEETS_CREDENTIALS_JSON),

            scopes=SCOPES

        )

    # Second: try local file (best for local development)
    if settings.GOOGLE_SHEETS_CREDENTIALS_FILE:

        credentials_path = Path(settings.BASE_DIR) / settings.GOOGLE_SHEETS_CREDENTIALS_FILE
        print(credentials_path)
        return Credentials.from_service_account_file(

            str(credentials_path),

            scopes=SCOPES

        )

    raise ValueError("Google Sheets credentials are missing")


def get_raw_sheet_data():
    credentials = get_google_credentials()

    service = build("sheets", "v4", credentials=credentials)

    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=settings.GOOGLE_SHEET_ID,
            range=settings.GOOGLE_SHEET_RANGE,
            majorDimension="ROWS",
        )
        .execute()
    )

    return result


def print_result(result):
    data = result["values"]
    header = data[0]
    first_row = data[1]

    for question, answer in zip(header, first_row):
        print(f"{question}: {answer}")


TIMESTAMP_INDEX = 0
NAME_INDEX = 1
SHOW_NAME_INDEX = 2
RATING_1_INDEX = 3
RATING_2_INDEX = 4
RATING_3_INDEX = 5
RATING_4_INDEX = 6
RATING_5_INDEX = 7
COMMENT_INDEX = 8

ALLOW_NAME_VALUES = "يمكنك عرض الاسم"


def get_cell(row, index, default=""):
    if index < len(row):
        return str(row[index]).strip()
    return default


def to_int(value):
    return int(str(value).strip())


def import_reviews_from_sheet():

    result = get_raw_sheet_data()
    rows = result.get("values", [])

    if len(rows) <= 1:
        return

    for row in rows[1:]:  # skip header
        if not any(str(cell).strip() for cell in row):
            continue

        timestamp_value = get_cell(row, TIMESTAMP_INDEX)
        if not timestamp_value:
            continue

        # إذا الرد موجود مسبقًا، تجاهله
        if Review.objects.filter(source_timestamp=timestamp_value).exists():
            continue

        name_value = get_cell(row, NAME_INDEX)
        show_name_value = get_cell(row, SHOW_NAME_INDEX).strip().lower()
        comment_value = get_cell(row, COMMENT_INDEX, "")

        if show_name_value == ALLOW_NAME_VALUES:
            review_name_value = name_value
        else:
            review_name_value = " "

        try:
            rating_1_value = to_int(get_cell(row, RATING_1_INDEX))
            rating_2_value = to_int(get_cell(row, RATING_2_INDEX))
            rating_3_value = to_int(get_cell(row, RATING_3_INDEX))
            rating_4_value = to_int(get_cell(row, RATING_4_INDEX))
            rating_5_value = to_int(get_cell(row, RATING_5_INDEX))
        except (ValueError, TypeError):
            continue

        Review.objects.create(
            source_timestamp=timestamp_value,
            review_name=review_name_value,
            rating_1=rating_1_value,
            rating_2=rating_2_value,
            rating_3=rating_3_value,
            rating_4=rating_4_value,
            rating_5=rating_5_value,
            comment=comment_value,
            status="pending",
        )
