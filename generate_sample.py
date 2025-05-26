import math
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

__OUTPUT_FOLDER = Path("samples")
__OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
__OUTPUT_FILE = __OUTPUT_FOLDER.joinpath(
    f"{datetime.now().strftime("%Y%m%d_%H%M%S")}_sample.xlsx"
)

# Alguns limites para latitude e longitude para geração (mais ou menos
# america do sul, evitando oceanos.)
__LAT_LIMITS = (-3, -33)
__LON_LIMITS = (-70, -45)

__DEFAULT_PERIODS = 7  # Horizonte default
__DEFAULT_PLANT_STORAGE_CAPACITY_RANGE = (50000000, 150000000)  # Plant storage capacity
__DEFAULT_DIST_CEN_STORAGE_CAPACITY_RANGE = (10000000, 30000000)  # Dist. Cent. storage
__DEFAULT_PLANTS = 3  # Number of plants default
__DEFAULT_CUSTOMERS = 15  # Number of customers default
__DEFAULT_ROUTES_RATE = 0.7  # % of pairs of plants and customers connected
__DEFAULT_SIZES = [
    "9.1oz Sleek",
    "12oz",
    "12oz Sleek",
    "16oz",
    "24oz",
]
__DEFAULT_PRODUCTS_PER_SIZE = 5

__DEFAULT_FREIGHT_PER_KM = 7.1  # Reais / Km Average
__DEFAULT_DAILY_DISTANCE_KM = 400  # Average daily traveled distance


def lat_lon_dist(
    origin: tuple[float, float], destination: tuple[float, float]
) -> float:
    """
    Calcula a "Haversine distance" para 2 pontos de latitude e longitude.
    """
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(
        math.radians(lat1)
    ) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d


def random_lat_lon() -> tuple[float, float]:
    """
    Generates a pair of random Latitude and Longitude given the
    limits in constants.
    """
    return (
        random.uniform(__LAT_LIMITS[0], __LAT_LIMITS[1]),
        random.uniform(__LON_LIMITS[0], __LON_LIMITS[1]),
    )


def gen_periods(number_of_periods: int) -> list[datetime]:
    """
    Generate a list of periods
    """
    one_day = timedelta(days=1)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    periods = []
    for _ in range(number_of_periods):
        periods.append(today)
        today += one_day

    return periods


def gen_plants(number_of_plants: int) -> pd.DataFrame:
    """
    Generate the plants sample
    """
    plants = []
    for idx in range(number_of_plants):
        lat, lon = random_lat_lon()
        plants.append(
            {
                "name": f"Plant {idx}",
                "lat": lat,
                "lon": lon,
                "storage_capacity": random.randint(
                    __DEFAULT_PLANT_STORAGE_CAPACITY_RANGE[0],
                    __DEFAULT_PLANT_STORAGE_CAPACITY_RANGE[1],
                ),
            }
        )

    return pd.DataFrame(data=plants)


def gen_dist_centers(plants: pd.DataFrame) -> pd.DataFrame:
    """
    Para cada planta, gerar alguns centros de distribuição nas redondezas.
    """
    dist_centers = []
    for _, plant in plants.iterrows():
        nbrm_of_warehouses = random.randint(0, 3)
        for _ in range(nbrm_of_warehouses):
            # Generate lat and lon in a range of +- 2 of the plant
            tmp_lat = plant["lat"] + random.uniform(-2, 2)
            tmp_lon = plant["lon"] + random.uniform(-2, 2)
            dist_centers.append(
                {
                    "name": f"Warehouse {len(dist_centers)+1}",
                    "plant": plant["name"],
                    "lat": tmp_lat,
                    "lon": tmp_lon,
                    "storage_capacity": random.randint(
                        __DEFAULT_DIST_CEN_STORAGE_CAPACITY_RANGE[0],
                        __DEFAULT_DIST_CEN_STORAGE_CAPACITY_RANGE[1],
                    ),
                }
            )

    return pd.DataFrame(data=dist_centers)


