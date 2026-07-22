import ast
import pandas as pd
import numpy as np
import itertools


def process_combined_results(
    scenario_results, scenario_group, year, product, impact_category
):
    cols_to_drop = [col for col in scenario_results.columns if "baseline" in col] + [
        "Unnamed: 0"
    ]
    scenario_results = scenario_results.drop(cols_to_drop, axis=1)
    scenario_results.rename({"index": "reference_product_name"}, axis=1, inplace=True)
    scenario_results.set_index("reference_product_name", inplace=True)

    scenario_results = scenario_results.reset_index().melt(
        id_vars="reference_product_name",
        var_name="_col",
        value_name="value",
    )
    scenario_results["scenario"] = (
        scenario_group.split("+")[0]
        + "+"
        + scenario_results["_col"].apply(lambda x: "+".join(ast.literal_eval(x)))
    )
    scenario_results["scenario_group"] = scenario_group
    scenario_results["final_product_name"] = product
    scenario_results["year"] = year
    scenario_results["impact_category"] = impact_category
    scenario_results = scenario_results.drop(columns=["_col"])

    scenario_results = scenario_results.dropna()
    scenario_results.drop(
        scenario_results[scenario_results["reference_product_name"] == "Score"].index,
        inplace=True,
    )

    scenario_results["share"] = scenario_results["value"] / scenario_results.groupby(
        ["final_product_name", "scenario", "year", "impact_category"]
    )["value"].transform("sum")

    return scenario_results[
        [
            "scenario_group",
            "scenario",
            "year",
            "final_product_name",
            "impact_category",
            "reference_product_name",
            "value",
            "share",
        ]
    ]


def process_results(scenario_results, scenario_group, year, product, impact_category):
    scenario_results = scenario_results.drop(columns=["Unnamed: 0", "baseline"])
    scenario_results.rename({"index": "reference_product_name"}, axis=1, inplace=True)
    scenario_results.set_index("reference_product_name", inplace=True)

    scenario_results = scenario_results.reset_index().melt(
        id_vars="reference_product_name",
        var_name="_col",
        value_name="value",
    )
    scenario_results["scenario"] = (
        scenario_group.split("+")[0] + "+" + scenario_results["_col"]
    )
    scenario_results["scenario_group"] = scenario_group
    scenario_results["final_product_name"] = product
    scenario_results["year"] = year
    scenario_results["impact_category"] = impact_category
    scenario_results = scenario_results.drop(columns=["_col"])

    scenario_results = scenario_results.dropna()
    scenario_results.drop(
        scenario_results[scenario_results["reference_product_name"] == "Score"].index,
        inplace=True,
    )

    scenario_results["share"] = scenario_results["value"] / scenario_results.groupby(
        ["final_product_name", "scenario", "year", "impact_category"]
    )["value"].transform("sum")

    return scenario_results[
        [
            "scenario_group",
            "scenario",
            "year",
            "final_product_name",
            "impact_category",
            "reference_product_name",
            "value",
            "share",
        ]
    ]


def process_non_grouped_results(results, scenario):
    df = results.drop(columns=["Unnamed: 0", "unit", "database"])

    df.set_index("index", inplace=True)

    df = df.melt(
        id_vars=["reference product", "name", "location"],
        var_name="_col",
        value_name=f"value_{scenario}",
    )

    df["final_product_name"] = df["_col"].str.split("|").str[0].str.split(",").str[0]

    df = df[
        [
            "final_product_name",
            "reference product",
            "name",
            "location",
            f"value_{scenario}",
        ]
    ].dropna()

    return df


def process_all_impacts_results(scenario_results, scenario, year, product):
    scenario_results["final_product_name"] = product
    scenario_results["scenario"] = scenario

    scenario_results.rename({"index": "reference_product_name"}, axis=1, inplace=True)
    scenario_results.set_index("reference_product_name", inplace=True)

    scenario_results.drop(columns=["Unnamed: 0"], inplace=True)

    scenario_results = scenario_results.reset_index().melt(
        id_vars=["scenario", "reference_product_name", "final_product_name"],
        var_name="_col",
        value_name="value",
    )

    split = scenario_results["_col"].str.split("|", n=2, expand=True)
    scenario_results["impact_category"] = split[1].str.strip()
    scenario_results = scenario_results.drop(columns=["_col"])

    scenario_results = scenario_results.dropna()

    scenario_results.drop(
        scenario_results[scenario_results["reference_product_name"] == "Score"].index,
        inplace=True,
    )
    scenario_results["share"] = scenario_results["value"] / scenario_results.groupby(
        ["final_product_name", "impact_category", "scenario"]
    )["value"].transform("sum")

    scenario_results["year"] = year
    scenario_results["scenario_group"] = scenario

    return scenario_results[
        [
            "scenario_group",
            "scenario",
            "year",
            "final_product_name",
            "impact_category",
            "reference_product_name",
            "value",
            "share",
        ]
    ]


def process_timeline_results(scenario_results, scenario, product, impact_category):
    scenario_results["final_product_name"] = product
    scenario_results["scenario"] = scenario
    scenario_results.rename({"index": "reference_product_name"}, axis=1, inplace=True)
    scenario_results.set_index("reference_product_name", inplace=True)
    scenario_results.drop(columns=["Unnamed: 0"], inplace=True)
    scenario_results = scenario_results.reset_index().melt(
        id_vars=["scenario", "reference_product_name", "final_product_name"],
        var_name="_col",
        value_name="value",
    )

    scenario_results["year"] = scenario_results["_col"].str[-4:]

    scenario_results["impact_category"] = impact_category
    scenario_results = scenario_results.drop(columns=["_col"])
    scenario_results = scenario_results.dropna()

    scenario_results.drop(
        scenario_results[scenario_results["reference_product_name"] == "Score"].index,
        inplace=True,
    )
    scenario_results["share"] = scenario_results["value"] / scenario_results.groupby(
        ["final_product_name", "scenario", "year"]
    )["value"].transform("sum")

    scenario_results["scenario_group"] = scenario

    return scenario_results[
        [
            "scenario_group",
            "scenario",
            "year",
            "final_product_name",
            "impact_category",
            "reference_product_name",
            "value",
            "share",
        ]
    ]


