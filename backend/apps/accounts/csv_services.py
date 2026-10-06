import csv
import io
import logging
from django.db import transaction
from .models import Program

logger = logging.getLogger(__name__)

def process_program_csv(uploaded_file, preview_only=False):
    """
    Parses and validates a CSV of programs, returning a preview or executing the import.
    Returns a tuple: (success: bool, response_data: dict, status_code: int)
    """
    try:
        decoded_file = uploaded_file.read().decode('utf-8-sig')
        csv_reader = csv.DictReader(io.StringIO(decoded_file))

        errors = []
        parsed_rows = []
        department_codes_in_csv = set()
        planned_actions = []

        for row_num, row in enumerate(csv_reader, start=2):
            name = (row.get('name') or '').strip()
            code = (row.get('code') or '').strip()
            program_type = (row.get('program_type') or '').strip().lower()
            description = (row.get('description') or '').strip()
            department_code_row = (row.get('department_code') or '').strip()

            if not name or not code or not program_type:
                errors.append({'row': row_num, 'error': 'Missing name, code, or program_type'})
                continue

            if program_type not in ['department', 'course']:
                errors.append({'row': row_num, 'error': f'Invalid program_type: {program_type}'})
                continue

            if program_type == 'department':
                department_codes_in_csv.add(code)

            existing_program = Program.objects.filter(program_type=program_type, code=code).first()
            action_name = 'updated' if existing_program else 'created'

            parsed_rows.append({
                'row_num': row_num,
                'name': name,
                'code': code,
                'program_type': program_type,
                'description': description,
                'department_code': department_code_row,
            })
            planned_actions.append({
                'row_num': row_num,
                'name': name,
                'code': code,
                'program_type': program_type,
                'action': action_name,
            })

        existing_departments = Program.objects.filter(program_type=Program.ProgramType.DEPARTMENT)
        existing_department_map = {dept.code: dept for dept in existing_departments}

        for row in parsed_rows:
            if row['program_type'] != 'course':
                continue
            dept_code = row['department_code']
            if not dept_code:
                continue
            if dept_code not in existing_department_map and dept_code not in department_codes_in_csv:
                errors.append({
                    'row': row['row_num'],
                    'error': f'Department "{dept_code}" does not exist in database or CSV',
                })

        created_preview = [item for item in planned_actions if item['action'] == 'created']
        updated_preview = [item for item in planned_actions if item['action'] == 'updated']
        summary = {
            'total_rows': len(parsed_rows),
            'created_count': len(created_preview),
            'updated_count': len(updated_preview),
            'error_count': len(errors),
            'preview_only': preview_only,
        }

        if preview_only:
            return True, {
                'message': 'Validation completed' if not errors else f'Validation failed with {len(errors)} errors',
                'summary': summary,
                'created': created_preview,
                'updated': updated_preview,
                'errors': errors,
            }, 200

        if errors:
            return False, {
                'message': f'Import blocked with {len(errors)} errors',
                'summary': summary,
                'created': [],
                'updated': [],
                'errors': errors,
            }, 400

        imported = []
        created = []
        updated = []
        department_map = dict(existing_department_map)

        with transaction.atomic():
            for row in parsed_rows:
                program_data = {
                    'name': row['name'],
                    'code': row['code'],
                    'program_type': row['program_type'],
                    'description': row['description'],
                    'is_active': True,
                }

                existing = Program.objects.filter(program_type=row['program_type'], code=row['code']).first()
                write_action = 'updated' if existing else 'created'

                if existing:
                    for key, value in program_data.items():
                        setattr(existing, key, value)
                    program = existing
                else:
                    program = Program.objects.create(**program_data)

                if row['program_type'] == 'course' and row['department_code']:
                    program.department = department_map.get(row['department_code'])
                    program.save()
                elif row['program_type'] == 'department':
                    department_map[row['code']] = program
                    program.save()

                item = {'id': program.id, 'name': program.name, 'code': program.code, 'action': write_action}
                imported.append(item)
                if write_action == 'created':
                    created.append(item)
                else:
                    updated.append(item)

        return True, {
            'message': f'Import completed. {len(created)} created, {len(updated)} updated.',
            'summary': {**summary, 'preview_only': False},
            'imported': imported,
            'created': created,
            'updated': updated,
            'errors': [],
        }, 200

    except Exception as exc:
        logger.error('Error processing program CSV import: %s', exc, exc_info=True)
        return False, {'error': 'Error processing CSV file.'}, 400
