rs.initiate(
  {
    _id : "rs0-shard",
    members: [
      { _id : 0, host : "mongodb-shard-0:27018" },
      { _id : 1, host : "mongodb-shard-1:27018" },
      { _id : 2, host : "mongodb-shard-2:27018" }
    ]
  }
)
