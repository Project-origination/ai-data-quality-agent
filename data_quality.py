import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

VALID_COUNTRIES = {
    "France",
    "Belgium",
    "Luxembourg",
    "Switzerland",
}

EMAIL_PATTERN = (
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)


SEVERITY_MULTIPLIERS = {
    "Critical": 3.0,
    "High": 1.5,
    "Medium": 1.0,
    "Low": 0.5,
}


DIMENSION_WEIGHTS = {
    "Completeness": 0.15,
    "Uniqueness": 0.30,
    "Validity": 0.30,
    "Consistency": 0.10,
    "Statistical Health": 0.15,
}


# ============================================================
# HELPERS
# ============================================================

def clamp_score(value):
    """
    Ensure a score always remains between 0 and 100.
    """

    return max(
        0.0,
        min(
            100.0,
            value,
        ),
    )


def add_issue(
    issues,
    category,
    severity,
    column,
    rows,
    message,
):
    """
    Add a standardized quality issue.
    """

    issues.append(
        {
            "category": category,
            "severity": severity,
            "column": column,
            "affected_rows": int(rows),
            "message": message,
        }
    )


def weighted_quality_score(
    dimension_scores,
):
    """
    Calculate the overall Data Quality Score.

    Only dimensions that could actually be evaluated
    are included in the weighted calculation.
    """

    weighted_total = 0.0
    active_weight = 0.0

    for dimension, score in dimension_scores.items():

        if score is None:
            continue

        weight = DIMENSION_WEIGHTS[
            dimension
        ]

        weighted_total += (
            score * weight
        )

        active_weight += weight

    if active_weight == 0:
        return 100

    return round(
        weighted_total
        / active_weight
    )


# ============================================================
# MAIN QUALITY ENGINE
# ============================================================

