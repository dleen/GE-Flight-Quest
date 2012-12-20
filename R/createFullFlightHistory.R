library(stringr)
library(lubridate)

flightHistory12 <- 
  read.csv("../Data/InitialTrainingSet_rev1/2012_11_12/FlightHistory/flighthistory.csv")

flightHistory13 <- 
  read.csv("../Data/InitialTrainingSet_rev1/2012_11_13/FlightHistory/flighthistory.csv")

flightHistory14 <- 
  read.csv("../Data/InitialTrainingSet_rev1/2012_11_14/FlightHistory/flighthistory.csv")

flightHistory15 <- 
  read.csv("../Data/InitialTrainingSet_rev1/2012_11_15/FlightHistory/flighthistory.csv")

flightHistory16 <- 
  read.csv("../Data/InitialTrainingSet_rev1/2012_11_16/FlightHistory/flighthistory.csv")

flightHistory17 <- 
  read.csv("../Data/InitialTrainingSet_rev1/2012_11_17/FlightHistory/flighthistory.csv")

flightHistory18 <- 
  read.csv("../Data/InitialTrainingSet_rev1/2012_11_18/FlightHistory/flighthistory.csv")

flightHistory19 <- 
  read.csv("../Data/InitialTrainingSet_rev1/2012_11_19/FlightHistory/flighthistory.csv")

flightHistory20 <- 
  read.csv("../Data/InitialTrainingSet_rev1/2012_11_20/FlightHistory/flighthistory.csv")

flightHistory21 <- 
  read.csv("../Data/InitialTrainingSet_rev1/2012_11_21/FlightHistory/flighthistory.csv")

flightHistory22 <- 
  read.csv("../Data/InitialTrainingSet_rev1/2012_11_22/FlightHistory/flighthistory.csv")

flightHistory23 <- 
  read.csv("../Data/InitialTrainingSet_rev1/2012_11_23/FlightHistory/flighthistory.csv")

flightHistory24 <- 
  read.csv("../Data/InitialTrainingSet_rev1/2012_11_24/FlightHistory/flighthistory.csv")

flightHistory25 <- 
  read.csv("../Data/InitialTrainingSet_rev1/2012_11_25/FlightHistory/flighthistory.csv")

flightHistory <- rbind(flightHistory12, flightHistory13, flightHistory14, 
                       flightHistory15, flightHistory16, flightHistory17, 
                       flightHistory18, flightHistory19, flightHistory20,
                       flightHistory21, flightHistory22, flightHistory23, 
                       flightHistory24, flightHistory25)

rm(flightHistory12, flightHistory13, flightHistory14, 
   flightHistory15, flightHistory16, flightHistory17, 
   flightHistory18, flightHistory19, flightHistory20,
   flightHistory21, flightHistory22, flightHistory23, 
   flightHistory24, flightHistory25)

# Replace missing values with NA
flightHistory[flightHistory == "MISSING"] = NA

for(i in 9:18) {
  flightHistory[,i] <- ymd_hms(str_sub(flightHistory[,i], 1, 19))
}

# Remove rows where any of the flight times are NA, other columns
# being NA is ok for this file.
# flightHistory <- flightHistory[complete.cases(flightHistory[,c(9:18)]),]

# Local time scheduled gate departure
flightHistory$local_time_scheduled_gate_departure <- flightHistory$scheduled_gate_departure
hour(flightHistory$local_time_scheduled_gate_departure) <- 
  hour(flightHistory$local_time_scheduled_gate_departure) - 
  flightHistory$departure_airport_timezone_offset

# Local time scheduled runway departure
flightHistory$local_time_scheduled_runway_departure <- flightHistory$scheduled_runway_departure
hour(flightHistory$local_time_scheduled_runway_departure) <- 
  hour(flightHistory$local_time_scheduled_runway_departure) - 
  flightHistory$departure_airport_timezone_offset

# Local time actual gate departure
flightHistory$local_time_actual_gate_departure <- flightHistory$actual_gate_departure
hour(flightHistory$local_time_actual_gate_departure) <- 
  hour(flightHistory$local_time_actual_gate_departure) - 
  flightHistory$departure_airport_timezone_offset

# Local time actual runway departure
flightHistory$local_time_actual_runway_departure <- flightHistory$actual_runway_departure
hour(flightHistory$local_time_actual_runway_departure) <- 
  hour(flightHistory$local_time_actual_runway_departure) - 
  flightHistory$departure_airport_timezone_offset

# Local time actual runway arrival
flightHistory$local_time_actual_runway_arrival <- flightHistory$actual_runway_arrival
hour(flightHistory$local_time_actual_runway_arrival) <- 
  hour(flightHistory$local_time_actual_runway_arrival) - 
  flightHistory$arrival_airport_timezone_offset

# Add runway departure delay (actual - scheduled) to flightHistory
# as.interval creates a time interval between the two instants
# int_length returns seconds, divide by 60 for minutes
flightHistory$runway_departure_delay_mins <-
  int_length(as.interval(flightHistory[,"scheduled_runway_departure"],
                         flightHistory[,"actual_runway_departure"]))/60

# Add gate departure delay (actual - scheduled) to flightHistory
flightHistory$gate_departure_delay_mins <-
  int_length(as.interval(flightHistory[,"scheduled_gate_departure"],
                         flightHistory[,"actual_gate_departure"]))/60

# Add runway arrival delay (actual - scheduled) to flightHistory
flightHistory$runway_arrival_delay_mins <-
  int_length(as.interval(flightHistory[,"scheduled_runway_arrival"],
                         flightHistory[,"actual_runway_arrival"]))/60

# Add gate arrival delay (actual - scheduled) to flightHistory
flightHistory$gate_arrival_delay_mins <-
  int_length(as.interval(flightHistory[,"scheduled_gate_arrival"],
                         flightHistory[,"actual_gate_arrival"]))/60

# Add published length of flight to flightHistory
flightHistory$published_flight_length <-
  int_length(as.interval(flightHistory[,"published_departure"],
                         flightHistory[,"published_arrival"]))/60

write.csv(flightHistory, file="flighthistory_full.csv")