from Shared_models.models import *
from django.db.models import Case, When, IntegerField
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone

from Shared_models.exeptions import *




def create_comment(text, creator, application, visible=True):
    current_date = timezone.now()
    if not text:
        raise TextEmptyError()
    if application.status == Application.Status.CLOSED:
        raise ApplicationClosedError()

    if application.status == Application.Status.REJECTED:
        raise ApplicationRejectedError()

    Comment.objects.create(
        is_viewable = visible,
        text = text,
        creator = creator,
        created_at = current_date,
        application = application
    )

def save_application_update(application):
    if not application.name:
        raise TextEmptyError()
    if application.status == Application.Status.CLOSED:
        raise ApplicationClosedError()
    if application.status == Application.Status.REJECTED:
        raise ApplicationRejectedError()
    application.save()

def toggle_application_status(application, user):
    current_status = application.status
    if application.status in [Application.Status.CLOSED, Application.Status.REJECTED]:
        raise InvalidStatusTransitionError()

    if current_status == Application.Status.IN_PROGRESS:
        application.status = Application.Status.WAITING_CLIENT

    elif current_status == Application.Status.WAITING_CLIENT:
        application.status = Application.Status.RESOLVED

    elif current_status == Application.Status.RESOLVED:
        application.status = Application.Status.CLOSED
        application.finished_at = timezone.now()  # Фіксуємо час завершення

    else:
        raise InvalidStatusTransitionError("Invalid status transition.")

    application.save()
    return application

def reject_application(application):

    if application.status in [Application.Status.CLOSED, Application.Status.REJECTED]:
        raise InvalidStatusTransitionError("Cannot reject a closed or rejected application.")

    application.status = Application.Status.REJECTED
    application.finished_at = timezone.now()
    application.save()
    return application

def attach_performer_func(application, agent):
    if application.status != Application.Status.NEW:
        raise InvalidStatusTransitionError()

    application.status = Application.Status.IN_PROGRESS
    application.performer = agent

    application.save()

