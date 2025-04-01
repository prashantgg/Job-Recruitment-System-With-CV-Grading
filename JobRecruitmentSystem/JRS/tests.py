from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from .models import HR, Candidate, Job, JobApplication, InterviewSchedule, CvGrading
from requests import patch
from .cv_grading import compute_similarity
from .models import CvGrading, Job, HR, JobApplication
from django.contrib.auth.models import Group
from unittest.mock import patch
from datetime import timedelta
from django.utils.timezone import now
import json
from django.contrib.auth.models import User
from django.contrib.messages import get_messages




class HRRegistrationTestCase(TestCase):

    def setUp(self):
        self.valid_user_data = {
            'username': 'validuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'validuser@example.com',
            'password': 'password123'
        }

    def test_hr_registration_valid(self):
        # Try to register a valid HR user
        response = self.client.post(reverse("JRS:register_hr"), self.valid_user_data)
        
        # Assert that the response is a redirect
        self.assertEqual(response.status_code, 302)
        
        # Assert that it redirects to the HR login page after successful registration
        self.assertRedirects(response, reverse("JRS:hr_login_page"))
        
        # Assert that the user is created
        user = User.objects.get(username=self.valid_user_data['username'])
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password(self.valid_user_data['password']))

    def test_hr_registration_duplicate_username(self):
        # First, create a valid HR user
        self.client.post(reverse("JRS:register_hr"), self.valid_user_data)
        
        # Try to register another HR user with the same username
        response = self.client.post(reverse("JRS:register_hr"), self.valid_user_data)
        
        # Assert that the response is a redirect (this should go back to the register page)
        self.assertEqual(response.status_code, 302)
        
        # Assert that it redirects to the HR register page when a duplicate username is used
        self.assertRedirects(response, reverse("JRS:hr_register_page"))
        
        # Assert that the error message is displayed
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(msg.message == "Username already exists for an HR profile." for msg in messages))


class HRLoginTestCase(TestCase):

    def setUp(self):
        self.valid_user_data = {
            'username': 'validuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'validuser@example.com',
            'password': 'password123'
        }
        # Register the user first
        self.client.post(reverse("JRS:register_hr"), self.valid_user_data)

    def test_hr_login_valid(self):
        # Now, try to log in with valid credentials
        response = self.client.post(reverse("JRS:hr_login"), {
            'username': self.valid_user_data['username'],
            'email': self.valid_user_data['email'],
            'password': self.valid_user_data['password'],
        })
        
        # Assert that the response is a redirect
        self.assertEqual(response.status_code, 302)
        
        # Assert that it redirects to the HR dashboard page after a successful login
        self.assertRedirects(response, reverse("JRS:hr_dashboard"))

    def test_hr_login_invalid_username(self):
        # Try to log in with an invalid username
        response = self.client.post(reverse("JRS:hr_login"), {
            'username': 'invaliduser',
            'email': self.valid_user_data['email'],
            'password': self.valid_user_data['password'],
        })
        
        # Assert that the response is a redirect (back to the login page)
        self.assertEqual(response.status_code, 302)
        
        # Assert that it redirects to the HR login page
        self.assertRedirects(response, reverse("JRS:hr_login_page"))
        
        # Assert that the error message is displayed
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(msg.message == "Invalid username or password" for msg in messages))

    def test_hr_login_invalid_password(self):
        # Try to log in with an invalid password
        response = self.client.post(reverse("JRS:hr_login"), {
            'username': self.valid_user_data['username'],
            'email': self.valid_user_data['email'],
            'password': 'wrongpassword',
        })
        
        # Assert that the response is a redirect (back to the login page)
        self.assertEqual(response.status_code, 302)
        
        # Assert that it redirects to the HR login page
        self.assertRedirects(response, reverse("JRS:hr_login_page"))
        
        # Assert that the error message is displayed
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(msg.message == "Invalid username or password" for msg in messages))

    def test_hr_login_invalid_email(self):
        # Try to log in with an invalid email
        response = self.client.post(reverse("JRS:hr_login"), {
            'username': self.valid_user_data['username'],
            'email': 'wrongemail@example.com',
            'password': self.valid_user_data['password'],
        })
        
        # Assert that the response is a redirect (back to the login page)
        self.assertEqual(response.status_code, 302)
        
        # Assert that it redirects to the HR login page
        self.assertRedirects(response, reverse("JRS:hr_login_page"))
        
        # Assert that the error message is displayed
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(msg.message == "Invalid email address." for msg in messages))



