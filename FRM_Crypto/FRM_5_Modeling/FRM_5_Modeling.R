# install.packages("quantreg")
setwd("~/HU/WiSe1920/Digital Economy and Data Analysis/project")

library(quantreg)

source("FRM_qrL1.r")
# https://github.com/QuantLet/FRM/blob/master/FRM_lambda_series/FRM_qrL1.r


source("quantilelasso.r")
# https://github.com/QuantLet/FRM/blob/master/FRM_lambda_series/quantilelasso.r


# variables


# read the data
data <- read.csv(file = '1718hourlyReturn_withZEC.csv')
macro <- read.csv(file = 'macro1718.csv')


# generate a data matrix with standardized return
xx0 <- data[,-1]
xx0 <- scale(xx0) 


# generate a data matrix with standardized macroeconomic variables
m <- macro[,-1]
m <- scale(m)




# start the linear quantile lasso estimation for each coins


for (k in 1:ncol(xx0)) {
  
  
  cat("Coin:", k, "\n")
  
  
  # log return of firm k
  
  
  y              = as.matrix(xx0[, k])
  
  
  # log returns of firms except firm k
  
  
  xx1            = as.matrix(xx0[, -k]) 
  
  
  # number of rows of log return
  
  
  n              = nrow(xx1)
  
  
  # number of covariates
  
  
  p              = ncol(xx1) + ncol(m)
  
  
  # quantile level
  
  
  tau            = 0.05
  
  
  # window size
  
  
  ws             = 48 
  # also try the ws = 24 and compare
  
  
  
  # lambda calculated from linear quantile lasso
  
  
  lambda_l       = matrix(0, (n - ws), 1)
  beta_l       = matrix(0, (n - ws), p)
  
  
  # start the moving window estimation
  
  
  for (i in 1:(n - ws)) {
    
    
    cat("time:",i,"\n")
    
    
    yw  = y[i:(i + ws)]
    
    
    mw  = m[i:(i + ws), ]
    
    
    xx          = xx1[i:(i + ws), ]
    
    
    # all the independent variables
    
    
    xxw         = cbind(xx, mw)
    
    
    fit         = linear(yw, xxw, tau, i, k)
    
    
    lambda_l[i] = fit$lambda.in
    
    beta_l[i,] = fit$beta.in
    
    cat("lambda:",lambda_l[i],"\n")
    cat("beta:",beta_l[i,],"\n")
    
    
  }
  
  
  write.csv(lambda_l, file = paste("lambda_l_", k, ".csv", sep = ""))
  write.csv(beta_l, file = paste("beta_l_", k, ".csv", sep = ""))
  
} 





# calculate the average of 12 lambda series

full.lambda = matrix(0, nrow(xx0)-ws, ncol(xx0))


for (j in (1:ncol(xx0))) {
  
  
  lambda.firm      = read.csv(file = paste("lambda_l_", j, ".csv", sep = ""))
  
  
  full.lambda[, j] = as.matrix(lambda.firm)[, 2]
  
  
}



# FRM based on 12 coins


average_lambda = 1/ncol(xx0) * (rowSums(full.lambda))
date = data$time[(ws+1):length(data$time)]

lambdas = data.frame('time' = date, 'FRM' = average_lambda)
write.csv(lambdas, 'lambdas.csv')



# plot the FRM Crypto

xtick = match(c("12/1/2017 12:00", "1/1/2018 12:00",
                "2/1/2018 12:00", "3/1/2018 12:00", "4/1/2018 12:00"),
              data$time) - ws
plot(average_lambda, type = 'l', xaxt = 'n', xlab = ' ', ylab = 'FRM_crypto')
axis(side = 1, at = xtick, labels = c('2017 Dec', '2018 Jan',
                                      '2018 Feb', '2018 Mar', '2018 Apr'), las = 2)
legend('topright', legend='FRM', col='black',
       lty=1, cex=0.8)
