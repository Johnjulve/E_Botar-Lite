import csv
import io
from django.test import TestCase
from apps.accounts.services.roster_sync import StudentRosterParser
from apps.accounts.models import Program

class RosterSyncTests(TestCase):
    def setUp(self):
        Program.objects.create(name='Bachelor of Science in Computer Science', code='BSCS', program_type=Program.ProgramType.COURSE)

    def test_parser_normalizes_data(self):
        csv_content = (
            "Student ID,Email,First Name,Last Name,Course,Year Level,Section\n"
            " 2024-10001 , JOHN.DOE@university.edu.ph ,JOHN,DOE, BSCS ,1st Year,A\n"
        )
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        parser = StudentRosterParser()
        parsed_records, errors = parser.parse_file(csv_file, filename='test.csv')
        if errors:
            print("ERRORS:", errors)
        self.assertEqual(len(parsed_records), 1)
        
        row = parsed_records[0]
        self.assertEqual(row['student_id'], '2024-10001')
        self.assertEqual(row['email'], 'john.doe@university.edu.ph')
        self.assertEqual(row['first_name'], 'JOHN')
        self.assertEqual(row['last_name'], 'DOE')
        self.assertEqual(row['course_code'], 'BSCS')
        self.assertEqual(row['year_level'], '1st Year')
        self.assertEqual(row['section'], 'A')
