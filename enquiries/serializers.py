from rest_framework import serializers
from .models import Enquiry, CallHistory, EnquiryNew, Testimonial


class CallHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = CallHistory
        fields = '__all__'


class EnquirySerializer(serializers.ModelSerializer):

    call_history = CallHistorySerializer(
        many=True,
        read_only=True
    )

    course_name = serializers.CharField(
        source='course.name',
        read_only=True
    )

    responsible_person_name = serializers.CharField(
        source='responsible_person.username',
        read_only=True
    )

    class Meta:
        model = Enquiry
        fields = '__all__'


class EnquiryNewSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.name", read_only=True)
    responsible_person_name = serializers.CharField(
        source="responsible_person.first_name",
        read_only=True
    )

    class Meta:
        model = EnquiryNew
        fields = "__all__"

    def validate(self, attrs):
        enquiry_type = attrs.get("enquiry_type")
        course = attrs.get("course")

        if enquiry_type == "COURSE" and not course:
            raise serializers.ValidationError({
                "course": "Course is required for course enquiries."
            })

        if enquiry_type == "INTERNSHIP":
            attrs["course"] = None

        return attrs

    def create(self, validated_data):
        validated_data.pop("status", None)
        validated_data.pop("feedback", None)
        validated_data.pop("responsible_person", None)
        validated_data.pop("recommended_by", None)

        return EnquiryNew.objects.create(**validated_data)


class TestimonialSerializer(serializers.ModelSerializer):

    class Meta:
        model = Testimonial
        fields = "__all__"