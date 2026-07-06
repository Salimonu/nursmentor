import csv
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from cbt.models import Question, Option


class Command(BaseCommand):
    help = 'Import questions and options from CSV or JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            type=str,
            help='Path to the CSV or JSON file containing questions'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['csv', 'json'],
            help='File format (csv or json). Auto-detected if not specified.'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing questions before importing'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        file_format = options['format']
        clear_existing = options['clear']

        # Validate file exists
        if not Path(file_path).exists():
            raise CommandError(f'File not found: {file_path}')

        # Auto-detect format if not specified
        if not file_format:
            if file_path.endswith('.csv'):
                file_format = 'csv'
            elif file_path.endswith('.json'):
                file_format = 'json'
            else:
                raise CommandError('Cannot auto-detect format. Please specify --format csv or --format json')

        # Clear existing data if requested
        if clear_existing:
            Question.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared existing questions'))

        # Import based on format
        if file_format == 'csv':
            self.import_csv(file_path)
        elif file_format == 'json':
            self.import_json(file_path)

    def import_csv(self, file_path):
        """Import questions from CSV file.
        
        Expected CSV columns:
        text, category, option_a, option_b, option_c, option_d, correct_option, rationale
        """
        created_count = 0
        skipped_count = 0

        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            if not reader.fieldnames:
                raise CommandError('CSV file is empty or malformed')

            required_fields = {'text', 'category', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option'}
            if not required_fields.issubset(set(reader.fieldnames)):
                raise CommandError(f'CSV must have columns: {", ".join(required_fields)}')

            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                try:
                    # Validate required fields
                    if not row.get('text', '').strip():
                        self.stdout.write(self.style.WARNING(f'Row {row_num}: Skipped (missing text)'))
                        skipped_count += 1
                        continue

                    if not row.get('category', '').strip():
                        self.stdout.write(self.style.WARNING(f'Row {row_num}: Skipped (missing category)'))
                        skipped_count += 1
                        continue

                    # Validate category
                    category = row['category'].strip()
                    valid_categories = [cat[0] for cat in Question.Category.choices]
                    if category not in valid_categories:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Row {row_num}: Skipped (invalid category: {category})'
                            )
                        )
                        skipped_count += 1
                        continue

                    # Validate correct_option
                    correct_option = row.get('correct_option', '').strip().lower()
                    if correct_option not in ['a', 'b', 'c', 'd']:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Row {row_num}: Skipped (invalid correct_option: {correct_option})'
                            )
                        )
                        skipped_count += 1
                        continue

                    # Create question
                    question = Question.objects.create(
                        text=row['text'].strip(),
                        category=category,
                    )

                    # Create option
                    Option.objects.create(
                        question=question,
                        option_a=row['option_a'].strip(),
                        option_b=row['option_b'].strip(),
                        option_c=row['option_c'].strip(),
                        option_d=row['option_d'].strip(),
                        correct_option=correct_option,
                        rationale=row.get('rationale', '').strip() or None,
                    )

                    created_count += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Row {row_num}: Error - {str(e)}'))
                    skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'✓ Import complete: {created_count} created, {skipped_count} skipped')
        )

    def import_json(self, file_path):
        """Import questions from JSON file.
        
        Expected JSON format:
        [
            {
                "text": "Question text",
                "category": "fundamentals_of_nursing",
                "option_a": "Option A",
                "option_b": "Option B",
                "option_c": "Option C",
                "option_d": "Option D",
                "correct_option": "b",
                "rationale": "Why B is correct"
            },
            ...
        ]
        """
        created_count = 0
        skipped_count = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)
        except json.JSONDecodeError as e:
            raise CommandError(f'Invalid JSON: {str(e)}')

        if not isinstance(data, list):
            raise CommandError('JSON must be an array of question objects')

        for item_num, item in enumerate(data, start=1):
            try:
                # Validate required fields
                if not isinstance(item, dict):
                    self.stdout.write(self.style.WARNING(f'Item {item_num}: Skipped (not a dict)'))
                    skipped_count += 1
                    continue

                required_fields = {'text', 'category', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option'}
                if not required_fields.issubset(set(item.keys())):
                    self.stdout.write(
                        self.style.WARNING(
                            f'Item {item_num}: Skipped (missing fields: {", ".join(required_fields - set(item.keys()))})'
                        )
                    )
                    skipped_count += 1
                    continue

                if not item.get('text', '').strip():
                    self.stdout.write(self.style.WARNING(f'Item {item_num}: Skipped (missing text)'))
                    skipped_count += 1
                    continue

                # Validate category
                category = item['category'].strip()
                valid_categories = [cat[0] for cat in Question.Category.choices]
                if category not in valid_categories:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Item {item_num}: Skipped (invalid category: {category})'
                        )
                    )
                    skipped_count += 1
                    continue

                # Validate correct_option
                correct_option = item.get('correct_option', '').strip().lower()
                if correct_option not in ['a', 'b', 'c', 'd']:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Item {item_num}: Skipped (invalid correct_option: {correct_option})'
                        )
                    )
                    skipped_count += 1
                    continue

                # Create question
                question = Question.objects.create(
                    text=item['text'].strip(),
                    category=category,
                )

                # Create option
                Option.objects.create(
                    question=question,
                    option_a=item['option_a'].strip(),
                    option_b=item['option_b'].strip(),
                    option_c=item['option_c'].strip(),
                    option_d=item['option_d'].strip(),
                    correct_option=correct_option,
                    rationale=item.get('rationale', '').strip() or None,
                )

                created_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Item {item_num}: Error - {str(e)}'))
                skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'✓ Import complete: {created_count} created, {skipped_count} skipped')
        )
