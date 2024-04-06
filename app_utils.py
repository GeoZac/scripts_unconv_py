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
    table.add_column("Sensor Id")
    table.add_column("Sensor name")
    table.add_column(
        "Description",
        max_width=40,
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
