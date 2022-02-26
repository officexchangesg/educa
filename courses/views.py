from django.views.generic.list import ListView
from .models import Course

from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, \
                                      DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, \
                                       PermissionRequiredMixin

from .models import Course
class ManageCourseListView(ListView):
    model = Course
    template_name = 'courses/manage/course/list.html'
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

class OwnerMixin(object):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)
class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
class OwnerCourseMixin(OwnerMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')
class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'
    permission_required = 'courses.view_course'
class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'
class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'
class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'

from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet
class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None
    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course,
                             data=data)
    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course,
                                        id=pk,
                                        owner=request.user)
        return super().dispatch(request, pk)
    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course,
                                        'formset': formset})
    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course,
                                        'formset': formset})

# Adding content to course module
from django.forms.models import modelform_factory
from django.apps import apps
from .models import Module, Content
class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'
    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses',
                                  model_name=model_name)
        return None
    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner',
                                                 'order',
                                                 'created',
                                                 'updated'])
        return Form(*args, **kwargs)
    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module,
                                       id=module_id,
                                       course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         owner=request.user)
        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,
                                        'object': self.obj})
    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model,
                            instance=self.obj,
                            data=request.POST,
                            files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(module=self.module,
                                    item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form,
                                        'object': self.obj})


# The ContentDeleteView class retrieves the Content object with the given ID. 
# It deletes the related Text, Video, Image, or File object. 
# Finally, it deletes the Content object and redirects the user to the module_content_list 
# URL to list the other contents of the module.
class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content,
                               id=id,
                               module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)

class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'
    def get(self, request, module_id):
        module = get_object_or_404(Module,
                                   id=module_id,
                                   course__owner=request.user)
        return self.render_to_response({'module': module})


from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
# view that receives the new order of module IDs encoded in JSON.
class ModuleOrderView(CsrfExemptMixin,
                      JsonRequestResponseMixin,
                      View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id,
                   course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})

# build a similar view to order a module's contents. 
class ContentOrderView(CsrfExemptMixin,
                       JsonRequestResponseMixin,
                       View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id,
                       module__course__owner=request.user) \
                       .update(order=order)
        return self.render_json_response({'saved': 'OK'})

# You retrieve all subjects, using the ORM's annotate() method with the Count() aggregation function to include the total number of courses for each subject
# You retrieve all available courses, including the total number of modules contained in each course
# If a subject slug URL parameter is given, you retrieve the corresponding subject object and limit the query to the courses that belong to the given subject
# You use the render_to_response() method provided by TemplateResponseMixin to render the objects to a template and return an HTTP response
from django.db.models import Count
from .models import Subject
from django.core.cache import cache


# class CourseListView(TemplateResponseMixin, View):
#     model = Course
#     template_name = 'courses/course/list.html'
#     def get(self, request, subject=None):
#         subjects = cache.get('all_subjects')
#         if not subjects:
#             subjects = Subject.objects.annotate(
#                         total_courses=Count('courses'))
#             cache.set('all_subjects', subjects)
#         courses = Course.objects.annotate(
#                        total_modules=Count('modules'))
#         if subject:
#             subject = get_object_or_404(Subject, slug=subject)
#             courses = courses.filter(subject=subject)
#         return self.render_to_response({'subjects': subjects,
#                                         'subject': subject,
#                                         'courses': courses})
class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'
    def get(self, request, subject=None):
        subjects = cache.get('all_subjects')
        if not subjects:
            subjects = Subject.objects.annotate(
                           total_courses=Count('courses'))
            cache.set('all_subjects', subjects)
        all_courses = Course.objects.annotate(
                           total_modules=Count('modules'))
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            key = f'subject_{subject.id}_courses'
            courses = cache.get(key)
            if not courses:
                courses = all_courses.filter(subject=subject)
                cache.set(key, courses)
        else:
            courses = cache.get('all_courses')
            if not courses:
                courses = all_courses
                cache.set('all_courses', courses)
        return self.render_to_response({'subjects': subjects,
                                        'subject': subject,
                                        'courses': courses})



# a detail view for displaying a single course overview. 
# This view inherits from the generic DetailView provided by Django. 
# You specify the model and template_name attributes. 
# Django's DetailView expects a primary key (pk) or slug URL parameter to retrieve a single object for the given model. 
# The view renders the template specified in template_name, including the Course object in the template context variable object.
from django.views.generic.detail import DetailView
from students.forms import CourseEnrollForm
class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(
                                   initial={'course':self.object})
        return context

