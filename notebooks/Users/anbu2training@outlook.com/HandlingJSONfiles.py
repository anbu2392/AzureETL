# Databricks notebook source
# MAGIC %fs ls /mnt/training

# COMMAND ----------

dbBlogDF= spark.read.option("inferSchema","True").option("header","True").json("/mnt/training/databricks-blog.json")


# COMMAND ----------

dbBlogDF.printSchema()

# COMMAND ----------

StructType(List(
  StructField(authors,ArrayType(StringType,true),true),
  StructField(categories,ArrayType(StringType,true),true),
  StructField(content,StringType,true),
  StructField(creator,StringType,true),
  StructField(dates,
              StructType(List(
                StructField(createdOn,StringType,true),
                StructField(publishedOn,StringType,true),
                StructField(tz,StringType,true))),true),
  StructField(description,StringType,true),StructField(id,LongType,true),
  StructField(link,StringType,true),StructField(slug,StringType,true),
  StructField(status,StringType,true),StructField(title,StringType,true)
))

# COMMAND ----------

#select few columns 
display(dbBlogDF.select("authors","categories","dates"))from

# COMMAND ----------

display(dbBlogDF.select("dates.createdOn","dates.publishedOn"))

# COMMAND ----------

from pyspark.sql.functions import date_format
dbBlog2DF=dbBlogDF.withColumn("publishedOn",date_format("dates.publishedOn", "yyyy-MM-dd"))


# COMMAND ----------

from pyspark.sql.functions import year
display(dbBlog2DF.filter(year("publishedOn") > 1990 ))

# COMMAND ----------

#analysis on Array.

from pyspark.sql.functions import size

dbBlogDF.select(size("authors"),"authors").show()

# COMMAND ----------

display(dbBlogDF.select(col("authors")[0].alias("primaryAuthor"),"authors"))

# COMMAND ----------

from pyspark.sql.functions import explode

display(dbBlogDF.select("title","authors",explode("authors").alias("author")).filter(size("authors")>1).orderBy("title"))

# COMMAND ----------

#authored by Michael Armbrust
from pyspark.sql.functions import array_contains

michealAmbrustDF=dbBlogDF.select("title","link").filter(array_contains("authors","Michael Armbrust"))
display(michealAmbrustDF)

# COMMAND ----------

#unique categories

uniqueCategoriesDF= dbBlogDF.select(explode("categories").alias("category")).distinct().orderBy("category")
display(uniqueCategoriesDF)

# COMMAND ----------

#count of category
from pyspark.sql.functions import count
display(dbBlogDF.select(explode("categories").alias("category")).groupby("category").agg(count("*").alias("Total")).orderBy("Category",ascending=True))

# COMMAND ----------

