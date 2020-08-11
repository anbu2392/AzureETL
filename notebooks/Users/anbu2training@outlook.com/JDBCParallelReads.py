# Databricks notebook source
#format for postgresql url jdbc:postgresql://server1.databricks.traning:5432/training
jdbcHostName="server1.databricks.training"
jdbcPort=5432
jdbcDatabase="training"

jdbcUrl ="jdbc:postgresql://{0}:{1}/{2}".format(jdbcHostName,jdbcPort,jdbcDatabase)

# COMMAND ----------

connectionProps ={
  "user":"readonly",
  "password":"readonly"
}

# COMMAND ----------

accountDF = spark.read.jdbc(url=jdbcUrl, table="Account",properties = connectionProps)

# COMMAND ----------

dfMin=accountDF.select(min("insertID")).first()[0]
dfMax=accountDF.select(max("insertID")).first()[0]

# COMMAND ----------

#now connect parallely

accountDFParallel = spark.read.jdbc(
  url=jdbcUrl,
  table="Account",
  properties=connectionProps,
  lowerBound=dfMin,
  upperBound=dfMax,
  numPartitions=12
)

# COMMAND ----------

print(accountDF.rdd.getNumPartitions())
print(accountDFParallel.rdd.getNumPartitions())

# COMMAND ----------

# MAGIC %timeit accountDF.describe()
# MAGIC %timeit accountDFParallel.describe()