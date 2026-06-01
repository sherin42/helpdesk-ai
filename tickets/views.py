from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import TicketForm, DepartmentForm, CommentForm
from .models import Ticket, Department, Comment, TicketHistory
from accounts.models import User
from .forms import TicketEditForm
from .ai_utils import predict_department
from .priority_ai import predict_priority
from django.http import JsonResponse


from django.utils import timezone
from datetime import timedelta


# =========================
# ADMIN CHECK
# =========================
def is_admin(user):
    return user.is_authenticated and (
        user.is_superuser or user.role == 'admin'
    )


# =========================
# STAFF CHECK
# =========================
def is_staff(user):
    return user.is_authenticated and user.role == 'staff'


# =========================
# CREATE TICKET
# =========================
@login_required
def create_ticket(request):

    if request.method == 'POST':

        form = TicketForm(request.POST)

        if form.is_valid():

            ticket = form.save(commit=False)

            # COMBINE TITLE + DESCRIPTION
            text = (
                ticket.title +
                " " +
                ticket.description
            )

            # =========================
            # AI DEPARTMENT PREDICTION
            # =========================

            predicted_department, confidence = predict_department(text)

            # if AI confidence is low

            if confidence < 0.40:

                department, created = Department.objects.get_or_create(
                    name="Support"
                )

            else:

                department = Department.objects.get(
                    name=predicted_department
                )
            ticket.department = department

            # =========================
            # AUTO STAFF ASSIGNMENT
            # =========================

            staff_members = User.objects.filter(
                role='staff',
                department=department
            )

            least_busy_staff = None

            minimum_tickets = None

            for staff in staff_members:

                active_tickets = Ticket.objects.filter(

                    assigned_to=staff,

                    status__in=['open', 'in_progress']

                ).count()

                if minimum_tickets is None or active_tickets < minimum_tickets:

                    minimum_tickets = active_tickets

                    least_busy_staff = staff


            # ASSIGN STAFF
            if least_busy_staff:

                ticket.assigned_to = least_busy_staff

                ticket.last_assigned_at = timezone.now()

                # staff assigned but work not started yet
                ticket.status = 'open'

            # =========================
            # USER PRIORITY OVERRIDE
            # =========================

            # if user selected priority
            if ticket.priority:

                ticket.priority = ticket.priority

            # otherwise AI predicts
            else:

                predicted_priority = predict_priority(text)

                ticket.priority = predicted_priority.lower()

            ticket.created_by = request.user

            ticket.save()

            # =========================
            # CREATION HISTORY
            # =========================

            TicketHistory.objects.create(

                ticket=ticket,

                action=(
                    f'Ticket created with '
                    f'AI department: {ticket.department.name} '
                    f'and priority: {ticket.priority}'
                ),

                performed_by=request.user

            )

            # =========================
            # AUTO ASSIGNMENT HISTORY
            # =========================

            if least_busy_staff:

                TicketHistory.objects.create(

                    ticket=ticket,

                    action=f'Automatically assigned to {least_busy_staff.username}',

                    performed_by=None

                )

            return redirect('ticket_list')

    else:

        form = TicketForm()

    return render(request, 'tickets/create_ticket.html', {
        'form': form
    })

# =========================
# USER TICKETS
# =========================
@login_required
def ticket_list(request):

    tickets = Ticket.objects.all().order_by('-created_at')

    # 🔍 SEARCH
    search = request.GET.get('search')

    if search:
        tickets = tickets.filter(
            title__icontains=search
        )

    # 📌 STATUS FILTER
    status = request.GET.get('status')

    if status:
        tickets = tickets.filter(
            status=status
        )

    # 🏢 DEPARTMENT FILTER
    department = request.GET.get('department')

    if department:
        tickets = tickets.filter(
            department__id=department
        )

    # 🚨 PRIORITY FILTER
    priority = request.GET.get('priority')

    if priority:
        tickets = tickets.filter(
            priority=priority
        )

    # 👤 USER LOGIC
    if request.user.role != 'admin':

        tickets = tickets.filter(
            created_by=request.user
        )

    departments = Department.objects.all()

    return render(request, 'tickets/ticket_list.html', {
        'tickets': tickets,
        'departments': departments
    })


