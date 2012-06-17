import datetime
from collections import OrderedDict

import django.views.generic
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from core.models import Flatshare
from core.forms import FlatCreationForm
from recipes.models import Recipe


class CreateFlatView(django.views.generic.CreateView):
    model = Flatshare
    form_class = FlatCreationForm

    def form_valid(self, form):
        # Update flat object
        self.object = form.save(commit=False)
        self.object.admin = self.request.user
        self.object.save()

        # Update admin object
        self.object.admin.get_profile().flat = self.object
        self.object.admin.get_profile().save()

        return redirect('dashboard')


create_flat = login_required(
    CreateFlatView.as_view(template_name='core/create-flat.html'))


@login_required
def join_flat(request, flat_token):
    flat = get_object_or_404(Flatshare, token=flat_token)
    request.user.get_profile().flat = flat
    request.user.get_profile().save()
    return redirect('dashboard')


def dashboard(request):
    if not request.user.is_authenticated():
        return render(request, 'core/home.html')

    flat = request.user.get_profile().flat

    if flat is None:
        return redirect('create_flat')

    if flat.latest_pairing:
        date_candidates = OrderedDict()
        for flatmate in flat.latest_pairing.get_all_flatmates():
            for candidate in flat.latest_pairing.start_time_candidates.filter(user=flatmate.user):
                if candidate.day not in date_candidates:
                    date_candidates[candidate.day] = {'votes': 0, 'start': candidate.time}
                else:
                    if candidate.time != None:
                        date_candidates[candidate.day]['votes'] += 1
                        date_candidates[candidate.day]['start'] = max(
                            date_candidates[candidate.day]['start'],
                            candidate.time,
                        )
    else:
        date_candidates = None

    return render(request, 'core/dashboard.html', {
        'user': request.user.get_profile(),
        'flat': flat,
        'range': range(flat.size - flat.flatmates.count()),
        'latest_pairing': flat.latest_pairing,
        'latest_pairing_date_candidates': date_candidates,
        'gmaps_url': flat.latest_pairing and flat.latest_pairing.gmaps_url(flat),
    })


@login_required
def save_schedule(request):
    if request.method == 'POST':
        start_time_candidates = iter(request.user.get_profile().get_start_time_candidates_for_latest_pairing())
        times = request.POST.getlist('start_time')
        for start_time in times:
            if start_time:
                hour, minute = map(int, start_time.split(':'))
                candidate = start_time_candidates.next()
                candidate.time = datetime.time(hour=hour, minute=minute)
                candidate.save()

    return redirect('dashboard')


@login_required
def vote_for_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user = request.user.get_profile()
    user.vote(recipe)
    return redirect('dashboard')


def facebook_connect(request):
    return redirect('/facebook/connect/?facebook_login=1&register_next=%s' % request.GET['next'])
