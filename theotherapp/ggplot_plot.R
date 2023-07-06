#!/usr/bin/env Rscript

library(argparser, quietly=TRUE)
library(ggplot2)
library(tidyr)
library(dplyr)
library(Polychrome)
library(svglite)
library(plotly)
library(RColorBrewer)

# Create a parser
parser <- arg_parser("Test parsing arguments")

# Add command line arguments
parser <- add_argument(parser, "--filename", help="", nargs=Inf)
parser <- add_argument(parser, "--groupcat", help="", nargs=Inf)
parser <- add_argument(parser, "--plottype", help="", nargs=Inf)
parser <- add_argument(parser, "--height", help="", nargs=Inf)
parser <- add_argument(parser, "--width", help="", nargs=Inf)
parser <- add_argument(parser, "--title", help="", nargs=Inf)
parser <- add_argument(parser, "--xlab", help="", nargs=Inf)
parser <- add_argument(parser, "--ylab", help="", nargs=Inf)
parser <- add_argument(parser, "--colorscale", help="", nargs=Inf)
parser <- add_argument(parser, "--interactive", help="", nargs=Inf)
parser <- add_argument(parser, "--pool", help="", nargs=Inf)
# Possible values: "relative", "absolute"
# Determines if percentages or absolute counts
parser <- add_argument(parser, "--abs_rel", help="", nargs=Inf)
parser <- add_argument(parser, "--taxonomic_rank", help="", nargs=Inf)

# Parse the command line arguments
argv <- parse_args(parser)

# Read csv files
print("Reading csv files...")
filenames <- lapply(argv$filename, sprintf, fmt="media/%s.csv")
files <- lapply(filenames, read.csv2)

# Create colormap if there is more than one file TEMPORARY
all_taxa <- c()
for (i in 1:length(files)){
  all_taxa <- append(all_taxa, files[[i]]$taxon)
}
all_taxa <- unique(all_taxa)
colors <- c("#000000", "#67dab8", "#20c997", "#1ba97f", "#168967", "#11694f",
            "#81b4fe", "#61c0cf", "#17a2b8", "#13889b", "#0c5460", "#86cfda",
            "#cff0ff", "#e4ffb0", "#ffcece", "#3485fd", "#9d7ed5", "#6f42c1",
            "#e374ab", "#d63384", "#b42b6f", "#92235a", "#6f1b45", "#608eda",
            "#094bac", "#05285b", "#e25563", "#b92d3a", "#d9290d", "#96242f",
            "#721c24", "#4f1319", "#fd933a", "#d56a11", "#ac560e", "#decd87",
            "#677821", "#84420a", "#593a21", "#febc85", "#e9aab0", "#e77681",
            "#ffd556", "#ffc107", "#d6a206", "#bcd35f", "#696f50", "#445500",
            "#ff6600", "#ad8305", "#8fd19e", "#6dc381", "#4ab563", "#228c3a",
            "#155724", "#afecda", "#80ffe6", "#80ffb3", "#ffe9a6", "#a8cbfe",
            "#c8a9fa", "#f0b6d3", "#4b2d83", "#3a2264", "#590ed5", "#bbff39",
            "#dfffa0", "#fff239", "#c142bf", "#a142c1", "#b912f1", "#e904ff",
            "#882192", "#ab18ff", "#93d12e", "#9fad26", "#ff0000", "#aa0000",
            "#ff00cc", "#ffaaee", "#aa0088", "#d400aa", "#ff0066", "#165044",
            "#bbfff1", "#ff80b2", "#e580ff", "#aa00d4", "#0000ff", "#8787de",
            "#1c1c24", "#373748", "#53536c", "#48373e", "#6c535d", "#ac939d",
            "#c8b7be", "#6f6f91", "#b7b7c8", "#9393ac", "#dbdbe3")
if (length(colors) >= length(all_taxa)) {
  colormap <- data.frame(taxon = all_taxa, color = sample(colors, length(all_taxa)))
} else {
  p <- createPalette(len(all_taxa), "#ffffff")
  colormap <- data.frame(taxon = all_taxa, color = p)
}


MEDIA_DIR <- file.path(getwd(), "media")

print("Creating plots...")