def add_activity_metrics_vs_scenario(full_results, reference_scenario):
    df = full_results.copy()

    # ==========================================
    # 1. Define reference name + filters
    # ==========================================
    if reference_scenario == "baseline":
        reference_scenario_name = "baseline"
        ref_filter = df["scenario"] == reference_scenario

    else:
        reference_scenario_name = "background_2050"
        ref_filter = (df["scenario"] == reference_scenario) & (df["year"] == "2050")

    ref_col = f"value_{reference_scenario_name}"
    total_col = f"total_{reference_scenario_name}"

    var_abs_col = f"variation_activity_vs_{reference_scenario_name}"
    var_pct_col = f"variation_activity_vs_{reference_scenario_name}_pct"
    contrib_col = f"contribution_activity_vs_{reference_scenario_name}_pct"

    # ==========================================
    # 2. Build reference values (activity level)
    # ==========================================
    reference_value = (
        df.loc[
            ref_filter,
            [
                "reference_product_name",
                "final_product_name",
                "impact_category",
                "value",
            ],
        ]
        .groupby(
            ["reference_product_name", "final_product_name", "impact_category"],
            as_index=False,
        )
        .sum()
        .rename(columns={"value": ref_col})
    )

    # ==========================================
    # 3. Build total reference (per product + impact)
    # ==========================================
    total_reference = (
        reference_value.groupby(
            ["final_product_name", "impact_category"], as_index=False
        )[ref_col]
        .sum()
        .rename(columns={ref_col: total_col})
    )

    # ==========================================
    # 4. Merge reference
    # ==========================================
    df = df.merge(
        reference_value,
        on=["reference_product_name", "final_product_name", "impact_category"],
        how="left",
    )

    df = df.merge(
        total_reference,
        on=["final_product_name", "impact_category"],
        how="left",
    )

    # ==========================================
    # 5. Compute metrics only for non-reference rows
    # ==========================================
    mask = ~ref_filter

    denom_var = df.loc[mask, ref_col].replace(0, np.nan)
    denom_contrib = df.loc[mask, total_col].replace(0, np.nan)

    df.loc[mask, var_abs_col] = df.loc[mask, "value"] - df.loc[mask, ref_col]
    df.loc[mask, var_pct_col] = df.loc[mask, var_abs_col] / denom_var
    df.loc[mask, contrib_col] = df.loc[mask, var_abs_col] / denom_contrib

    # ==========================================
    # 6. Clean reference rows
    # ==========================================
    df[var_abs_col] = df[var_abs_col].fillna(0)
    df[var_pct_col] = df[var_pct_col].fillna(0)
    df[contrib_col] = df[contrib_col].fillna(0)

    # ==========================================
    # 7. Cleanup
    # ==========================================
    df.drop(columns=[ref_col, total_col], inplace=True)

    return df


def get_baseline_sdf(activity_list):
    sdf_data = []

    for activity in activity_list:
        for exc in activity.exchanges():
            sdf_data.append(
                {
                    "from activity name": exc.input["name"],
                    "from reference product": exc.input.get("reference product"),
                    "from location": exc.input.get("location"),
                    "from unit": exc.input.get("unit"),
                    "from categories": exc.input.get("categories"),
                    "from database": exc.input.get("database"),
                    "from key": str((exc.input.get("database"), exc.input.get("code"))),
                    "to activity name": activity["name"],
                    "to reference product": activity["reference product"],
                    "to location": activity["location"],
                    "to categories": activity.get("categories"),
                    "to database": activity["database"],
                    "to key": str((activity.get("database"), activity.get("code"))),
                    "flow type": exc["type"],  # technosphere / biosphere / production
                    "baseline": exc["amount"],
                }
            )

    sdf_df = pd.DataFrame(sdf_data)

    return sdf_df


def generate_methane_mitigation_scenario(
    sdf_baseline,
    feed_agri_products,
    exclusions_yield,
    CH4_name,
    scenario_name,
    yield_variation,
    feeding_level_variation,
    CH4_intensity_variation,
):
    sdf_milk_scenario = sdf_baseline.copy()

    sdf_milk_scenario = sdf_milk_scenario[
        (sdf_milk_scenario["flow type"] != "production")
    ]

    exclusions_yield = exclusions_yield[exclusions_yield["product"] == "cheese"]

    column_scenario = f"{scenario_name}"

    mask_feeding = (sdf_milk_scenario["from unit"] == "kilogram") & (
        sdf_milk_scenario["from reference product"].str.contains(
            "|".join(feed_agri_products), case=False, na=False
        )
    )

    mask_exclusions_yield = sdf_milk_scenario["from activity name"].isin(
        exclusions_yield["from activity name"]
    )

    sdf_milk_scenario.loc[(mask_exclusions_yield), column_scenario] = (
        sdf_milk_scenario.loc[(mask_exclusions_yield), "baseline"]
    )

    sdf_milk_scenario.loc[mask_feeding, column_scenario] = (
        sdf_milk_scenario.loc[mask_feeding, "baseline"] * (1 + feeding_level_variation)
    ) / (1 + yield_variation)
    sdf_milk_scenario.loc[(~mask_feeding & ~mask_exclusions_yield), column_scenario] = (
        sdf_milk_scenario.loc[(~mask_feeding & ~mask_exclusions_yield), "baseline"]
        / (1 + yield_variation)
    )

    sdf_milk_scenario.loc[
        sdf_milk_scenario["from activity name"] == CH4_name, column_scenario
    ] = sdf_milk_scenario.loc[
        sdf_milk_scenario["from activity name"] == CH4_name, "baseline"
    ] * (1 + CH4_intensity_variation)

    return sdf_milk_scenario


