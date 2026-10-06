from django.test import TestCase
import pandas as pd
from apps.accounts.services.roster_sync import StudentRosterParser, classify_roster_diff
from apps.accounts.models import Program

class RosterSyncTests(TestCase):
    def test_parser_normalizes_data(self):
        df = pd.DataFrame({
            'Student ID': [' 2024-10001 '],
            'Email': [' JOHN.DOE@university.edu.ph '],
            'First Name': ['JOHN'],
            'Last Name': ['DOE'],
            'Course': [' BSCS '],
            'Year Level': ['1st Year'],
            'Section': ['A']
        })
        
        parsed_df = StudentRosterParser.parse_dataframe(df)
        self.assertEqual(len(parsed_df), 1)
        row = parsed_df.iloc[0]
        self.assertEqual(row['student_id'], '2024-10001')
        self.assertEqual(row['email'], 'john.doe@university.edu.ph')
        self.assertEqual(row['first_name'], 'John')
        self.assertEqual(row['last_name'], 'Doe')
        self.assertEqual(row['course'], 'BSCS')
        self.assertEqual(row['year_level'], '1')
        self.assertEqual(row['section'], 'A')
