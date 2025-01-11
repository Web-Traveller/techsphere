# main/views.py #}
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, TeamCreationForm, PaymentSubmissionForm, TeamMemberFormSet, ContactForm, CompetitionRegistrationForm, IndividualRegistrationForm, TeamMemberForm
from .models import CustomUser, Competition, Team, TeamMember, TeamCompetitionRegistration, ContactMessage
from django.contrib import messages
from django.http import JsonResponse
from django.forms import modelformset_factory

def home(request):
    competitions = Competition.objects.all().only('id', 'name', 'description', 'rules', 'prize', 'image', 'rulebook_link','coordinator_details','max_team_size', 'is_individual')
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save(commit=False)
            contact_message.status = 'unread'
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
                password=form.cleaned_data['password'],
                name = form.cleaned_data['name']
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
    registered_competitions = []
    try:
        registered_competitions_team = TeamCompetitionRegistration.objects.filter(team__team_leader=request.user).select_related('competition', 'team')
        registered_competitions_individual = TeamCompetitionRegistration.objects.filter(user=request.user).select_related('competition')
    except Team.DoesNotExist:
        pass
    registered_competitions = list(registered_competitions_team) + list(registered_competitions_individual)
    return render(request, 'main/dashboard.html', {'registered_competitions': registered_competitions})

@login_required
def create_team(request, competition_id=None, team_id=None):
    competition = get_object_or_404(Competition, pk=competition_id) if competition_id else None
    team = get_object_or_404(Team, pk=team_id) if team_id else None

    team_leader_data = TeamMember.objects.filter(user=request.user).first()
    initial_data = {}
    if team_leader_data:
      initial_data = {
           'team-leader-name': team_leader_data.name,
           'team-leader-phone': team_leader_data.phone,
           'team-leader-branch': team_leader_data.branch,
           'team-leader-year': team_leader_data.year,
           'team-leader-college': team_leader_data.college_name
         }

    if request.method == 'POST':
        team_form = TeamCreationForm(request.POST, instance = team)
        TeamMemberFormSet = modelformset_factory(TeamMember, form=TeamMemberForm, extra=3, can_delete = True, fields = ['name', 'email', 'phone', 'branch', 'year', 'college_name'] )
        team_member_formset = TeamMemberFormSet(request.POST)
        if team_form.is_valid() :
            team = team_form.save(commit=False)
            team.team_leader = request.user
            team.competition = competition
            team.save()
            
            team_member = TeamMember.objects.filter(team=team).first()
            if team_member:
                team_member.name = request.POST.get('team-leader-name', '')
                team_member.phone = request.POST.get('team-leader-phone', '')
                team_member.branch = request.POST.get('team-leader-branch', '')
                team_member.year = request.POST.get('team-leader-year', '')
                team_member.college_name = request.POST.get('team-leader-college', '')
                team_member.save()
            else:
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
            member_added = False
            if team_member_formset.is_valid():
                for form in team_member_formset:
                   if form.cleaned_data:
                        team_member = form.save(commit = False);
                        team_member.team=team;
                        team_member.save();
                        member_added = True;
                if team or member_added:
                    messages.success(request, 'Team Details Updated.')
                    return redirect('main:payment_page', competition_id=competition_id, team_id = team.pk)
            else:
                messages.error(request, 'Team should have minimum one member.')
                team.delete()
    else:
        team_form = TeamCreationForm(instance = team)
        if team:
           team_member_queryset = TeamMember.objects.filter(team=team).exclude(user=request.user)
           TeamMemberFormSet = modelformset_factory(TeamMember, form=TeamMemberForm, extra=3, can_delete = True, fields = ['name', 'email', 'phone', 'branch', 'year', 'college_name'] )
           team_member_formset = TeamMemberFormSet(queryset=team_member_queryset)
        else:
           TeamMemberFormSet = modelformset_factory(TeamMember, form=TeamMemberForm, extra=3, can_delete = True, fields = ['name', 'email', 'phone', 'branch', 'year', 'college_name'] )
           team_member_formset = TeamMemberFormSet(queryset=TeamMember.objects.none())

    return render(request, 'main/create_team.html', {'form': team_form, 'team_member_formset': team_member_formset, 'user': request.user, 'team_leader_data': initial_data, 'competition':competition, 'team':team})

