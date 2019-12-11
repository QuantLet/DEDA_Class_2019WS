library(data.table)
library(lubridate)
library(xts)
library(forecast)
library(ggplot2)
library(rugarch)

## settings ##
Sys.setenv(LANG = "en") # set environment language to English
Sys.setlocale("LC_TIME", "en_US.UTF-8") # set timestamp language to English
## ##

## themes & functions ##
#
ts_theme <- theme(panel.border = element_blank(), panel.background = element_blank(),
                  panel.grid.minor = element_line(colour = "grey90"),
                  panel.grid.major = element_line(colour = "grey90"),
                  axis.text = element_text(size = 14, face = "bold"),
                  axis.title = element_text(size = 24, face = "bold"),
                  strip.text = element_text(size = 14, face = "bold"),
                  plot.title = element_text(size = 24, face = "bold", hjust = .5)
)
#

# https://stackoverflow.com/questions/13343677/converting-internationally-formatted-strings-to-numeric
strip <- function(x){
  z <- gsub("[^0-9,.]", "", x)
  z <- gsub("\\.", "", z)
  gsub(",", ".", z)
}
#
## ##

## read data ##
ma_energy <- fread("m_a_energy.csv", dec = ",")
## ##

## reshape ##
num_cols <- c("Deal Value", "Acquiror Net Sales LTM", "Acquiror EBIT LTM", "Acquiror EBITDA LTM", "Acquiror Pre-tax Income LTM",
              "Acquiror Net Income LTM", "Acquiror Earnings Per Share LTM", "Acquiror Total Assets", "Net Sales LTM",
              "EBIT LTM", "EBITDA LTM", "Pre-tax Income LTM", "Cash and Short Term", "Total Assets", "Short Term Debt",
              "Net Debt", "Total Liabilities", "Total Debt", "Common Equity", "Equity Value at Announcement", 
              "Equity Value at Effective Date", "Acquiror Financial Advisor Credit", "Target Financial Advisor Imputed Fees Per Advisor",
              "Target Legal Advisor Credit", "Deal Value inc. Net Debt of Target")
date_cols <- c("Announcement Date", "Date of Acquiror Financials", "Date of Target Financials", "Effective Date")
ma_energy[, (num_cols) := lapply(.SD, function(x) as.numeric(strip(x))), .SDcols = num_cols]
ma_energy[, (date_cols) := lapply(.SD, function(x) dmy(x)), .SDcols = date_cols]
ma_energy[, year := year(`Announcement Date`)]
ma_energy[, yearmonth := as.yearmon(`Announcement Date`, "%Y %m")]
ma_energy[, quarter := quarter(`Announcement Date`, with_year = TRUE)]
ma_energy[, month := month(`Announcement Date`)]
setkey(ma_energy, `Announcement Date`)
## ##

## get number of m&a per month ##
N_per_month <- ma_energy[`Deal Status` %in% "Completed", .N, by = c("yearmonth")]
N_per_month[, Date := as.Date(yearmonth)]
DT_N <- data.table("Date" = seq(from = as.Date(N_per_month$yearmonth[1]), to = as.Date(N_per_month$yearmonth[nrow(N_per_month)]), by = "1 month"))
DT_N[N_per_month, N := i.N, on = "Date"]
DT_N[is.na(N), N := 0]
DT_N[, Diff_N := c(0, diff(N))] # first differences
setkey(DT_N, Date) # sort by date

N_per_month <- DT_N[Date > as.Date("1996-12-31") & Date < as.Date("2019-01-01")] # subset to only include values after liberalization wave
N_per_month <- N_per_month[complete.cases(N_per_month)] # keep only rows without any NA values
setkey(N_per_month, Date)
N_per_month[, index := 1:nrow(N_per_month)]
## ##

## plotting ##

# time series dataset #
MERGERS_ACQUISITIONS_ENERGY <- xts(N_per_month[Date < as.Date("2020-01-01")]$Diff_N, order.by = as.yearmon(N_per_month[Date < as.Date("2020-01-01")]$Date), frequency = 12)

# plot #
plot(MERGERS_ACQUISITIONS_ENERGY, type = "h")

# autocorrelation #
ggtsdisplay(MERGERS_ACQUISITIONS_ENERGY)

