
#include <Eigen/Dense>
using namespace Eigen;

/**
 * @param  
 */
void generateMigration(
    ArrayXXi& MigNumMat,
    const ArrayXXf& disappear_mat,
    ArrayXXi& ExistingMatrix,
    ArrayXXi& MigAgeMatrix
){
   int nrows =  MigNumMat.sum();
   int ncols = 34; // ask Gang
   // 86 * 3
   int start,idx = 0;
   int sub_immi_num = 0; // col sums 
   int num = 0;
   ArrayXf rate;
   ArrayXXf temp;
   // i is index for year 
   // from year 1991 
   for (int i = 1; i < ncols; ++i ){
    ArrayXi vec = MigNumMat.col(i);
    sub_immi_num = vec.sum();
    // sub block -1; means 
    ExistingMatrix.block(start, 0,sub_immi_num, i ) = -1;
    for (int j = 0; j < 86 ; j++){
        num = vec[j];
        idx = j - i + 33;
        // equivalent to j - i age ; and age it converted to index j -i + 33 
        // disappear rate 

        rate = disappear_mat.block(idx,i,1,ncols - i);
        temp = rate.replicate(1,num).transpose();
        ExistingMatrix.block(start,i+1,num, ncols + 1 - i)
        =  (temp <= 
        Rand::balanced<ArrayXXf>(num, ncols - i, urng,0,1)).cast<int>();
             
    }
   }  
}
