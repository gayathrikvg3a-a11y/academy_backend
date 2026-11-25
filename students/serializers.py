from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.contrib.auth.models import User

from rest_framework import serializers

from courses.models import Lesson
from dashboard.models import Role

from .models import FCMDevice, Staff, Student, StudentCertificate, StudentLessonProgress
from payments.serializers import PaymentSerializer
from .models import FeeType, PaymentType




class StudentCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCertificate
        fields = "__all__"

class StudentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Student
        fields = "__all__"
        extra_kwargs = {
            "user": {"read_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password", "Student@123")

        # Create student first (student_id is generated in save())
        student = Student.objects.create(**validated_data)

        # Create corresponding Django user
        user = User.objects.create_user(
            username=student.student_id,   # Login ID
            email=student.email,
            password=password,
            first_name=student.student_name,
        )

        # Link user with student
        student.user = user
        student.save(update_fields=["user"])

        return student

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        if instance.user:
            instance.user.first_name = validated_data.get(
                "student_name", instance.student_name
            )
            instance.user.email = validated_data.get(
                "email", instance.email
            )

            if password:
                instance.user.set_password(password)

            instance.user.save()

        return super().update(instance, validated_data)

    
class StudentPaymentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    receipt_number = serializers.CharField()
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    payment_date = serializers.DateField()

    payment_method_name = serializers.CharField(
        source="payment_method.name"
    )
    payment_type_name = serializers.CharField(
    source="payment_type.payment_type_name",
    read_only=True
    )


class StudentSerializer(serializers.ModelSerializer):

    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    certificates = StudentCertificateSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    course_name = serializers.CharField(source="course.name",read_only=True)
    course_duration = serializers.CharField(source="course.duration",read_only=True)
    fee_type_name = serializers.CharField(source="fee_type.name",read_only=True)
    batch_name = serializers.CharField(source="batch.batch_name",read_only=True)

    fee_option_name = serializers.CharField(source="fee_option.option_name",read_only=True)
    fee_option_fee = serializers.DecimalField(source="fee_option.fee",max_digits=10,decimal_places=2,read_only=True)

    total_paid = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()
    final_fee = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = "__all__"

    @transaction.atomic
    def create(self, validated_data):

        username = validated_data.pop("username", None)
        password = validated_data.pop("password", None)
        validated_data.pop("confirm_password", None)

        # Assign Student role automatically
        student_role = Role.objects.get(role_name="Student")

        student = Student.objects.create(
            role=student_role,
            **validated_data
        )

        if student.fee_option:
            student.course_fee = student.fee_option.fee
            student.save(update_fields=["course_fee"])

        login_username = username or student.student_id

        if User.objects.filter(username=login_username).exists():
            raise serializers.ValidationError({
                "username": "This username already exists."
            })

        user = User.objects.create_user(
            username=login_username,
            email=student.email,
            password=password or student.phone,
            first_name=student.student_name,
        )

        student.user = user
        student.save(update_fields=["user"])

        return student

    def validate(self, attrs):

        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        if password and password != confirm_password:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })
        course = attrs.get("course")
        fee_option = attrs.get("fee_option")

        # Ensure selected fee option belongs to selected course
        if course and fee_option and fee_option.course_id != course.id:
            raise serializers.ValidationError({
                "fee_option": "Selected fee option does not belong to the selected course."
            })

        return attrs

    @transaction.atomic
    def update(self, instance, validated_data):

        validated_data.pop("username", None)
        validated_data.pop("password", None)
        validated_data.pop("confirm_password", None)
        fee_option = validated_data.get("fee_option")

        # If fee option changes, update base course fee
        if fee_option:
            validated_data["course_fee"] = fee_option.fee

        return super().update(instance, validated_data)

    def get_total_paid(self, obj):
        return obj.payments.aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

    def get_final_fee(self, obj):
        # Highest priority: student-specific discounted fee
        if obj.discounted_fee is not None:
            return obj.discounted_fee

        # Otherwise use selected fee option fee
        if obj.fee_option:
            return obj.fee_option.fee

        # Fallback to course fee
        return obj.course_fee

    def get_balance(self, obj):
        total_paid = self.get_total_paid(obj)
        final_fee = self.get_final_fee(obj)
        return Decimal(final_fee) - Decimal(total_paid)

    def get_payment_status(self, obj):

        total_paid = self.get_total_paid(obj)
        final_fee = Decimal(self.get_final_fee(obj))

        if total_paid == Decimal("0.00"):
            return "PENDING"

        if total_paid >= final_fee:
            return "PAID"

        return "PARTIAL"