# distribution #
gghistogram(MERGERS_ACQUISITIONS_ENERGY, add.kde = T)

# forecast ARIMA model #
autoplot(mstl((MERGERS_ACQUISITIONS_ENERGY)))
stl <- stl(MERGERS_ACQUISITIONS_ENERGY, s.window = "periodic")
fc_arima <- forecast::forecast(stl, method = "arima", h = 12)
## ##

## fit garch ##

# create timeseries dataset
dataset <- N_per_month$Diff_N # add the desired vector of M&A here
date <- N_per_month$Date # date index

# specify model parameters #
gspec.ru <- ugarchspec(distribution="std") # specifications
garch_fit <- ugarchfit(gspec.ru, dataset) # fit based on gspec.ru

# simulate 
bootp <- ugarchboot(garch_fit, method = c("Partial", "Full")[1], n.ahead = 12, n.bootpred = 500) # make prediction with bootstrapping
garch_sim <- ugarchsim(garch_fit, nsim = 12) # simulate from garch_fit
garch_roll <- ugarchroll(gspec.ru, dataset, forecast.length = 12, refit.every = 2) # rolling  forecast

#DT_fit <- data.table("date" = tail(DT_N$Date, 9), garch_roll@forecast$density[1:9, 1:2])
DT_fit <- data.table("date" = tail(DT_N$Date, 9), "forec" = bootp@forc@forecast$seriesFor[1:9], "sigma" = bootp@forc@forecast$sigmaFor[1:9]) # extract forecasted values
DT_fit[, sigma_down := sigma*(-1)] # create confidence interval
names(DT_fit) <- c("date", "point_forecast", "sigma_up", "sigma_down")

# create datset for plotting
pred <- DT_fit$point_forecast
real <- tail(DT_N$Diff_N, 9)

cmpre <- data.table(value = c(pred, real),
                    date = c(rep(tail(DT_N$Date, 9), 2)),
                    type = c(rep("GARCH", length(pred)), rep("Real", length(real))))

# plot GARCH prediction vs real forecast #

ggplot(data = cmpre[type %in% "Real"], aes(date, value, color="No. of M&A (Real)")) +
  geom_line(size = 0.8) +
  geom_line(data = DT_fit, size = 0.8, aes(y = point_forecast, color="Forecast GARCH")) +
  geom_ribbon(data=DT_fit, aes(x = date, ymin=sigma_up ,ymax=sigma_down), alpha=0.2, inherit.aes = FALSE, fill = "#F8766D") +
  ts_theme +
  coord_cartesian(ylim = c(4,-4)) +
  labs(colour="Legend", x = "Calendar Year", y = "No. of M&A",
       title = "Comparison of Real M&A and GARCH Forecast") +
  theme(legend.position = c(0, 1), legend.justification = c(0, 1)) +
  scale_color_manual(values = c("#F8766D", "#00BFC4"), breaks = c("No. of M&A (Real)", "Forecast GARCH")) +
  scale_x_date(date_breaks = "3 months", date_labels =  "%m %Y") +
  theme(panel.background = element_rect(fill = "transparent"), # bg of the panel
        plot.background = element_rect(fill = "transparent", color = NA), # bg of the plot
        panel.grid.major = element_blank(), # get rid of major grid
        panel.grid.minor = element_blank(), # get rid of minor grid
        legend.background = element_rect(fill = "transparent"), # get rid of legend bg
        legend.box.background = element_rect(fill = "transparent")) # get rid of legend panel bg

# ACF Plot ##
bacf <- acf(real_vs_pois$Real, plot = FALSE)
bacfdf <- with(bacf, data.frame(lag, acf))

# CI # https://stackoverflow.com/questions/42753017/adding-confidence-intervals-to-plotted-acf-in-ggplot2
alpha <- 0.95
conf.lims <- c(-1,1)*qnorm((1 + alpha)/2)/sqrt(bacf$n.used)


