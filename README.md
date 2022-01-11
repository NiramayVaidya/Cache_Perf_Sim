The original repository is here- https://github.com/abhijeeetkumar/CachePerformanceOnMatMul
Following are the steps for its usage-

# CachePerformanceonMatMul
CSE530 Class project

For generating matrices:-
python utils/random_matrix_generator.py --n 100 --dump input_matrix.in --sparsity 100

For running kernel and simulator:-
source run_kernel.sh

For running simulator:-
source run_simulator.sh <path to traces>

My changes are in the assignment branches. The assignment-1 branch consists of the different kernels for which cache perf analysis has been done. the assignment-2 branch consists of the implementations for the different cache policies (inclusive and exclusive, whereas NINE was already provided as the baseline).
