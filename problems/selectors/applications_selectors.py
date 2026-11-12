from Shared_models.models import *
from django.db.models import Case, When, IntegerField
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db.models import Q


def select_performers():
    return CustomUser.objects.filter(applications_to_do__isnull=False).distinct()


def _apply_filters_and_sorting(applications, status=None, priority=None, category=None, creating_date=None, q=None,
                               order_by="date", order_direction="ASC"):
    if status:
        applications = applications.filter(status=status)
    if priority:
        applications = applications.filter(priority=priority)
    if category:
        applications = applications.filter(category_id=category)
    if creating_date:
        applications = applications.filter(created_at__date=creating_date)
    if q:
        applications = applications.filter(name__icontains=q)

    prefix = "-" if order_direction.upper() == "DESC" else ""

    if order_by == "date" or order_by == "created_at":
        applications = applications.order_by(f"{prefix}created_at")

    elif order_by == "priority":
        priority_order = Case(
            When(priority='critical', then=1),
            When(priority='high', then=2),
            When(priority='medium', then=3),
            When(priority='low', then=4),
            default=5,
            output_field=IntegerField(),
        )

        if order_direction.upper() == "DESC":
            priority_order = Case(
                When(priority='critical', then=4),
                When(priority='high', then=3),
                When(priority='medium', then=2),
                When(priority='low', then=1),
                default=0,
                output_field=IntegerField(),
            )

        applications = applications.annotate(priority_weight=priority_order).order_by("priority_weight")
    else:
        applications = applications.order_by("-created_at")

    return applications


def select_client_applications(user, status=None, priority=None, category=None, creating_date=None, q=None,
                               order_by="date", order_direction="ASC"):
    applications = Application.objects.filter(creator=user)
    return _apply_filters_and_sorting(
        applications, status, priority, category, creating_date, q, order_by, order_direction
    )


def select_agent_applications(agent, status=None, priority=None, category=None, creating_date=None, q=None,
                              order_by="date", order_direction="ASC"):
    applications = Application.objects.filter(Q(status=Application.Status.NEW) | Q(performer=agent))
    return _apply_filters_and_sorting(
        applications, status, priority, category, creating_date, q, order_by, order_direction
    )


def select_manager_applications(status=None, priority=None, category=None, creating_date=None, performer=None, q=None,
                                order_by="date", order_direction="ASC"):
    applications = Application.objects.all()
    if performer:
        applications = applications.filter(performer__username=performer)

    return _apply_filters_and_sorting(
        applications, status, priority, category, creating_date, q, order_by, order_direction
    )

def select_application(application_id, user):
    if user.role == CustomUser.Role.MANAGER:
        return get_object_or_404(Application, id=application_id)

    if user.role == CustomUser.Role.CLIENT:
        return get_object_or_404(Application, id=application_id, creator=user)

    if user.role == CustomUser.Role.AGENT:
        return get_object_or_404(
            Application.objects.filter(
                Q(status=Application.Status.NEW) | Q(performer=user)
            ),
            id=application_id
        )

    raise Http404("U can`t go here")


def get_client_open_applications_count(user):
    open_statuses = [
        Application.Status.NEW,
        Application.Status.IN_PROGRESS,
        Application.Status.WAITING_CLIENT,
    ]

    return Application.objects.filter(
        creator=user,
        status__in=open_statuses
    ).count()


def can_client_create_application(user):
    open_count = get_client_open_applications_count(user)
    return open_count < 5

def select_application_comments(application, user):
    comments = Comment.objects.filter(application=application).order_by("created_at")

    if user.role == CustomUser.Role.CLIENT:
        comments = comments.filter(is_viewable=True)

    return comments