from django.contrib.auth.models import AbstractUser
from django.shortcuts import render, redirect
from Shared_models.models import *
from .selectors.applications_selectors import *
#from .services.measure_services import book_measure
from django.contrib import messages

from .forms import ApplicationCreationForm

from django.contrib.auth.decorators import login_required
from .decorators import staff_required, manager_required, client_required

def home(request):
    return render(request, "problems/home.html")


@login_required
def applications_list(request):
    q = request.GET.get("q", "").strip()
    order_by = request.GET.get("order_by", "").strip()
    order_direction = request.GET.get("order_direction", "").strip()
    created_date = request.GET.get("created_date", "").strip()
    status = request.GET.get("status", "").strip()
    priority = request.GET.get("priority", "").strip()
    category = request.GET.get("category", "").strip()

    priorities = Application.Priority.choices
    statuses = Application.Status.choices
    categories = Application_category.objects.all()

    user_role = request.user.role


    context = {
        "order_by": order_by,
        "order_direction": order_direction,
        "created_date": created_date,
        "status": status,
        "priority": priority,
        "category": category,
        "priorities": priorities,
        "statuses": statuses,
        "categories": categories,
        "query": q,
    }

    if user_role == CustomUser.Role.CLIENT:
        context["applications"] = select_client_applications(
            user=request.user,
            status=status,
            priority=priority,
            category=category,
            creating_date=created_date,
            q=q,
            order_by=order_by,
            order_direction=order_direction
        )

    elif user_role == CustomUser.Role.AGENT:
        context["applications"] = select_agent_applications(
            agent=request.user,
            status=status, priority=priority, category=category,
            creating_date=created_date, q=q, order_by=order_by, order_direction=order_direction
        )

    elif user_role == CustomUser.Role.MANAGER:
        performer_username = request.GET.get("performer", "").strip()
        context["performer"] = performer_username
        context["performers"] = select_performers()

        context["applications"] = select_manager_applications(
            status=status, priority=priority, category=category,
            creating_date=created_date, q=q, order_by=order_by,
            order_direction=order_direction, performer=performer_username
        )
    else:
        context["applications"] = []

    return render(request, "problems/applications_list.html", context)

@login_required
def application_detail(request, application_id):
    application = select_application(application_id, request.user)
    comments = select_application_comments(application, request.user)
    return render(
        request,
        "problems/application_detail.html",
        {
            "application": application,
            "comments": comments
        }
    )

@client_required
def create_application(request):
    if request.method == 'POST':
        if not can_client_create_application(request.user):
            messages.error(request, "You can`t have more then 5")
            return redirect('applications_list')

        form = ApplicationCreationForm(request.POST)
        if form.is_valid():
            form.save(creator=request.user)
            messages.success(request, "Success")
            return redirect('applications_list')


    else:
        form = ApplicationCreationForm()

    return render(request, 'problems/create_application.html', {'form': form})