def generate_sdf_supplements(
    sdf_baseline,
    feed_agri_products,
    cow_feeding_DM_conversion,
    ei_mitigation,
    supplement_name,
    scenario_name,
    dose_supplement,
):
    sdf_baseline = sdf_baseline[sdf_baseline["flow type"] != "production"]

    mask_feeding = (sdf_baseline["from unit"] == "kilogram") & (
        sdf_baseline["from reference product"].str.contains(
            "|".join(feed_agri_products), case=False, na=False
        )
    )

    sdf_baseline_feed = sdf_baseline.loc[mask_feeding]

    sdf_baseline_feed = sdf_baseline_feed.merge(
        cow_feeding_DM_conversion,
        left_on="from activity name",
        right_on="activity name",
        how="left",
    )

    sdf_baseline_feed["baseline_DM"] = (
        sdf_baseline_feed["baseline"] * sdf_baseline_feed["conversion_to_kgDM"]
    )

    dmi = sdf_baseline_feed.groupby(
        ["to activity name", "to location"], as_index=False
    )["baseline_DM"].sum()

    dmi[f"{scenario_name}"] = dmi["baseline_DM"] * dose_supplement

    milk_production_cols = [c for c in sdf_baseline.columns if c.startswith("to ")] + [
        "flow type"
    ]

    milk_production_data = sdf_baseline[milk_production_cols].drop_duplicates(
        subset=["to activity name", "to location"]
    )

    milk_production_data = milk_production_data.merge(
        dmi[["to activity name", "to location", f"{scenario_name}"]],
        on=["to activity name", "to location"],
        how="inner",
    )

    supplement_activity = [
        activity for activity in ei_mitigation if supplement_name in activity["name"]
    ]

    supplement_activity_sdf = get_baseline_sdf(supplement_activity)
    supplement_activity_sdf = supplement_activity_sdf[
        supplement_activity_sdf["flow type"] == "production"
    ]

    from_cols = [c for c in supplement_activity_sdf.columns if c.startswith("from ")]

    supplement_sdf = (
        supplement_activity_sdf[from_cols]
        .drop_duplicates()
        .assign(_tmp=1)
        .merge(milk_production_data.assign(_tmp=1), on="_tmp")
        .drop(columns="_tmp")
    )

    return supplement_sdf


def generate_potato_scenario(
    sdf_baseline,
    exclusions_yield,
    CO2_name,
    N2O_name,
    scenario_name,
    yield_variation,
    CO2_variation,
    N2O_variation,
):
    sdf_potato_scenario = sdf_baseline.copy()

    sdf_potato_scenario = sdf_potato_scenario[
        (sdf_potato_scenario["flow type"] != "production")
    ]

    exclusions_yield = exclusions_yield[exclusions_yield["product"] == "potato"]

    column_scenario = f"{scenario_name}"

    mask_exclusions_yield = sdf_potato_scenario["from activity name"].isin(
        exclusions_yield["from activity name"]
    )

    sdf_potato_scenario.loc[(mask_exclusions_yield), column_scenario] = (
        sdf_potato_scenario.loc[(mask_exclusions_yield), "baseline"]
    )

    sdf_potato_scenario.loc[(~mask_exclusions_yield), column_scenario] = (
        sdf_potato_scenario.loc[(~mask_exclusions_yield), "baseline"]
        / (1 + yield_variation)
    )
    sdf_potato_scenario.loc[
        sdf_potato_scenario["from activity name"] == CO2_name, column_scenario
    ] = sdf_potato_scenario.loc[
        sdf_potato_scenario["from activity name"] == CO2_name, "baseline"
    ] * ((1 + CO2_variation) / (1 + yield_variation))
    sdf_potato_scenario.loc[
        sdf_potato_scenario["from activity name"] == N2O_name, column_scenario
    ] = sdf_potato_scenario.loc[
        sdf_potato_scenario["from activity name"] == N2O_name, "baseline"
    ] * ((1 + N2O_variation) / (1 + yield_variation))

    return sdf_potato_scenario


