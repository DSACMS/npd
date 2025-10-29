import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Script generated for node Amazon S3
AmazonS3_node1756922065412 = glueContext.create_dynamic_frame.from_catalog(database="ndh-glue-data-catalog", table_name="endpoint_pfile", transformation_ctx="AmazonS3_node1756922065412")

# Script generated for node Amazon S3
AmazonS3_node1756922135936 = glueContext.write_dynamic_frame.from_options(frame=AmazonS3_node1756922065412, connection_type="s3", format="glueparquet", connection_options={"path": "s3://ndh-glue-s3-output/endpoint_pfile/", "partitionKeys": []}, format_options={"compression": "snappy"}, transformation_ctx="AmazonS3_node1756922135936")

job.commit()