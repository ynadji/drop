#options(width=220)
#dmatrix_file = commandArgs(trailingOnly = TRUE)[1]
#ds <- read.table(dmatrix_file, header=TRUE, row.names=1, sep='\t')
#print(summary(ds))

games <- c("dns","dnsnever")
#games <- c("dns1","dnsw","tcpw","tcp1","tcp2","tcp3")

gains <- function(ds, control.colname, var.colname) {
  tmp <- subset(ds, ds[control.colname] < ds[var.colname])
  list(
      Summary=summary(tmp[var.colname] - tmp[control.colname]),
      Count=nrow(tmp),
      Gains=tmp[var.colname] - tmp[control.colname],
      Data=tmp
      )
}

losses <- function(ds, control.colname, var.colname) {
  tmp <- subset(ds, ds[control.colname] > ds[var.colname])
  list(
    Summary=summary(abs(tmp[var.colname] - tmp[control.colname])),
    Count=nrow(tmp),
    Data=tmp
    )
}

main <- function(file, games) {
  results <- c()
  # as.is=TRUE reads in strings as strings (instead of factors). we need this
  # so we can split on ',' to get and idea of the new domains we saw.
  ds <- read.table(file, header=TRUE, row.names=1, sep='\t', as.is=TRUE)
  for(game in games) {
    colname <- paste(game, "domaincount", sep="")
    res <- gains(ds, "nonedomaincount", colname)
    results <- append(results, res)
    print(paste("nonedomaincount <", colname))
    print(res$Summary)
    print(table(res$Gains))
    print(paste(res$Count, "/", nrow(ds)))

    colname <- paste(game, "ipcount", sep="")
    res <- gains(ds, "noneipcount", colname)
    results <- append(results, res)
    print(paste("noneipcount <", colname))
    print(res$Summary)
    print(table(res$Gains))
    print(paste(res$Count, "/", nrow(ds)))
  }
}
