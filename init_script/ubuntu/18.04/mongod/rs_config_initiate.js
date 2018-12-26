rs.initiate(
  {
    _id : "rs0-config",
    configsvr: true,
    members: [
      { _id : 0, host : "mongodb-config-0:27019" },
      { _id : 1, host : "mongodb-config-1:27019" },
      { _id : 2, host : "mongodb-config-2:27019" }
    ]
  }
)
