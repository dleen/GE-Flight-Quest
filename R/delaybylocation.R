library(stringr)
library(lubridate)

flightHistory <- read.csv("flighthistory.csv")
# Replace missing values with NA
flightHistory[flightHistory == "MISSING"] = NA

# Remove rows where any of the flight times are NA, other columns
# being NA is ok for this file.
flightHistory <- flightHistory[complete.cases(flightHistory[,c(6,10:19)]),]

for(i in 10:19) {
  flightHistory[,i] <- ymd_hms(str_sub(flightHistory[,i], 1, 19))
}

delayMins <- int_length(
    as.interval(
      flightHistory$scheduled_runway_arrival, 
      flightHistory$actual_runway_arrival
    )
  )/60

meanDelayByAirport <- 
  aggregate(delayMins ~ flightHistory$departure_airport_code, FUN = mean, na.rm=T)

meanDelayByAirport <- meanDelayByAirport[order(meanDelayByAirport$delayMins, decreasing=T),]

names(meanDelayByAirport) <- c("airportCode", "delayMins")

mde <- meanDelayByAirport$delayMins[1:20]
nam <- meanDelayByAirport$airportCode[1:20]

barplot(height=mde, names.arg=nam, las=1, horiz=T)

singleAirport <- flightHistory[flightHistory$departure_airport_code == "CEC",]
delayMinsSingle <- int_length(
  as.interval(
    singleAirport$scheduled_runway_arrival, 
    singleAirport$actual_runway_arrival
  )
)/60

barplot(delayMinsSingle)