# =========================
# ADMIN - ALL TICKETS
# =========================
@user_passes_test(is_admin)
def all_tickets(request):

    tickets = Ticket.objects.all().order_by('-created_at')

    # 🔍 SEARCH
    search = request.GET.get('search')

    if search:
        tickets = tickets.filter(
            title__icontains=search
        )

    # 📌 STATUS FILTER
    status = request.GET.get('status')

    if status:
        tickets = tickets.filter(
            status=status
        )

    # 🏢 DEPARTMENT FILTER
    department = request.GET.get('department')

    if department:
        tickets = tickets.filter(
            department__id=department
        )

    # 🚨 PRIORITY FILTER
    priority = request.GET.get('priority')

    if priority:
        tickets = tickets.filter(
            priority=priority
        )

    departments = Department.objects.all()

    return render(request, 'tickets/ticket_list.html', {
        'tickets': tickets,
        'departments': departments
    })


# =========================
# ESCALATED TICKETS
# =========================
@user_passes_test(is_admin)
def escalated_tickets(request):

    tickets = Ticket.objects.filter(
        status='escalated'
    ).order_by('-created_at')

    return render(request, 'tickets/ticket_list.html', {
        'tickets': tickets
    })

# =========================
# ASSIGN TICKET TO STAFF
# =========================
@user_passes_test(is_admin)
def assign_ticket(request, ticket_id):

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    # ONLY STAFF FROM SAME DEPARTMENT
    staff_users = User.objects.filter(
        role='staff',
        department=ticket.department
    )

    # =========================
    # STAFF WORKLOAD DATA
    # =========================

    staff_data = []

    for staff in staff_users:

        active_tickets = Ticket.objects.filter(
            assigned_to=staff,
            status__in=['open', 'in_progress']
        ).count()

        staff_data.append({
            'staff': staff,
            'active_tickets': active_tickets
        })

    # SORT BY LOWEST WORKLOAD
    staff_data.sort(
        key=lambda x: x['active_tickets']
    )

    if request.method == 'POST':

        staff_id = request.POST.get('staff')

        staff_user = get_object_or_404(
            User,
            id=staff_id,
            role='staff'
        )

        old_staff = ticket.assigned_to

        ticket.assigned_to = staff_user

        if old_staff != staff_user:

            ticket.last_assigned_at = timezone.now()

            action_text = (
                f"Ticket reassigned from "
                f"{old_staff.username if old_staff else 'Unassigned'} "
                f"to {staff_user.username}. "
                f"SLA timer restarted."
            )

        else:

            action_text = (
                f"Ticket assignment reviewed. "
                f"Assigned staff remains {staff_user.username}."
            )

        ticket.status = 'open'

        ticket.save()

        TicketHistory.objects.create(

            ticket=ticket,

            action=action_text,

            performed_by=request.user

        )

        return redirect('all_tickets')

    return render(request, 'tickets/assign_ticket.html', {

        'ticket': ticket,

        'staff_data': staff_data

    })

# =========================
# EDIT TICKET
# =========================
@user_passes_test(is_admin)
def edit_ticket(request, ticket_id):

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    if request.method == 'POST':

        form = TicketEditForm(
            request.POST,
            instance=ticket
        )

        if form.is_valid():
            form.save()

            return redirect('all_tickets')

    else:
        form = TicketEditForm(instance=ticket)

    return render(request, 'tickets/edit_ticket.html', {
        'form': form
    })


# =========================
# DELETE TICKET
# =========================
@user_passes_test(is_admin)
def delete_ticket(request, ticket_id):

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    ticket.delete()

    return redirect('all_tickets')


# =========================
# DEPARTMENT LIST
# =========================
@user_passes_test(is_admin)
def department_list(request):

    departments = Department.objects.all()

    form = DepartmentForm()

    if request.method == 'POST':

        form = DepartmentForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('department_list')

    return render(request, 'tickets/department_list.html', {
        'departments': departments,
        'form': form
    })


# =========================
# EDIT DEPARTMENT
# =========================
@user_passes_test(is_admin)
def edit_department(request, id):

    department = get_object_or_404(
        Department,
        id=id
    )

    if request.method == 'POST':

        form = DepartmentForm(
            request.POST,
            instance=department
        )

        if form.is_valid():
            form.save()

            return redirect('department_list')

    else:
        form = DepartmentForm(instance=department)

    return render(request, 'tickets/edit_department.html', {
        'form': form
    })


