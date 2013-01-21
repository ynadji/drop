library(e1071)

partition.ds <- function(ds, ratio=0.9) {
  ntrain <- round(nrow(ds) * ratio)
  tindex <- sample(nrow(ds), ntrain)
  return(list(trainset=ds[tindex,], testset=ds[-tindex,]))
}

ds <- read.csv(file="20vms/all.labeled.features", sep="\t", header=FALSE, row.names=1)
colnames(ds) <- c("d1", "d2", "d3", "i1", "i2", "i3", "classlabel")

# SVM tuning
tuned <- tune.svm(classlabel~., data=ds, gamma = 10^(-6:-1), cost = 10^(-1:1))
summary(tuned) # gamma: 0.1, cost: 1

# Crossvalidation
cv <- svm(classlabel~., data=ds, cross=10, gamma=0.1, cost=1)
summary(cv)
# Results:
# Number of Support Vectors:  73
#
# ( 22 2 8 15 20 6 )
#
# Number of Classes:  6 
# 10-fold cross-validation on training data:
# Total Accuracy: 96.4467 
# Single Accuracies:
#  94.91525 96.61017 93.22034 98.30508 96.61017 94.91525 100 98.30508 96.61017 95 

# Confusion matrix
table(cv$fitted, ds$classlabel)
