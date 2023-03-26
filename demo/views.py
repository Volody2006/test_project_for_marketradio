from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DetailView, ListView
from django.urls import reverse

from demo.models import SearchName
from demo.tasks import start_search


class CompositionIndexView(ListView):
    template_name = "index.html"
    context_object_name = "composition_list"

    def get_queryset(self):
        return SearchName.objects.all()


class CompositionDetailView(DetailView):
    model = SearchName
    template_name = "detail.html"


class CompositionCreateView(CreateView):
    template_name = "create.html"
    model = SearchName
    fields = ["file", ]
    object = None

    def form_valid(self, form):
        file_name = form.cleaned_data.get('file').name
        self.object = form.save(commit=False)
        self.object.file_name = file_name
        self.object.save()
        # Формирование задачи на шазам
        start_search(self.object)
        return HttpResponseRedirect(self.get_success_url())
