from django.shortcuts import render
from django.shortcuts import redirect, render, get_object_or_404
from voting_system.models import Region
from voting_system.models import Candidate
from voting_system.models import Election
from voting_system.forms import ElectionForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from voting_system.forms import LoginForm
from django.contrib.auth.hashers import make_password, check_password

from voting_system.views.CheckAuthorisation import CheckAuthorisation

from voting_system.models import Region, Candidate, Role, Party, Election
from voting_system.forms import *
from django.db import connection


from voting_system.models import Admin

def CreateDummyUser(request):
    admin_user = Admin()
    admin_user.id = 1
    admin_user.first_name = "John"
    admin_user.last_name = "Smith"
    admin_user.user_name = "j_smith"
    admin_user.password_hash = make_password("abc")
    admin_user.email = "smithj@email.com"
    # foreign key
    
    admin_user.save()

    return render(request, 'admin_interface/login/create_dummy_user.html')

def AdminUsers(request):
    admins = Admin.objects.all()
    
    return render(request, 'admin_interface/admin_users/admin_users.html', {'admins': admins})


def Login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = Admin.objects.get(user_name = request.POST.get('username'))
            
            if user is not None:
                if check_password(request.POST.get('password'), user.password_hash):
                    request.session['username'] = user.user_name
                    return render(request, 'admin_interface/login/success.html',{'user': user})
                else:
                    form = LoginForm()
                    return render(request, 'admin_interface/login/login.html',{'form': form,'message': "Incorrect Password"})
            else:
                form = LoginForm()

                return render(request, 'admin_interface/login/login.html',{'form': form,'message': "You could not be logged in."})
            
    else:
        form = LoginForm()
    return render(request, 'admin_interface/login/login.html',{'form': form,'message': ""})

def Logout(request):
    try:
        del request.session['username']
    except:
        pass
    
    return render(request, 'admin_interface/login/logged_out.html',{})
    




def populate_regions(request):
	if not Region.objects.all():
		Region.populate_regions()
		return redirect('regions')
	return render(request, 'admin_interface/populate_regions.html')

def regions(request):
	regions = Region.objects.all().order_by('id')
	are_regions = True
	if not regions:
		are_regions = False
	return render(request, 'admin_interface/regions.html', {'regions': regions, 'are_regions': are_regions})

def populate_voter_codes(request):
    if request.method == "POST":
        form = VoterCodeForm(request.POST)
        if form.is_valid():
            election = form.instance.election
            form.save(commit=False)
            print(election)
            VoterCode.populate_voter_codes(election)
            return redirect('elections')
    else:
        form = VoterCodeForm()
    return render(request, 'admin_interface/populate_voter_codes.html', {'form': form})

def voter_codes(request):
    voter_codes = VoterCode.objects.all().order_by('id')
    return render(request, 'admin_interface/voter_codes.html', {'voter_codes': voter_codes})

def candidates(request):
	candidates = Candidate.objects.all().order_by('id')
	return render(request, 'admin_interface/view_candidates.html', {'candidates': candidates})

def candidate_create(request):
	if request.method == "POST":
		
		form = CandidateForm(request.POST)
		party = request.POST.get('party_id')
		if form.is_valid():

			candidate = form.save(commit=False)


			candidate.id = getNextID('candidates')
			candidate.party_id = party
			candidate.save()
		return redirect('candidates')
	else:
		form = CandidateForm()
		
		return render(request, 'admin_interface/candidate_form.html', {'form': form})

def candidate_edit(request, id=None):
	candidate = get_object_or_404(Candidate, id=id)
	if request.method == "POST":
		form = CandidateForm(request.POST, instance=candidate)
		if form.is_valid():
			candidate = form.save(commit=False)
			candidate.save()
			return redirect('candidates')
	else:
		form = CandidateForm(instance=candidate)
		form.fields['party_id'].initial = candidate.party_id
	return render(request, 'admin_interface/candidate_form.html', {'form': form})

