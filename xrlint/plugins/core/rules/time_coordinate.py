import re


from xrlint.node import DataArrayNode
from xrlint.plugins.core.plugin import plugin
from xrlint.rule import RuleContext, RuleOp


_EXAMPLE_UNIT_1 = "seconds since 2010-10-8 15:15:42.5 -6:00"
_EXAMPLE_UNIT_2 = "days since 2000-01-01 +0:00"

_AMBIGUOUS_UNITS_OF_TIME = (
    "years",
    "year",
    "y",
    "months",
    "month",
    "m",
)

_UNAMBIGUOUS_UNITS_OF_TIME = (
    "days",
    "day",
    "d",
    "hours",
    "hour",
    "hr",
    "h",
    "minutes",
    "minute",
    "min",
    "seconds",
    "second",
    "sec",
    "s",
)

_ALL_UNITS_OF_TIME = (*_AMBIGUOUS_UNITS_OF_TIME, *_UNAMBIGUOUS_UNITS_OF_TIME)

_RE_DATE = re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$")
_RE_TIME = re.compile(r"^\d{1,2}:\d{1,2}:\d{1,2}(\.\d{1,6})?$")
_RE_TZ = re.compile(r"^[+-]\d{1,2}:\d{1,2}$")


@plugin.define_rule(
    "time-coordinate",
    version="1.0.0",
    type="problem",
    description=(
        "Time coordinates should have valid and unambiguous time units encoding."
    ),
    docs_url=(
        "https://cfconventions.org/cf-conventions/cf-conventions.html#time-coordinate"
    ),
)
class TimeCoordinate(RuleOp):
    def data_array(self, ctx: RuleContext, node: DataArrayNode):
        array = node.data_array
        attrs = array.attrs
        encoding = array.encoding

        units: str | None = encoding.get("units", attrs.get("units"))
        if units is None:
            if _is_time_by_name(attrs):
                ctx.report("Missing 'units' attribute for time coordinate.")
            # No more to check w.o. time units
            return
        elif not isinstance(units, str):
            if _is_time_by_name(attrs):
                ctx.report(
                    f"Invalid 'units' attribute for time coordinate,"
                    f" expected type str, got {type(units).__name__}."
                )
            # No more to check w.o. time units
            return

        units_ok = True
        units_parts = units.split(" ")
        num_unit_parts = len(units_parts)
        is_time_by_units = num_unit_parts >= 3 and units_parts[1] == "since"
        if not is_time_by_units:
            if not _is_time_by_name(attrs):
                # Not a time coordinate
                return
            units_ok = False
        else:
            # We have time units

            if not encoding.get("calendar", attrs.get("calendar")):
                ctx.report(
                    "Attribute/encoding 'calendar' should be specified.",
                )

            uot_part = units_parts[0]
            date_part = units_parts[2]
            time_part = None
            tz_part = None

            if uot_part not in _ALL_UNITS_OF_TIME:
                ctx.report(
                    f"Unrecognized units of measure for time"
                    f" in 'units' attribute: {units!r}.",
                    suggestions=[
                        _units_format_suggestion(),
                        _units_of_time_suggestion(),
                    ],
                )
            elif uot_part in _AMBIGUOUS_UNITS_OF_TIME:
                ctx.report(
                    f"Ambiguous units of measure for time in"
                    f" 'units' attribute: {units!r}.",
                    suggestions=[
                        _units_format_suggestion(),
                        _units_of_time_suggestion(),
                    ],
                )

            if num_unit_parts == 3:
                pass
            elif num_unit_parts == 4:
                time_or_tz_part = units_parts[3]
                if _RE_TIME.match(time_or_tz_part):
                    time_part = time_or_tz_part
                else:
                    tz_part = time_or_tz_part
            elif num_unit_parts == 5:
                time_part = units_parts[3]
                tz_part = units_parts[4]
            else:
                time_part = units_parts[-2]
                tz_part = units_parts[-1]
                units_ok = False

            if units_ok and not _RE_DATE.match(date_part):
                units_ok = False
            if units_ok and time_part and not _RE_TIME.match(time_part):
                units_ok = False
            if units_ok and tz_part and not _RE_TZ.match(tz_part):
                units_ok = False

            if not tz_part:
                ctx.report(
                    f"Missing timezone in 'units' attribute: {units!r}.",
                    suggestions=[
                        _units_format_suggestion(),
                        f"Append timezone specification, e.g., use"
                        f" {' '.join(units_parts[:-1] + ['+0:00'])!r}.",
                    ],
                )

        if not units_ok:
            ctx.report(
                f"Invalid 'units' attribute: {units!r}.",
                suggestions=[_units_format_suggestion()],
            )


def _units_format_suggestion():
    use_units_format_msg = (
        f"Specify 'units' attribute using the UDUNITS format,"
        f" e.g., {_EXAMPLE_UNIT_1!r} or {_EXAMPLE_UNIT_2!r}."
    )
    return use_units_format_msg


def _units_of_time_suggestion():
    return f"Use one of {', '.join(map(repr, _UNAMBIGUOUS_UNITS_OF_TIME))}"


def _is_time_by_name(attrs):
    return attrs.get("standard_name") == "time" or attrs.get("axis") == "T"
