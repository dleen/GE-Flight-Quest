# Remove "unnecessary" columns
# flightHistory <- subset(flightHistory, select = -c(airline_code,
#                                                    flight_number,
#                                                    departure_airport_code,
#                                                    arrival_airport_code,
#                                                    creator_code,
#                                                    scheduled_air_time,
#                                                    scheduled_block_time,
#                                                    scheduled_aircraft_type,
#                                                    actual_aircraft_type,
#                                                    icao_aircraft_type_actual))

library(ggplot2)


flightHistory <- read.csv("flighthistory_full.csv")

# qplot(local_time_scheduled_runway_departure, runway_arrival_delay_mins, data=flightHistory)
# 
late <- flightHistory[flightHistory$gate_arrival_delay_mins > 0,]
#late <- late[late$runway_arrival_delay_mins > 30,]

#late <- late[late$actual_gate_departure > ymd_hms("2012-11-13 00:00:00"),]
# 
# qplot(hour(local_time_actual_runway_departure), 
#       runway_arrival_delay_mins, 
#       data=late, 
#       stat="identity",
#       geom="bar",
#       alpha=0.2)
# 
test <- aggregate(x = list(late$gate_arrival_delay_mins), 
                  by = list(hour(late$local_time_scheduled_gate_departure)), FUN=mean)
# 
names(test) <- c("hour", "mean_delay_mins")
barplot(height=test$mean_delay_mins, names.arg=test$hour)
# 
# test <- test[order(test$mean_delay_mins, decreasing=T),]
# test <- test[1:20,]
# 
# qplot(mean_delay_mins,
#       airline_)
# 
# # test <- 
# #   flightHistory[flightHistory$actual_runway_departure > ymd_hms("2012-11-21 11:00:00"),]
# 
# # plot(test$actual_runway_departure, delayMins)
# # m1 <- glm(delayMins ~ test$actual_runway_departure)
# # abline(m1, col="red")

flightHistory <- subset(flightHistory, select = -c(airline_code,
                                                   departure_airport_code,
                                                   arrival_airport_code,
                                                   creator_code,
                                                   published_departure,
                                                   published_arrival,
                                                   scheduled_air_time,
                                                   scheduled_block_time,
                                                   scheduled_aircraft_type,
                                                   actual_aircraft_type,
                                                   icao_aircraft_type_actual))

dt <- data.table(flightHistory)

dt <- dt[complete.cases(dt)]

dtweek <- dt[,list(length=length(flight_history_id)), 
             by=wday(local_time_actual_gate_departure)]

late <- flightHistory[flightHistory$gate_arrival_delay_mins > 0,]
dtl <- data.table(late)
dtlweek <- dtl[,list(length=length(flight_history_id)), 
               by=wday(local_time_actual_gate_departure)]

lateper <- dtlweek
lateper$length <- 100*lateper$length/dtweek$length
lateper <- lateper[complete.cases(lateper)]
lateper <- lateper[order(lateper$wday)]
barplot(height=lateper$length, names.arg=lateper$wday)


dtairline_icao <- dt[,list(mean=mean(gate_arrival_delay_mins)), by=airline_icao_code]
barplot(height=dtairline_icao$mean, names.arg=dtairline_icao$airline_icao_code)

dttimeofday <- dtl[,list(mean=mean(gate_arrival_delay_mins, na.rm=T),
                        se=sqrt(var(gate_arrival_delay_mins, na.rm=T)/(length(gate_arrival_delay_mins)))), 
                  by=hour(local_time_scheduled_runway_departure)]
dttimeofday <- dttimeofday[complete.cases(dttimeofday)]
dttimeofday <- dttimeofday[order(dttimeofday$hour)]


p <- ggplot(dttimeofday, aes(x=hour, y=mean))
p <- p + geom_bar(stat="identity")
p <- p + geom_errorbar(aes(ymin = mean-se, ymax = mean+se, color="red"))
p