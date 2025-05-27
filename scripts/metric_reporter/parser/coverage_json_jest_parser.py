"""Module for parsing Jest json files."""

from collections import defaultdict
from typing import Any


class JestJsonParser:
    """Jest JSON parser."""

    @staticmethod
    def parse_jest_json(json_data: dict[str, Any]):
        """Parse Jest json file."""
        totals: dict[str, Any] = defaultdict(lambda: {"count": 0, "covered": 0})

        for filepath, metrics in json_data.items():
            # Statements
            statement_map = metrics["statementMap"]
            statement_hits = metrics["s"]
            for statement_id, lines_of_coverage in statement_map.items():
                start_line = lines_of_coverage["start"]["line"]
                end_line = lines_of_coverage["end"]["line"]
                lines = range(start_line, end_line + 1)
                line_count = len(lines)

                totals["line"]["count"] += line_count
                totals["statement"]["count"] += 1

                if statement_hits[statement_id] > 0:
                    totals["line"]["covered"] += line_count
                    totals["statement"]["covered"] += 1

            # Functions
            func_hits = metrics["f"]
            totals["function"]["count"] += len(func_hits)
            totals["function"]["covered"] += sum(1 for count in func_hits.values() if count > 0)

            # Branches
            branch_hits = metrics["b"]
            for branch in branch_hits.values():
                totals["branch"]["count"] += len(branch)
                totals["branch"]["covered"] += sum(1 for hit in branch if hit > 0)

        # Uncovered lines
        for item in totals.values():
            item["not_covered"] = item["count"] - item["covered"]

        # Compute percentages
        for key, val in totals.items():
            val["percent"] = (
                round((val["covered"] / val["count"]) * 100, 2) if val["count"] > 0 else 100.0
            )
        return totals
