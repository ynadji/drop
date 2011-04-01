#!/usr/bin/env python
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

dns1 = [1L, 5L, 5L, 1L, 4L, 1L, 1L, 3L, 1L, 3L, 3L, 2L, 10L, 1L, 1L,
        1L, 1L, 1L, 6L, 5L, 5L, 1L, 5L, 4L, 14L, 1L, 1L, 3L, 3L, 1L,
        1L, 1L, 3L, 1L, 1L, 7L, 1L, 1L, 3L, 20L, 1L, 1L, 4L, 1L, 5L,
        1L, 2L, 3L, 1L, 1L, 11L, 5L, 1L, 6L, 1L, 28L, 7L, 1L, 1L, 2L,
        9L, 2L, 3L, 5L, 1L, 2L, 10L, 1L, 5L, 1L, 1L, 5L, 1L, 5L, 1L,
        2L, 5L, 1L, 6L, 1L, 1L, 5L, 5L, 5L, 6L, 1L, 1L, 1L, 3L, 1L, 1L,
        8L, 3L, 1L, 1L, 10L, 1L]
dnsw = [14L, 3L, 14L, 20L, 14L, 10L, 14L, 14L, 3L, 3L, 12L, 2L, 14L,
        34L, 14L, 3L, 4L, 3L, 14L, 14L, 21L, 1L, 10L, 1L, 3L, 1L, 14L,
        1L, 2L, 1L, 14L, 1L, 2L, 3L, 10L, 14L, 1L, 1L, 19L, 2L, 2L, 7L,
        14L, 3L, 1L, 14L, 14L, 1L, 1L, 3L, 1L, 1L, 10L, 18L, 1L, 14L,
        1L, 14L, 1L, 1L, 14L, 2L, 1L, 29L, 6L, 3L, 2L, 1L, 1L, 14L, 4L,
        1L, 2L, 31L, 3L, 14L, 14L, 14L, 3L, 1L, 1L, 14L, 2L, 1L, 1L,
        2L, 18L, 1L, 2L, 1L, 14L, 1L, 3L, 1L, 1L, 4L, 14L, 2L, 14L, 1L,
        14L, 14L, 1L, 1L, 1L, 14L, 7L, 1L, 14L, 1L, 14L, 1L, 2L, 14L,
        1L, 14L, 11L, 14L, 14L, 2L, 8L, 5L, 4L, 2L, 4L, 14L, 4L, 14L,
        6L, 1L, 19L, 3L]
tcpw = [1L, 10L, 1L, 3L, 3L, 3L, 1L, 11L, 9L, 2L, 55L, 3L, 6L, 36L,
        1L, 5L, 33L, 1L, 1L, 1L, 2L, 1L, 1L, 1L, 1L, 13L, 2L, 3L, 6L,
        1L, 1L, 1L, 1L, 1L, 3L, 10L, 41L, 1L, 1L, 1L, 3L, 6L, 2L, 1L,
        9L, 1L, 9L, 15L, 1L, 1L, 3L, 6L, 6L, 9L, 2L, 1L, 7L, 1L, 1L,
        1L, 5L, 1L, 1L, 7L, 45L, 1L, 4L, 8L, 1L, 1L, 28L, 1L, 7L, 11L,
        45L, 3L, 1L, 1L, 1L, 5L, 3L, 7L, 22L, 4L, 1L, 1L, 17L, 1L, 1L,
        1L, 2L, 1L, 4L, 1L, 3L, 27L, 3L, 2L, 1L, 4L, 2L, 1L, 6L, 2L,
        1L, 6L, 7L, 54L, 1L, 1L, 1L, 1L, 1L, 3L, 1L, 1L, 1L, 44L, 1L,
        7L, 18L, 1L, 1L, 51L, 1L, 1L, 2L, 1L, 1L, 1L, 39L, 3L, 2L, 1L,
        7L, 1L, 37L, 1L, 1L, 53L, 1L, 3L, 1L, 23L, 42L, 56L, 27L, 8L,
        3L, 4L, 1L, 6L, 1L, 3L, 5L, 1L, 13L, 1L, 40L, 1L, 1L, 8L, 6L,
        1L, 3L]
