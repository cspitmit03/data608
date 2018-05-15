#
# This is the server logic of a Shiny web application. You can run the 
# application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
# 
#    http://shiny.rstudio.com/
#
# File <- "leaned-cdc-mortality-1999-2010-2.csv"
# Files <- list.files(path=file.path("~"),recursive=T,include.dirs=T)
# Path.file <- names(unlist(sapply(Files,grep,pattern=File))[1])
# Dir.wd <- dirname(Path.file)

library(shiny)
library(ggplot2)
library(dplyr)

MyData <- read.csv(file="~/Documents/GitHub/data608/Project3/Interactive/cleaned-cdc-mortality-1999-2010-2.csv", 
                   header=TRUE, sep=",")

# Define server logic required to draw a histogram
shinyServer(function(input, output) {
  
  # Question 1
  selectedData <- reactive({
    subset(MyData[order(MyData$Crude.Rate),], ICD.Chapter == input$disease & Year == input$year) %>% group_by(ICD.Chapter) %>% 
      mutate(Crude.Weighted = weighted.mean(Crude.Rate, Population))   
  })
  
  output$plot1 <- renderPlot({
    barplot(selectedData()$Crude.Rate, main = paste("Crude Rates by State for \n",input$disease), 
            ylab="States (Sorted)", xlab="Rates", col=rainbow(50), names.arg=selectedData()$State,las=2, horiz=TRUE, cex.names=0.5)
    abline(v=weighted.mean(selectedData()$Crude.Rate, selectedData()$Population),lwd=4)
    text(weighted.mean(selectedData()$Crude.Rate*1.05, selectedData()$Population),8,
         labels = paste("National Average",round(weighted.mean(selectedData()$Crude.Rate, selectedData()$Population),2)), srt=90)
  })

  
  # Question 2
  
  selectedData2 <- reactive({
    MyData %>%
      group_by(MyData$ICD.Chapter,MyData$Year) %>% 
      mutate(Crude.Weighted = weighted.mean(Crude.Rate, Population)) %>% 
      subset(State == input$state & ICD.Chapter == input$disease2) %>% arrange(Crude.Rate)
  })
  if(is.null(selectedData2)){
    output$text <- renderText({paste(input$state,"does not have data")})
  }
  else{
    output$plot2 <- renderPlot({
      lines(
        barplot(selectedData2()$Crude.Rate, 
                names.arg=selectedData2()$Year, main=paste("National vs State Rates \n",input$disease2), xlab="Year", ylab="Rates", col=topo.colors(12), 
                ylim=c(0, max(selectedData2()$Crude.Weighted, selectedData2()$Crude.Rate)+5)), 
        y=selectedData2()$Crude.Weighted, type ="o", lwd=2, pch=19,col="orange")
      legend("topright",legend=c("State - BarPlot","National - Line Chart"), text.col=c("blue","orange"), bty="n")
  })  
}
})
