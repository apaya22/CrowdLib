from rest_framework import serializers


class MadlibSerializer(serializers.Serializer):
    _id = serializers.CharField(read_only=True)
    title = serializers.CharField(required=True)
    blank_count = serializers.IntegerField()
    template = serializers.JSONField()
    blanks = serializers.JSONField()

    class Meta:
        fields = ['_id', 'title', 'blank_count', 'template', 'blanks']