def add_label(full_results, consuming_activities_tractor, feed_agri_products):
    full_results["label"] = full_results["reference_product_name"]

    # Energy
    full_results.loc[
        full_results["reference_product_name"].str.match("heat,"), "label"
    ] = "heat"
    full_results.loc[
        full_results["reference_product_name"].str.match("electricity"), "label"
    ] = "electricity"
    full_results.loc[
        (
            full_results["reference_product_name"].str.match(
                "diesel, burned in diesel-electric generating set"
            )
        ),
        "label",
    ] = "diesel electricity generation"
    full_results.loc[
        (full_results["reference_product_name"].str.match("diesel"))
        & (~full_results["reference_product_name"].str.contains("burned")),
        "label",
    ] = "diesel production"
    full_results.loc[
        full_results["reference_product_name"].str.match("hard coal"), "label"
    ] = "hard coal"

    # Transport
    full_results.loc[
        full_results["reference_product_name"].str.match("transport, freight, lorry")
        | full_results["reference_product_name"].str.match(
            "transport, freight, light commercial vehicle"
        ),
        "label",
    ] = "road transport"
    full_results.loc[
        full_results["reference_product_name"].str.match("transport, freight, train"),
        "label",
    ] = "train transport"
    full_results.loc[
        full_results["reference_product_name"].str.match("transport, freight, sea"),
        "label",
    ] = "sea transport"
    full_results.loc[
        full_results["reference_product_name"].str.match(
            "transport, freight, inland waterways, barge"
        ),
        "label",
    ] = "barge transport"

    # Agriculture
    full_results.loc[
        (
            full_results["reference_product_name"].str.match("land tenure")
            | full_results["reference_product_name"].str.match("land use change")
        ),
        "label",
    ] = "land management"
    full_results.loc[
        full_results["reference_product_name"].isin(consuming_activities_tractor),
        "label",
    ] = "agricultural operations"
    full_results.loc[
        full_results["reference_product_name"].str.contains(
            "|".join(feed_agri_products), case=False, na=False
        ),
        "label",
    ] = "cow feed agri-products"

    return full_results


def get_consuming_activities(activity_list):
    consuming_activities = set()

    for activity in activity_list:
        for exc in activity.upstream():
            consuming_activities.add(exc.output)

    return consuming_activities


def prepare_waterfall_data(
    data, product, background_scenario, mitigation_scenario, cutoff_value, label_to_show
):
    columns = [
        "scenario",
        "final_product_name",
        "year",
        "label",
        "value",
        "variation_activity_vs_baseline",
        "variation_activity_vs_background_2050",
        "contribution_activity_vs_baseline_pct",
        "contribution_activity_vs_background_2050_pct",
    ]
    data = data.loc[
        (data["final_product_name"] == product)
        & (data["impact_category"] == "climate change")
    ][columns]

    results_background = (
        data[(data["scenario"] == background_scenario) & (data["year"] == 2050)][
            [
                "label",
                "variation_activity_vs_baseline",
                "contribution_activity_vs_baseline_pct",
            ]
        ]
        .rename(
            columns={
                "variation_activity_vs_baseline": "CO2e",
                "contribution_activity_vs_baseline_pct": "CO2e_pct",
            }
        )
        .groupby("label", as_index=False)
        .sum()
        .sort_values(by="CO2e")
    )

    results_background = (
        results_background.groupby(["label"], as_index=False)
        .sum()
        .sort_values(by="CO2e")
    )
    results_background.loc[results_background["CO2e_pct"] > -cutoff_value, "label"] = (
        "other"
    )
    results_background = (
        results_background.groupby(["label"], as_index=False)
        .sum()
        .sort_values(by="CO2e")
    )

    sum_results_background = pd.DataFrame(
        {
            "label": "Background improvements",
            "CO2e": [results_background["CO2e"].sum()],
            "CO2e_pct": [results_background["CO2e_pct"].sum()],
        }
    )

    results_mitigation = (
        data[(data["scenario"] == mitigation_scenario) & (data["year"] == 2050)][
            [
                "label",
                "variation_activity_vs_background_2050",
                "contribution_activity_vs_background_2050_pct",
            ]
        ]
        .rename(
            columns={
                "variation_activity_vs_background_2050": "CO2e",
                "contribution_activity_vs_background_2050_pct": "CO2e_pct",
            }
        )
        .groupby("label", as_index=False)
        .sum()
        .sort_values(by="CO2e")
    )

    mask_variations_to_show = results_mitigation["label"].isin(label_to_show)

    results_mitigation.loc[~mask_variations_to_show, "label"] = "other"
    results_mitigation = (
        results_mitigation.groupby(["label"], as_index=False)
        .sum()
        .sort_values(by="CO2e")
    )

    results_mitigation["label"] = (
        results_mitigation["label"].fillna("").astype(str) + " · vs background"
    )

    totals = data.groupby(["final_product_name", "scenario", "year"], as_index=False)[
        "value"
    ].sum()

    total_baseline = totals[
        (totals["final_product_name"] == product) & (totals["scenario"] == "baseline")
    ][["scenario", "value"]].rename(columns={"scenario": "label", "value": "CO2e"})
    total_background = totals[
        (totals["final_product_name"] == product)
        & (totals["scenario"] == background_scenario)
        & (totals["year"] == 2050)
    ][["scenario", "value"]].rename(columns={"scenario": "label", "value": "CO2e"})
    total_mitigation = totals[
        (totals["final_product_name"] == product)
        & (totals["scenario"] == mitigation_scenario)
        & (totals["year"] == 2050)
    ][["scenario", "value"]].rename(columns={"scenario": "label", "value": "CO2e"})

    df_to_concat = (
        [
            total_baseline,
            sum_results_background,
            total_background,
            results_mitigation,
            total_mitigation,
        ]
        if mitigation_scenario != ""
        else [total_baseline, results_background, total_background]
    )

    waterfall_data = pd.concat(df_to_concat)
    waterfall_data = waterfall_data.reset_index(drop=True)

    return waterfall_data


