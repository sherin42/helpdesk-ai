from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count

from .forms import RegisterForm, StaffCreationForm

from tickets.models import Ticket, TicketHistory
from accounts.models import User
from .forms import UserEditForm
from accounts.forms import ProfileUpdateForm

# HOME PAGE
def home(request):
    return render(request, 'index.html')

# ✅ ADMIN CHECK
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


# 🔐 LOGIN VIEW
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)   # 🔥 creates session
            return redirect('dashboard')
        else:
            return render(request, 'registration/login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'registration/login.html')


# 🚪 LOGOUT VIEW
def logout_view(request):
    logout(request)
    return redirect('login')


# 📝 REGISTER VIEW
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            
            user = form.save()

            user.role = 'admin'
            user.is_staff = True
            user.is_superuser = True

            user.save()

            return redirect('login')
        else:
            print(form.errors)
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


# 📊 DASHBOARD (PROTECTED)
@login_required
def dashboard(request):

    # =========================
    # ADMIN DASHBOARD
    # =========================

    if request.user.role == 'admin':

        total_tickets = Ticket.objects.count()

        open_tickets = Ticket.objects.filter(
            status='open'
        ).count()

        in_progress_tickets = Ticket.objects.filter(
            status='in_progress'
        ).count()

        resolved_tickets = Ticket.objects.filter(
            status='resolved'
        ).count()

        escalated_tickets = Ticket.objects.filter(
            status='escalated'
        ).count()

        # DEPARTMENT ANALYTICS
        department_data = Ticket.objects.values(
            'department__name'
        ).annotate(
            total=Count('id')
        )

        department_labels = [
            item['department__name']
            for item in department_data
        ]

        department_counts = [
            item['total']
            for item in department_data
        ]

        # PRIORITY ANALYTICS
        priority_data = Ticket.objects.values(
            'priority'
        ).annotate(
            total=Count('id')
        )

        priority_labels = [
            item['priority']
            for item in priority_data
        ]

        priority_counts = [
            item['total']
            for item in priority_data
        ]

        # STAFF WORKLOAD
        workload_data = User.objects.filter(
            role='staff'
        ).annotate(
            total_tickets=Count('assigned_tickets')
        )

        workload_labels = [
            staff.username
            for staff in workload_data
        ]

        workload_counts = [
            staff.total_tickets
            for staff in workload_data
        ]

        recent_activities = TicketHistory.objects.order_by(
            '-created_at'
        )[:5]

        context = {

            'dashboard_type': 'admin',

            'total_tickets': total_tickets,
            'open_tickets': open_tickets,
            'in_progress_tickets': in_progress_tickets,
            'resolved_tickets': resolved_tickets,
            'escalated_tickets': escalated_tickets,

            'department_labels': department_labels,
            'department_counts': department_counts,

            'priority_labels': priority_labels,
            'priority_counts': priority_counts,

            'workload_labels': workload_labels,
            'workload_counts': workload_counts,

            'recent_activities': recent_activities
        }

        return render(
            request,
            'accounts/dashboard.html',
            context
        )

    # =========================
    # STAFF DASHBOARD
    # =========================

    elif request.user.role == 'staff':

        assigned_tickets = Ticket.objects.filter(
            assigned_to=request.user
        )

        total_assigned = assigned_tickets.count()

        open_tickets = assigned_tickets.filter(
            status='open'
        ).count()

        in_progress_tickets = assigned_tickets.filter(
            status='in_progress'
        ).count()

        resolved_tickets = assigned_tickets.filter(
            status='resolved'
        ).count()

        escalated_tickets = assigned_tickets.filter(
            status='escalated'
        ).count()

        recent_tickets = assigned_tickets.order_by(
            '-created_at'
        )[:5]

        context = {

            'dashboard_type': 'staff',

            'total_assigned': total_assigned,

            'open_tickets': open_tickets,

            'in_progress_tickets': in_progress_tickets,

            'resolved_tickets': resolved_tickets,

            'escalated_tickets': escalated_tickets,

            'recent_tickets': recent_tickets
        }

        return render(
            request,
            'accounts/dashboard.html',
            context
        )

    # =========================
    # USER DASHBOARD
    # =========================

    else:

        user_tickets = Ticket.objects.filter(
            created_by=request.user
        )

        total_tickets = user_tickets.count()

        open_tickets = user_tickets.filter(
            status='open'
        ).count()

        in_progress_tickets = user_tickets.filter(
            status='in_progress'
        ).count()

        resolved_tickets = user_tickets.filter(
            status='resolved'
        ).count()

        escalated_tickets = user_tickets.filter(
            status='escalated'
        ).count()

        recent_tickets = user_tickets.order_by(
            '-created_at'
        )[:5]

        context = {

            'dashboard_type': 'user',

            'total_tickets': total_tickets,

            'open_tickets': open_tickets,

            'in_progress_tickets': in_progress_tickets,

            'resolved_tickets': resolved_tickets,

            'escalated_tickets': escalated_tickets,

            'recent_tickets': recent_tickets
        }

        return render(
            request,
            'accounts/dashboard.html',
            context
        )

# =========================
# ALL USERS
# =========================
@user_passes_test(is_admin)
def user_list(request):

    users = User.objects.all()

    # 📌 ROLE FILTER
    role = request.GET.get('role')

    if role:
        users = users.filter(
            role=role
        )

    return render(request, 'accounts/user_list.html', {
        'users': users
    })


# =========================
# EDIT USER
# =========================
@user_passes_test(is_admin)
def edit_user(request, user_id):

    user = User.objects.get(id=user_id)

    if request.method == 'POST':

        form = UserEditForm(
            request.POST,
            instance=user
        )

    else:

        form = UserEditForm(instance=user)

    # =========================
    # NORMAL USER
    # =========================
    if user.role == 'user':

        form.fields.pop('department')

    # =========================
    # STAFF
    # =========================
    elif user.role == 'staff':

        form.fields.pop('age')
        form.fields.pop('gender')
        form.fields.pop('location')

    # =========================
    # ADMIN
    # =========================
    elif user.role == 'admin':

        form.fields.pop('department')
        form.fields.pop('age')
        form.fields.pop('gender')
        form.fields.pop('location')

    if request.method == 'POST':

        if form.is_valid():

            form.save()

            return redirect('user_list')

    return render(request, 'accounts/edit_user.html', {
        'form': form
    })

# =========================
# DELETE USER
# =========================
@user_passes_test(is_admin)
def delete_user(request, user_id):

    user = User.objects.get(id=user_id)

    user.delete()

    return redirect('user_list')

# 👨‍💼 ADD STAFF (ADMIN ONLY)
@user_passes_test(is_admin)
def add_staff(request):
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'staff'
            user.save()
            return redirect('dashboard')
    else:
        form = StaffCreationForm()

    return render(request, 'accounts/add_staff.html', {'form': form})

# =========================
# USER PROFILE
# =========================
@login_required
def profile(request):

    user = request.user

    context = {
        'user_obj': user
    }

    if user.role == 'user':

        context['created_tickets'] = Ticket.objects.filter(
            created_by=user
        ).count()

        context['open_tickets'] = Ticket.objects.filter(
            created_by=user,
            status__in=['open', 'in_progress']
        ).count()

        context['resolved_tickets'] = Ticket.objects.filter(
            created_by=user,
            status='resolved'
        ).count()

    elif user.role == 'staff':

        context['assigned_tickets'] = Ticket.objects.filter(
            assigned_to=user
        ).count()

        context['open_assigned'] = Ticket.objects.filter(
            assigned_to=user,
            status__in=['open', 'in_progress']
        ).count()

        context['resolved_assigned'] = Ticket.objects.filter(
            assigned_to=user,
            status='resolved'
        ).count()

    return render(
        request,
        'accounts/profile.html',
        context
    )

# =========================
# USER EDIT PROFILE
# =========================
@login_required
def edit_profile(request):

    if request.user.role == 'staff':

        fields = [
            'name',
            'email',
            'username',
            'department',
        ]

    else:

        fields = [
            'name',
            'email',
            'username',
            'age',
            'gender',
            'location',
        ]

    class DynamicProfileForm(ProfileUpdateForm):

        class Meta(ProfileUpdateForm.Meta):
            field = fields

    if request.method == 'POST':

        form = DynamicProfileForm(
            request.POST,
            instance=request.user
        )

        if form.is_valid():

            form.save()

            return redirect('profile')

    else:

        form = DynamicProfileForm(
            instance=request.user
        )

    return render(
        request,
        'accounts/edit_profile.html',
        {
            'form': form
        }
    )