# Databricks notebook source
# MAGIC %fs head /mnt/training/zips.json

# COMMAND ----------

#schema Inference
zipsDF = spark.read.json("/mnt/training/zips.json")
zipsDF.printSchema()

# COMMAND ----------

zipsSchema = zipsDF.schema
print(type(zipsSchema))

[field for field in zipsSchema]

# COMMAND ----------

from pyspark.sql.types import StructType, StructField, IntegerType, StringType

zipsSchema2 = StructType([
  StructField("city", StringType(), True), 
  StructField("pop", IntegerType(), True) 
])

zipDF2= spark.read.schema(zips2Schema).json("/mnt/training/zips.json")
display(zipDF2)

# COMMAND ----------

from pyspark.sql.types import StructType, StructField, IntegerType, StringType, ArrayType, FloatType
zip3Schema = StructType([
  StructField("city",StringType(),True),
  StructField("loc",
            ArrayType(FloatType(),True),True),
  StructField("pop",IntegerType(),True)
])

zipDF3= spark.read.schema(zip3Schema).json("/mnt/training/zips.json")

display(zipDF3)

# COMMAND ----------

# MAGIC %fs head /mnt/training/UbiqLog4UCI/14_F/log_1-6-2014.txt

# COMMAND ----------

smartphoneDF=spark.read.json("/mnt/training/UbiqLog4UCI/14_F/log*")

# COMMAND ----------

cols=set(smartphoneDF.columns)
print(smartphoneDF.columns)

# COMMAND ----------

smartphoneDF.printSchema()

# COMMAND ----------

from pyspark.sql.types import StructField,StructType,StringType
from pyspark.sql.functions import col

smsSchema = StructType([
  StructField("SMS",StringType(),True)
])

# COMMAND ----------

smsDF=(spark.read
      .schema(smsSchema)
      .json("/mnt/training/UbiqLog4UCI/14_F/log*")
      .filter(col("SMS").isNotNull())
      )
display(smsDF)

# COMMAND ----------

#full schema for sms

schema2= StructType([
  StructField("SMS",StructType([
    StructField("Address",StringType(),True),
    StructField("date",StringType(),True),
    StructField("metadata",StructType([
      StructField("name",StringType(),True)
    ]),True),    
  ]),True)
])

SMSDF2=(spark.read.schema(schema2).json("/mnt/training/UbiqLog4UCI/14_F/log*").filter(col("SMS").isNotNull()))

display(SMSDF2)

# COMMAND ----------

schemaJson= SMSDF2.schema.json()
print(schemaJson)

# COMMAND ----------

smsCorruptDF=(spark.read
             .option("mode","PERMISSIVE")
             .option("columnNameOfCorruptRecord","SMSCorrupt")
             .json("/mnt/training/UbiqLog4UCI/14_F/log*")
             .select("SMS","SMSCorrupt")
              .filter(col("SMSCorrupt").isNotNull())
             )
display(smsCorruptDF)

# COMMAND ----------

#use BadRecordsPath

smsCorrupt2DF =(spark.read
                .option("badRecordsPath", "/tmp/corruptSMS")
                .json("/mnt/training/UbiqLog4UCI/14_F/log*")
)

display(smsCorrupt2DF)

# COMMAND ----------

corruptCount=spark.read.json("/tmp/corruptSMS/*/*/*").count()
print(corruptCount)

# COMMAND ----------

