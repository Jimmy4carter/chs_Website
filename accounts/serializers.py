 
from rest_framework import serializers
from .models import Students, MidTerm, EndTerm, ExamFile, ClassAverage, NotificationApp, AffectiveDomain, Psycomotor, Terms, Subjects, SessionYearModel, StudyMaterial
from onlinecbt.models import Quiz, QuizSchedule, ObjectiveQuestion, ObjectiveOption, TheoryQuestion, StudentAnswer, StudentProgress, QuizResult

class TermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terms
        fields = ['id', 'name', 'status']

class SubjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = '__all__'  # Include all fields or specify the ones you need

class SessionYearModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionYearModel
        fields = '__all__'  # Include all fields or specify the ones you need

class MidTermSerializer(serializers.ModelSerializer):
    term = TermsSerializer()
    subjects_id = SubjectsSerializer()  # Include subjects details
    session_year = SessionYearModelSerializer()  # Include session year details

    class Meta:
        model = MidTerm
        fields = '__all__'

class EndTermSerializer(serializers.ModelSerializer):
    term = TermsSerializer()
    subjects_id = SubjectsSerializer()  # Include subjects details
    session_year = SessionYearModelSerializer()  # Include session year details

    class Meta:
        model = EndTerm
        fields = '__all__'

class ClassAverageSerializer(serializers.ModelSerializer):
    term = TermsSerializer()
    session_year = SessionYearModelSerializer()  # Include session year details
    
    class Meta:
        model = ClassAverage
        fields = '__all__'

class NotificationStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationApp
        fields = '__all__'

class AffectiveDomainSerializer(serializers.ModelSerializer):
    term = TermsSerializer()
    
    class Meta:
        model = AffectiveDomain
        fields = '__all__'

class PsycomotorSerializer(serializers.ModelSerializer):
    term = TermsSerializer()
    
    class Meta:
        model = Psycomotor
        fields = '__all__'

class StudentsSerializer(serializers.ModelSerializer):
    midterm_results = serializers.SerializerMethodField()
    endterm_results = serializers.SerializerMethodField()
    class_averages = serializers.SerializerMethodField()
    notifications = serializers.SerializerMethodField()
    affective_domains = serializers.SerializerMethodField()
    psycomotor_skills = serializers.SerializerMethodField()

    class Meta:
        model = Students
        fields = [
            'id', 'gender', 'profile_pic', 'address', 'religion',
            'origin_state', 'dob', 'admission_class', 'admission_ses',
            'parent_name', 'parent_email', 'parent_phone',
            'class_category', 'class_id', 'session_year_id', 'admin', 'updated_at',
            'midterm_results', 'endterm_results', 'class_averages', 'notifications',
            'affective_domains', 'psycomotor_skills'
        ]
        depth = 1

    def get_midterm_results(self, obj):
        midterms = MidTerm.objects.filter(students_id=obj)
        return MidTermSerializer(midterms, many=True).data

    def get_endterm_results(self, obj):
        endterms = EndTerm.objects.filter(students_id=obj)
        return EndTermSerializer(endterms, many=True).data

    def get_class_averages(self, obj):
        averages = ClassAverage.objects.filter(students_id=obj)
        return ClassAverageSerializer(averages, many=True).data

    def get_notifications(self, obj):
        notifications = NotificationApp.objects.filter(status=1)
        return NotificationStudentSerializer(notifications, many=True).data

    def get_affective_domains(self, obj):
        domains = AffectiveDomain.objects.filter(student_id=obj)
        return AffectiveDomainSerializer(domains, many=True).data

    def get_psycomotor_skills(self, obj):
        skills = Psycomotor.objects.filter(student_id=obj)
        return PsycomotorSerializer(skills, many=True).data



# ----CBT app 

class ObjectiveOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectiveOption
        fields = '__all__'

class ObjectiveQuestionSerializer(serializers.ModelSerializer):
    options = ObjectiveOptionSerializer(many=True, read_only=True)

    class Meta:
        model = ObjectiveQuestion
        fields = '__all__'

class TheoryQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheoryQuestion
        fields = '__all__'

class QuizScheduleSerializer(serializers.ModelSerializer):
    quiz = serializers.CharField(source='quiz.title')

    class Meta:
        model = QuizSchedule
        fields = '__all__'

class QuizSerializer(serializers.ModelSerializer):
    objective_questions = ObjectiveQuestionSerializer(many=True, read_only=True)
    theory_questions = TheoryQuestionSerializer(many=True, read_only=True)
    schedules = QuizScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = '__all__'

class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = '__all__'

class StudentProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProgress
        fields = '__all__'

class QuizResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizResult
        fields = '__all__'

class SyncQuizDataSerializer(serializers.ModelSerializer):
    quizzes = QuizSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['quizzes']


class UploadQuizDataSerializer(serializers.Serializer):
    quiz_result = QuizResultSerializer()
    student_answers = StudentAnswerSerializer(many=True)
    student_progress = StudentProgressSerializer()

    def create(self, validated_data):
        quiz_result_data = validated_data.get("quiz_result")
        student_answers_data = validated_data.get("student_answers", [])
        student_progress_data = validated_data.get("student_progress")

        student = quiz_result_data["student"]
        schedule = quiz_result_data["schedule"]

        # **Update or Create QuizResult**
        quiz_result, _ = QuizResult.objects.update_or_create(
            student=student,
            schedule=schedule,
            defaults=quiz_result_data
        )

        # **Update or Create StudentProgress**
        student_progress, _ = StudentProgress.objects.update_or_create(
            student=student,
            schedule=schedule,
            defaults=student_progress_data
        )

        # **Optimize StudentAnswer Handling**
        existing_answers = StudentAnswer.objects.filter(
            student=student,
            schedule=schedule
        ).in_bulk(field_name='id')  # Fetch all existing answers in bulk

        new_answers = []
        updated_answers = []

        for answer_data in student_answers_data:
            objective_question = answer_data.get("objective_question")
            theory_question = answer_data.get("theory_question")

            # Create a lookup key based on objective or theory question
            lookup_key = (objective_question if objective_question else theory_question)

            if lookup_key in existing_answers:
                # Update existing answer
                existing_answer = existing_answers[lookup_key]
                for field, value in answer_data.items():
                    setattr(existing_answer, field, value)
                updated_answers.append(existing_answer)
            else:
                # Create new answer
                new_answers.append(StudentAnswer(**answer_data))

        # Bulk insert new answers
        if new_answers:
            StudentAnswer.objects.bulk_create(new_answers, ignore_conflicts=True)

        # Bulk update existing answers
        if updated_answers:
            StudentAnswer.objects.bulk_update(updated_answers, fields=['selected_option', 'is_correct', 'theory_answer', 'is_submitted', 'submitted_at'])

        return {
            "quiz_result": quiz_result.id,
            "student_answers_count": len(student_answers_data),
            "student_progress": student_progress.id,
        }

        
# ------------Materials--------

class ExamFileSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(source='subject.subject_name')  # Get subject name
    exam_pdf = serializers.FileField()  # File URL
    code = serializers.CharField()  # Unique code

    class Meta:
        model = ExamFile
        fields = ['subject', 'exam_pdf', 'code']


class StudyMaterialSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.subject_name')  # Get subject name

    class Meta:
        model = StudyMaterial
        fields = ['subject_name', 'material_type', 'pdf_url', 'file']

