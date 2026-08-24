import os
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from apps.accounts.models import Program, UserProfile
from apps.elections.models import Party, SchoolPosition, SchoolElection, ElectionPosition
from apps.candidates.models import Candidate
from apps.voting.models import Ballot, VoteChoice, VoteReceipt
from apps.voting.vote_ledger import append_vote_blocks_for_ballot


class Command(BaseCommand):
    help = 'Seed initial data for E-Botar Lite'

    def handle(self, *args, **options):
        self.stdout.write('Seeding initial data...')

        # 1. Admin User
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@ebotar.edu.ph',
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin12345')
            admin.save()
            UserProfile.objects.create(user=admin, student_id='ADMIN-0001')
            self.stdout.write(self.style.SUCCESS('Created admin user (admin / admin12345)'))
        else:
            self.stdout.write('Admin user already exists.')

        # 2. Programs (Departments & Courses)
        ccs, _ = Program.objects.get_or_create(
            code='CCS',
            program_type=Program.ProgramType.DEPARTMENT,
            defaults={'name': 'College of Computer Studies', 'description': 'Computing & Informatics'}
        )
        coe, _ = Program.objects.get_or_create(
            code='COE',
            program_type=Program.ProgramType.DEPARTMENT,
            defaults={'name': 'College of Engineering', 'description': 'Engineering & Technology'}
        )

        bscs, _ = Program.objects.get_or_create(
            code='BSCS',
            program_type=Program.ProgramType.COURSE,
            defaults={'name': 'BS in Computer Science', 'department': ccs}
        )
        bsit, _ = Program.objects.get_or_create(
            code='BSIT',
            program_type=Program.ProgramType.COURSE,
            defaults={'name': 'BS in Information Technology', 'department': ccs}
        )

        # 3. Student Users
        students_data = [
            ('juan.delacruz', 'Juan', 'Dela Cruz', '2024-10001', ccs, bscs, '3rd Year', 'A'),
            ('maria.santos', 'Maria', 'Santos', '2024-10002', ccs, bscs, '3rd Year', 'A'),
            ('pedro.penduko', 'Pedro', 'Penduko', '2024-10003', ccs, bsit, '4th Year', 'B'),
            ('ana.reyes', 'Ana', 'Reyes', '2024-10004', coe, None, '2nd Year', 'A'),
        ]

        created_students = []
        for username, fname, lname, student_id, dept, course, year, sec in students_data:
            s_user, s_created = User.objects.get_or_create(
                username=username,
                defaults={'email': f"{username}@snsu.edu.ph", 'first_name': fname, 'last_name': lname}
            )
            if s_created:
                s_user.set_password('student12345')
                s_user.save()
            profile, _ = UserProfile.objects.get_or_create(
                user=s_user,
                defaults={
                    'student_id': student_id,
                    'department': dept,
                    'course': course,
                    'year_level': year,
                    'section': sec,
                    'is_verified': True
                }
            )
            created_students.append(s_user)

        self.stdout.write(self.style.SUCCESS(f'Ensured {len(created_students)} student users.'))

        # 4. Positions
        positions_info = [
            ('President', 'Chief Executive of USC', 1),
            ('Vice President', 'Assistant Chief Executive', 2),
            ('Secretary', 'Records and Communications', 3),
            ('Treasurer', 'Finance and Budgeting', 4),
            ('Auditor', 'Accountability and Review', 5),
        ]
        positions = []
        for name, desc, order in positions_info:
            pos, _ = SchoolPosition.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'display_order': order}
            )
            positions.append(pos)

        # 5. Parties
        forward_party, _ = Party.objects.get_or_create(
            name='Forward Party',
            defaults={'color': '#0b6e3b', 'description': 'Progress, innovation, and leadership.'}
        )
        alliance_party, _ = Party.objects.get_or_create(
            name='Alliance Party',
            defaults={'color': '#1d4ed8', 'description': 'Unity, service, and excellence.'}
        )

        # 6. Active University Election
        now = timezone.now()
        election, el_created = SchoolElection.objects.get_or_create(
            start_year=now.year,
            end_year=now.year + 1,
            election_type='university',
            defaults={
                'description': 'Annual University Student Council General Election',
                'start_date': now - timedelta(hours=2),
                'end_date': now + timedelta(days=5),
                'is_active': True,
                'created_by': admin
            }
        )

        # Enable positions for election
        for idx, pos in enumerate(positions):
            ElectionPosition.objects.get_or_create(
                election=election,
                position=pos,
                defaults={'order': idx, 'is_enabled': True}
            )

        # 7. Direct Candidates (Admin assigned)
        if len(created_students) >= 3:
            # Candidate 1: Juan for President (Forward Party)
            Candidate.objects.get_or_create(
                user=created_students[0],
                election=election,
                position=positions[0],
                defaults={
                    'party': forward_party,
                    'manifesto': 'Empowering students through technology and transparency.',
                    'is_active': True
                }
            )
            # Candidate 2: Maria for President (Alliance Party)
            Candidate.objects.get_or_create(
                user=created_students[1],
                election=election,
                position=positions[0],
                defaults={
                    'party': alliance_party,
                    'manifesto': 'Dedicated to holistic campus welfare and student rights.',
                    'is_active': True
                }
            )
            # Candidate 3: Pedro for Vice President (Forward Party)
            Candidate.objects.get_or_create(
                user=created_students[2],
                election=election,
                position=positions[1],
                defaults={
                    'party': forward_party,
                    'manifesto': 'Bridging the gap between the administration and the student body.',
                    'is_active': True
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with initial data!'))