# =========================
# DELETE DEPARTMENT
# =========================
@user_passes_test(is_admin)
def delete_department(request, id):

    department = get_object_or_404(
        Department,
        id=id
    )

    department.delete()

    return redirect('department_list')


# =========================
# TICKET DETAIL + COMMENTS
# =========================
@login_required
def ticket_detail(request, id):

    ticket = get_object_or_404(
        Ticket,
        id=id
    )

    comments = ticket.comments.all()

    if request.method == 'POST':

        form = CommentForm(request.POST)

        if form.is_valid():

            comment = form.save(commit=False)

            comment.ticket = ticket

            comment.user = request.user

            comment.save()

            TicketHistory.objects.create(
                ticket=ticket,
                action='Comment added',
                performed_by=request.user
            )

            return redirect('ticket_detail', id=id)

    else:
        form = CommentForm()

    # =========================
    # SLA TIMER
    # =========================

    now = timezone.now()

    if ticket.priority == 'high':

        sla_limit = timedelta(hours=24)

    elif ticket.priority == 'medium':

        sla_limit = timedelta(hours=48)

    else:

        sla_limit = timedelta(hours=72)

    if ticket.last_assigned_at:

        elapsed_time = now - ticket.last_assigned_at

    else:

        elapsed_time = now - ticket.created_at

    remaining_time = sla_limit - elapsed_time

    remaining_hours = int(
        remaining_time.total_seconds() // 3600
    )

    sla_breached = remaining_time.total_seconds() <= 0

    return render(request, 'tickets/ticket_detail.html', {

        'ticket': ticket,

        'comments': comments,

        'form': form,

        'remaining_time': remaining_time,

        'remaining_hours': remaining_hours,

        'sla_breached': sla_breached,

    })


# =========================
# STAFF TICKETS
# =========================
@user_passes_test(is_staff)
def staff_tickets(request):

    tickets = Ticket.objects.filter(
        assigned_to=request.user
    ).order_by('-created_at')

     # 🔍 SEARCH
    search = request.GET.get('search')

    if search:
        tickets = tickets.filter(
            title__icontains=search
        )

    # 📌 STATUS FILTER
    status = request.GET.get('status')

    if status:
        tickets = tickets.filter(
            status=status
        )
    
    # 🚨 PRIORITY FILTER
    priority = request.GET.get('priority')

    if priority:
        tickets = tickets.filter(
            priority=priority
        )

    return render(request, 'tickets/staff_tickets.html', {
        'tickets': tickets
    })


# =========================
# UPDATE TICKET STATUS
# =========================
@user_passes_test(is_staff)
def update_ticket_status(request, ticket_id):

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    if request.method == 'POST':

        new_status = request.POST.get('status')

        ticket.status = new_status

        ticket.save()

        TicketHistory.objects.create(

            ticket=ticket,

            action=f'Status changed to {new_status}',

            performed_by=request.user

        )

        return redirect('staff_tickets')

    return render(request, 'tickets/update_status.html', {
        'ticket': ticket
    })

# =========================
# ESCALATE TICKET
# =========================
@user_passes_test(is_staff)
def escalate_ticket(request, ticket_id):

    ticket = get_object_or_404(
        Ticket,
        id=ticket_id
    )

    if request.method == 'POST':

        reason = request.POST.get('reason')

        ticket.status = 'escalated'
        ticket.escalation_reason = reason
        ticket.save()

        TicketHistory.objects.create(
            ticket=ticket,
            action='Ticket escalated',
            performed_by=request.user
        )

        return redirect('staff_tickets')

    return render(request, 'tickets/escalate_ticket.html', {
        'ticket': ticket
    })

@login_required
def ai_prediction(request):

    text = request.GET.get('text', '')

    if not text:

        return JsonResponse({
            'department': '',
            'priority': ''
        })

    # =========================
    # DEPARTMENT PREDICTION
    # =========================

    predicted_department, confidence = predict_department(text)

    # LOW CONFIDENCE → SUPPORT
    if confidence < 0.40:

        predicted_department = "Support"

    # =========================
    # PRIORITY PREDICTION
    # =========================

    predicted_priority = predict_priority(text)

    return JsonResponse({

        'department': predicted_department,

        'priority': predicted_priority,

        'confidence': round(confidence, 2)

    })

