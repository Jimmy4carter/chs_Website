
from django.urls import path
from accounts.ApiViews import StudentLoginView, SyncQuizData, UploadQuizDataView, RetrieveStudentResults, get_exam_files, get_study_materials

urlpatterns = [
    path('api/student-login/', StudentLoginView.as_view(), name='student-login'),
    path('sync-quiz-data/<int:student_id>/', SyncQuizData.as_view(), name='sync-quiz-data'),
    path('retrieve-student-results/<int:student_id>/', RetrieveStudentResults.as_view(), name='retrieve-student-results'),
    path('upload-quiz-data/<int:student_id>/', UploadQuizDataView.as_view(), name='upload_quiz_data'),
    path('api/exam-files/<int:student_id>/', get_exam_files, name='exam_files_api'),
    path('study-materials/', get_study_materials, name='get_study_materials'),
]
