import numpy as np
import scipy.interpolate as inter
from PIL import Image


def nearest_neighbor(station_data):
    """Given lake station data, calculate nearest neighbor for every point
       in the 2D array of the display.
       Returns the 2D array"""

    vals = []
    points = []
    for station in station_data:
        if 'value' in station_data[station]:
            vals.append(station_data[station]['value'])
            points.append(station_data[station]['location'])
    values = np.asarray(vals)
    grid_x, grid_y = np.mgrid[0:49:50j, 0:9:10j]
    grid_z = inter.griddata(points, values, (grid_x, grid_y), method='nearest')

    return grid_z


def remove_non_edges(neighbor_data):
    """Replaces all data in array with nan except for edge nodes, excluding
       the nodes below 30 nodes of depth in the first column. This is necessary
       in order to acheive the desired gradient.
       Returns 2D array of same size."""

    new_array = np.empty((50, 10))
    new_array[:] = np.NAN
    new_array[0] = neighbor_data[0]                # first row
    new_array[-1] = neighbor_data[-1]              # last row
    new_array[0:30, 0] = neighbor_data[0:30, 0]    # first column
    new_array[:, -1] = neighbor_data[:, -1]        # last column

    return new_array


def reintroduce_station_data(station_data, edge_array):
    """Takes an array of station data objects and inserts them into a 2D array
       that contains only values on its edges (from the previous, nearest
       neighbor calculation.
       Returns another 2D array"""

    pre_interpolated_array = np.copy(edge_array)
    for station in station_data:
        data = station_data[station]
        if 'value' in data:
            pre_interpolated_array[data['location'][0],
                data['location'][1]] = data['value']

    return pre_interpolated_array


def interpolate_station_data(station_array):
    """Takes a 2D array of station data and edge values (calculated from
       nearest neighbor) for interpolation.
       Returns an interpolated 2D array"""

    interpolated_array = np.copy(station_array)
    nans = np.isnan(interpolated_array)
    notnans = np.logical_not(nans)
    grid_x, grid_y = np.mgrid[0:49:50j, 0:9:10j]

    interpolated_array[nans] = inter.griddata((grid_x[notnans], grid_y[notnans]),
        interpolated_array[notnans], (grid_x[nans], grid_y[nans]), method='cubic')

    return interpolated_array


def generate_interpolated_array(data):
    """Takes station data and a 50x10 matrix and returns nicely interpolated
    results in the shape of Lake Champlain"""

    nn = nearest_neighbor(data)
    # plt.matshow(nn)
    # plt.show()

    just_edges = remove_non_edges(nn)
    # plt.matshow(just_edges)
    # plt.show()

    with_stations = reintroduce_station_data(data, just_edges)
    # plt.matshow(with_stations)
    # plt.show()

    interpolated = interpolate_station_data(with_stations)
    # plt.matshow(interpolated, cmap=plt.cm.hot)
    # plt.colorbar()
    # plt.show()

    lake_data = clip_data_to_lake(interpolated)
    # plt.matshow(lake_data, cmap=plt.cm.winter)
    # plt.colorbar()
    # plt.show()

    return lake_data


def find_current_boundary():
    """Finds all non-white pixels in the low-res image of lake champlain
    for use in an image clipper"""
    im = Image.open('img/champlain-low-res.png')

    lake_coords = []
    arr = np.array(im)
    for x, row in enumerate(arr):
        for z, item in enumerate(row):
            if not np.array_equal(item, np.array([255, 255, 255, 255])):
                lake_coords.append([x, z])

    return lake_coords


def clip_data_to_lake(image):
    """Clips a numpy array to the boundary of lake champlain, returning array
    with NaN when the coordinates are outside of the lake"""
    lake_boundary = find_current_boundary()
    arr = np.array(image)

    for x, row in enumerate(arr):
        for z, item in enumerate(row):
            if [x, z] not in lake_boundary:
                arr[x][z] = np.nan

    return arr