def candidate_delete(request, id=None):
	candidate = get_object_or_404(Candidate, id=id)
	candidate.delete()
	return redirect('candidates')


def elections(request):

    authorised,username = CheckAuthorisation(request,True,[("test_role",)])
    if(authorised):
        elections = Election.objects.all()
        return render(request, 'admin_interface/elections/elections.html', {'elections': elections})
    else:
        message = "You are not authorised to view this page."
        return render(request, 'admin_interface/login/not_authorised.html', {'message': message})



def election_create(request):
	if request.method == "POST":
		form = ElectionForm(request.POST)
		if form.is_valid():
			election = form.save(commit=False)
			party.id = getNextID('elections')
			election.save()
			return redirect('elections')
	else:
		form = ElectionForm()
	candidates = Candidate.objects.all()
	regions = Region.objects.all()
	return render(request, 'admin_interface/elections/election_form.html', {'form': form, 'candidates': candidates, 'regions': regions})


def election_edit(request, id=None):
	election = get_object_or_404(Election, id=id)
	if request.method == "POST":
		form = ElectionForm(request.POST, instance=election)
		if form.is_valid():
			election = form.save(commit=False)
			election.save()
			return redirect('elections')
	else:
		form = ElectionForm(instance=election)
	return render(request, 'admin_interface/elections/election_form.html', {'form': form})


def election_delete(request, id=None):
	election = get_object_or_404(Election, id=id)
	election.delete()
	return redirect('elections')


def roles(request):
	roles = Role.objects.all().order_by('id')
	return render(request, 'admin_interface/roles.html', {'roles' : roles})

def role_create(request):
	if request.method == "POST":
		form = RoleForm(request.POST)
		if form.is_valid():
			role = form.save(commit=False)
			role.id = getNextID('roles')
			
			role.save()
			return redirect('roles')
	else:
		form = RoleForm()
	return render(request, 'admin_interface/role_form.html', {'form': form})

def role_edit(request, id=None):
	role = get_object_or_404(Role, id=id)
	if request.method == "POST":
		form = RoleForm(request.POST, instance=role)
		if form.is_valid():
			role = form.save(commit=False)
			#role.id = request.user
			#role.name = request.user
			role.save()
			return redirect('roles')
	else:
		form = RoleForm(instance=role)
	return render(request, 'admin_interface/role_form.html', {'form': form})

def role_delete(request, id=None):
	role = get_object_or_404(Role, id=id)
	role.delete()
	return redirect('roles')

def party(request):
	parties = Party.objects.all().order_by('id')
	if not parties:
		are_parties = False
	else:
		are_parties = True
	return render(request, 'admin_interface/parties.html', {'parties': parties, 'are_parties': are_parties})

def party_create(request):
	if request.method == "POST":
		form = PartyForm(request.POST)
		if form.is_valid():
			party = form.save(commit=False)
			party.id = getNextID('parties')
			party.save()
			return redirect('party')
	else:
		form = PartyForm()
	return render(request, 'admin_interface/party_form.html', {'form': form})
def party_delete(request, id=None):

	party = get_object_or_404(Party, id=id)
	party.delete()
	return redirect('parties')

def party_edit(request, id=None):
	party = get_object_or_404(Party, id=id)
	if request.method == "POST":
		form = PartyForm(request.POST, instance=party)
		if form.is_valid():
			party = form.save(commit=False)
			
			party.save()
			return redirect('party')
	else:
		form = PartyForm(instance=party)
	return render(request, 'admin_interface/role_form.html', {'form': form})
def getNextID(tblName):
	cursor = connection.cursor()
	cursor.execute( "select nextval('"+tblName+"_id_seq')")
	row = cursor.fetchone()
	cursor.close()
	return row[0]

def isEmpty(elements):
	count = 0

	for element in elements:
		count += 1
	return {0: True}.get(count, False)