def gen_customers(number_of_customers: int) -> pd.DataFrame:
    """
    Generate the plants sample
    """
    plants = []
    for idx in range(number_of_customers):
        lat, lon = random_lat_lon()
        plants.append({"name": f"Customer {idx}", "lat": lat, "lon": lon})

    return pd.DataFrame(data=plants)


def gen_products(products_per_size: int) -> pd.DataFrame:
    """
    Gerar lista de produtos, cada produto possui um "size"
    """
    products = []
    for size in __DEFAULT_SIZES:
        for _ in range(products_per_size):
            products.append({"size": size, "product": f"Product {len(products) + 1}"})

    return pd.DataFrame(data=products)


def gen_routes(
    plants: pd.DataFrame, dist_centers: pd.DataFrame, customers: pd.DataFrame
):
    """
    Gerar rotas de atendimento (possíveis) a partir de plantas e centros de distribuição
    até clientes.
    """
    routes = []
    for _, plant in plants.iterrows():
        # Adiciona rota entre todos os warehouses e plantas
        for _, dist_center in dist_centers.iterrows():
            # Para o Warehouse
            routes.append(
                {
                    "origin": plant["name"],
                    "destination": dist_center["name"],
                    "distance": round(
                        lat_lon_dist(
                            origin=(plant["lat"], plant["lon"]),
                            destination=(dist_center["lat"], dist_center["lon"]),
                        ),
                        3,
                    ),
                }
            )

            # Do o Warehouse
            routes.append(
                {
                    "origin": dist_center["name"],
                    "destination": plant["name"],
                    "distance": round(
                        lat_lon_dist(
                            origin=(dist_center["lat"], dist_center["lon"]),
                            destination=(plant["lat"], plant["lon"]),
                        ),
                        3,
                    ),
                }
            )

        # Adiciona rota para todas as outras plantas (transferências)
        for _, plant_2 in plants[plants["name"] != plant["name"]].iterrows():
            routes.append(
                {
                    "origin": plant["name"],
                    "destination": plant_2["name"],
                    "distance": round(
                        lat_lon_dist(
                            origin=(plant["lat"], plant["lon"]),
                            destination=(plant_2["lat"], plant_2["lon"]),
                        ),
                        3,
                    ),
                }
            )

        for _, customer in customers.iterrows():
            # "Checa a sorte" para saber se haverá rota entre a planta e o cliente
            if random.uniform(0, 1) <= __DEFAULT_ROUTES_RATE:
                # Adicionar rota para planta e cliente
                routes.append(
                    {
                        "origin": plant["name"],
                        "destination": customer["name"],
                        "distance": round(
                            lat_lon_dist(
                                origin=(plant["lat"], plant["lon"]),
                                destination=(customer["lat"], customer["lon"]),
                            ),
                            3,
                        ),
                    }
                )

                # Adicionar também rotas a partir dos centros de distribuição associados à planta
                for _, dist_center in dist_centers[
                    dist_centers["plant"] == plant["name"]
                ].iterrows():
                    routes.append(
                        {
                            "origin": dist_center["name"],
                            "destination": customer["name"],
                            "distance": round(
                                lat_lon_dist(
                                    origin=(dist_center["lat"], dist_center["lon"]),
                                    destination=(customer["lat"], customer["lon"]),
                                ),
                                3,
                            ),
                        }
                    )

    routes = pd.DataFrame(data=routes)
    routes["leadtime"] = (
        (routes["distance"] / __DEFAULT_DAILY_DISTANCE_KM).round(0).astype(int)
    )
    routes["freight_cost"] = (
        routes["distance"] * (__DEFAULT_FREIGHT_PER_KM + random.uniform(-1, 1))
    ).round(3)

    return routes


def gen_demand(
    customers: pd.DataFrame, products: pd.DataFrame, periods: pd.DataFrame
) -> pd.DataFrame:
    """
    Gerar demandas de produtos para clientes em períodos.
    """
    demands = []
    tmp_products = products.to_dict(orient="records")
    for _, customer in customers.iterrows():
        products_for_customer = random.sample(
            tmp_products,
            random.randint(min(len(tmp_products), 3), min(len(tmp_products), 10)),
        )

        # Gerando algumas demandas aleatórias para os produtos selecionados para cada período
        for period in periods:
            products_with_demand = random.sample(
                products_for_customer,
                random.randint(
                    min(len(products_for_customer), 1),
                    min(len(products_for_customer), 3),
                ),
            )

            for product in products_with_demand:
                demands.append(
                    {
                        "period": period,
                        "customer": customer["name"],
                        "product_size": product["size"],
                        "product": product["product"],
                        # Trucks * Size of Truck
                        "demand": random.randint(2, 8) * 200000,
                    }
                )

    return pd.DataFrame(data=demands)


