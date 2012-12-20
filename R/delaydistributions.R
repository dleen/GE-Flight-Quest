library(stringr)
library(lubridate)

flightHistory <- read.csv("flighthistory.csv")
flightHistory[flightHistory == "MISSING"] = NA

for(i in 10:19) {
  flightHistory[,i] <- ymd_hms(str_sub(flightHistory[,i], 1, 19))
}

plot(
  density(
    as.duration(
      as.interval(
        flightHistory$scheduled_gate_arrival, flightHistory$actual_gate_arrival)
      )/60, na.rm = TRUE), xlim = c(-60,180))

plot(
  density(
    as.duration(
      as.interval(
        flightHistory$scheduled_runway_arrival, flightHistory$actual_runway_arrival)
    )/60, na.rm = TRUE), xlim = c(-60,180))


#plot(flightHistory$actual_gate_departure,
#     as.duration(
#       as.interval(
#         flightHistory$scheduled_runway_arrival, flightHistory$actual_runway_arrival)
#     )/60/60
#     )

min(flightHistory$actual_gate_departure, na.rm = T)
max(flightHistory$actual_gate_departure, na.rm = T)
