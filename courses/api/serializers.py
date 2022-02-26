from rest_framework import serializers
from ..models import Subject, Course,Module
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'title', 'slug']

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['order', 'title', 'description']
class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    class Meta:
        model = Course
        fields = ['id', 'subject', 'title', 'slug', 'overview',
                  'created', 'owner', 'modules']
# Serializing course contents
# You need to serialize course contents. The Content model includes a generic foreign key that 
# allows you to associate objects of different content models. Yet, you added a common render() method 
# for all content models in the previous chapter. You can use this method to provide rendered contents to your API.

from ..models import Content
class ItemRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return value.render()
class ContentSerializer(serializers.ModelSerializer):
    item = ItemRelatedField(read_only=True)
    class Meta:
        model = Content
        fields = ['order', 'item']

# You need an alternative serializer for the Module model that includes its contents, 
# and an extended Course serializer as well.
class ModuleWithContentsSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True)
    class Meta:
        model = Module
        fields = ['order', 'title', 'description', 'contents']
class CourseWithContentsSerializer(serializers.ModelSerializer):
    modules = ModuleWithContentsSerializer(many=True)
    class Meta:
        model = Course
        fields = ['id', 'subject', 'title', 'slug',
                  'overview', 'created', 'owner', 'modules']
