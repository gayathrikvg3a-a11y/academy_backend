from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import check_password
from django.db.models import Q

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    login_identifier = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields.pop("username", None)

    def validate(self, attrs):
        login_identifier = attrs.get("login_identifier")
        password = attrs.get("password")

        try:
            user = User.objects.get(
                Q(username__iexact=login_identifier) |
                Q(email__iexact=login_identifier)
            )
        except User.DoesNotExist:
            raise AuthenticationFailed(
                {"error": "Invalid username/email or password."}
            )

        if not check_password(password, user.password):
            raise AuthenticationFailed(
                {"error": "Invalid username/email or password."}
            )

        if not user.is_active:
            raise AuthenticationFailed(
                {"error": "Your account is inactive."}
            )

        refresh = self.get_token(user)

        student = getattr(user, "student_profile", None)
        staff = getattr(user, "staff_profile", None)   # ✅ Add this

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,

                # Student fields
                "student_id": student.student_id if student else None,
                "student_name": student.student_name if student else None,

                # Staff fields
                "staff_id": staff.staff_id if staff else None,
                "staff_name": staff.staff_name if staff else None,
                "domain": staff.get_domain_display() if staff else None,

                # Role
                "role": (
                    "Student"
                    if student
                    else staff.role.role_name if staff else "Admin"
                ),
            }
        }