ggplot(data = bacfdf, mapping = aes(x = lag, y = acf)) +
  geom_hline(aes(yintercept = 0)) +
  geom_hline(aes(yintercept = conf.lims[1]), linetype = 3, color = 'darkblue') + 
  geom_hline(aes(yintercept = conf.lims[2]), linetype = 3, color = 'darkblue') +
  geom_segment(mapping = aes(xend = lag, yend = 0)) +
  ts_theme +
  theme(panel.background = element_rect(fill = "transparent"), # bg of the panel
        plot.background = element_rect(fill = "transparent", color = NA), # bg of the plot
        panel.grid.major = element_blank(), # get rid of major grid
        panel.grid.minor = element_blank(), # get rid of minor grid
        legend.background = element_rect(fill = "transparent"), # get rid of legend bg
        legend.box.background = element_rect(fill = "transparent")) # get rid of legend panel bg

#tsdisp <- ggtsdisplay(dataset)
# ggsave(ggtsdisplay(dataset), filename = "tr_tst2.png",  bg = "transparent")


##
# plot distribution #
bins <- min(500, grDevices::nclass.FD(na.exclude(MERGERS_ACQUISITIONS_ENERGY)))
binwidth <- (max(MERGERS_ACQUISITIONS_ENERGY, na.rm = TRUE) - min(MERGERS_ACQUISITIONS_ENERGY, na.rm = TRUE))/bins

ggplot(MERGERS_ACQUISITIONS_ENERGY, aes(x=MERGERS_ACQUISITIONS_ENERGY)) +
  xlab("Number of mergers in month") + ylab("Count") +
  ggtitle("Distribution of observed mergers per month") +
  scale_x_continuous() +
  geom_histogram(      # Histogram with density instead of count on y-axis
    binwidth=binwidth,
    colour="skyblue2", fill="skyblue2") +
  ts_theme

ggplot(N_per_month, aes(x=yearmonth,xend=yearmonth,y=0,yend=N)) +
  geom_segment(aes(color="Net Revenue")) +
  ts_theme +
  theme(legend.position = c(0, 1),legend.justification = c(0, 1))+
  scale_color_manual(values = c("#00BFC4"), breaks = c("Net Revenue")) +
  labs(colour="Legend", x = "Calendar Year", y = "Number of M&A", title = "M&A / Month in Energy Sector (Germany)")  +
  theme(panel.background = element_rect(fill = "transparent"), # bg of the panel
        plot.background = element_rect(fill = "transparent", color = NA), # bg of the plot
        panel.grid.major = element_blank(), # get rid of major grid
        panel.grid.minor = element_blank(), # get rid of minor grid
        legend.background = element_rect(fill = "transparent"), # get rid of legend bg
        legend.box.background = element_rect(fill = "transparent"))  + theme(legend.position= "none") # get rid of legend panel bg

#

##
DT_N_subs <- DT_N[Date > as.Date("1996-12-31")]

## plot distribution vs estimated Poisson distribution # 
m_a_pois <- rpois(10^6, mean(DT_N_subs$N))

# some alternative fit as comparison to fitting Poisson distribution based on empirical mean of series #
# set.seed(10^4)
# m_a_pois <- rpois(10^6, 2.3)
# m_a_pois <- m_a_pois -1
# m_a_pois <- m_a_pois[m_a_pois >= 0]

real_vs_pois <- data.table("Date" = DT_N_subs$Date,"Real" = DT_N_subs$N, "Poisson" = sample(m_a_pois, nrow(DT_N_subs)))

ggplot(real_vs_pois, aes(x=Date,xend=Date,y=0,yend=Poisson)) +
  #geom_segment(col = "#00BFC4") + # if yend = Real
  geom_segment(col = "#F8766D") + # if yend = Poisson
  ts_theme +
  coord_cartesian(ylim = c(max(real_vs_pois$Real),0)) +
  theme(legend.position = c(0, 1),legend.justification = c(0, 1))+
  labs(colour="Legend", x = "Calendar Year", y = "Number of M&A", title = "Distribution of M&A / Month in Energy Sector (Germany)")  +
  theme(panel.background = element_rect(fill = "transparent"), # bg of the panel
        plot.background = element_rect(fill = "transparent", color = NA), # bg of the plot
        panel.grid.major = element_blank(), # get rid of major grid
        panel.grid.minor = element_blank(), # get rid of minor grid
        legend.background = element_rect(fill = "transparent"), # get rid of legend bg
        legend.box.background = element_rect(fill = "transparent")) # get rid of legend panel bg