def gen_lines(plants: pd.DataFrame) -> pd.DataFrame:
    """
    Gerar linhas de produção para as plantas.
    """
    lines = []
    for _, plant in plants.iterrows():
        tmp_number_of_lines = random.randint(1, 3)
        for idx in range(tmp_number_of_lines + 1):
            lines.append({"plant": plant["name"], "name": f"{plant['name']}_{idx+1}"})

    return pd.DataFrame(data=lines)


def gen_capability(
    lines: pd.DataFrame, products: pd.DataFrame, periods: list[datetime]
) -> pd.DataFrame:
    """
    Gerar as capabilidades das linhas nos perídos, qual size a linha pode produzir
    em um determinado período.
    """
    capabilities = []
    sizes = list(products["size"].unique())
    for _, line in lines.iterrows():
        tmp_capable_size = random.choice(sizes)
        for period in periods:
            capabilities.append(
                {"line": line["name"], "period": period, "size": tmp_capable_size}
            )

            # Uma pequena chance de "trocar" o size disponível na linhas no próximo período
            if random.uniform(0, 1) <= 0.1:  # 10 %
                tmp_capable_size = random.choice(sizes)

    return pd.DataFrame(capabilities)


def gen_prod_capacity(
    capabilities: pd.DataFrame, products: pd.DataFrame
) -> pd.DataFrame:
    """
    Gerar as taxas de produção (produção por dia) para as linhas e sizes
    """
    # Gerar a taxa de produção "base" para os sizes
    rates = []
    sizes = list(products["size"].unique())
    base_rates = {}
    for size in sizes:
        base_rates[size] = random.uniform(1500000, 3000000)  # 1.5M a 3M / Dia

    for _, capability in capabilities.iterrows():
        rates.append(
            {
                "line": capability["line"],
                "period": capability["period"],
                "size": capability["size"],
                # 0.2M-0.7M of random variation on the day (noise)
                "rate": int(
                    round(
                        base_rates[capability["size"]] + random.uniform(200000, 700000),
                        0,
                    )
                ),
            }
        )

    return pd.DataFrame(data=rates)


periods = gen_periods(__DEFAULT_PERIODS)
plants = gen_plants(__DEFAULT_PLANTS)
lines = gen_lines(plants=plants)
dist_centers = gen_dist_centers(plants=plants)
customers = gen_customers(__DEFAULT_CUSTOMERS)
products = gen_products(__DEFAULT_PRODUCTS_PER_SIZE)
routes = gen_routes(plants=plants, dist_centers=dist_centers, customers=customers)
demands = gen_demand(customers=customers, products=products, periods=periods)
capabilities = gen_capability(lines=lines, products=products, periods=periods)
rates = gen_prod_capacity(capabilities=capabilities, products=products)


with pd.ExcelWriter(__OUTPUT_FILE, engine="openpyxl") as writer:
    pd.DataFrame(data=periods).to_excel(writer, sheet_name="Periods", index=True)
    plants.to_excel(writer, sheet_name="Plants", index=False)
    lines.to_excel(writer, sheet_name="Lines", index=False)
    dist_centers.to_excel(writer, sheet_name="Dist. Centers", index=False)
    customers.to_excel(writer, sheet_name="Customers", index=False)
    products.to_excel(writer, sheet_name="Products", index=False)
    routes.to_excel(writer, sheet_name="Routes", index=False)
    demands.to_excel(writer, sheet_name="Demands", index=False)
    capabilities.to_excel(writer, sheet_name="Capabilities", index=False)
    rates.to_excel(writer, sheet_name="Rates", index=False)
