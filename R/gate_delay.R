gd <- read.csv("average_gate_delay_by_arrival_airport_and_airline.csv")

spec <- gd[gd$arrival_airport_icao_code == "KAUS",]

hist(spec$gate_delay_seconds, breaks=5)