def prepare_waterfall_figure(waterfall_data):
    wd = waterfall_data.reset_index(drop=True)
    n = len(wd)
    waterfall_x = wd["label"].fillna("").astype(str).tolist()
    waterfall_y = wd["CO2e"].astype(float).tolist()

    total_index = set(wd.index[wd["CO2e_pct"].isna()].tolist())
    has_wf_measure = "wf_measure" in wd.columns

    waterfall_measure = []
    for i in range(n):
        if has_wf_measure and pd.notna(wd["wf_measure"].iloc[i]):
            waterfall_measure.append(wd["wf_measure"].iloc[i])
            continue
        if i == 0:
            waterfall_measure.append("absolute")
        elif i == n - 1:
            waterfall_measure.append("total")
        elif i in total_index:
            waterfall_measure.append("total")
        else:
            waterfall_measure.append("relative")

    impact_red = wd["CO2e"].to_numpy()
    impact_red_pct = wd["CO2e_pct"].to_numpy()

    waterfall_text = []
    for i in range(n):
        m = waterfall_measure[i]
        val = float(impact_red[i])
        p = impact_red_pct[i]
        if m == "relative" and not pd.isna(p):
            waterfall_text.append(f"{float(p) * 100:.1f}%")
        else:
            waterfall_text.append(f"{val:.3f}")

    return waterfall_x, waterfall_y, waterfall_measure, waterfall_text


def add_carrying_capacity(
    waterfall_data, carrying_capacity, product, allocation_method
):
    mask = (allocated_carrying_capacity["product"] == product) & (
        allocated_carrying_capacity["allocation"] == allocation_method
    )
    allocated_carrying_capacity_value = float(
        allocated_carrying_capacity.loc[mask, "value"].iloc[0]
    )
    mit_co2e = float(waterfall_data.iloc[-1]["CO2e"])
    gap = allocated_carrying_capacity_value - mit_co2e
    gap_pct = gap / mit_co2e

    cc_label = f"Carrying capacity – {allocation_method} allocation"
    gap_row = pd.DataFrame(
        [
            {
                "label": "Gap to carrying capacity",
                "CO2e": gap,
                "CO2e_pct": gap_pct,
            }
        ]
    )
    cc_row = pd.DataFrame(
        [
            {
                "label": cc_label,
                "CO2e": allocated_carrying_capacity_value,
                "CO2e_pct": float("nan"),
            }
        ]
    )
    return pd.concat([waterfall_data, gap_row, cc_row], ignore_index=True)


def is_feed(act, feed_agri_products):
    ref = (act.get("reference product") or "").lower()
    unit = (act.get("unit") or "").lower()

    return unit == "kilogram" and any(f in ref for f in feed_agri_products)


def is_production(act):
    name = act["name"].lower()
    return "production" in name


def extract_feed_supply_chain(start_activities, feed_agri_products):
    sdf_data = []
    visited = set()

    activity_list = start_activities
    tier = 1

    while len(activity_list) > 0:
        print(f"Tier {tier}")

        next_activities = set()

        for activity in activity_list:
            act_key = (activity.get("database"), activity.get("code"))

            if act_key in visited:
                continue
            visited.add(act_key)

            for exc in activity.exchanges():
                if exc["type"] == "production":
                    continue

                input_act = exc.input

                input_is_feed = is_feed(input_act, feed_agri_products)

                if is_feed(activity, feed_agri_products) and is_production(activity):
                    sdf_data.append(
                        {
                            "from activity name": input_act["name"],
                            "from reference product": input_act.get(
                                "reference product"
                            ),
                            "from location": input_act.get("location"),
                            "from unit": input_act.get("unit"),
                            "from categories": input_act.get("categories"),
                            "from database": input_act.get("database"),
                            "from key": str(
                                (input_act.get("database"), input_act.get("code"))
                            ),
                            "to activity name": activity["name"],
                            "to reference product": activity.get("reference product"),
                            "to location": activity.get("location"),
                            "to categories": activity.get("categories"),
                            "to database": activity.get("database"),
                            "to key": str(
                                (activity.get("database"), activity.get("code"))
                            ),
                            "flow type": exc["type"],
                            "tier": tier,
                            "baseline": exc["amount"],
                        }
                    )

                if input_is_feed:
                    next_activities.add(input_act)

        print(f"New activites to explore: {len(next_activities)}")

        activity_list = list(next_activities)
        tier += 1

    sdf_feed = pd.DataFrame(sdf_data)

    cols_order = list(sdf_feed.columns)

    sdf_feed = sdf_feed.groupby(["from key", "to key"], as_index=False).agg(
        {
            "from activity name": "first",
            "from reference product": "first",
            "from location": "first",
            "from unit": "first",
            "from categories": "first",
            "from database": "first",
            "to activity name": "first",
            "to reference product": "first",
            "to location": "first",
            "to categories": "first",
            "to database": "first",
            "flow type": "first",
            "tier": "min",
            "baseline": "sum",
        }
    )

    return sdf_feed[cols_order]


def generate_cow_feed_scenario(
    sdf_baseline,
    CO2_name,
    N2O_name,
    scenario_name,
    yield_variation,
    CO2_variation,
    N2O_variation,
):
    sdf_feed_scenario = sdf_baseline.copy()

    sdf_feed_scenario = sdf_feed_scenario[
        (sdf_feed_scenario["flow type"] != "production")
    ]

    column_scenario = f"{scenario_name}"

    sdf_feed_scenario.loc[:, column_scenario] = sdf_feed_scenario.loc[:, "baseline"] / (
        1 + yield_variation
    )
    sdf_feed_scenario.loc[
        sdf_feed_scenario["from activity name"] == CO2_name, column_scenario
    ] = sdf_feed_scenario.loc[
        sdf_feed_scenario["from activity name"] == CO2_name, "baseline"
    ] * ((1 + CO2_variation) / (1 + yield_variation))
    sdf_feed_scenario.loc[
        sdf_feed_scenario["from activity name"] == N2O_name, column_scenario
    ] = sdf_feed_scenario.loc[
        sdf_feed_scenario["from activity name"] == N2O_name, "baseline"
    ] * ((1 + N2O_variation) / (1 + yield_variation))

    return sdf_feed_scenario


