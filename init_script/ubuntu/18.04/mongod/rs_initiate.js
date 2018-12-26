rs.initiate( {
   _id : "rs0",
   members: [
      { _id: 0, host: "mongodb-rs-0:27017" },
      { _id: 1, host: "mongodb-rs-1:27017" },
      { _id: 2, host: "mongodb-rs-2:27017" }
   ]
})
