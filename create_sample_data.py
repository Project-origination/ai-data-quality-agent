import pandas as pd

data = [
    {
        "customer_id": 1,
        "customer_name": "Alpine Retail",
        "country": "Switzerland",
        "email": "contact@alpine-retail.ch",
        "age": 38,
        "revenue": 12500,
        "signup_date": "2025-01-10",
    },
    {
        "customer_id": 2,
        "customer_name": "Maison Nova",
        "country": "France",
        "email": "hello@maisonnova.fr",
        "age": 42,
        "revenue": 9800,
        "signup_date": "2025-02-15",
    },
    {
        "customer_id": 3,
        "customer_name": "Benelux Direct",
        "country": "Belgium",
        "email": "sales@beneluxdirect.be",
        "age": 35,
        "revenue": 11100,
        "signup_date": "2025-03-20",
    },
    {
        "customer_id": 4,
        "customer_name": "Lux Partners",
        "country": "Luxembourg",
        "email": "info@luxpartners.lu",
        "age": 50,
        "revenue": 15400,
        "signup_date": "2025-04-05",
    },
    {
        "customer_id": 5,
        "customer_name": "Helvetia Digital",
        "country": "Switzerland",
        "email": None,
        "age": 29,
        "revenue": 8700,
        "signup_date": "2025-05-11",
    },
    {
        "customer_id": 5,
        "customer_name": "Helvetia Digital",
        "country": "Switzerland",
        "email": "team@helvetia-digital.ch",
        "age": 29,
        "revenue": 9100,
        "signup_date": "2025-05-11",
    },
    {
        "customer_id": 7,
        "customer_name": "Data Horizon",
        "country": "France",
        "email": "contact-datahorizon",
        "age": 31,
        "revenue": 10200,
        "signup_date": "2025-06-01",
    },
    {
        "customer_id": 8,
        "customer_name": "Nova Insights",
        "country": "Belgium",
        "email": "contact@novainsights.be",
        "age": 230,
        "revenue": 13600,
        "signup_date": "2025-06-18",
    },
    {
        "customer_id": 9,
        "customer_name": "BlueMetric",
        "country": "France",
        "email": "hello@bluemetric.fr",
        "age": -4,
        "revenue": 7200,
        "signup_date": "2025-07-02",
    },
    {
        "customer_id": 10,
        "customer_name": "Insight Works",
        "country": "Frnace",
        "email": "team@insightworks.fr",
        "age": 44,
        "revenue": 9800,
        "signup_date": "2025-07-15",
    },
    {
        "customer_id": 11,
        "customer_name": "Enterprise One",
        "country": "Switzerland",
        "email": "finance@enterpriseone.ch",
        "age": 47,
        "revenue": 250000,
        "signup_date": "2025-08-01",
    },
    {
        "customer_id": 12,
        "customer_name": None,
        "country": "Luxembourg",
        "email": "unknown@example.com",
        "age": 39,
        "revenue": 11800,
        "signup_date": "2025-08-12",
    },
]

df = pd.DataFrame(data)

output_path = "data/customers_dirty.csv"
df.to_csv(output_path, index=False)

print(f"Sample dataset created: {output_path}")
print(df)