##

DT_N_subs[, Poisson := sample(m_a_pois, nrow(DT_N_subs))]
names(DT_N_subs)[2] <- c("Real")
DT_N_subs[, Real := as.numeric(Real)]
DT_N_subs[, Poisson := as.numeric(Poisson)]

DT_N_plot <- melt(DT_N_subs, id.vars = "Date", measure.vars = c("Poisson", "Real"))

dataset_distr <- DT_N_plot

# bins_distr <- min(500, grDevices::nclass.FD(na.exclude(dataset_distr$Real)))
# binwidth_distr <- (max(dataset_distr, na.rm = TRUE) - min(dataset_distr, na.rm = TRUE))/bins_distr

# histogram
ggplot(DT_N_plot[variable %in% "Real"], aes (x = value, group = variable, col = variable)) +
  #geom_histogram( binwidth = 0.5) + # if use both
  #geom_histogram(col = "#00BFC4", binwidth = 0.5) + # if y = Real
  geom_histogram(data = DT_N_plot[variable %in% "Poisson"], col = "#F8766D", binwidth = 0.) + # if y = Poisson
  ts_theme +
  coord_cartesian(ylim = c(85, 0), xlim = c(8, 0)) + # if y not both
  theme(legend.position = c(0, 1),legend.justification = c(0, 1))+
  labs(colour="Legend", x = "Number of M&A", y = "N", title = "Distribution of M&A / Month in Energy Sector (Germany)")  +
  theme(panel.background = element_rect(fill = "transparent"), # bg of the panel
        plot.background = element_rect(fill = "transparent", color = NA), # bg of the plot
        panel.grid.major = element_blank(), # get rid of major grid
        panel.grid.minor = element_blank(), # get rid of minor grid
        legend.background = element_rect(fill = "transparent"), # get rid of legend bg
        legend.box.background = element_rect(fill = "transparent")) # get rid of legend panel bg

# density
ggplot(DT_N_plot, aes (x = value, group = variable, col = variable)) +
  geom_density(bw = 1) + # if use both
  #geom_histogram(col = "#00BFC4") + # if y = Real
  #geom_histogram(data = DT_N_plot[variable %in% "Poisson"], col = "#F8766D") + # if y = Poisson
  ts_theme +
  theme(legend.position = c(0, 1),legend.justification = c(0, 1))+
  labs(colour="Legend", x = "Calendar Year", y = "Number of M&A", title = "Distribution of M&A / Month in Energy Sector (Germany)")  +
  theme(panel.background = element_rect(fill = "transparent"), # bg of the panel
        plot.background = element_rect(fill = "transparent", color = NA), # bg of the plot
        panel.grid.major = element_blank(), # get rid of major grid
        panel.grid.minor = element_blank(), # get rid of minor grid
        legend.background = element_rect(fill = "transparent"), # get rid of legend bg
        legend.box.background = element_rect(fill = "transparent")) # get rid of legend panel bg

## qqplot ##
x <- DT_N_subs$Real; y <- DT_N_subs$Poisson

sx <- sort(x); sy <- sort(y)
lenx <- length(sx)
leny <- length(sy)
if (leny < lenx)sx <- approx(1L:lenx, sx, n = leny)$y
if (leny > lenx)sy <- approx(1L:leny, sy, n = lenx)$y

DT_qq <- data.table(sx, sy)
DT_qq[,.N, by = sx]
DT_qq[,.N, by = sy]

ggplot() + 
  geom_point(aes(x=sx, y = sy)) +
  ts_theme +
  theme(legend.position = c(0, 1),legend.justification = c(0, 1))+
  labs(colour="Legend", x = "Real", y = "Poisson", title = "QQ-Plot of real vs estimated distribution")  +
  theme(panel.background = element_rect(fill = "transparent"), # bg of the panel
        plot.background = element_rect(fill = "transparent", color = NA), # bg of the plot
        panel.grid.major = element_blank(), # get rid of major grid
        panel.grid.minor = element_blank(), # get rid of minor grid
        legend.background = element_rect(fill = "transparent"), # get rid of legend bg
        legend.box.background = element_rect(fill = "transparent"))  + theme(legend.position= "none")