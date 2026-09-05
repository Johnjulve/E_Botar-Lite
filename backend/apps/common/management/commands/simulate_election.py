import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from apps.accounts.models import Program, UserProfile
from apps.elections.models import SchoolElection, SchoolPosition, ElectionPosition
from apps.candidates.models import Candidate
from apps.voting.models import Ballot, VoteChoice, VoteReceipt, VoteBlock
from apps.voting.vote_ledger import append_vote_blocks_for_ballot, verify_election_vote_chain
from apps.voting.services import VotingDataService


class Command(BaseCommand):
    help = 'Simulate a high-turnout realistic election with blockchain blocks and receipts'

    def handle(self, *args, **options):
        self.stdout.write('Starting high-turnout election simulation...')

        # Find active election
        election = SchoolElection.objects.filter(is_active=True).first()
        if not election:
            self.stdout.write(self.style.ERROR('No active election found. Please run seed_data first.'))
            return

        election_positions = election.election_positions.filter(is_enabled=True)
        if not election_positions.exists():
            self.stdout.write(self.style.ERROR('No enabled positions found in active election.'))
            return

        positions = [ep.position for ep in election_positions]

        # Fetch courses
        courses = list(Program.objects.filter(program_type=Program.ProgramType.COURSE))

        first_names = [
            'Gabriel', 'Joshua', 'Christian', 'Daniel', 'Angelo', 'Mark', 'Paul', 'Anthony',
            'Patricia', 'Samantha', 'Nicole', 'Angelica', 'Bea', 'Clarisse', 'Danielle', 'Erika',
            'Francis', 'Harold', 'Ian', 'Kevin', 'Lance', 'Michael', 'Nathan', 'Oliver'
        ]
        last_names = [
            'Bautista', 'Castillo', 'Dela Cruz', 'Flores', 'Garcia', 'Hernandez', 'Ignacio',
            'Jimenez', 'Lim', 'Mendoza', 'Navarro', 'Ocampo', 'Pascual', 'Quinto', 'Ramos',
            'Salazar', 'Tolentino', 'Umali', 'Valdez', 'Villanueva', 'Yambao', 'Zamora'
        ]

        created_students = []
        for i, (fn, ln) in enumerate(zip(first_names, last_names), start=101):
            username = f"{fn.lower()}.{ln.lower().replace(' ', '')}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f"{username}@ebotar.edu.ph",
                    'first_name': fn,
                    'last_name': ln,
                    'is_staff': False,
                    'is_superuser': False,
                }
            )
            if created:
                user.set_password('student12345')
                user.save()
                course = random.choice(courses) if courses else None
                UserProfile.objects.create(
                    user=user,
                    student_id=f"2026-{10000 + i}",
                    department=course.department if course else None,
                    course=course,
                    year_level=str(random.randint(1, 4)),
                    section=str(random.randint(1, 4)),
                    is_verified=True,
                )
            created_students.append(user)

        self.stdout.write(f' -> Populated {len(created_students)} student profiles.')

        # Simulate Voting (85% turnout)
        voters_to_cast = created_students[:int(len(created_students) * 0.85)]
        votes_cast = 0

        for voter in voters_to_cast:
            if Ballot.objects.filter(election=election, user=voter).exists():
                continue

            # Pick choices per position
            selected_candidates = []
            for pos in positions:
                cands = list(Candidate.objects.filter(election=election, position=pos, is_active=True))
                if cands:
                    selected = random.choice(cands)
                    selected_candidates.append((pos, selected))

            if not selected_candidates:
                continue

            with transaction.atomic():
                receipt = VoteReceipt.objects.create(
                    user=voter,
                    election=election,
                    ip_address='127.0.0.1',
                )

                ballot = Ballot.objects.create(
                    user=voter,
                    election=election,
                    receipt=receipt,
                    ip_address='127.0.0.1',
                    user_agent='Simulated Voter Agent/1.0',
                )

                choices_saved = []
                for pos, cand in selected_candidates:
                    choice = VoteChoice.objects.create(
                        ballot=ballot,
                        position=pos,
                        candidate=cand,
                    )
                    choice.anonymize()
                    choices_saved.append(choice)

                # Append to Blockchain Ledger
                append_vote_blocks_for_ballot(
                    election_id=election.id,
                    ballot_identifier=str(ballot.pk),
                    receipt_secret=receipt.receipt_hash,
                    user_id=voter.id,
                    choices=choices_saved,
                )

                votes_cast += 1

        VotingDataService.invalidate_voting_cache(election.id)

        # Audit Chain
        chain_valid, message = verify_election_vote_chain(election)
        total_blocks = VoteBlock.objects.filter(election=election).count()
        total_voters = User.objects.filter(is_staff=False, is_superuser=False).count()
        total_ballots = Ballot.objects.filter(election=election).count()
        turnout = (total_ballots / total_voters * 100) if total_voters else 0

        self.stdout.write(self.style.SUCCESS('=================================================='))
        self.stdout.write(self.style.SUCCESS('   E-BOTAR LITE: SIMULATION COMPLETED!            '))
        self.stdout.write(self.style.SUCCESS('=================================================='))
        self.stdout.write(f' Election Title:        {election.title}')
        self.stdout.write(f' Registered Students:   {total_voters}')
        self.stdout.write(f' Total Ballots Cast:    {total_ballots}')
        self.stdout.write(f' Turnout Percentage:    {turnout:.1f}%')
        self.stdout.write(f' Blockchain Blocks:     {total_blocks} block(s)')
        self.stdout.write(f' Blockchain Integrity:  {"VALID (TAMPER-FREE)" if chain_valid else "INVALID"}')
        self.stdout.write(self.style.SUCCESS('=================================================='))