# Do work based on the passed arguments
for (i in 1:length(files)) {

  print("###########DEBUG files:")
  print(files)

  data = files[[i]]
  if ("percentage" %in% colnames(data)) {
    data$percentage <- as.double(data$percentage)
  }

  print("############# DEBUG abs_rel:")
  print(argv$abs_rel[i])

  data_column_name <- 'count'
  if (argv$abs_rel[i] == "relative") {
    data_column_name <- "percentage"
  }

  print("################ DEBUG data_column_name:")
  print(data_column_name)

  print("############# DEBUG taxonomic_rank:")
  taxonomic_rank <- argv$taxonomic_rank[i];
  print(taxonomic_rank)

  pool <- argv$pool[i]
  if (pool == "off"){
    raw_xgroup = "sample_id"
  } else {
    raw_xgroup = argv$groupcat[i]
  }

  print("###############DEBUG raw_xgroup")
  print(raw_xgroup)

  xgroup <- parse(text=raw_xgroup)

  raw_groupby <- argv$groupcat[i]
  print("###############DEBUG raw_groupby")
  print(raw_groupby)

  groupby <- parse(text=raw_groupby)


    blank_theme <- theme_minimal()+
    theme(
      panel.border = element_blank()
    )

  #creating plot base
  if (argv$plottype[i] == 'stacked_bar') {
    plot <- ggplot(data, aes(x = as.factor(eval(xgroup)), y = as.numeric(!!sym(data_column_name)), fill = taxon)) +
      geom_col(width=0.75) +
      facet_grid(.~eval(groupby), scales = "free_x", space = "free_x") +
      theme_minimal() + blank_theme + theme(axis.text.x = element_text(angle=90))
  }


  if (argv$plottype[i] == 'pie'){
    plot <-	ggplot(data, aes(x = as.factor(eval(xgroup)), y = as.numeric(eval(parse(text=data_column_name))), fill = taxon)) +
      geom_bar(stat="identity", width=1) + coord_polar("y", start=0) + blank_theme
  }

  if (argv$plottype[i] == 'heatmap'){
    cols <- colnames(data)[!colnames(data) %in% c('taxon', 'count', 'percentage')]
    data <- data %>% complete(taxon, nesting(data[c(cols)])) %>% mutate(!!sym(data_column_name) := ifelse(is.na(!!sym(data_column_name)), 0, !!sym(data_column_name)))

    plot <-    ggplot(data, aes(x = as.factor(eval(xgroup)), y = as.factor(taxon), fill = as.numeric(eval(parse(text=data_column_name))))) +
      labs(fill = data_column_name) +
      geom_tile() +
      facet_grid(rows = .~eval(parse(text=argv$groupcat[i])), scales = "free_x", space = "free_x", drop = TRUE) +
      theme_dark() + scale_fill_distiller(palette = eval(paste(text = argv$colorscale[i]))) + theme(axis.text.x = element_text(angle=90))
  }

  #setting the colorscale TEMPORARY
  if (argv$plottype[i] != 'heatmap'){
    plot <- plot + scale_fill_manual(values = colormap$color)
  }

  title <- argv$title[i]
  x_lab <- argv$xlab[i]
  y_lab <- argv$ylab[i]

  # SVG sizes are in inches, not pixels
  res <- 96
  height <- as.numeric(argv$height[i])
  width <- as.numeric(argv$width[i])
  #svglite(filename=sprintf("media/%s_plot.svg", argv$filename[i]), height=as.numeric(argv$height[i])/res,
  #                                                                 width=as.numeric(argv$width[i])/res)
  if (argv$interactive[i] == "off"){
    print("Creatic static svg plot...")
    #setting the titles
    plot <- plot + labs(title = title, x = x_lab, y = y_lab)

    new_file_path = file.path(MEDIA_DIR, sprintf("%s_plot.svg", argv$filename[i]))
    print(sprintf("Saving new static svg plot file: %s", new_file_path))

    svg(filename=new_file_path, height=height/res, width=width/res)
    plot(plot)
    dev.off()
  } else {
    print("Creating interactive html plot...")
    p <- ggplotly(plot)
    p$x$layout$title <- title
    p$x$layout$xaxis$title <- x_lab
    p$x$layout$yaxis$title <- y_lab
    # this is a bit hardcodeish, but alas
    p$x$layout$annotations[[1]] <- NA
    p$x$layout$annotations[[2]] <- NA

    #out_json <- plotly:::to_JSON(p)
    #write(out_json, file=sprintf("media/%s_plot.json", argv$filename[i]))

    new_file_path = file.path(MEDIA_DIR, sprintf("%s_plot.html", argv$filename[i])) 
    print(sprintf("Saving new interactive html plot file: %s", new_file_path))
    htmlwidgets::saveWidget(p, file=new_file_path, selfcontained=TRUE)
  }
}
print("Finished.")