tcp1 = [2L, 1L, 1L, 20L, 1L, 3L, 1L, 10L, 3L, 2L, 7L, 1L, 1L, 3L, 1L,
        1L, 34L, 2L, 1L, 1L, 1L, 1L, 1L, 6L, 1L, 1L, 1L, 2L, 1L, 10L,
        1L, 3L, 2L, 1L, 21L, 5L, 1L, 1L, 3L, 10L, 1L, 1L, 9L, 1L, 10L,
        1L, 1L, 3L, 1L, 1L, 2L, 1L, 10L, 1L, 1L, 3L, 1L, 10L, 2L, 1L,
        1L, 18L, 7L, 6L, 1L, 1L, 7L, 10L, 1L, 1L, 1L, 1L, 16L, 3L, 1L,
        3L, 16L, 3L, 1L, 1L, 1L, 1L, 1L, 1L, 31L, 3L, 1L, 1L, 2L, 1L,
        6L, 1L, 1L, 7L, 3L, 1L, 10L, 3L, 1L, 6L, 1L, 4L, 3L, 2L, 1L,
        1L, 44L, 1L, 1L, 1L, 1L, 1L, 3L, 1L, 1L, 54L, 1L, 3L, 1L, 1L,
        1L, 1L, 3L, 1L, 14L, 1L, 1L, 2L, 1L, 11L, 3L, 1L, 11L, 1L, 10L,
        1L, 2L, 1L, 1L]
tcp2 = [1L, 1L, 25L, 1L, 1L, 2L, 9L, 2L, 14L, 1L, 1L, 1L, 9L, 1L, 36L,
        14L, 1L, 2L, 1L, 1L, 7L, 1L, 1L, 3L, 1L, 1L, 1L, 20L, 1L, 1L,
        1L, 1L, 1L, 9L, 1L, 1L, 1L, 10L, 1L, 1L, 2L, 10L, 1L, 9L, 1L,
        1L, 1L, 1L, 1L, 1L, 1L, 6L, 3L, 11L, 3L, 4L, 1L, 14L, 1L, 2L,
        1L, 3L, 1L, 2L, 1L, 25L, 3L, 1L, 1L, 1L, 2L, 2L, 1L, 10L, 14L,
        2L, 1L, 1L, 7L, 14L, 1L, 1L, 2L, 1L, 6L, 1L, 1L, 1L, 1L, 1L,
        1L, 2L, 14L, 4L, 2L, 1L, 1L, 1L, 2L, 1L, 1L, 3L, 1L, 1L, 10L,
        1L, 1L, 1L, 27L, 2L, 4L, 1L, 1L, 1L, 3L, 1L, 14L, 1L]
tcp3 = [1L, 1L, 41L, 1L, 3L, 2L, 1L, 1L, 3L, 38L, 1L, 1L, 9L, 36L,
        1L, 1L, 1L, 2L, 1L, 1L, 1L, 2L, 1L, 1L, 2L, 1L, 3L, 45L, 1L,
        1L, 3L, 3L, 1L, 9L, 1L, 10L, 1L, 2L, 10L, 1L, 1L, 9L, 1L, 28L,
        1L, 3L, 1L, 1L, 24L, 1L, 6L, 1L, 14L, 3L, 10L, 3L, 21L, 1L, 20L,
        1L, 4L, 3L, 24L, 2L, 1L, 1L, 1L, 1L, 26L, 3L, 1L, 2L, 1L, 6L,
        3L, 1L, 7L, 2L, 1L, 1L, 1L, 2L, 24L, 1L, 1L, 2L, 5L, 1L, 1L,
        6L, 1L, 1L, 1L, 1L, 1L, 2L, 1L, 1L, 2L, 23L, 3L, 1L, 10L, 1L,
        1L, 4L, 1L, 27L, 1L, 1L, 1L, 1L, 10L, 1L, 10L, 1L, 1L, 1L]

# Thank you color brewer (http://colorbrewer2.org/)
dnscolors = ['#1B9E77', '#D95F02']
dnsgames = [dns1, dnsw]
dnsnames = ['$G_{\mathrm{dns1}}$', '$G_{\mathrm{dnsw}}$']

tcpcolors = ['#7570B3', '#E7298A', '#66A61E', '#E6AB02']
tcpgames = [tcpw, tcp1, tcp2, tcp3]
tcpnames = ['$G_{\mathrm{tcpw}}$', '$G_{\mathrm{tcp1}}$', '$G_{\mathrm{tcp2}}$', '$G_{\mathrm{tcp3}}$']

plt.subplot(211)
for game, color, name in zip(tcpgames, tcpcolors, tcpnames):
    n, bins, patches = plt.hist(game, len(game), facecolor=color, alpha=0.75, range=(1, 60), label=name)
#n, bins, patches = plt.hist(tcpgames, len(max(tcpgames, key=len)), color=tcpcolors, range=(1, 60), label=tcpnames)
# Not sure why the commented-out line above doesn't work. It's treating the list of colors as a single
# color value, rather than the color for each entry.

plt.grid(True)
plt.ylabel('Frequency of samples')
plt.xlabel('(a) Raw increase in IP addresses')
plt.legend()

plt.subplot(212)
for game, color, name in zip(dnsgames, dnscolors, dnsnames):
    n, bins, patches = plt.hist(game, len(game), facecolor=color, alpha=0.75, range=(1, 60), label=name)

plt.grid(True)
plt.ylabel('Frequency of samples')
plt.xlabel('(b) Raw increase in domain names')
plt.legend()

plt.show()