def get_baseline_production_exchanges(activities, background_database, future_columns):
    consuming_activities = set()
    for activity in activities:
        for exc in activity.upstream():
            consuming_activities.add(exc.output)

    sdf_baseline_consuming_activities = get_baseline_sdf(
        sorted(consuming_activities, key=lambda a: a.get("name", ""))
    )

    activities_names = {a["name"] for a in activities}
    sdf_baseline_exchanges = (
        sdf_baseline_consuming_activities[
            (
                sdf_baseline_consuming_activities["from activity name"].isin(
                    activities_names
                )
                & (
                    sdf_baseline_consuming_activities["to database"]
                    == background_database.name
                )
            )
        ]
        .reset_index(drop=True)
        .copy()
    )

    sdf_baseline_exchanges = sdf_baseline_exchanges.assign(
        **{c: sdf_baseline_exchanges["baseline"] for c in future_columns}
    )

    return sdf_baseline_exchanges


def model_projection_activity(projection_activities, co2_name):
    projection_sdfs = []
    for projection_activity in projection_activities:
        for exc in projection_activity.exchanges():
            if exc.input.get("name") == co2_name:
                projection_sdfs.append(
                    {
                        "from activity name": exc.input["name"],
                        "from reference product": exc.input.get("reference product"),
                        "from location": exc.input.get("location"),
                        "from unit": exc.input.get("unit"),
                        "from categories": exc.input.get("categories"),
                        "from database": exc.input.get("database"),
                        "from key": str(
                            (exc.input.get("database"), exc.input.get("code"))
                        ),
                        "to activity name": projection_activity["name"],
                        "to reference product": projection_activity[
                            "reference product"
                        ],
                        "to location": projection_activity["location"],
                        "to categories": projection_activity.get("categories"),
                        "to database": projection_activity["database"],
                        "to key": str(
                            (
                                projection_activity.get("database"),
                                projection_activity.get("code"),
                            )
                        ),
                        "flow type": exc["type"],
                        "baseline": exc["amount"],
                    }
                )

    projection_sdf = pd.DataFrame(projection_sdfs)

    return projection_sdf


def generate_historical_projection(
    sdf_baseline_exchanges, projection_sdf, year, future_columns
):
    target_year = [year]

    sdf_baseline = sdf_baseline_exchanges.copy()
    sdf_nulled = sdf_baseline.copy().assign(**{c: 0.0 for c in target_year})
    sdf_baseline = sdf_baseline_exchanges.copy().assign(
        **{c: 0.0 for c in future_columns if c not in target_year}
    )
    n_baseline = len(sdf_baseline)
    sdf_stacked = pd.concat([sdf_baseline, sdf_nulled], ignore_index=True, sort=False)

    mask_baseline = sdf_stacked.index < n_baseline
    from_pfx, to_pfx = "from ", "to "
    mp = projection_sdf.drop_duplicates(subset=["to location"], keep="first").set_index(
        "to location"
    )
    loc_series = sdf_stacked.loc[mask_baseline, "from location"]
    for col in sdf_stacked.columns:
        if not isinstance(col, str) or not col.startswith(from_pfx):
            continue
        to_col = to_pfx + col[len(from_pfx) :]
        if to_col not in mp.columns:
            continue
        sdf_stacked.loc[mask_baseline, col] = loc_series.map(mp[to_col]).values

    sdf_historical_projection = sdf_stacked.drop(
        columns=["from unit", "baseline"], errors="ignore"
    ).reset_index(drop=True)

    cols_order = list(sdf_historical_projection.columns)
    year_cols = [c for c in future_columns if c in sdf_historical_projection.columns]
    meta_cols = [
        c
        for c in sdf_historical_projection.columns
        if c not in year_cols and c not in ("from key", "to key")
    ]
    agg_map = {c: "first" for c in meta_cols}
    agg_map.update({c: "sum" for c in year_cols})
    sdf_historical_projection = sdf_historical_projection.groupby(
        ["from key", "to key"], as_index=False, sort=False
    ).agg(agg_map, numeric_only=False)
    sdf_historical_projection = sdf_historical_projection[cols_order]

    return sdf_historical_projection


def get_activity_information(activity_list):
    sdf_data = []
    for activity in activity_list:
        sdf_data.append(
            {
                "from activity name": activity["name"],
                "from reference product": activity["reference product"],
                "from location": activity["location"],
                "from categories": activity.get("categories"),
                "from database": activity["database"],
                "from key": str((activity.get("database"), activity.get("code"))),
            }
        )
    sdf_data = pd.DataFrame(sdf_data)
    return sdf_data


