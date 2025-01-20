from xrlint.node import DataArrayNode
from xrlint.plugins.core.rules import plugin
from xrlint.rule import RuleContext, RuleOp


_EXPECTED_UNITY_FORMAT = "<unit> since <date> <time> <timezone>"


@plugin.define_rule(
    "time-coordinate",
    version="1.0.0",
    type="problem",
    description=(
        "Time coordinate (standard_name='time') should have"
        " unambiguous time units encoding."
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

        if node.name not in ctx.dataset.coords or attrs.get("standard_name") != "time":
            return

        if attrs.get("long_name") != "time":
            ctx.report("Attribute 'long_name' should be 'time'.")

        use_units_format_msg = (
            f"Specify 'units' attribute using format {_EXPECTED_UNITY_FORMAT!r}."
        )

        calendar: str | None = encoding.get("calendar", attrs.get("calendar"))
        units: str | None = encoding.get("units", attrs.get("units"))
        if not units or not calendar:
            if not calendar:
                ctx.report(
                    "Attribute 'calendar' should be specified.",
                )
            if not units:
                ctx.report(
                    "Attribute 'units' should be specified.",
                    suggestions=[use_units_format_msg],
                )
                # next checks concern units only
                return

        units_parts = units.split(" ")
        # note, may use regex here
        if len(units_parts) >= 4 and units_parts[1] == "since":
            # format seems ok, check timezone part
            last_part = units_parts[-1]
            has_tz = last_part.lower() == "utc" or last_part[0] in ("+", "-")
            if not has_tz:
                ctx.report(
                    f"Missing timezone in 'units' attribute: {units}",
                    suggestions=[
                        use_units_format_msg,
                        f"Append timezone specification, e.g., use"
                        f" {' '.join(units_parts[:-1] + ['utc'])!r}.",
                    ],
                )
            # units ok
            return

        ctx.report(
            f"Invalid 'units' attribute: {units}",
            suggestions=[use_units_format_msg],
        )