from batch.serializers import BatchSerializer
from masters.serializers import FeeTypeSerializer
from courses.serializers import StudentCourseSerializer
class StudentProfileSerializer(serializers.ModelSerializer):

    user_id = serializers.IntegerField(source="user.id",read_only=True)
    course = StudentCourseSerializer(read_only=True,)
    batch = BatchSerializer(read_only=True,)
    fee_type = FeeTypeSerializer(read_only=True,)
    payments = PaymentSerializer(many=True,read_only=True,)
    certificates = StudentCertificateSerializer(many=True,read_only=True,)
    total_paid = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()

    total_lessons = serializers.SerializerMethodField()
    completed_lessons = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    next_lesson = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "id",
            "user_id",
            "student_id",
            "student_name",
            "student_photo",
            "phone",
            "whatsapp",
            "email",
            "gender",
            "date_of_birth",
            "address",
            "district",
            "state",
            "pincode",
            "college",
            "academic_stream",
            "roll_number",
            "joining_date",
            "remarks",
            "recommended_by",
            "status",

            "course",
            "batch",
            "fee_type",

            "payments",
            "certificates",

            "course_fee",
            "total_paid",
            "balance",
            "payment_status",

            "total_lessons",
            "completed_lessons",
            "progress_percentage",
            "next_lesson",
        ]

    def get_total_paid(self, obj):
        return sum(payment.amount for payment in obj.payments.all())

    def get_balance(self, obj):
        total = sum(payment.amount for payment in obj.payments.all())
        return obj.course_fee - total

    def get_payment_status(self, obj):
        total = sum(payment.amount for payment in obj.payments.all())

        if total == 0:
            return "PENDING"

        if total >= obj.course_fee:
            return "PAID"

        return "PARTIAL"

    def get_total_lessons(self, obj):
        if not obj.course:
            return 0

        return Lesson.objects.filter(
            course=obj.course,
            is_published=True
        ).count()

    def get_completed_lessons(self, obj):
        if not obj.course:
            return 0

        return StudentLessonProgress.objects.filter(
            student=obj,
            is_completed=True,
            lesson__course=obj.course
        ).count()

    def get_progress_percentage(self, obj):
        total = self.get_total_lessons(obj)
        completed = self.get_completed_lessons(obj)

        if total == 0:
            return 0

        return round((completed / total) * 100)

    def get_next_lesson(self, obj):
        if not obj.course:
            return None

        completed_ids = StudentLessonProgress.objects.filter(
            student=obj,
            is_completed=True
        ).values_list("lesson_id", flat=True)

        lesson = Lesson.objects.filter(
            course=obj.course,
            is_published=True
        ).exclude(
            id__in=completed_ids
        ).order_by(
            "module__module_order",
            "lesson_order"
        ).first()

        if lesson:
            return {
                "id": lesson.id,
                "title": lesson.lesson_title,
                "module": lesson.module.title,
                "duration_minutes": lesson.duration_minutes,
            }

        return None



class StudentProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "student_name",
            "student_photo",
            "phone",
            "whatsapp",
            "email",
            "gender",
            "date_of_birth",
            "address",
            "district",
            "state",
            "pincode",
            "college",
            "academic_stream",
        ]

    def validate_email(self, value):
        student = self.instance

        if Student.objects.exclude(pk=student.pk).filter(email=value).exists():
            raise serializers.ValidationError(
                "A student with this email already exists."
            )

        return value

    def validate_phone(self, value):
        student = self.instance

        if Student.objects.exclude(pk=student.pk).filter(phone=value).exists():
            raise serializers.ValidationError(
                "A student with this phone number already exists."
            )

        return value

    def update(self, instance, validated_data):

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if instance.user:
            instance.user.first_name = instance.student_name
            instance.user.email = instance.email
            instance.user.save()

        return instance



class FCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = [
            "device",
            "device_id",
            "reg_token",
        ]


class LogoutFCMDeviceSerializer(serializers.Serializer):
    device_id = serializers.CharField()


class StudentLessonProgressSerializer(serializers.ModelSerializer):

    lesson_title = serializers.CharField(source="lesson.lesson_title",read_only=True)
    module_title = serializers.CharField(source="lesson.module.title",read_only=True)

    class Meta:
        model = StudentLessonProgress
        fields = [
            "id",
            "student",
            "lesson",
            "lesson_title",
            "module_title",
            "is_completed",
            "completed_at",
            "remarks",
        ]


class StaffSerializer(serializers.ModelSerializer):

    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Staff
        fields = "__all__"

    def validate(self, attrs):

        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password and password != confirm_password:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        return attrs

    @transaction.atomic
    def create(self, validated_data):

        username = validated_data.pop("username", None)
        password = validated_data.pop("password", None)
        validated_data.pop("confirm_password", None)

        # Get selected role
        role = validated_data.pop("role")

        staff = Staff.objects.create(
            role=role,
            **validated_data
        )

        login_username = username or staff.staff_id

        if User.objects.filter(username=login_username).exists():
            raise serializers.ValidationError({
                "username": "Username already exists."
            })

        user = User.objects.create_user(
            username=login_username,
            email=staff.email,
            password=password or staff.phone,
            first_name=staff.staff_name,
        )

        staff.user = user
        staff.save(update_fields=["user"])

        return staff

    @transaction.atomic
    def update(self, instance, validated_data):
        validated_data.pop("username", None)
        validated_data.pop("password", None)
        validated_data.pop("confirm_password", None)

        return super().update(instance, validated_data)