def switch_fuel_tractors(
    sdf_tractor_consuming_baseline,
    sdf_electricity_data,
    diesel_combustion_flows,
    calorific_value_diesel,
    conversion_factor_kWh_to_MJ,
    efficiency_diesel_tractor,
    efficiency_electric_tractor,
    sdf_cols,
):
    mask_diesel_technosphere = (
        (sdf_tractor_consuming_baseline["flow type"] == "technosphere")
        & (
            sdf_tractor_consuming_baseline["from reference product"].str.contains(
                "diesel"
            )
        )
        & (
            ~sdf_tractor_consuming_baseline["from activity name"].str.contains(
                "co-generation"
            )
        )
    )
    mask_diesel_combustion = (
        sdf_tractor_consuming_baseline["flow type"] == "biosphere"
    ) & (
        sdf_tractor_consuming_baseline["from activity name"].str.contains(
            "|".join(diesel_combustion_flows), case=False, na=False
        )
    )

    sdf_electric_tractors = sdf_tractor_consuming_baseline[
        mask_diesel_technosphere | mask_diesel_combustion
    ]

    # Remove combustion flows to biosphere

    sdf_electric_tractors.loc[
        sdf_electric_tractors["flow type"] == "biosphere", "electric_tractor"
    ] = 0

    # Remove diesel flows for the scenario with electric tractors

    diesel_flows_to_remove = sdf_electric_tractors[
        sdf_electric_tractors["flow type"] == "technosphere"
    ].copy()
    diesel_flows_to_remove["electric_tractor"] = 0

    # Prepare the amount of electricity flows in both scenarios

    sdf_electric_tractors.loc[
        sdf_electric_tractors["flow type"] == "technosphere", "electric_tractor"
    ] = np.where(
        sdf_electric_tractors.loc[
            sdf_electric_tractors["flow type"] == "technosphere", "from unit"
        ]
        == "kilogram",
        sdf_electric_tractors.loc[
            sdf_electric_tractors["flow type"] == "technosphere", "baseline"
        ]
        * calorific_value_diesel
        / conversion_factor_kWh_to_MJ
        * efficiency_diesel_tractor
        / efficiency_electric_tractor,
        sdf_electric_tractors.loc[
            sdf_electric_tractors["flow type"] == "technosphere", "baseline"
        ]
        / conversion_factor_kWh_to_MJ
        * efficiency_diesel_tractor
        / efficiency_electric_tractor,
    )

    sdf_electric_tractors.loc[
        sdf_electric_tractors["flow type"] == "technosphere", "baseline"
    ] = 0

    sdf_electric_tractors = sdf_electric_tractors.merge(
        sdf_electricity_data, on=["from location"], how="left", suffixes=("_x", "_y")
    )

    for c_y in [
        c
        for c in sdf_electric_tractors.columns
        if c.startswith("from ") and c.endswith("_y")
    ]:
        c_x = c_y.replace("_y", "_x")

        if c_x in sdf_electric_tractors.columns:
            sdf_electric_tractors.loc[
                sdf_electric_tractors["flow type"] == "technosphere", c_x
            ] = sdf_electric_tractors.loc[
                sdf_electric_tractors["flow type"] == "technosphere", c_y
            ].values

    sdf_electric_tractors = sdf_electric_tractors.drop(
        columns=[
            c
            for c in sdf_electric_tractors.columns
            if c.startswith("from ") and c.endswith("_y")
        ],
        errors="ignore",
    )

    sdf_electric_tractors = sdf_electric_tractors.rename(
        columns={
            c: c.replace("_x", "")
            for c in sdf_electric_tractors.columns
            if c.startswith("from ") and c.endswith("_x")
        }
    )

    sdf_electric_tractors = pd.concat(
        [sdf_electric_tractors, diesel_flows_to_remove], ignore_index=True
    )

    sdf_electric_tractors.drop(columns=["from unit"], inplace=True)

    cols_order = list(sdf_electric_tractors.columns)

    scenario_cols = [c for c in sdf_electric_tractors.columns if c not in sdf_cols]
    meta_cols = [
        c
        for c in sdf_electric_tractors.columns
        if c not in scenario_cols and c not in ("from key", "to key")
    ]
    agg_map = {c: "first" for c in meta_cols}
    agg_map.update({c: "sum" for c in scenario_cols})
    sdf_electric_tractors = sdf_electric_tractors.groupby(
        ["from key", "to key"], as_index=False, sort=False
    ).agg(agg_map, numeric_only=False)

    return sdf_electric_tractors[cols_order]


def prepare_future_emissions(predicted_impacts, baseline_impacts):
    predicted_impacts["year"] = predicted_impacts["year"].astype(str)
    baseline_impacts = baseline_impacts[
        [
            "name",
            "location",
            "EF v3.1 | climate change | global warming potential (GWP100)",
        ]
    ].rename(
        columns={
            "EF v3.1 | climate change | global warming potential (GWP100)": "emissions_intensity_baseline",
            "location": "to location",
        }
    )

    future_years = predicted_impacts[["year"]].drop_duplicates().sort_values("year")
    baseline_expanded = baseline_impacts.merge(future_years, how="cross")

    future_impacts = predicted_impacts.merge(baseline_expanded, on=["year"], how="left")
    future_impacts["emissions_intensity"] = future_impacts[
        "emissions_intensity_baseline"
    ] * (1 + future_impacts["%_reduction_vs_baseline"] / 100)

    return future_impacts


def import_scenario_parameters(scenario_definitions, scenario_group):
    scenarios_group = scenario_definitions[
        scenario_definitions["scenario_group"] == scenario_group
    ][["scenario", "variable", "unit", "value"]]

    mask_percentage_values = scenarios_group["unit"] == "%"
    scenarios_group.loc[mask_percentage_values, "value"] = (
        scenarios_group.loc[mask_percentage_values, "value"]
        .str.split("%")
        .str[0]
        .astype(float)
    )
    scenarios_group.loc[~mask_percentage_values, "value"] = scenarios_group.loc[
        ~mask_percentage_values, "value"
    ].astype(float)

    return scenarios_group


