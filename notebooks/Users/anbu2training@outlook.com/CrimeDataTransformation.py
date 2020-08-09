# Databricks notebook source
# 3 parameters

dbutils.widgets.text("accountName","","Account Name")
dbutils.widgets.text("accountKey","", "Account Key")
dbutils.widgets.text("containerName","","Container Name")

# COMMAND ----------

accountName= dbutils.widgets.get("accountName")
accountKey= dbutils.widgets.get("accountKey")
containerName= dbutils.widgets.get("containerName")

# COMMAND ----------

connectionString = "wasbs://{}@{}.blob.core.windows.net/crimeData".format(containerName,accountName)

# COMMAND ----------

spark.conf.set("fs.azure.account.key."+accountName+".blob.core.windows.net",accountKey)

# COMMAND ----------

#createDF for each dataset

bostonDF = spark.read.parquet("%s/Crime-Data-Boston-2016.parquet" % (connectionString))
chicagoDF = spark.read.parquet("%s/Crime-Data-Chicago-2016.parquet" % (connectionString))
dallasDF =  spark.read.parquet("%s/Crime-Data-Dallas-2016.parquet" % (connectionString))
losAngelesDF = spark.read.parquet("%(connectionString)s/Crime-Data-Los-Angeles-2016.parquet" % locals())
newOrleansDF = spark.read.parquet("%(connectionString)s/Crime-Data-New-Orleans-2016.parquet" % locals())
newYorkDF = spark.read.parquet("%(connectionString)s/Crime-Data-New-York-2016.parquet" % locals())
phillyDF = spark.read.parquet("%(connectionString)s/Crime-Data-Philadelphia-2016.parquet" % locals())


# COMMAND ----------

#import required libraries
import datetime 
from pyspark.sql.functions import col,lit,lower,month,unix_timestamp,upper
from pyspark.sql.types import *

# COMMAND ----------

homicidesBostonDF =(bostonDF.withColumn("city",lit("Boston"))
                   .select("month",col("OFFENSE_CODE_GROUP").alias("offense"), col("city"))
                   .filter(lower(col("offense")).contains("homicide"))
                   )

homicidesChicagoDF= (chicagoDF.withColumn("city",lit("Chicago"))
                     .select(month("date").alias("month"),col("primaryType").alias("offense"),col("city"))
                     .filter(lower(col("primaryType")).contains("homicide"))
)
homicidesDallasDF= (dallasDF.withColumn("city",lit("Dallas"))
                   .select(month(unix_timestamp(col("callDateTime"),"M/d/yyyy h:mm:ss a").cast("timestamp")).alias("month"), col("typeOfIncident").alias("offense"),col("city"))
                    .filter(lower(col("typeOfIncident")).contains("murder") | lower(col("typeOfIncident")).contains("manslaughter"))
                   )

homicidesLosAngelesDF = (losAngelesDF.withColumn("city",lit("Los Angeles"))
                         .select(month(col("dateOccurred")).alias("month"), col("crimeCodeDescription").alias("offense"), col("city"))
                         .filter(lower(col("crimeCodeDescription")).contains("homicide") | lower(col("crimeCodeDescription")).contains("manslaughter"))
)

homicidesNewOrleansDF = (newOrleansDF.withColumn("city", lit("New Orleans"))
                         .select(month(col("Occurred_Date_Time")).alias("month"),col("Incident_Description").alias("offense"),col("city"))
                         .filter(lower(col("Incident_Description")).contains("homicide") | lower(col("Incident_Description")).contains("murder"))
)

homicidesNewYorkDF = ( newYorkDF.withColumn("city",lit("New York"))
                       .select(month(col("reportDate")).alias("month"),col("offenseDescription").alias("offense"),col("city"))
                       .filter(lower(col("offenseDescription")).contains("murder") | lower(col("offenseDescription")).contains("homicide"))
)

homicidesPhillyDF  = ( phillyDF.withColumn("city",lit("Philadelphia"))
                      .select(month(col("dispatch_date")).alias("month"),col("text_general_code").alias("offense"),col("city"))
                      .filter(lower(col("text_general_code")).contains("homicide"))
                     )




# COMMAND ----------

# merge all into single DF

homicidesDF = homicidesBostonDF.union(homicidesChicagoDF).union(homicidesDallasDF).union(homicidesLosAngelesDF).union(homicidesNewOrleansDF).union(homicidesNewYorkDF).union(homicidesPhillyDF)

# COMMAND ----------

homicidesDF.write.mode("overwrite").saveAsTable("Homicides_2016")

# COMMAND ----------

# return ok to the job

import json
dbutils.notebook.exit(json.dumps({
  "status": "ok"
  "message" : "Cleaned data and joined into a table"
  "tables": ["Homicides_2016"]
}))