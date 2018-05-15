#
# This is the user-interface definition of a Shiny web application. You can
# run the application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
# 
#    http://shiny.rstudio.com/
#
#setwd("~/Documents/GitHub/data608/Project3/Interactive")
library(shiny)
library(ggplot2)

# Define UI for application that plots Question 1 and Question 2



navbarPage(
  "Infectuous Diseses Dashboard",
  tabPanel(
    "Question 1",
    sidebarPanel(
            selectInput('disease', 'Select Cause', as.character(unique(MyData$ICD.Chapter))),
            selectInput('year', 'Select Year', as.character(unique(MyData$Year)),selected=2010)
          ),
        mainPanel(
          #Setting the multiplot size as 800x600 for better visibility
          plotOutput('plot1',width = 800, height = 600)
        )
    ),
  tabPanel(
    "Question 2",
    sidebarPanel(
      selectInput('disease2', 'Select Cause', as.character(unique(MyData$ICD.Chapter))),
      selectInput('state', 'Select State', as.character(unique(MyData$State)),selected="CA")
    ),
    mainPanel(
      if(is.null(plotOutput('plot2',width = 800, height = 600))){
        textOutput(text)
      }
      else{
        #Setting the multiplot size as 800x600 for better visibility
        plotOutput('plot2',width = 800, height = 600)        
      }
    )
  ),
  #tags$footer("Created by Cesar Espitia 3/11/2018 for Data 608 Spring 2018"))
  tags$footer(HTML(paste("", tags$span(style="color:red", "Project 3 created by Cesar Espitia 3/11/2018 for Data 608 Spring 2018"), sep = "")))
)
