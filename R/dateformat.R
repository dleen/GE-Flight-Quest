library(stringr)
library(lubridate)

flightHistory <- 
  read.csv("../Data/InitialTrainingSet_rev1/2012_11_12/FlightHistory/flighthistory.csv")
# Replace missing values with NA
flightHistory[flightHistory == "MISSING"] = NA

for(i in 10:19) {
  flightHistory[,i] <- ymd_hms(str_sub(flightHistory[,i], 1, 19))
}