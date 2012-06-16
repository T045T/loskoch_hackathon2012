import django.views.generic
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from core.models import Flatshare
from core.forms import FlatCreationForm


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


@login_required
def dashboard(request):
    flat = request.user.get_profile().flat
    return render(request, 'core/dashboard.html', {'flat': flat})
