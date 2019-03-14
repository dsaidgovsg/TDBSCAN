"""
Python implementation of t_dbscan
"""
from haversine import haversine


def t_dbscan(
        list_coordinates,
        min_points,
        eps,
        ceps,
        stop_min_points,
        stop_eps,
        stop_ceps,
        move_ability):
    """
    Function to find the stops from the coordinates

    Parameters:
      list_coordinates contains a list of 2-dimensional tuples (index, (lat, lon))
      min_points the number of minimum points
      eps the first search radius in meters
      ceps the second search radius in meters
      stop_min_points the number of minimum points for the stop search
      stop_eps the first stop search radius in meters
      stop_ceps the second stop search radius in meters
      moveability the move metrics that range from 0 to 1

    Returns:
      main_label: A list of binary label with 1 as stop
    """
    def expand_cluster(
            result_neighbors,
            cluster_id,
            label,
            eps,
            ceps,
            min_index_offset,
            inner_list_coordinates):
        """
        Function to include more coordinates into the cluster

        Parameters:
          result_neighbors contains a list of 2-dimensional tuples (index, (lat, lon))
          cluster id is the value of the cluster id
          label is a list of cluster id
          eps the first search radius in meters
          ceps the second search radius in meters
          min_index_offset is the index of the first element
          inner_list_coordiantes contains a list of 2-dimensional tuples (index, (lat, lon))
        """
        count = 0
        while count < len(result_neighbors):
            point = result_neighbors[count]
            index = point[0]
            if label[index] == -1:
                label[index] = cluster_id
            elif label[index] == 0:
                label[index] = cluster_id
                expanding_cluster = get_neighbors(
                    result_neighbors[count],
                    eps,
                    ceps,
                    inner_list_coordinates,
                    min_index_offset)
                if len(expanding_cluster) >= min_points:
                    result_neighbors = result_neighbors + expanding_cluster
            count += 1

    def get_neighbors(each, eps, ceps, list_coordinates, min_index_offset):
        """
        Function to find coordinates that satisfy the search radius

        Parameters:
          each contains a 2-dimensional tuple in this format, (index, (lat, lon))
          eps the first search radius in meters
          ceps the second search radius in meters
          list_coordiantes contains a list of 2-dimensional tuples (index, (lat, lon))
          min_index_offset is the index of the first element
        """
        eps_km = eps / 1000
        ceps_km = ceps / 1000
        index, coordinates = each
        result = [each]
        i = index - min_index_offset + 1
        while i < len(list_coordinates):
            coordinates_ = list_coordinates[i][1]
            if haversine(coordinates, coordinates_) <= eps_km:
                result.append(list_coordinates[i])
            elif haversine(coordinates, coordinates_) >= ceps_km:
                break
            i += 1
        return result

    def traj_direct_dist(cluster):
        """
        Function to calculate the haversine distance from the first and last element

        Parameters:
          cluster is a list of tuples in this format, (lat,lon)

        Return:
          Distance in km
        """
        return haversine(cluster[0], cluster[-1])

    def traj_curve_dist(cluster):
        """
        Function to calculate the curved distance

        Parameters:
          cluster is a list of tuples in this format, (lat,lon)

        Return:
          Distance in km
        """
        total_dist = 0
        for index, each in enumerate(cluster):
            if index < len(cluster) - 1:
                total_dist += haversine(each, cluster[index + 1])
        return total_dist

    def moveability(cluster):
        """
        Function to calculate the moveability metrics

        Parameters:
          cluster is a list of tuples in this format, (lat,lon)

        Return:
          Metrics between 0 and 1
        """
        if traj_curve_dist(cluster) == 0:
            return 0
        return traj_direct_dist(cluster) / traj_curve_dist(cluster)

    def find_key_with_the_highest_count(dict_cluster):
        """
        Function to return key that has the highest number of counts

        Parameters:
          dict_cluster a dictionary of cluster id(key) and coordinates' index(value)

        Return:
          key with the highest number of counts
        """
        return max(dict_cluster, key=lambda k: len(dict_cluster[k]))

    def main_run(inner_list_coordinates, eps, ceps, min_points):
        """
        Function that returns t_dbscan function

        Parameters:
          list_coordiantes contains a list of 2-dimensional tuples (index, (lat, lon))
          eps the first search radius in meters
          ceps the second search radius in meters
          min_points the minimum number of points to be considered as a cluster

        Return:
          dict_cluster a dictionary of cluster id(key) and coordinates' index(value)
        """
        label = [0] * (len(list_coordinates) + 1)
        cluster_id = 1
        min_index_offset = inner_list_coordinates[0][0]

        for each in inner_list_coordinates:
            index = each[0]
            result_neighbors = get_neighbors(
                each, eps, ceps, inner_list_coordinates, min_index_offset)
            if label[index] == 0:
                if len(result_neighbors) >= min_points:
                    label[index] = cluster_id
                    expand_cluster(
                        result_neighbors,
                        cluster_id,
                        label,
                        eps,
                        ceps,
                        min_index_offset,
                        inner_list_coordinates)
                    cluster_id += 1
                else:
                    label[index] = -1

        dict_cluster = {}
        for cluster_id in range(1, max(label) + 1):
            dict_cluster[cluster_id] = []
            for index, value in enumerate(label):
                if value == cluster_id:
                    dict_cluster[cluster_id].append(index - 1)

        return dict_cluster

    dict_cluster = main_run(list_coordinates, eps, ceps, min_points)

    key_exceed = []
    move_dict_cluster = {}
    main_label = [0] * len(list_coordinates)

    for key, value in dict_cluster.items():
        coordinates = []
        tuple_array = []
        for each in value:
            coordinates.append(list_coordinates[each][1])
            tuple_array.append(list_coordinates[each])
        if moveability(coordinates) > move_ability:
            key_exceed.append(key)
        else:
            move_dict_cluster[key] = tuple_array

    for key, value in move_dict_cluster.items():
        dict_cluster = main_run(
            value, stop_eps, stop_ceps, stop_min_points)
        if dict_cluster:
            main_label[dict_cluster[find_key_with_the_highest_count(
                dict_cluster)][0]] = 1

    return main_label


if __name__ == "__main__":
    TEST_COORDINATES = [(1, (1.348378, 103.737931)),
                        (2, (1.348378, 103.737931)), (3, (1.348378, 103.737931))]
    t_dbscan(TEST_COORDINATES, 2, 50, 150, 2, 10, 30, 0.95)