class TestPostJobView(TestCase):
    def setUp(self):
        """ Set up users and job posting for testing post job view """
        # Create HR user
        self.hr_user = get_user_model().objects.create_user(
            username='hr_user',
            password='testpassword',
        )
        
        # Create an HR instance and link it to the user
        self.hr_instance = HR.objects.create(user=self.hr_user)

        # Create candidate user
        self.candidate_user = get_user_model().objects.create_user(
            username='candidateuser',
            password='testpassword',
        )

        # Add HR user to the HR group
        hr_group = Group.objects.create(name='HR')
        self.hr_user.groups.add(hr_group)

    def test_post_jobs_authenticated_hr(self):
        """ Test for HR to post a job """
        self.client.login(username='hr_user', password='testpassword')
        response = self.client.post(reverse('JRS:post_jobs'), {
            'title': 'Data Analyst',
            'company': 'DataTech',
            'location': 'California',
            'job_type': 'Full-time',
            'salary': '60000',
            'experience': '3+ years',
            'skills': 'SQL, Python',
            'education': 'Master\'s',
            'description': 'Analyze data',
            'deadline': '2025-06-01',
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after posting
        self.assertTrue(Job.objects.filter(title='Data Analyst').exists())  # Job is created

    def test_post_jobs_unauthenticated_user(self):
        """ Test for unauthenticated user trying to post a job """
        response = self.client.post(reverse('JRS:post_jobs'), {
            'title': 'Data Analyst',
            'company': 'DataTech',
            'location': 'California',
            'job_type': 'Full-time',
            'salary': '60000',
            'experience': '3+ years',
            'skills': 'SQL, Python',
            'education': 'Master\'s',
            'description': 'Analyze data',
            'deadline': '2025-06-01',
        })
        self.assertEqual(response.status_code, 302)  # Should redirect to login page


class TestDeleteJobView(TestCase):
    def setUp(self):
        """ Set up users and job postings for testing delete job view """
        # Create HR user
        self.hr_user = get_user_model().objects.create_user(
            username='hr_user',
            password='testpassword',
        )
        
        # Create an HR instance and link it to the user
        self.hr_instance = HR.objects.create(user=self.hr_user)

        # Create candidate user
        self.candidate_user = get_user_model().objects.create_user(
            username='candidateuser',
            password='testpassword',
        )

        # Create a job post
        self.job = Job.objects.create(
            title='Software Engineer',
            company='Tech Corp',
            location='New York',
            job_type='Full-time',
            salary=50000,
            experience='2+ years',
            skills='Python, Django',
            education='Bachelor',
            description='Develop software applications',
            deadline='2025-05-01',
            posted_by=self.hr_instance,  # Use HR instance here
        )

        # Add HR user to the HR group
        hr_group = Group.objects.create(name='HR')
        self.hr_user.groups.add(hr_group)

    def test_delete_job_authenticated_hr(self):
        """ Test for HR to delete a job """
        self.client.login(username='hr_user', password='testpassword')
        response = self.client.post(reverse('JRS:delete_job', kwargs={'job_id': self.job.id}))
        self.assertEqual(response.status_code, 302)  # Should redirect after deletion
        self.assertFalse(Job.objects.filter(id=self.job.id).exists())  # Job is deleted

    def test_delete_job_unauthorized_user(self):
        """ Test for unauthorized user trying to delete a job """
        self.client.login(username='candidateuser', password='testpassword')
        response = self.client.post(reverse('JRS:delete_job', kwargs={'job_id': self.job.id}))
        self.assertEqual(response.status_code, 403)  # Forbidden for unauthorized users


class TestUpdateJobView(TestCase):
    def setUp(self):
        """ Set up users and job postings for testing update job view """
        # Create HR user
        self.hr_user = get_user_model().objects.create_user(
            username='hr_user',
            password='testpassword',
        )
        
        # Create an HR instance and link it to the user
        self.hr_instance = HR.objects.create(user=self.hr_user)

        # Create candidate user
        self.candidate_user = get_user_model().objects.create_user(
            username='candidateuser',
            password='testpassword',
        )

        # Create a job post
        self.job = Job.objects.create(
            title='Software Engineer',
            company='Tech Corp',
            location='New York',
            job_type='Full-time',
            salary=50000,
            experience='2+ years',
            skills='Python, Django',
            education='Bachelor',
            description='Develop software applications',
            deadline='2025-05-01',
            posted_by=self.hr_instance,  # Use HR instance here
        )

        # Add HR user to the HR group
        hr_group = Group.objects.create(name='HR')
        self.hr_user.groups.add(hr_group)

    def test_update_job_authenticated_hr(self):
        """ Test for HR to update a job """
        self.client.login(username='hr_user', password='testpassword')
        response = self.client.post(reverse('JRS:update_job', kwargs={'job_id': self.job.id}), {
            'title': 'Senior Software Engineer',
            'company': 'Tech Corp',
            'location': 'New York',
            'job_type': 'Full-time',
            'salary': '70000',
            'experience': '5+ years',
            'skills': 'Python, Django, Cloud',
            'education': 'Master\'s',
            'description': 'Lead development team',
            'deadline': '2025-07-01',
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after update
        self.job.refresh_from_db()
        self.assertEqual(self.job.title, 'Senior Software Engineer')  # Check updated title

    def test_update_job_unauthorized_user(self):
        """ Test for unauthorized user trying to update a job """
        self.client.login(username='candidateuser', password='testpassword')
        response = self.client.post(reverse('JRS:update_job', kwargs={'job_id': self.job.id}), {
            'title': 'Senior Software Engineer',
            'company': 'Tech Corp',
            'location': 'New York',
            'job_type': 'Full-time',
            'salary': '70000',
            'experience': '5+ years',
            'skills': 'Python, Django, Cloud',
            'education': 'Master\'s',
            'description': 'Lead development team',
            'deadline': '2025-07-01',
        })
        self.assertEqual(response.status_code, 403)  # Forbidden for unauthorized users




class TestCvGradingSimilarity(TestCase):
    def setUp(self):
        """ Set up users, job, and job application for testing compute_similarity """
        # Create an HR user
        self.hr_user = User.objects.create_user(username="hr_manager")
        self.hr = HR.objects.create(user=self.hr_user)

        # Create a Candidate user
        self.candidate_user = User.objects.create_user(username="candidate_user")
        self.candidate = Candidate.objects.create(user=self.candidate_user)

        # Create a Job
        self.job = Job.objects.create(
            title="Software Engineer",
            experience="2 years",
            education="Bachelor's in Computer Science",
            skills="Python, Django, Machine Learning",
            posted_by=self.hr,
            deadline=now() + timedelta(days=30),  # Ensure deadline is set
        )

        # Create a fake resume file for the candidate
        resume_file = SimpleUploadedFile("resume.pdf", b"dummy content", content_type="application/pdf")
        
        # Create a Job Application with a resume attached
        self.job_application = JobApplication.objects.create(
            job=self.job,
            candidate=self.candidate,  # ✅ Ensure this field is filled
            status="Pending",
            resume=resume_file  # Attach the resume
        )
    
    @patch("JRS.cv_grading.extract_text_from_pdf")  # Mocking PDF text extraction
    def test_compute_similarity(self, mock_extract_text):
        """ Test compute_similarity function """
        mock_extract_text.return_value = "Python Django Machine Learning AI"
        
        # Compute similarity
        similarity_score = compute_similarity(self.job_application)  # Use the correct reference
        
        # Expecting a reasonably high score since skills match
        self.assertTrue(similarity_score > 50)


class TestCvGradingBulkGrade(TestCase):
    def setUp(self):
        """ Set up users, job, and job application for testing bulk CV grading """
        # Create an HR user
        self.hr_user = User.objects.create_user(username="hr_manager")
        self.hr = HR.objects.create(user=self.hr_user)

        # Create a Candidate user
        self.candidate_user = User.objects.create_user(username="candidate_user")
        self.candidate = Candidate.objects.create(user=self.candidate_user)

        # Create a Job
        self.job = Job.objects.create(
            title="Software Engineer",
            experience="2 years",
            education="Bachelor's in Computer Science",
            skills="Python, Django, Machine Learning",
            posted_by=self.hr,
            deadline=now() + timedelta(days=30),  # Ensure deadline is set
        )

        # Create a fake resume file for the candidate
        resume_file = SimpleUploadedFile("resume.pdf", b"dummy content", content_type="application/pdf")
        
        # Create a Job Application with a resume attached
        self.job_application = JobApplication.objects.create(
            job=self.job,
            candidate=self.candidate,  # ✅ Ensure this field is filled
            status="Pending",
            resume=resume_file  # Attach the resume
        )
    
    @patch("JRS.cv_grading.extract_text_from_pdf")  # Mocking PDF text extraction
    def test_grade_all_cvs(self, mock_extract_text):
        """ Test for grading all CVs for a specific job """
        mock_extract_text.return_value = "Python Django Machine Learning AI"
        
        # Corrected URL
        response = self.client.get(f"/grade-all-cvs/{self.job.id}/")

        # Verify response is JSON with success status
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["success"])
        
        # Verify that CvGrading entries were created
        self.assertEqual(CvGrading.objects.count(), 1)
        
        # Verify grading is updated in the database
        grading = CvGrading.objects.first()
        self.assertTrue(grading.score > 50)
        self.assertIn(grading.recommendation, ["Highly Recommended", "Moderately Recommended", "Not Recommended"])

class ScheduleInterviewTestCase(TestCase):
    
    def setUp(self):
        """Set up the necessary test data."""
        
        # Create HR User and assign to HR group
        self.hr_user = HR.objects.create(
            user=get_user_model().objects.create_user(username="hr_user", password="password"),
            first_name="HR", last_name="User", username="hr_user", email="hr@example.com"
        )
        
        # Create a 'HR' group and assign it to the HR user
        hr_group = Group.objects.create(name="HR")
        self.hr_user.user.groups.add(hr_group)

        # Create Candidate User
        self.candidate_user = Candidate.objects.create(
            user=get_user_model().objects.create_user(username="candidate", password="password"),
            first_name="John", last_name="Doe", username="candidate", email="candidate@example.com"
        )

        # Mock a file for resume (a simple text file in this case)
        resume_file = SimpleUploadedFile("resume.pdf", b"file_content", content_type="application/pdf")

        # Create a Job posting
        self.job = Job.objects.create(
            title="Software Developer",
            description="Job description here",
            company="Tech Company",
            location="New York",
            job_type="Full-time",
            salary="100000",
            experience="3 years",
            skills="Python, Django",
            education="Bachelor's",
            deadline=timezone.now() + timezone.timedelta(days=10),
            posted_by=self.hr_user
        )

        # Create a JobApplication for the candidate with the resume file
        self.job_application = JobApplication.objects.create(
            candidate=self.candidate_user,
            job=self.job,
            cover_letter="This is a cover letter.",
            resume=resume_file,  # Assign the mock resume file here
            cover_letter_file=None,
            status="Accepted"
        )

        # Create CvGrading for the application
        self.cv_grading = CvGrading.objects.create(
            application=self.job_application,
            score=85.0,
            recommendation="Highly Recommended"
        )
        
        # Log in as HR user and check if login is successful
        login_success = self.client.login(username="hr_user", password="password")
        self.assertTrue(login_success, "Login failed for HR user")

    def test_schedule_interview_get(self):
        """Test the GET request (rendering the interview scheduling page)."""
        
        # URL to view the interview scheduling page
        url = reverse("JRS:schedule_interview", kwargs={"job_id": self.job.id})

        # Send GET request to view the schedule interview page
        response = self.client.get(url)

        # Assert the response is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Check if candidate details are passed to the context
        self.assertIn("candidates_with_details", response.context)
        self.assertEqual(len(response.context["candidates_with_details"]), 1)

    def test_schedule_interview_post_create(self):
        """Test the POST request (creating a new interview schedule)."""
        
        # URL to schedule an interview
        url = reverse("JRS:schedule_interview", kwargs={"job_id": self.job.id})
        
        # Interview date to schedule
        interview_date = timezone.now() + timezone.timedelta(days=1)
        
        # POST request to schedule the interview
        response = self.client.post(url, {"candidate_id": self.job_application.id, "interview_date": interview_date})
        
        # Assert redirect to the same page
        self.assertRedirects(response, url)
        
        # Check if the interview schedule was created
        interview_schedule = InterviewSchedule.objects.filter(
            candidate=self.candidate_user, job=self.job
        ).first()
        
        self.assertIsNotNone(interview_schedule)
        self.assertEqual(interview_schedule.scheduled_date.date(), interview_date.date())
        self.assertEqual(interview_schedule.status, "Scheduled")
        
    def test_schedule_interview_post_update(self):
        """Test the POST request (updating an existing interview schedule)."""
        
        # Create an initial interview schedule for the candidate
        initial_interview_date = timezone.now() + timezone.timedelta(days=1)
        InterviewSchedule.objects.create(
            candidate=self.candidate_user,
            job=self.job,
            scheduled_date=initial_interview_date,
            status="Scheduled"
        )
        
        # New interview date
        new_interview_date = timezone.now() + timezone.timedelta(days=2)
        
        # URL to schedule an interview
        url = reverse("JRS:schedule_interview", kwargs={"job_id": self.job.id})
        
        # POST request to update the interview date
        response = self.client.post(url, {"candidate_id": self.job_application.id, "interview_date": new_interview_date})
        
        # Assert redirect to the same page
        self.assertRedirects(response, url)
        
        # Check if the interview schedule was updated
        interview_schedule = InterviewSchedule.objects.filter(
            candidate=self.candidate_user, job=self.job
        ).first()
        
        self.assertEqual(interview_schedule.scheduled_date.date(), new_interview_date.date())
        self.assertEqual(interview_schedule.status, "Scheduled")

