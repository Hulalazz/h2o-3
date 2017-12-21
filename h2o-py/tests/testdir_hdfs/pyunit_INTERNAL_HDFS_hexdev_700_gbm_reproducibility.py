import sys
sys.path.insert(1,"../../../")
import h2o
from tests import pyunit_utils
from h2o.estimators.gbm import H2OGradientBoostingEstimator
from random import randint

# HEXDEV-700: GBM reproducibility issue.
def gbm_reproducibility():
    # Check if we are running inside the H2O network by seeing if we can touch
    # the namenode.
    hadoop_namenode_is_accessible = pyunit_utils.hadoop_namenode_is_accessible()

    if hadoop_namenode_is_accessible:
    # run GBM twice with true_reproducibility = True
        seedv = randint(1,10000000000)
        ntree = 50
        auc2 = runGBM(seedv, ntree)
        print(auc2)

    else:
        raise EnvironmentError

def runGBM(seedV, nt):
    #import data frame
    hdfs_name_node = pyunit_utils.hadoop_namenode()
    hdfs_csv_file = "/datasets/reproducibility_issue.csv.zip"
    url_csv = "hdfs://{0}{1}".format(hdfs_name_node, hdfs_csv_file)
    h2oframe_csv = h2o.import_file(url_csv)
    gbm = H2OGradientBoostingEstimator(distribution='bernoulli', ntrees=nt, seed= seedV, max_depth = 4,
                                       min_rows = 7, score_tree_interval=nt)
    gbm.train(x=list(range(2,365)), y="response", training_frame=h2oframe_csv)

    print("Model run time (ms) is {0}".format(gbm._model_json["output"]["run_time"]))

    auc = pyunit_utils.extract_from_twoDimTable(gbm._model_json['output']['training_metrics']._metric_json['thresholds_and_metric_scores'], 'threshold', takeFirst=False)
    h2o.remove(h2oframe_csv)
    h2o.remove(gbm)
    return auc

if __name__ == "__main__":
    pyunit_utils.standalone_test(gbm_reproducibility)
else:
    gbm_reproducibility()