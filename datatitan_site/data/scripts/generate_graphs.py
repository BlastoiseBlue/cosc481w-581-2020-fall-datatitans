from django.core.cache import cache
from django.db.models import F, TextField, FloatField, IntegerField
from django.db.models.functions import Cast
import os
import pandas as pd

from data.models import Country


def gen_graph(
    *iso_codes, category: str, chart_type: str = "line", metric: str = "raw"
) -> dict:
    """Creates a graph that tracks a data category over time for an arbitrary number of countries.

    :param iso_codes: ISO codes of countries to create graphs for
    :param category: The category of data to track (currently supported categories: total_cases, total_deaths)
    :param chart_type: The type of graph to generate (currently supported graphs: line)
    :param metric: Whether to display raw numbers, or to display the numbers per thousand/million
    :return: A dictionary representing the generated graph
    :rtype: dict
    """
    if len(iso_codes) == 0:
        return {}
    category_name = (
        f"""{"new" if chart_type.lower() == "bar" else "total"}_{category.lower()}"""
    )
    if metric == "normalized":
        category_name += f"""_per_{"thousand" if category == "tests" else "million"}"""

    selected_countries = Country.objects.filter(iso_code__in=iso_codes)

    title = (
        category_name.replace("_", " ").title()
        + " in "
        + ", ".join(selected_countries.values_list("name", flat=True))
    )

    data: pd.DataFrame = (
        pd.read_parquet(
            os.getenv("INPUT_FILE"),
            columns=["date", category_name],
        )
        .round(decimals=3)
        .loc[list(iso_codes)]
    )
    # data["iso_code"] = data["iso_code"].astype("category")
    # data["date"] = pd.to_datetime(
    #     data["date"], yearfirst=True, infer_datetime_format=True
    # )
    # data["date"] = data["date"].dt.date
    # data = data.set_index(["iso_code", "date"]).sort_index().round(decimals=3)
    # data = data.loc[list(iso_codes)]

    data_sets = []
    if chart_type.lower() == "line":
        # Fairly simple implementation
        # base_query = CovidDataClean.objects.filter(iso_code__in=iso_codes)
        data_sets = [
            {
                "label": code,
                # "data": list(
                #     base_query.filter(iso_code=code).values(
                #         x=Cast(F("date"), TextField()),
                #         y=Cast(F(category_name.lower()), IntegerField()),
                #     )
                # ),
                "data": data.loc[code]
                .dropna()
                .rename(columns={"date": "x", category_name: "y"})
                .to_dict("records"),
                # "parsing": {
                #     "yAxisKey": category_name.lower()
                # }
            }
            for code in iso_codes
        ]
    elif chart_type.lower() == "bar":
        # This was an absolute nightmare to figure out
        # base_query = CovidDataMonthly.objects.filter(iso_code__in=iso_codes)
        data_sets = [
            {
                "label": code,
                # "data": list(
                #     base_query.filter(iso_code=code).values(
                #         x=Cast(F("month"), TextField()),
                #         y=Cast(
                #             F(category_name.lower()),
                #             IntegerField() if metric == "raw" else FloatField(),
                #         ),
                #     )
                # ),
                "data": data.loc[code]
                .groupby(pd.Grouper(key="date", freq="M"))
                .agg(y=pd.NamedAgg(category_name, "sum"))
                .reset_index()
                .rename(columns={"date": "x"})
                .to_dict("records"),
                # "stack": code
            }
            for code in iso_codes
        ]
    return {
        "type": chart_type.lower(),
        "data": {"datasets": data_sets},
        "options": {
            "title": {"display": True, "text": title},
            "scales": {
                "xAxes": [
                    {
                        "type": "time",
                        "time": {"unit": "month", "tooltipFormat": "YYYY-MM-DD"},
                        "stacked": chart_type.lower() == "bar",
                        "offset": True,
                    }
                ],
                # "yAxes": [{
                #     "stacked": chart_type.lower() == "bar"
                # }]
            },
        },
    }
