import django.views.generic
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from recipes.models import Recipe


class CreateRecipeView(django.views.generic.CreateView):
    model = Recipe

    def form_valid(self, form):
        # Update flat object
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()

        return redirect('dashboard')


add_recipe = login_required(
    CreateRecipeView.as_view(template_name='recipes/create.html'))
