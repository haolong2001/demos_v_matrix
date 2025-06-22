#!/bin/bash

# Script to run forecast_2050 multiple times
# Usage: ./run_multiple_times.sh [number_of_runs]

NUM_RUNS=${1:-10}  # Default to 10 runs if no argument provided

echo "Running forecast_2050 $NUM_RUNS times..."

for i in $(seq 1 $NUM_RUNS); do
    echo "=== Running iteration $i/$NUM_RUNS ==="
    ./forecast_2050
    if [ $? -ne 0 ]; then
        echo "Error: forecast_2050 failed on iteration $i"
        exit 1
    fi
    echo "=== Completed iteration $i/$NUM_RUNS ==="
    echo
done

echo "All $NUM_RUNS iterations completed successfully!" 