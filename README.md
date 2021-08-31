When run etl.py the app will generate 2 csv files with current date in the name.  
It is running in loop so when new files are added it will generate reports automatically.  

If there is no mapping file it will generate reports for all domains.  
If there is no data files it will do nothing.

# Problem  
As a company we would need to identify how many players were acquired (converted) in a month and how their activity as well as revenues are retained during the course of their lifetime with a gaming operator we sent traffic to.  

# Solution  
A set of two cohort reports based on sales data which show:  

* Count of First Time Depositing players per month and how many are retained the following months.  

* Amount of Net Revenue of first time depositing players per month and how much of that value is retained the following months of their lifetime.  

Both with the capability to filter for the domain (“DomainID”) to be able to monitor the performance per website.   

# Task  
Create a data model, set up data transformations to generate the two cohort reports from the provided sample data, considering automated updates if new, monthly sales data was made available.  

# Source Data Scope  

* Monthly Customer Revenue Files (how much revenue was generated per customer per month)   

* Monthly Customer Deposits Files (how much funds were deposited per customer per month)   

* Marketing Source Files (to map “DomainID” against revenue, deposits files to identify where the customer came from)   

Let’s also assume that all the monthly reports available cover the all-time performance of this company and its customers.  

# Source Data Naming Convention
Each file will be named consistently such as   

“b_2018-06c_CustomerDeposits”  

Whereas the “b_” tag provides the reporting month and the “c_tag” the name of the report.  
