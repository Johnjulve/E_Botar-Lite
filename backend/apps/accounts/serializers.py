from django.contrib.auth.models import User
from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserProfile, Program
from .utils import parse_year_level_value, staff_can_manage_student_profile
from apps.common.files.file_urls import absolute_file_url


def lookup_program_by_code(code, program_type, error_field):
    label = 'Department' if program_type == Program.ProgramType.DEPARTMENT else 'Course'
    try:
        return Program.objects.get(code=code, program_type=program_type)
    except Program.DoesNotExist:
        raise serializers.ValidationError({
            error_field: f'{label} with code "{code}" does not exist.',
        })


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ['id', 'name', 'code', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source='department.code', read_only=True, allow_null=True)
    department_name = serializers.CharField(source='department.name', read_only=True, allow_null=True)
    department_label = serializers.SerializerMethodField()
    department_code = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Program
        fields = [
            'id', 'department', 'department_code', 'department_name', 'department_label',
            'name', 'code', 'program_type', 'description',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'department', 'department_name', 'department_label', 'program_type']

    def get_department_label(self, obj):
        return obj.department.name if obj.department else 'Unassigned'

    def create(self, validated_data):
        department_code = validated_data.pop('department_code', None)
        validated_data['program_type'] = Program.ProgramType.COURSE
        program = Program.objects.create(**validated_data)
        if department_code:
            program.department = lookup_program_by_code(
                department_code, Program.ProgramType.DEPARTMENT, 'department_code'
            )
            program.save()
        return program

    def update(self, instance, validated_data):
        department_code = validated_data.pop('department_code', None)
        if department_code is not None:
            instance.department = (
                lookup_program_by_code(
                    department_code, Program.ProgramType.DEPARTMENT, 'department_code'
                )
                if department_code
                else None
            )
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ProgramSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source='department.code', read_only=True, allow_null=True)
    department_name = serializers.CharField(source='department.name', read_only=True, allow_null=True)
    department_label = serializers.SerializerMethodField()
    department_code = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Program
        fields = [
            'id', 'name', 'code', 'program_type', 'description',
            'department', 'department_code', 'department_name', 'department_label',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'department', 'department_name', 'department_label']

    def get_department_label(self, obj):
        if obj.program_type != Program.ProgramType.COURSE:
            return None
        return obj.department.name if obj.department else 'Unassigned'

    def create(self, validated_data):
        department_code = validated_data.pop('department_code', None)
        program = Program.objects.create(**validated_data)
        if department_code:
            program.department = lookup_program_by_code(
                department_code, Program.ProgramType.DEPARTMENT, 'department_code'
            )
            program.save()
        return program

    def update(self, instance, validated_data):
        department_code = validated_data.pop('department_code', None)
        if department_code is not None:
            instance.department = (
                lookup_program_by_code(
                    department_code, Program.ProgramType.DEPARTMENT, 'department_code'
                )
                if department_code
                else None
            )
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    department_code = serializers.CharField(source='department.code', read_only=True, allow_null=True)
    department_name = serializers.CharField(source='department.name', read_only=True, allow_null=True)
    course_code = serializers.CharField(source='course.code', read_only=True, allow_null=True)
    course_name = serializers.CharField(source='course.name', read_only=True, allow_null=True)
    department = serializers.CharField(write_only=True, required=False, allow_null=True)
    course = serializers.CharField(write_only=True, required=False, allow_null=True)
    avatar_url = serializers.SerializerMethodField()
    is_profile_complete = serializers.SerializerMethodField()
    missing_fields = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'student_id', 'middle_name',
            'department', 'department_code', 'department_name',
            'course', 'course_code', 'course_name',
            'year_level', 'section', 'avatar', 'avatar_url',
            'is_verified', 'is_profile_complete', 'missing_fields',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['is_verified', 'created_at', 'updated_at']

    def get_avatar_url(self, obj):
        return absolute_file_url(obj.avatar, self.context.get('request'))

    def get_is_profile_complete(self, obj):
        return obj.is_profile_complete()

    def get_missing_fields(self, obj):
        return obj.get_missing_fields()

    def update(self, instance, validated_data):
        dept_code = validated_data.pop('department', None)
        course_code = validated_data.pop('course', None)

        if dept_code is not None:
            instance.department = lookup_program_by_code(
                dept_code, Program.ProgramType.DEPARTMENT, 'department'
            ) if dept_code else None

        if course_code is not None:
            instance.course = lookup_program_by_code(
                course_code, Program.ProgramType.COURSE, 'course'
            ) if course_code else None

        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'is_staff', 'is_superuser', 'is_active', 'profile']
        read_only_fields = ['is_staff', 'is_superuser']


class UserNestedSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'is_staff', 'is_superuser', 'is_active', 'date_joined']


class UserProfileListSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    is_staff = serializers.BooleanField(source='user.is_staff', read_only=True)
    is_superuser = serializers.BooleanField(source='user.is_superuser', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    department = DepartmentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True, allow_null=True)
    course_code = serializers.CharField(source='course.code', read_only=True, allow_null=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'user_id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'student_id', 'department', 'department_code', 'course', 'course_code', 'year_level', 'section',
            'is_staff', 'is_superuser', 'is_active', 'is_verified', 'avatar_url',
            'created_at'
        ]

    def get_avatar_url(self, obj):
        return absolute_file_url(obj.avatar, self.context.get('request'))


class UserVotingStatusListSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    student_id = serializers.CharField(read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True, allow_null=True)
    course_code = serializers.CharField(source='course.code', read_only=True, allow_null=True)
    has_voted = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user_id', 'student_id', 'full_name', 'department_code', 'course_code', 'year_level', 'section', 'has_voted']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    middle_name = serializers.CharField(required=False, allow_blank=True)
    department = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    course = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    year_level = serializers.CharField(required=False, allow_blank=True)
    section = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'middle_name', 'password', 'password_confirm', 'department', 'course', 'year_level', 'section']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        middle_name = validated_data.pop('middle_name', '')
        dept_code = validated_data.pop('department', None)
        course_code = validated_data.pop('course', None)
        year_level = validated_data.pop('year_level', '')
        section = validated_data.pop('section', '')
        password = validated_data.pop('password')

        user = User.objects.create_user(password=password, **validated_data)
        
        dept = None
        if dept_code:
            dept = Program.objects.filter(code=dept_code, program_type=Program.ProgramType.DEPARTMENT).first()
        course = None
        if course_code:
            course = Program.objects.filter(code=course_code, program_type=Program.ProgramType.COURSE).first()

        UserProfile.objects.create(
            user=user,
            middle_name=middle_name,
            department=dept,
            course=course,
            year_level=year_level,
            section=section
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        profile, _ = UserProfile.objects.get_or_create(user=user)

        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name(),
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'student_id': profile.student_id,
            'department_code': profile.department.code if profile.department else None,
            'department_name': profile.department.name if profile.department else None,
            'course_code': profile.course.code if profile.course else None,
            'course_name': profile.course.name if profile.course else None,
            'year_level': profile.year_level,
            'section': profile.section,
            'avatar_url': absolute_file_url(profile.avatar, self.context.get('request')),
            'is_profile_complete': profile.is_profile_complete(),
        }
        return data