def add_biochar_impacts(sdf_baseline, scenario_name, biochar_activity, dose_biochar):
    sdf_biochar_scenario = sdf_baseline.copy()
    sdf_biochar_scenario = sdf_biochar_scenario[
        sdf_biochar_scenario["flow type"] == "production"
    ]

    production_cols = [
        c for c in sdf_biochar_scenario.columns if c.startswith("to ")
    ] + ["flow type"]

    production_data = sdf_biochar_scenario[production_cols].drop_duplicates(
        subset=["to activity name", "to location"]
    )

    production_data[f"{scenario_name}"] = dose_biochar

    biochar_sdf = get_baseline_sdf(biochar_activity)
    biochar_sdf = biochar_sdf[biochar_sdf["flow type"] == "production"]

    from_cols = [c for c in biochar_sdf.columns if c.startswith("from ")]

    biochar_sdf = (
        biochar_sdf[from_cols]
        .drop_duplicates()
        .assign(_tmp=1)
        .merge(production_data.assign(_tmp=1), on="_tmp")
        .drop(columns="_tmp")
    )

    biochar_sdf.loc[:, "flow type"] = "technosphere"

    return biochar_sdf


def generate_improved_fertilizer_rate_scenario(
    product,
    sdf_baseline,
    exclusions_yield,
    CO2_name,
    N2O_name,
    scenario_name,
    yield_variation,
    CO2_variation,
    N2O_variation,
    N_fertilizer_to_scale,
    variation_N_fertilizer,
):
    sdf_scenario = sdf_baseline.copy()

    sdf_scenario = sdf_scenario[(sdf_scenario["flow type"] != "production")]

    exclusions_yield = exclusions_yield[exclusions_yield["product"] == product]

    column_scenario = f"{scenario_name}"

    mask_exclusions_yield = sdf_scenario["from activity name"].isin(
        exclusions_yield["from activity name"]
    )
    mask_N_fertilizer = (sdf_scenario["flow type"] == "technosphere") & (
        sdf_scenario["from activity name"].str.contains("|".join(N_fertilizer_to_scale))
    )

    sdf_scenario.loc[(mask_exclusions_yield), column_scenario] = sdf_scenario.loc[
        (mask_exclusions_yield), "baseline"
    ]
    sdf_scenario.loc[(mask_N_fertilizer), column_scenario] = sdf_scenario.loc[
        (mask_N_fertilizer), "baseline"
    ] * (1 + variation_N_fertilizer)

    sdf_scenario.loc[
        (~(mask_exclusions_yield | mask_N_fertilizer)), column_scenario
    ] = sdf_scenario.loc[(~(mask_exclusions_yield | mask_N_fertilizer)), "baseline"] / (
        1 + yield_variation
    )
    sdf_scenario.loc[
        sdf_scenario["from activity name"] == CO2_name, column_scenario
    ] = sdf_scenario.loc[sdf_scenario["from activity name"] == CO2_name, "baseline"] * (
        (1 + CO2_variation) / (1 + yield_variation)
    )
    sdf_scenario.loc[
        sdf_scenario["from activity name"] == N2O_name, column_scenario
    ] = sdf_scenario.loc[sdf_scenario["from activity name"] == N2O_name, "baseline"] * (
        (1 + N2O_variation) / (1 + yield_variation)
    )

    return sdf_scenario


def combine_scenarios(
    sdf1,
    sdf2,
    sdf_cols,
    sep="+",
):
    sdf1 = sdf1.set_index(["from key", "to key", "flow type"], drop=False)
    sdf2 = sdf2.set_index(["from key", "to key", "flow type"], drop=False)

    scenarios1 = [c for c in sdf1.columns if c not in sdf_cols]
    scenarios2 = [c for c in sdf2.columns if c not in sdf_cols]

    combined_index = sdf1.index.union(sdf2.index)

    out = pd.DataFrame(index=combined_index, columns=sdf_cols)

    out.loc[sdf1.index, sdf_cols] = sdf1[sdf_cols]
    out.loc[sdf2.index, sdf_cols] = sdf2[sdf_cols]

    combined_cols = []

    for s1, s2 in itertools.product(scenarios1, scenarios2):
        combined_name = f"{s1}{sep}{s2}"
        combined_cols.append(combined_name)

        out[combined_name] = np.nan
        out.loc[sdf1.index, combined_name] = pd.to_numeric(sdf1[s1]).to_numpy()
        out.loc[sdf2.index, combined_name] = pd.to_numeric(sdf2[s2]).to_numpy()

    out[combined_cols] = out[combined_cols].apply(pd.to_numeric)

    return out.reset_index(drop=True)


def close_results(all_results):
    # ==========================================
    # Activity definition
    # ==========================================
    key_cols = ["final_product_name", "reference_product_name"]

    # ==========================================
    # Scenario dimensions
    # ==========================================
    scenario_cols = ["scenario_group", "scenario", "year", "impact_category"]

    # ==========================================
    # 1. Activity space
    # only by impact category
    # ==========================================
    activity_space = all_results[["impact_category"] + key_cols].drop_duplicates()

    # ==========================================
    # 2. Scenario space
    # ==========================================
    scenario_space = all_results[scenario_cols].drop_duplicates()

    # ==========================================
    # 3. Create closed space
    # ==========================================
    closed_space = scenario_space.merge(
        activity_space, on="impact_category", how="left"
    )

    # ==========================================
    # 4. Merge original data
    # ==========================================
    closed_results = closed_space.merge(
        all_results, on=scenario_cols + key_cols, how="left"
    )

    # ==========================================
    # 5. Fill missing values
    # ==========================================
    closed_results["value"] = closed_results["value"].fillna(0)

    closed_results["share"] = closed_results["share"].fillna(0)

    # ==========================================
    # 6. Sort
    # ==========================================
    closed_results = closed_results.sort_values(scenario_cols + key_cols).reset_index(
        drop=True
    )

    return closed_results
