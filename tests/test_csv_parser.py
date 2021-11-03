from schedule_bot import csv_parser


def test_fetch_classes_schedules_from_csv():
    classes_schedules = csv_parser._fetch_classes_schedules_from_csv(
        "tests/test.csv"
    )
