from load_data import group_metric_data_by_month, get_max_value
from interpolation import generate_interpolated_array
from matrix_to_gif import generate_gif
from matplotlib import cm
import numpy as np

YEARS = range(1995, 2015)
MONTHS = range(1, 13)
METRICS = [
    'Chloride',
    'Chlorophyll-a',
    'Secchi Depth',
    'Total Phosphorus',
    'Alkalinity',
    'Temperature',
    'Total Nitrogen',
    'Dissolved Oxygen'
]


def generate_lake_gifs(metrics=METRICS):
    """Generate 2D Lake GIFs for defined metrics"""

    for metric in metrics:
        print "Starting to generate: %s" % metric
        generate_lake_gif(metric)


def generate_lake_gif(metric):
    """Generate a GIF of Lake Champlain, displaying how a metric has changed
       over the course of the long term lake monitoring program"""

    print "Generate 2D Lake gif for %s" % metric

    max_value = get_max_value(metric)

    data = generate_lake_array(metric)
    normalized = normalize_values(data, max_value)
    a = map_value_to_color(normalized)
    arrays = [np.asarray(a[i], 'uint8') for i, f in enumerate(a)]
    generate_gif(arrays, metric.replace(' ', '-').lower())


def generate_lake_array(metric, remove_null_months=True):
    """Generate an array of raw Lake Champlain metric data, for creation of 2D
       and 3D GIFs"""

    lake_data = group_metric_data_by_month(metric)

    arrays = []
    for year in YEARS:
        for month in MONTHS:
            station_data = station_map()
            if not lake_data[year][month]:  # if month contains no data
                if remove_null_months:
                    continue
                else:
                    # show 0 for whole lake for month
                    # 4 = random station, whole lake will be extrapolated
                    station_data[4]['value'] = 0
            else:
                for station in lake_data[year][month]:
                    data = lake_data[year][month][station]
                    monthly_value = sum(data) / len(data)
                    station_data[station]['value'] = monthly_value
            array = generate_interpolated_array(station_data)
            arrays.append(array.tolist())

    return arrays


# TODO: probably need min value as well, otherwise scaling from max to zero
def normalize_values(array, max_value):
    """Normalize values to 0 -> 1"""

    data = array
    for i, x in enumerate(data):
        for j, y in enumerate(x):
            for k, z in enumerate(y):
                value = data[i][j][k]
                if max_value:
                    data[i][j][k] = value / max_value
                else:
                    data[i][j][k] = value

    return data


def map_value_to_color(a):
    vfunc = np.vectorize(map_values_to_colors, otypes=[object])

    arrays = []
    for array in a:
        mapped_list = vfunc(array).tolist()
        arrays.append(mapped_list)

    return arrays


def station_map():
    """A map of all station IDs to their coordinates on the low-res
       Lake Champlain image """

    return {
        51: {
            'location': [1, 9],
        },
        50: {
            'location': [2, 7],
        },
        40: {
            'location': [10, 8],
        },
        34: {
            'location': [14, 6],
        },
        46: {
            'location': [4, 4],
        },
        36: {
            'location': [11, 2],
        },
        33: {
            'location': [14, 0],
        },
        25: {
            'location': [17, 4],
        },
        19: {
            'location': [21, 3],
        },
        21: {
            'location': [21, 5],
        },
        16: {
            'location': [23, 6],
        },
        9: {
            'location': [30, 3],
        },
        7: {
            'location': [34, 0],
        },
        4: {
            'location': [40, 0],
        },
        2: {
            'location': [48, 0],
        }
    }


def map_values_to_colors(x):
    """To be consumed by np.vectorize to transform nan values to black
       and provide the color map"""

    if np.isnan(x):
        return [0, 0, 0]
    elif x < 0:
        return list(cm.hot(0, bytes=True)[:3])
    else:
        return list(cm.hot(x, bytes=True)[:3])

generate_lake_gifs()
