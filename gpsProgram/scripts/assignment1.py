# havthet = havdelgam + cosgam1*cosgam2*havdellam
#d = 2rarcsin(sqrthavthet)
#from resource https://en.wikipedia.org/wiki/Haversine_formula
import math

def hav(thet):
  return math.sin(thet / 2) ** 2

def d(lat1, long1, lat2, long2, R = 6371):
  lat1, long1, lat2, long2 = map(math.radians, [lat1, long1, lat2, long2])#needs to be radians
  a = hav(abs(lat1-lat2)) + math.cos(lat1)*math.cos(lat2)*hav(abs(long1-long2))
  return 2*R*math.asin(math.sqrt(a))
  

print(d(45.5, -122.7, 44, -123))#testing with eugene portland

lat1, long1 = 52.5200, 13.4050  # Berlin
lat2, long2 = 48.8566, 2.3522   # Paris
print(d(lat1, long1, lat2, long2))#testing w paris berlin

def two_arrays(array1, array2):
  size1 = len(array1)
  size2 = len(array2)

  array3= []#will hold the associated closest point from array2 to array1 point
  for i in range(size1):
    min = math.inf
    for j in range(size2):
      dist = d(array1[i][0], array1[i][1], array2[j][0], array2[j][1])
      if dist < min:
        min = dist
        point = array2[j]
    array3.append(point)
  return array1, array3

print(two_arrays([[52.5200, 13.4050], [45.5, -122.7], [45, -122.7]], [[44, -123],[48.8566, 2.3522]]))