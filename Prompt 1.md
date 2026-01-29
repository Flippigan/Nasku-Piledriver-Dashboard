You are a senior software engineer with a specilization in dashboards and OOP. I am in the planning phase of a dashboard, where I want to think very hard about the objects that will be in my dashboard. 

This dashboards goal is to provide VDC engineers aiding in the construciton of a solar site with a easy to understand view of the status of the project. The site is organized into zones called inverters, and each inverter contains  between 1000 - 2000 piles. The role of a VDC engineer is to wait for an inverter's piles to be installed, and then perform a scan of that inverter using a laser scanner. 

The following is the flow of events that I want help displaying when they become relevant after all previous events have been concluded. INVERTER 1 is one of 35, or any number of them for furure projects. The number needs to be adjustable by the user.

INVERTER 1
- [ ] First Scan
- [ ] Processed
- [ ] Points Picked
- [ ] Pushed to ArcGIS
- [ ] Remediation Performed
- [ ] Second Scan Complete
- [ ] Processed
- [ ] Points Picked
- [ ] Pushed to ArcGIS
- [ ] Second Remediation Performed
- [ ] Walk Down

For each event, I would like to assign variables, and I would like to be able to attatched more variables to each inverter later in case additional conditions arrise. The core functionality would be to have either an external data source or the user change a bianary or continous variable, and based on the variables, display a "next step". Said next step typically being the next item in the list.

A core function of the program happens before the first scan. The first scan should be triggered by all piles in an inverter being "driven" into the ground (completed). 
The way 