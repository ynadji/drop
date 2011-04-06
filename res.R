study <- "representative"
#study <- "longterm"

if (study == "longterm") {
  games <- c("dnsw","tcpw")
} else {
  games <- c("dns1","dnsw","tcpw","tcp1","tcp2","tcp3")
}

gains <- function(ds, control.colname, var.colname) {
  print(paste(control.colname, var.colname))
  tmp <- subset(ds, ds[control.colname] < ds[var.colname] & ds[var.colname] < 100)
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

istcp <- function(game) {
  return(substr(game, 1, 1) == "t")
}

jaccard <- function(s1, s2) {
  isect <- nrow(merge(s1, s2, all=FALSE))
  uni   <- nrow(merge(s1, s2, all=TRUE))
  print(paste(isect, "/", uni, ": ", isect/uni))
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
    print("Domain values:")
    dput(res$Gains[, 1])
    #print(table(res$Gains))
    print(paste(res$Count, "/", nrow(ds), ":", res$Count/nrow(ds)))

    colname <- paste(game, "ipcount", sep="")
    res <- gains(ds, "noneipcount", colname)
    results <- append(results, res)
    print(paste("noneipcount <", colname))
    print(res$Summary)
    print("IP values:")
    dput(res$Gains[, 1])
    #print(table(res$Gains))
    print(paste(res$Count, "/", nrow(ds), ":", res$Count/nrow(ds)))
  }

  print("Overall:")
  if (study == "representative") {
    overall <- subset(ds, (dns1domaincount > nonedomaincount & dns1domaincount < 100) |
                          (dnswdomaincount > nonedomaincount & dnswdomaincount < 100) |
                          (tcpwipcount > noneipcount & tcpwipcount < 100) |
                          (tcp1ipcount > noneipcount & tcp1ipcount < 100) |
                          (tcp2ipcount > noneipcount & tcp2ipcount < 100) |
                          (tcp3ipcount > noneipcount & tcp3ipcount < 100)
                     )
  } else {
    overall <- subset(ds, (dnswdomaincount > nonedomaincount & dnswdomaincount < 100) |
                          (tcpwipcount > noneipcount & tcpwipcount < 100))
  }
  print(paste(nrow(overall), "/", nrow(ds), ":", nrow(overall)/nrow(ds)))
  print("Overlap:")
  for (g1 in games) {
    if (istcp(g1)) {
      g1gains <- gains(ds, "noneipcount", paste(g1, "domaincount", sep=""))
    }
    else
    {
      g1gains <- gains(ds, "nonedomaincount", paste(g1, "ipcount", sep=""))
    }

    for (g2 in games) {
      #if (istcp(g1) == istcp(g2)) {
        if (istcp(g2)) {
          g2gains <- gains(ds, "noneipcount", paste(g2, "domaincount", sep=""))
        }
        else
        {
          g2gains <- gains(ds, "nonedomaincount", paste(g2, "ipcount", sep=""))
        }

        print(paste(g1, "vs.", g2))
        jaccard(g1gains$Data, g2gains$Data)
      #}
    }
  }

  if (study == "representative") {
    dns1 <- subset(ds, (dns1domaincount > nonedomaincount & dns1domaincount < 100))
    dnsw <- subset(ds, (dnswdomaincount > nonedomaincount & dnswdomaincount < 100))
    tcpw <- subset(ds, (tcpwipcount > noneipcount & tcpwipcount < 100))
    tcp1 <- subset(ds, (tcp1ipcount > noneipcount & tcp1ipcount < 100))
    tcp2 <- subset(ds, (tcp2ipcount > noneipcount & tcp2ipcount < 100))
    tcp3 <- subset(ds, (tcp3ipcount > noneipcount & tcp3ipcount < 100))

    dns <- merge(dns1, dnsw, all=TRUE)
    tcp <- merge(tcpw, merge(tcp1, merge(tcp2, tcp3, all=TRUE), all=TRUE), all=TRUE)

    print("dns vs. tcp")
    jaccard(dns, tcp)
  }
}

options(width=220)
input = commandArgs(trailingOnly = TRUE)[1]
#ds <- read.table(dmatrix_file, header=TRUE, row.names=1, sep='\t')
main(file=input, games=games)
