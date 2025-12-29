import isodate
from xrlint.node import DatasetNode
from xrlint.rule import RuleContext, RuleOp
from xrlint.plugins.acdd.plugin import plugin


def datetime_is_iso(date_str):
    """Attempts to parse a date formatted in ISO 8601 format"""
    try:
        if len(date_str) > 10:
            isodate.parse_datetime(date_str)
        else:
            isodate.parse_date(date_str)
        return True, []
    # The following errors qualify as non ISO8601 format
    except (TypeError, AttributeError, ValueError, isodate.ISO8601Error):
        return False, ["Datetime provided is not in a valid ISO 8601 format"]


@plugin.define_rule(
    "1.3-dates-iso-format",
    version="1.3",
    description="ACDD date attributes must be in ISO format.",
    docs_url="https://wiki.esipfed.org/Attribute_Convention_for_Data_Discovery_1-3",
)
class IsoDates(RuleOp):
    def validate_dataset(self, ctx: RuleContext, node: DatasetNode):
        for attr in (
            "date_created",
            "date_issued",
            "date_modified",
            "date_metadata_modified",
        ):
            if attr in node.dataset.attrs:
                value = node.dataset.attrs[attr]
                iso_check, _msg = datetime_is_iso(value)

                if not iso_check:
                    ctx.report(
                        f"Attribute '{attr}' is not in ISO format: {value!r}",
                        suggestions=[
                            "Change '{attr}' to be in ISO format (e.g. YYYY-MM-DDThh:mm:ssZ).",
                        ],
                    )