def check_team_name(request):
    team_name = request.GET.get('team_name')
    if team_name:
        available = not Team.objects.filter(name=team_name).exists()
    else:
        available = False
    return JsonResponse({'available': available})

# Removed login_required decorator
def competition_detail(request, pk):
    competition = get_object_or_404(Competition, pk=pk)
    return render(request, 'main/competition_detail.html', {'competition': competition})

@login_required
def register_for_competition(request, pk):
    competition = get_object_or_404(Competition, pk=pk)
    if not competition.is_individual:
       try:
           team = Team.objects.get(team_leader=request.user, competition = competition)
           return redirect('main:create_team', competition_id = competition.pk, team_id= team.pk)
       except Team.DoesNotExist:
           return redirect('main:create_team', competition_id = competition.pk)
    else:
        try:
           registration = TeamCompetitionRegistration.objects.get(user=request.user, competition = competition)
           return redirect('main:payment_page', competition_id=competition.pk)
        except TeamCompetitionRegistration.DoesNotExist:
            return redirect('main:payment_page', competition_id=competition.pk)

@login_required
def payment_page(request, competition_id, team_id=None):
    competition = get_object_or_404(Competition, pk=competition_id)
    team = get_object_or_404(Team, pk=team_id) if team_id else None
    registration = None
    if not team:
       try:
          registration = TeamCompetitionRegistration.objects.get(user=request.user, competition = competition)
       except TeamCompetitionRegistration.DoesNotExist:
          pass

    if request.method == 'POST':
        payment_form = PaymentSubmissionForm(request.POST, request.FILES)
        individual_form = IndividualRegistrationForm(request.POST)
        if payment_form.is_valid():
            participant_details = {}
            if team:
                for member in team.members_details.all():
                     participant_details[f"member_{member.id}"] = {
                        "name" : member.name,
                        "email": member.email,
                        "phone": member.phone,
                        "branch": member.branch,
                        "year" : member.year,
                        "college_name": member.college_name,
                        }
            else:
                 if individual_form.is_valid():
                   participant_details["participant_1"] = {
                        "name" : individual_form.cleaned_data['name'],
                        "email": request.user.email,
                         "phone": individual_form.cleaned_data['phone'],
                         "branch": individual_form.cleaned_data['branch'],
                         "year" : individual_form.cleaned_data['year'],
                        "college_name": individual_form.cleaned_data['college_name'],
                    }
                 else :
                    messages.error(request, 'Some error on individual data submission.')
                    return render(request, 'main/payment_page.html', {'competition': competition,  'payment_form':payment_form, 'team':team, 'individual_form': individual_form})

            payment_screenshot = payment_form.cleaned_data['payment_screenshot']
            transaction_number = payment_form.cleaned_data['transaction_number']

            registration = TeamCompetitionRegistration.objects.create(
                 team = team,
                 user=request.user if not team else None,
                 competition=competition,
                 transaction_number=transaction_number,
                 payment_screenshot=payment_screenshot,
                 payment_status='pending',
                 participant_details= participant_details
             )
            messages.success(request, 'Your Payment Details are submitted, we will notify you with verification details soon.')
            return redirect('main:message_page', pk=registration.pk)
        else:
            messages.error(request, 'Some error on payment submission.')
            return render(request, 'main/payment_page.html', {'competition': competition,  'payment_form':payment_form, 'team':team, 'individual_form': IndividualRegistrationForm(initial={'name':request.user.name, 'email':request.user.email}) if registration is None else IndividualRegistrationForm(initial=registration.participant_details['participant_1'])})
    else:
        payment_form = PaymentSubmissionForm()
        individual_form = IndividualRegistrationForm(initial={'name':request.user.name, 'email':request.user.email}) if registration is None else IndividualRegistrationForm(initial=registration.participant_details['participant_1'])
    return render(request, 'main/payment_page.html', {'competition': competition, 'payment_form':payment_form, 'team':team, 'individual_form': individual_form})

def message_page(request, pk):
    registration = get_object_or_404(TeamCompetitionRegistration, pk=pk)
    return render(request, 'main/message_page.html', {'registration': registration})