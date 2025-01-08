from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, TeamCreationForm, PaymentSubmissionForm, TeamMemberFormSet, ContactForm
from .models import CustomUser, Competition, Team, TeamMember, TeamCompetitionRegistration, ContactMessage
from django.contrib import messages
from django.http import JsonResponse

def home(request):
    competitions = Competition.objects.all()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save(commit=False)
            contact_message.status = 'unread'  # Set the default status
            contact_message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('main:home')
    else:
        form = ContactForm()
    return render(request, 'main/home.html', {'competitions': competitions, 'form': form})


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('main:dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return render(request, 'registration/login.html',
                          {'form': {'email': {'errors': []}, 'password': {'errors': []}}})
    else:
        return render(request, 'registration/login.html',
                      {'form': {'email': {'errors': []}, 'password': {'errors': []}}})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = CustomUser.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('main:login')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def logout(request):
    auth_logout(request)
    return redirect('main:home')


@login_required
def dashboard(request):
    team = None
    registered_competitions = []
    try:
        team = Team.objects.get(team_leader=request.user)
        registered_competitions = TeamCompetitionRegistration.objects.filter(team=team).select_related('competition')
    except Team.DoesNotExist:
        pass

    return render(request, 'main/dashboard.html', {'team': team, 'registered_competitions': registered_competitions})


@login_required
def create_team(request):
    team = None
    try:
        team = Team.objects.get(team_leader=request.user)
    except Team.DoesNotExist:
        pass
    if team:
        return redirect('main:dashboard')
    if request.method == 'POST':
        team_form = TeamCreationForm(request.POST)
        team_member_formset = TeamMemberFormSet(request.POST)
        if team_form.is_valid() and team_member_formset.is_valid():
            team = team_form.save(commit=False)
            team.team_leader = request.user
            team.save()

            member_added = False;
            team_member = TeamMember.objects.create(
                team=team,
                user=request.user,
                name = request.POST.get('team-leader-name', ''),
                email = request.user.email,
                phone = request.POST.get('team-leader-phone', ''),
                branch = request.POST.get('team-leader-branch', ''),
                year = request.POST.get('team-leader-year', ''),
                college_name=request.POST.get('team-leader-college', '')
             )
            member_added = True;
            for form in team_member_formset:
               if form.cleaned_data:
                    team_member = form.save(commit = False);
                    team_member.team=team;
                    team_member.save();
                    member_added = True;
            if member_added:
                messages.success(request, 'Team Created Successfully.')
                return redirect('main:dashboard')
            else:
                messages.error(request, 'Team should have minimum one member.')
                team.delete()
        else:
             messages.error(request, 'Team Name not available')
    else:
        team_form = TeamCreationForm()
        team_member_formset = TeamMemberFormSet()
    team_leader_data = TeamMember.objects.filter(user=request.user).first()
    return render(request, 'main/create_team.html', {'form': team_form, 'team_member_formset': team_member_formset, 'user': request.user, 'team_leader_data': team_leader_data})


def check_team_name(request):
    team_name = request.GET.get('team_name')
    if team_name:
        available = not Team.objects.filter(name=team_name).exists()
    else:
        available = False
    return JsonResponse({'available': available})


@login_required
def competition_detail(request, pk):
    competition = get_object_or_404(Competition, pk=pk)
    return render(request, 'main/competition_detail.html', {'competition': competition})


@login_required
def register_for_competition(request, pk):
    competition = get_object_or_404(Competition, pk=pk)
    team = None
    try:
        team = Team.objects.get(team_leader=request.user)
    except Team.DoesNotExist:
        messages.error(request, 'You must create a team before registering for a competition.')
        return redirect('main:create_team')
    try:
        TeamCompetitionRegistration.objects.get(team=team, competition=competition)
        messages.error(request, 'Your team is already registered for this competition')
        return redirect('main:dashboard')
    except TeamCompetitionRegistration.DoesNotExist:
        pass
    if request.method == 'POST':
        form = PaymentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            payment_screenshot = form.cleaned_data['payment_screenshot']
            transaction_number = form.cleaned_data['transaction_number']
            registration = TeamCompetitionRegistration.objects.create(
                team=team,
                competition=competition,
                transaction_number=transaction_number,
                payment_screenshot=payment_screenshot,
                payment_status='pending'  # set payment status to pending
            )
            messages.success(request, 'Your Payment Details are submitted, we will notify you with verification details soon.')
            return redirect('main:message_page', pk=registration.pk)
        else:
            messages.error(request, 'Some error on payment submission.')
    else:
        form = PaymentSubmissionForm()
    return render(request, 'main/payment_page.html', {'competition': competition, 'team': team, 'form': form})


def message_page(request, pk):
    registration = get_object_or_404(TeamCompetitionRegistration, pk=pk)
    return render(request, 'main/message_page.html', {'registration': registration})