
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, status
from django.db import transaction
from django.contrib.auth import authenticate
from .models import CustomUser, Students, ExamFile, SessionYearModel, StudyMaterial, Terms
from onlinecbt.models import Quiz, QuizSchedule, StudentAnswer, StudentProgress, QuizResult, ObjectiveQuestion, TheoryQuestion
from accounts.serializers import ExamFileSerializer, StudentsSerializer,  QuizSerializer, UploadQuizDataSerializer, StudentAnswerSerializer, StudentProgressSerializer, StudyMaterialSerializer, QuizScheduleSerializer, QuizResultSerializer

class StudentLoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        if user and hasattr(user, "students"):
            student = user.students
            serializer = StudentsSerializer(student)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)



# -----------Materials----

@api_view(['GET'])
def get_study_materials(request):
    student_id = request.query_params.get('student_id')
    material_type = request.query_params.get('material_type')

    if not student_id or not material_type:
        return Response({"error": "student_id and material_type are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        student = Students.objects.get(id=student_id)
    except Students.DoesNotExist:
        return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

    materials = StudyMaterial.objects.filter(
        subject__class_id=student.class_id,
        material_type=material_type,
        status=True  # Only return visible materials
    )

    serializer = StudyMaterialSerializer(materials, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_exam_files(request, student_id):
    # Fetch the student instance
    student = get_object_or_404(Students, id=student_id)

    # Get active session and term
    active_session = SessionYearModel.objects.filter(status=1).first()

    if not active_session:
        return Response({"message": "No active session or term found"}, status=status.HTTP_404_NOT_FOUND)

    # Fetch exam files that match the student's class and active session
    exam_files = ExamFile.objects.filter(
        class_name=student.class_id,
        session_year=active_session
    )

    # Serialize the data
    serializer = ExamFileSerializer(exam_files, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

# --------------CBT---------------------------------------


class SyncQuizData(APIView):
    def get(self, request, student_id):
        # Fetch the student instance
        student = get_object_or_404(Students, id=student_id)

        # Fetch schedules with status 'ongoing'
        ongoing_schedules = QuizSchedule.objects.filter(status='ongoing')

        # Get the quiz IDs linked to these schedules
        quiz_ids = ongoing_schedules.values_list('quiz_id', flat=True).distinct()

        # Fetch only quizzes that match these quiz IDs and belong to the student's class
        quizzes = Quiz.objects.filter(id__in=quiz_ids, subject__class_id=student.class_id)

        # Serialize the data
        serializer = QuizSerializer(quizzes, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class RetrieveStudentResults(APIView):
    def get(self, request, student_id):
        schedules = QuizSchedule.objects.filter(status__in=['result'])

        student_answers = StudentAnswer.objects.filter(student_id=student_id, schedule__in=schedules)
        quiz_results = QuizResult.objects.filter(student_id=student_id, schedule__in=schedules)
        student_progress = StudentProgress.objects.filter(student_id=student_id, schedule__in=schedules)

        return Response({
            "schedules": QuizScheduleSerializer(schedules, many=True).data,
            "student_answers": StudentAnswerSerializer(student_answers, many=True).data,
            "quiz_results": QuizResultSerializer(quiz_results, many=True).data,
            "student_progress": StudentProgressSerializer(student_progress, many=True).data,
        }, status=status.HTTP_200_OK)



class UploadQuizDataView(APIView):
    def post(self, request, student_id, *args, **kwargs):
        # Verify student exists
        student = get_object_or_404(CustomUser, id=student_id)

        serializer = UploadQuizDataSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():  # Ensures all or nothing is saved
                    saved_data = serializer.save()

                return Response(
                    {"message": "Quiz data uploaded successfully", "data": saved_data},
                    status=status.HTTP_201_CREATED
                )

            except Exception as e:
                return Response(
                    {"error": f"Failed to save quiz data: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
