from rest_framework import generics
from ..models import Subject
from .serializers import SubjectSerializer
class SubjectListView(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
class SubjectDetailView(generics.RetrieveAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

# REST framework provides an APIView class that builds API functionality on top of Django's View class. 
# The APIView class differs from View by using REST framework's custom Request and Response objects, 
# and handling APIException exceptions to return the appropriate HTTP responses. It also has a built-in authentication 
# and authorization system to manage access to views.

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Course
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
# class CourseEnrollView(APIView):
#     authentication_classes = (BasicAuthentication,)
#     permission_classes = (IsAuthenticated,)
#     def post(self, request, pk, format=None):
#         course = get_object_or_404(Course, pk=pk)
#         course.students.add(request.user)
#         return Response({'enrolled': True})

from rest_framework import viewsets
from .serializers import CourseSerializer
from rest_framework.decorators import action
from .permissions import IsEnrolled
from .serializers import CourseWithContentsSerializer

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    @action(detail=True,
            methods=['post'],
            authentication_classes=[BasicAuthentication],
            permission_classes=[IsAuthenticated])
    def enroll(self, request, *args, **kwargs):
        course = self.get_object()
        course.students.add(request.user)
        return Response({'enrolled': True})
# You use the action decorator with the parameter detail=True to specify an action that is performed on a single object.
# You specify that only the GET method is allowed for this action.
# You use the new CourseWithContentsSerializer serializer class that includes rendered course contents.
# You use both IsAuthenticated and your custom IsEnrolled permissions. By doing so, you make sure that only users enrolled on the course are able to access its contents.
# You use the existing retrieve() action to return the Course object.
    @action(detail=True,
            methods=['get'],
            serializer_class=CourseWithContentsSerializer,
            authentication_classes=[BasicAuthentication],
            permission_classes=[IsAuthenticated, IsEnrolled])
    def contents(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)







