# Databricks notebook source
# MAGIC %fs ls /mnt/training/dataframes/

# COMMAND ----------

peopleDF= spark.read.parquet("dbfs:/mnt/training/dataframes/people-10m.parquet/")
display(peopleDF)

# COMMAND ----------

peopleDF.printSchema

# COMMAND ----------

from pyspark.sql.functions import year
peopleDF.select("firstname","lastname","birthDate","gender").filter(year("birthDate") > "1990").filter("gender = 'F'").show()

# COMMAND ----------

#show data by birthYear
display(peopleDF.select("firstname","lastname",year("birthDate").alias("birthYear"),"gender").filter(year("birthDate") > "1990").filter("gender = 'F'"))

# COMMAND ----------

#show data based on birthYear for the name Mary

(peopleDF.select(year("birthDate").alias("birthYear"))
        .filter("firstName = 'Mary'")
        .filter("gender = 'F'")
        .groupBy("birthYear")
        .count()
        .orderBy("birthYear",ascending=False)
        .show()
       )

# COMMAND ----------

#get 2 poplular names from 1990
(peopleDF.select("firstName")
        .filter("gender = 'F'")
        .filter(year("birthDate") >  "1990")
        .groupBy("firstName")
        .count()
        .orderBy("count",ascending=False)
        .show()
       )

# COMMAND ----------

#compare names of donna and dorothy
from pyspark.sql.functions import col

dordonDF = (peopleDF.select("firstName",year("birthDate").alias("birthYear"))
         .filter((col("firstName")=="Donna") | (col("firstName") == "Dorothy"))
         .filter("gender = 'F'")
         .filter(year("birthDate") > "1990")
         .groupBy("birthYear","firstName")
         .count()
         .orderBy("birthYear")
)
display(dordonDF)

# COMMAND ----------

#save dordon as temp view

dordonDF.createOrReplaceTempView("DorDon")

# COMMAND ----------

# MAGIC %sql
# MAGIC 
# MAGIC select * from dordon

# COMMAND ----------

#top 10 female first names 

top10FemalesDF = peopleDF.select("firstName").filter("gender = 'F'").groupBy("firstName").count().orderBy(["count","firstName"],ascending=[0,1]).limit(10)
display(top10FemalesDF.orderBy("firstName"))

# COMMAND ----------

#using count and desc sql functions

from pyspark.sql.functions import count,desc
(peopleDF 
  .select("firstName") 
  .filter("gender = 'F'") 
  .groupBy("firstName")
  .agg(count("firstName").alias("total"))
  .orderBy(desc("total"), "firstName")
  .show(10)
)                          

# COMMAND ----------

