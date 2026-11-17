from django.contrib.auth.models import AbstractUser
from django.shortcuts import render, redirect
from Shared_models.models import *
from .selectors.applications_selectors import *
from .services.applications_services import *
#from .services.measure_services import book_measure
from django.contrib import messages

from .forms import ApplicationCreationForm, ApplicationCategoryForm

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
    if request.method == 'POST':
        if "add_comment" in request.POST:
            comment_text = request.POST.get("text", "").strip()
            try:
                create_comment(comment_text, request.user, application)
                return redirect('application_detail', application_id=application.id)
            except TextEmptyError as ex:
                messages.error(request, str(ex))
            except ApplicationClosedError as ex:
                messages.error(request, str(ex))
            except ApplicationRejectedError as ex:
                messages.error(request, str(ex))
            except DefaultError as ex:
                messages.error(request, str(ex))

        elif "add_hide_comment" in request.POST and request.user.role != CustomUser.Role.CLIENT:
            comment_text = request.POST.get("text", "").strip()
            try:
                create_comment(comment_text, request.user, application, visible=False)
                return redirect('application_detail', application_id=application.id)
            except TextEmptyError as ex:
                messages.error(request, str(ex))
            except ApplicationClosedError as ex:
                messages.error(request, str(ex))
            except ApplicationRejectedError as ex:
                messages.error(request, str(ex))
            except DefaultError as ex:
                messages.error(request, str(ex))
        elif "next_status" in request.POST and request.user.role != CustomUser.Role.CLIENT:
            try:
                toggle_application_status(application, request.user)
                messages.success(request, "Application status moved to the next step.")
                return redirect('application_detail', application_id=application.id)
            except InvalidStatusTransitionError as ex:
                messages.error(request, str(ex))
            except DefaultError as ex:
                messages.error(request, str(ex))


        elif "reject_application" in request.POST and request.user.role != CustomUser.Role.CLIENT:
            try:
                reject_application(application)
                messages.success(request, "Application has been rejected.")
                return redirect('application_detail', application_id=application.id)
            except InvalidStatusTransitionError as ex:
                messages.error(request, str(ex))
            except DefaultError as ex:
                messages.error(request, str(ex))


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

@client_required
def edit_application(request, application_id):
    application = select_application(application_id, request.user)
    if request.method == 'POST':
        form = ApplicationCreationForm(request.POST, instance=application)
        if form.is_valid():
            try:
                updated_application = form.save(commit=False)
                save_application_update(updated_application)
                return redirect("problems:applications_list")
            except TextEmptyError as ex:
                messages.error(request, str(ex))
            except ApplicationClosedError as ex:
                messages.error(request, str(ex))
            except ApplicationRejectedError as ex:
                messages.error(request, str(ex))
            except DefaultError as ex:
                messages.error(request, str(ex))

    else:
        form = ApplicationCreationForm(instance=application)

    return render(request, 'problems/create_application.html',
                  {
                      'form': form,
                      'application': application
                  })


@manager_required
def attach_performer(request, application_id):
    users = select_agents()
    application = select_application(application_id, request.user)

    if request.method == 'POST':
        agent_id = request.POST.get("agent_id", "").strip()
        agent = select_user(agent_id)
        try:
            attach_performer_func(application, agent)
            return redirect('application_detail', application_id=application.id)
        except DefaultError as ex:
            messages.error(request, str(ex))

    return render(request, 'problems/attach_performer.html',
                  {
                      'users': users,
                      'application': application
                  })

@login_required
def profile(request):
    user = request.user
    context = {"user": user}

    if user.role == CustomUser.Role.CLIENT:
        context["applications"] = Application.objects.filter(creator=user).order_by('-created_at')

    elif user.role == CustomUser.Role.AGENT:
        context["assigned_applications"] = Application.objects.filter(performer=user).order_by('-created_at')
        context["resolved_count"] = get_agent_resolved_count(user)

    elif user.role == CustomUser.Role.MANAGER:
        stats = get_manager_statistics()
        context["statuses_stats"] = stats["statuses_stats"]
        context["agents_stats"] = stats["agents_stats"]
        context["all_applications"] = Application.objects.all().order_by('-created_at')

    return render(request, 'problems/profile.html', context)


@manager_required
def create_application_category(request):
    if request.method == 'POST':
        form = ApplicationCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Категорію успішно створено!")
            return redirect('applications_list')
    else:
        form = ApplicationCategoryForm()

    return render(
        request,
        'problems/create_category.html',
        {'form': form}
    )


