

# Specify the path to the file
file <- 'data/AESFR_matrix_combine.dput'

# Use dget to read the dput file into R
AESFR_matrix_combine <- dget(file)

AESFR_matrix_combine[1,11,]

AESFR_matrix_combine[1,40,]

# Check the structure of the loaded data
str(AESFR_matrix_combine)

class(AESFR_matrix_combine)
# 1:12
# for past dataset, it's all the same 
# for the future dataset, it's of mean

# Open a connection to a binary file
bin_file <- file("data/bin/AESFR_matrix_combine.bin", "wb")

# Write the matrix to the binary file
writeBin(as.numeric(AESFR_matrix_combine), bin_file)

# Close the connection
close(bin_file)



# Open the binary file for reading
bin_file <- file("data/bin/AESFR_matrix_combine.bin", "rb")

# Calculate the total number of elements in the original array
num_elements <- 12 * 71 * 35

# Read the data from the binary file
binary_data <- readBin(bin_file, numeric(), n = num_elements)

# Close the connection
close(bin_file)

# Reshape the vector back to the original dimensions
AESFR_matrix_combine <- array(binary_data, dim = c(12, 71, 35))

AESFR_matrix_combine[1,11,]



class(AESFR_matrix_combine)
dim(AESFR_matrix_combine)



# Example 3D array (e.g., 2x3x4)
my_3d_array <- array(runif(24), dim = c(2, 3, 4))

# Open a binary file connection for writing
con <- file("AESFR_matrix_combine.bin", "wb")

# Write the array as a flat vector (column-major order)
writeBin(as.numeric(my_3d_array), con)

# Close the connection
close(con)

my_3d_array[1,,]
