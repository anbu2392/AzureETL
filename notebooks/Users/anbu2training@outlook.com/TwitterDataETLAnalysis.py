# Databricks notebook source
path ="/mnt/training/twitter/firehose/2018/01/08/18/twitterstream-1-2018-01-08-18-48-00-bcf3d615-9c04-44ec-aac9-25f966490aa4"

#will start with small data then i can use  "/mnt/training/twitter/firehose/2018/*/*/*/*" to all data

# COMMAND ----------

df=spark.read.json(path)

# COMMAND ----------

df.printSchema()

# COMMAND ----------

#schema and DF for Tweets
from pyspark.sql.types import StructType,StructField,IntegerType,StringType,LongType

tweetSchema = StructType([
  StructField("id",LongType(),True),
  StructField("user",StructType([
    StructField("id",LongType(),True)
  ]),True),
  StructField("lang",StringType(),True),
  StructField("text",StringType(),True),
  StructField("created_at",StringType(),True)
])

tweetDF= (spark.read
         .schema(tweetSchema)
         .json(path))
display(tweetDF)

# COMMAND ----------

#to check if we got all the expected rows
from pyspark.sql.functions import col
tweetCount= tweetDF.filter(col("id").isNotNull()).count()
print(tweetCount)

# COMMAND ----------

#create schema and DF for FullTweet
from pyspark.sql.types import StructField, StructType, ArrayType

fullTweetSchema = StructType([
  StructField("id", LongType(), True),
  StructField("user", StructType([
    StructField("id", LongType(), True),
    StructField("screen_name", StringType(), True),
    StructField("location", StringType(), True),
    StructField("friends_count", IntegerType(), True),
    StructField("followers_count", IntegerType(), True),
    StructField("description", StringType(), True)
  ]), True),
  StructField("entities", StructType([
    StructField("hashtags", ArrayType(
      StructType([
        StructField("text", StringType(), True)
      ]),
    ), True),
    StructField("urls", ArrayType(
      StructType([
        StructField("url", StringType(), True),
        StructField("expanded_url", StringType(), True),
        StructField("display_url", StringType(), True)
      ]),
    ), True)
  ]), True),
  StructField("lang", StringType(), True),
  StructField("text", StringType(), True),
  StructField("created_at", StringType(), True)
])

fullTweetDF = spark.read.schema(fullTweetSchema).json(path)
fullTweetDF.printSchema()
display(fullTweetDF)

# COMMAND ----------

#now we have 2 DF.
#step 1 filter nulls


fullTweetFilteredDF =(fullTweetDF.filter(col("id").isNotNull()))
tweetFilteredDF = tweetDF.filter(col("id").isNotNull())


# COMMAND ----------

display(fullTweetFilteredDF.select("created_at").limit(10))

# COMMAND ----------

from pyspark.sql.functions import length
length(tweetFilteredDF.created_at)

# COMMAND ----------

#twitter uses unique timestamp to convert into timestamp
from pyspark.sql.functions import unix_timestamp,to_timestamp,substring
from pyspark.sql.types import TimestampType
spark.sql("set spark.sql.legacy.timeParserPolicy=LEGACY")

timestampFormat ="EEE MMM dd HH:mm:ss ZZZZZ yyyy"
#timestampFormat ="yyyy-mm-dd HH:mm:ss"
spark.sql("set spark.sql.legacy.timeParserPolicy=LEGACY")
tweetsDF=(tweetFilteredDF.select(col("id").alias("tweet_id"),col("user.id").alias("user_id"),col("lang").alias("language"),col("text"),unix_timestamp(col("created_at"),timestampFormat).cast(TimestampType()).alias("createdAt")))
display(tweetsDF)

# COMMAND ----------

#create AccountDF from user section of JSON

accountDF = (fullTweetFilteredDF.select(col("user.id").alias("user_id"),col("user.screen_name").alias("screenName"),col("user.location"),col("user.friends_count").alias("friendsCount"),col("user.followers_count").alias("followersCount"),col("user.description"))            )

display(accountDF)

# COMMAND ----------

display(fullTweetFilteredDF.select(col("id").alias("tweetId"), explode("entities.urls").alias("urls")).select(col("tweetId"), col("urls.*")))

# COMMAND ----------

#explode to create hashtagDF and urlDF
from pyspark.sql.functions import explode

hashtagDF = (fullTweetFilteredDF.select(col("id").alias("tweetId"),explode("entities.hashtags.text"))
          )
urlDF=(fullTweetFilteredDF.select(col("id").alias("tweetId"), explode("entities.urls").alias("urls")).select(col("tweetId"), col("urls.url").alias("URL"),col("urls.display_url").alias("displayURL"),col("urls.expanded_url").alias("expandedURL")))

# COMMAND ----------

print(hashtagDF.count())
print(hashtagDF.distinct().count())


# COMMAND ----------

#save into parquet files

accountDF.write.mode("overwrite").parquet("/anbu/account.parquet")
hashtagDF.write.mode("overwrite").parquet("/anbu/hastag.parquet")
urlDF.write.mode("overwrite").parquet("/anbu/url.parquet")
tweetsDF.write.mode("overwrite").parquet("/anbu/tweets.parquet")
