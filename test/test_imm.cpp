



#include "migration.h"



using namespace Eigen;
using namespace std;



int main(){

    MigrationSimulator simulator;
    ArrayXf rates = disappear_mat[index].row(disappear_idx).segment(year, NUM_YEARS - year);
    ArrayXXf replicated_rates = rates.replicate(1, num_immigrants).transpose();
    ArrayXXi survival_status = (generateRandomValues(num_immigrants, NUM_YEARS - year) >= replicated_rates).cast<int>();
            



    return 0;
}