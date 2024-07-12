from datetime import datetime
from random import choices, shuffle
from string import ascii_uppercase, ascii_lowercase, digits

from rich.console import Console
from rich.table import Table


def value_or_alt(value, alt="-"):
    if not value:
        return alt
    return str(
        round(
            value,
            ndigits=3,
        ),
    )


def generate_random_string(length: str):
    return "".join(
        choices(
            ascii_uppercase + ascii_lowercase + digits,
            k=length,
        )
    )


def shuffle_string(string: str):
    string_list = list(string)
    shuffle(string_list)
    return "".join(string_list)


def find_location(sensor: dict):
    loc = sensor.get("sensorLocation")
    if loc:
        return loc.get("latitude"), loc.get("longitude")
    return None, None


def display_sensor_table(sensor_list):
    console = Console()

    table = Table(
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column(
        "Sensor Id",
        min_width=36,
    )
    table.add_column("Sensor name")
    table.add_column(
        "Description",
        overflow="crop",
    )
    table.add_column("Status")
    table.add_column("Deleted", justify="right")
    table.add_column("Loc. Lat. ", justify="center")
    table.add_column("Loc. Lang.", justify="center")
    table.add_column("Reading Count")

    for sensor in sensor_list:
        lat, long = find_location(sensor)
        table.add_row(
            sensor["id"],
            sensor["sensorName"],
            sensor["description"],
            sensor["sensorStatus"],
            str(sensor["deleted"]),
            value_or_alt(
                lat,
            ),
            value_or_alt(
                long,
            ),
            str(sensor["readingCount"]),
        )

    console.print(table)


def get_expiry_duration(expiry_string):
    expiry_date = datetime.fromisoformat(
        expiry_string[:-1],
    )
    current_date = datetime.now()
    delta = expiry_date - current_date

    days_delta = delta.days
    if days_delta < 0:
        return "Expired"
    if days_delta < 30:
        return f"Expiry in {days_delta} days"
    if days_delta < 180:
        days_delta = int(days_delta / 7)
        return f"Expiry in {days_delta} weeks"
    if days_delta < 365:
        days_delta = int(days_delta / 30)
        return f"Expiry in {days_delta} months"
    if days_delta > 365:
        days_delta = int(days_delta / 30)
        return f"Expiry in {days_delta} months"
    return "Failed to parse expiry"
