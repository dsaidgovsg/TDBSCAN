from haversine import haversine

def TDBSCAN(list_coordinates, minPoints, Eps, CEps, stop_minPoints, stop_Eps, stop_CEps, move_ability):
  """
  list_coordinates contains list of 2-dimensional tuples (index, (lat, lon))
  
  """
  def expandCluster(result_neighbors, cluster_id, label, Eps, CEps, min_index_offset, inner_list_coordinates):
    count = 1
    while count < len(result_neighbors):
      point = result_neighbors[count]
      index, coordinates = point
      if label[index] == -1:
        label[index] = cluster_id
      elif label[index] == 0:
        label[index] = cluster_id
        expandingCluster = getNeighbors(result_neighbors[count], Eps, CEps, inner_list_coordinates, min_index_offset)
        if (len(expandingCluster) >= minPoints): 
          result_neighbors = result_neighbors + expandingCluster
      count += 1
                      
                      
  def getNeighbors(each, Eps, CEps, list_coordinates, min_index_offset):

    Eps_km = Eps/1000
    CEps_km = CEps/1000
    index, coordinates = each
    result = [each]
    i = index - min_index_offset + 1
    while i < len(list_coordinates):
      index_, coordinates_ = list_coordinates[i] 
      if haversine(coordinates, coordinates_) <= Eps_km:
        result.append(list_coordinates[i])
      elif haversine(coordinates, coordinates_) >= CEps_km:
        break
      i += 1
    return result
      
  def trajDirectDist(cluster):
    """
    trajDirectDist takes in a list of temporal ordered coordinates and calculate the haversine distance from the start and end 
    """
    return haversine(cluster[0],cluster[-1])

  def trajCurveDist(cluster):
    """
    trajCurveDist takes in a list of temporal ordered coordinates and calculate the curve distance, as defined by the distance in between each   coordinates
    """
    total_dist = 0
    count = 0
    while count < len(cluster) - 1:
       total_dist += haversine(cluster[count], cluster[count+1])
       count += 1
    return total_dist

  def moveability(cluster):
    if trajCurveDist(cluster) == 0:
      return 0
    else:
      return trajDirectDist(cluster)/trajCurveDist(cluster)

  def check_for_key_with_highest_count(dic_cluster):
    max_val = 0
    max_key = 0
    for key,value in dic_cluster.items():
      if len(value) > max_val:
        max_val = len(value)
        max_key = key
    return dic_cluster[max_key][0]

  def main_run(inner_list_coordinates, Eps, CEps, minPoints):

    label = [0] * (len(list_coordinates) + 1)
    cluster_id = 1
    min_index_offset = inner_list_coordinates[0][0]

    for each in inner_list_coordinates:
      index, coordinates = each
      result_neighbors = getNeighbors(each, Eps, CEps, inner_list_coordinates, min_index_offset)
      if (label[index] == 0):
        if len(result_neighbors) >= minPoints:
          label[index] = cluster_id
          expandCluster(result_neighbors, cluster_id, label, Eps, CEps, min_index_offset, inner_list_coordinates)
          cluster_id += 1
        else:
          label[index] = -1

    dict_cluster = {}
    for cluster_id in range(1, max(label) + 1):
      dict_cluster[cluster_id] = []
      for index,value in enumerate(label):
        if value == cluster_id:
          dict_cluster[cluster_id].append(index-1)  

    return dict_cluster

        
  dict_cluster = main_run(list_coordinates, Eps, CEps, minPoints)
  
  key_exceed = []
  move_dict_cluster = {}
  main_label = [0] * len(list_coordinates)

  for key,value in dict_cluster.items():
    coordinates = []
    tuple_array = []
    for index,each in enumerate(value): 
      coordinates.append(list_coordinates[each][1])
      #format will be in index, (lat, lon)
      tuple_array.append(list_coordinates[each])
    if moveability(coordinates) > move_ability:
      key_exceed.append(key)
    else:
      move_dict_cluster[key] = tuple_array

  for key,value in move_dict_cluster.items():
    dict_cluster, dummy_label = main_run(value, stop_Eps, stop_CEps, stop_minPoints)
    if len(dict_cluster) > 0:
      main_label[check_for_key_with_highest_count(dict_cluster)] = 1

  return main_label