def analyze_data_quality(
    df: pd.DataFrame,
) -> dict:

    issues = []

    total_rows = len(df)

    total_columns = len(
        df.columns
    )

    total_cells = (
        total_rows
        * total_columns
    )


    # ========================================================
    # 1. COMPLETENESS
    # ========================================================

    total_missing = int(
        df.isna().sum().sum()
    )

    for column in df.columns:

        missing_count = int(
            df[column]
            .isna()
            .sum()
        )

        if missing_count > 0:

            add_issue(
                issues,
                category="Missing values",
                severity="High",
                column=column,
                rows=missing_count,
                message=(
                    f"{missing_count} missing value(s) "
                    f"detected in '{column}'."
                ),
            )


    if total_cells > 0:

        weighted_missing = (
            total_missing
            * SEVERITY_MULTIPLIERS[
                "High"
            ]
        )

        completeness_score = (
            100
            * (
                1
                - min(
                    1,
                    weighted_missing
                    / total_cells,
                )
            )
        )

        completeness_score = round(
            clamp_score(
                completeness_score
            )
        )

    else:

        completeness_score = 100


    # ========================================================
    # 2. UNIQUENESS
    # ========================================================

    duplicate_rows = int(
        df.duplicated().sum()
    )

    if duplicate_rows > 0:

        add_issue(
            issues,
            category="Duplicates",
            severity="High",
            column="All columns",
            rows=duplicate_rows,
            message=(
                f"{duplicate_rows} fully duplicated "
                "row(s) detected."
            ),
        )


    uniqueness_defects = 0

    uniqueness_denominator = (
        total_rows
    )


    if "customer_id" in df.columns:

        duplicated_ids = (
            df["customer_id"]
            .duplicated(
                keep=False
            )
        )

        duplicate_id_count = int(
            duplicated_ids.sum()
        )

        if duplicate_id_count > 0:

            add_issue(
                issues,
                category="Uniqueness",
                severity="Critical",
                column="customer_id",
                rows=duplicate_id_count,
                message=(
                    f"{duplicate_id_count} row(s) "
                    "use a duplicated customer ID."
                ),
            )

        uniqueness_defects = (
            duplicate_id_count
            * SEVERITY_MULTIPLIERS[
                "Critical"
            ]
        )

    else:

        uniqueness_defects = (
            duplicate_rows
            * SEVERITY_MULTIPLIERS[
                "High"
            ]
        )


    if uniqueness_denominator > 0:

        uniqueness_score = (
            100
            * (
                1
                - min(
                    1,
                    uniqueness_defects
                    / uniqueness_denominator,
                )
            )
        )

        uniqueness_score = round(
            clamp_score(
                uniqueness_score
            )
        )

    else:

        uniqueness_score = 100


    # ========================================================
    # 3. VALIDITY
    # ========================================================

    validity_tests = 0

    validity_defects = 0.0


    # Email validity

    if "email" in df.columns:

        email_values = (
            df["email"]
            .dropna()
            .astype(str)
        )

        validity_tests += len(
            email_values
        )

        valid_email_mask = (
            email_values
            .str.match(
                EMAIL_PATTERN
            )
        )

        invalid_email_count = int(
            (
                ~valid_email_mask
            ).sum()
        )

        if invalid_email_count > 0:

            add_issue(
                issues,
                category="Format",
                severity="High",
                column="email",
                rows=invalid_email_count,
                message=(
                    f"{invalid_email_count} malformed "
                    "email address(es) detected."
                ),
            )

        validity_defects += (
            invalid_email_count
            * SEVERITY_MULTIPLIERS[
                "High"
            ]
        )


    # Age business rule

    if "age" in df.columns:

        numeric_age = pd.to_numeric(
            df["age"],
            errors="coerce",
        )

        non_null_age = (
            numeric_age.notna()
        )

        validity_tests += int(
            non_null_age.sum()
        )

        invalid_age_mask = (
            non_null_age
            & (
                (numeric_age < 0)
                | (numeric_age > 120)
            )
        )

        invalid_age_count = int(
            invalid_age_mask.sum()
        )

        if invalid_age_count > 0:

            add_issue(
                issues,
                category="Business rule",
                severity="Critical",
                column="age",
                rows=invalid_age_count,
                message=(
                    f"{invalid_age_count} impossible "
                    "age value(s) detected."
                ),
            )

        validity_defects += (
            invalid_age_count
            * SEVERITY_MULTIPLIERS[
                "Critical"
            ]
        )


    if validity_tests > 0:

        validity_score = (
            100
            * (
                1
                - min(
                    1,
                    validity_defects
                    / validity_tests,
                )
            )
        )

        validity_score = round(
            clamp_score(
                validity_score
            )
        )

    else:

        validity_score = None


    # ========================================================
    # 4. CONSISTENCY
    # ========================================================

    consistency_score = None


    if "country" in df.columns:

        country_values = (
            df["country"]
            .dropna()
        )

        consistency_tests = len(
            country_values
        )

        invalid_country_mask = (
            ~country_values.isin(
                VALID_COUNTRIES
            )
        )

        invalid_country_count = int(
            invalid_country_mask.sum()
        )


        if invalid_country_count > 0:

            invalid_values = sorted(
                country_values[
                    invalid_country_mask
                ]
                .astype(str)
                .unique()
                .tolist()
            )

            add_issue(
                issues,
                category="Consistency",
                severity="Medium",
                column="country",
                rows=invalid_country_count,
                message=(
                    f"{invalid_country_count} unexpected "
                    "country value(s): "
                    + ", ".join(
                        invalid_values
                    )
                ),
            )


        if consistency_tests > 0:

            consistency_defects = (
                invalid_country_count
                * SEVERITY_MULTIPLIERS[
                    "Medium"
                ]
            )

            consistency_score = (
                100
                * (
                    1
                    - min(
                        1,
                        consistency_defects
                        / consistency_tests,
                    )
                )
            )

            consistency_score = round(
                clamp_score(
                    consistency_score
                )
            )


    # ========================================================
    # 5. STATISTICAL HEALTH
    # ========================================================

    statistical_score = None


    if "revenue" in df.columns:

        revenue = pd.to_numeric(
            df["revenue"],
            errors="coerce",
        )

        valid_revenue = (
            revenue.dropna()
        )


        if len(valid_revenue) >= 4:

            q1 = valid_revenue.quantile(
                0.25
            )

            q3 = valid_revenue.quantile(
                0.75
            )

            iqr = (
                q3 - q1
            )

            lower_bound = (
                q1
                - 1.5 * iqr
            )

            upper_bound = (
                q3
                + 1.5 * iqr
            )


            outlier_mask = (
                revenue.notna()
                & (
                    (revenue < lower_bound)
                    | (
                        revenue
                        > upper_bound
                    )
                )
            )

            outlier_count = int(
                outlier_mask.sum()
            )


            if outlier_count > 0:

                add_issue(
                    issues,
                    category="Outlier",
                    severity="Medium",
                    column="revenue",
                    rows=outlier_count,
                    message=(
                        f"{outlier_count} statistical "
                        "revenue outlier(s) detected."
                    ),
                )


            statistical_defects = (
                outlier_count
                * SEVERITY_MULTIPLIERS[
                    "Medium"
                ]
            )


            statistical_score = (
                100
                * (
                    1
                    - min(
                        1,
                        statistical_defects
                        / len(
                            valid_revenue
                        ),
                    )
                )
            )


            statistical_score = round(
                clamp_score(
                    statistical_score
                )
            )


    # ========================================================
    # DIMENSION SCORES
    # ========================================================

    dimension_scores = {
        "Completeness": (
            completeness_score
        ),

        "Uniqueness": (
            uniqueness_score
        ),

        "Validity": (
            validity_score
        ),

        "Consistency": (
            consistency_score
        ),

        "Statistical Health": (
            statistical_score
        ),
    }


    # ========================================================
    # OVERALL QUALITY SCORE
    # ========================================================

    quality_score = (
        weighted_quality_score(
            dimension_scores
        )
    )


    # ========================================================
    # SEVERITY COUNTS
    # ========================================================

    severity_counts = {
        severity: sum(
            issue["severity"]
            == severity
            for issue in issues
        )

        for severity in [
            "Critical",
            "High",
            "Medium",
            "Low",
        ]
    }


    # ========================================================
    # OUTPUT
    # ========================================================

    return {
        "quality_score": quality_score,

        "quality_dimensions": (
            dimension_scores
        ),

        "dimension_weights": (
            DIMENSION_WEIGHTS
        ),

        "total_rows": total_rows,

        "total_columns": total_columns,

        "total_issues": len(
            issues
        ),

        "severity_counts": (
            severity_counts
        ),

        "issues": issues,
    }