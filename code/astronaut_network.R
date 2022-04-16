# code generates network graph of astronaut pair photographed on ISS.

library(sqldf)
library(RColorBrewer)
library(dplyr)
library(visNetwork)
library(igraph)

setwd("F:\\Projects/ISSAPFaces//data/")

# read pairs data
pairs = read.csv("pairs.txt",encoding = "utf-8",header = FALSE)

# astronauts mapped as nodes in a graph, from and to names and agencies
colnames(pairs) = c('from','to','fromA','toA')

# read astronaut data 
astro_info = read.csv("astronaut-data.csv",encoding = "utf-8")
astro_info = sqldf("SELECT distinct name,agency 
              FROM astro_info") # only store name and agency

# df for all astronauts in the pairs data
astro_names = data.frame(name=unique(c(unique(pairs$to),unique(pairs$from))))

# edges df for network graph
network_edges <- data.frame(Source=pairs$from,
                    Target=pairs$to)

# each astronaut node is color coded based on agency
# for smaller agencies, 'Other' bucket is used.
color_map <- data.frame(Agency = unique(astro_info$agency), stringsAsFactors = F)
color_map <- sqldf("SELECT *, CASE WHEN Agency = '' THEN ''
              WHEN Agency = 'NASA' THEN '#56BBF1'
              WHEN Agency = 'ESA' THEN '#99d594'
              WHEN Agency = 'RSA' THEN '#F68989'
              WHEN Agency = 'JAXA' THEN '#fee08b'
              WHEN Agency = 'CSA' THEN '#fc8d59'
              ELSE '#e6f598' END as color 
              FROM color_map")

# create new df of astronaut name, agency, and agency color
astronauts = sqldf("SELECT a.name id, a.name label,ai.agency,color 
                    FROM astro_names a 
                    INNER JOIN astro_info ai ON a.name = ai.name
                    INNER JOIN color_map c ON ai.agency = c.agency")

# nodes for network are similar to astronauts df
network_nodes = sqldf("SELECT id,label,agency,color from astronauts")

# modify nodes agency labels to put others in 'Other' bin
network_nodes <- sqldf("SELECT id, label,
                        CASE WHEN agency IN ('KAP',
                                            'None',
                                            'AEB',
                                            'KAC',
                                            'ANGKASA') THEN 'Other' 
                        ELSE agency 
                        END AS agency2,color
                        FROM network_nodes")

# choose agency2 as new agency column
network_nodes = sqldf("SELECT id,label,agency2,color 
                       FROM network_nodes")

# convert network edges to unique edges with width as weight
network_edges = sqldf("SELECT Source,Target,COUNT(*) AS width 
                      FROM network_edges 
                      GROUP BY Source,Target")

# rename for visnetwork
colnames(network_edges) <- c("from", "to", "width")
colnames(network_nodes) = c("id", "label","group","color")

# for visualization purposes only
network_nodes$font.size = 30
network_edges$width = (network_edges$width/3)+1
network_nodes$label = ""

# generate network of nodes and edges
# make network selectable
# show legend of agency names color coded as nodes
# use Fruchterman-Reingold force directed graph layout
network = visNetwork(network_nodes, network_edges) %>%
  visIgraphLayout(layout = "layout_with_fr")%>%
  visNodes(size = 25)%>%
  visGroups(groupname = "NASA", color = "#56BBF1") %>%
  visGroups(groupname = "ESA", color = "#99d594") %>%
  visGroups(groupname = "RSA", color = "#F68989") %>%
  visGroups(groupname = "JAXA", color = "#fee08b") %>%
  visGroups(groupname = "CSA", color = "#fc8d59") %>%
  visGroups(groupname = "Other", color = "#e6f598") %>%
  visLegend(useGroups = TRUE)%>%
  visOptions(highlightNearest = list(enabled = T, hover = T), 
             nodesIdSelection = T)

network

# save to directory
visSave(network,file="astronaut_network.html")
