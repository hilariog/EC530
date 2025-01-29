import sys
import csv
import os
import ast
import math

# Get arguments passed from Node.js
file = sys.argv[1]
useCSV1 = sys.argv[8] == 'true'  # Convert string 'true'/'false' to boolean
useCSV2 = sys.argv[9] == 'true'  # Convert string 'true'/'false' to boolean

# Function to check if a value is a valid real number
def is_real_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

# Function to read CSV and get the specified columns
def read_csv_columns(file_path, col1, col2):
    data = []
    path = os.path.abspath(os.path.expanduser(file))
    # if not os.path.exists(path):
    #     print(f"File does not exist: {path}")
    #     sys.exit(1)
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) > max(col1, col2):  # Check if row has enough columns
                value1 = row[col1]
                value2 = row[col2]
                # Only add the pair if both values are valid real numbers
                if is_real_number(value1) and is_real_number(value2):
                    data.append([float(value1), float(value2)])
    return data

# Populate arrays with error checking
array1 = []
array2 = []

# If use CSV is enabled for Array 1
if useCSV1:
    columnIndex1A = int(sys.argv[2])  # 1-based index, convert to 0-based
    columnIndex2A = int(sys.argv[3])  # 1-based index, convert to 0-based
    array1 = read_csv_columns(file, columnIndex1A, columnIndex2A)
else:
    # Check if the manual entry is valid (skip empty or invalid numbers)
    try:
        manualEntry1 = ast.literal_eval(sys.argv[6])  # Convert string to list
        if isinstance(manualEntry1, list):  # Ensure it's a list
            for entry in manualEntry1:
                if isinstance(entry, list) and all(is_real_number(str(num)) for num in entry):
                    array1.append([float(num) for num in entry])
    except (ValueError, SyntaxError):
        print("Invalid format for manual entry 1")

# If use CSV is enabled for Array 2
if useCSV2:
    columnIndex1B = int(sys.argv[4])  # 1-based index, convert to 0-based
    columnIndex2B = int(sys.argv[5])  # 1-based index, convert to 0-based
    array2 = read_csv_columns(file, columnIndex1B, columnIndex2B)
else:
    # Check if the manual entry is valid (skip empty or invalid numbers)
    try:
        manualEntry2 = ast.literal_eval(sys.argv[7])  # Convert string to list
        if isinstance(manualEntry2, list):  # Ensure it's a list
            for entry in manualEntry2:
                if isinstance(entry, list) and all(is_real_number(str(num)) for num in entry):
                    array2.append([float(num) for num in entry])
    except (ValueError, SyntaxError):
        print("Invalid format for manual entry 1")

# Output the arrays as strings for the frontend
print(f"Array 1 input: {array1}")
print(f"Array 2 input: {array2}")

def hav(thet):
  return math.sin(thet / 2) ** 2

def d(lat1, long1, lat2, long2, R = 6371):
  lat1, long1, lat2, long2 = map(math.radians, [lat1, long1, lat2, long2])#needs to be radians
  a = hav(abs(lat1-lat2)) + math.cos(lat1)*math.cos(lat2)*hav(abs(long1-long2))
  return 2*R*math.asin(math.sqrt(a))

def two_arrays(arr1, arr2):
  size1 = len(arr1)
  size2 = len(arr2)
  array3 = []#will hold the associated closest point from array2 to array1 point
  for i in range(size1):
    min = math.inf
    for j in range(size2):
      dist = d(arr1[i][0], arr1[i][1], arr2[j][0], arr2[j][1])
      if dist < min:
        min = dist
        point = array2[j]
    array3.append(point)
  return array3

print(f"Output Array: {two_arrays(array1, array2)}")