# Disease Processing Module

This module contains a parallel processor for analyzing forecast data from multiple simulation runs.

## Overview

The `bmi_process_parallel` program automatically processes all forecast folders in the `output/` directory, implementing the same logic as the Python analysis code but with C++ performance and parallel processing.

## Features

- **Automatic folder detection**: Finds all forecast folders matching the pattern `YYYYMMDD_HHMMSS_RRRR`
- **Parallel processing**: Uses all available CPU cores for maximum performance
- **Binary file reading**: Reads the forecast matrix binary files directly
- **Dead person removal**: Filters out rows where all values are negative (dead people)
- **Thread-safe output**: Concurrent processing with synchronized logging
- **Error handling**: Graceful handling of missing files or corrupted data

## Compilation

```bash
cd src_disease
make -f Makefile.disease
```

## Usage

**Run from the parent directory (recommended):**
```bash
# From the main project directory
./build/BMI/bmi_process_parallel
```

**Or compile and run from src_disease directory:**
```bash
cd src_disease
make -f Makefile.bmi run
```

## Output

The program processes each forecast folder and outputs:
- Processing status for each folder
- Matrix statistics (original vs filtered row counts)
- Summary of successful and failed processing attempts

## Algorithm

For each forecast folder:
1. Read 8 binary matrix files (`forecast_matrix_0.bin` through `forecast_matrix_7.bin`)
2. For each matrix, remove rows where all values are negative (dead people)
3. Store the filtered matrices for further analysis

## Performance

- **Parallel processing**: Uses all available CPU cores
- **Memory efficient**: Processes one folder at a time per thread
- **Fast I/O**: Direct binary file reading without intermediate conversions

## Integration

This program can be integrated into the main build system:

```bash
cd src_disease
make -f Makefile.disease install
```

This will copy the compiled binary to `../build/disease_processor` for use in the main project.

## Workflow Integration

The disease processing module works with the main project workflow:

1. **Generate forecasts**: `for i in {1..10}; do ../build/forecast_2050 & done; wait`
2. **Process disease data**: `./disease_processor`
3. **Calculate BMI**: `../build/BMI/bmi_process_parallel`

## File Structure

- `parallel_disease_processor.cpp` - Main source code
- `bmi_process_parallel.cpp` - BMI calculation module
- `Makefile.disease` - Separate Makefile to avoid conflicts
- `Makefile.bmi` - BMI calculator Makefile
- `README.md` - This documentation 