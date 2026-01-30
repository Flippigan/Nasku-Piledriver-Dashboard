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

For each event, I would like to assign variables, and I would like to be able to attatched more variables to each inverter later in case additional conditions that would activate that event arrise. And I would like to have the ability to add more events later in case additional events become neccessary to track. The core functionality would be to have either an external data source or the user change a bianary or continous variable of an event, and based on the variable(s) checked, unchecked, or the continous value, display a "next step". Said next step being the next item in the list.

A core function of the program is to help users visualize what needs to be done NEXT for each inverter in a dashboard format with easy to see colors, red for needs to be done asap, yellow for fast approaching due date, and green for good. So for each variable, a due date should be assigned. Except for the first scan. The first scans status will be determiend by the number of installed piles. That data will be in the format of a Nasku.csv like so; 

name	processedAt	machine	positioningTime	hammeringTime	hammeringStatus	hammeringFlag	resultEasting	resultNorthing	resultAltitude
27117	2026-01-16T13:07:21.722-06:00[America/Chicago]	Doyle-2500-021_-_Machine_4	null	17870	COMPLETED	GOOD	689158.07286	111718.79695	276.68728

For a pile to be considered installed, both the hammering status and the hammering flag need to be COMPLETED and GOOD respectivly. If either of those are not just so, the pile is not installed. A key feature of the dashboard needs to be a status bar that starts out empty, and fills in with green proportional to the number of piles installed, with the bar being full when all piles are installed. The user needs to be able to be alerted when a status bar reaches certain milestone, which are configurable by the user.

Another core feature I'd like to a "Estimated time of completion". Which will be based on the rate piles are being driven at, measured by both hammering time and positioning time combined. I'm envisioning the "rate of piles being installed" being an average, that average should be calulated using the number of piles CURRENTLY installed, devided by the amount of time it took to complete them. So the formula would be (hammeringTime + positioningTime) / (Number of piles installed).

Another core tenant of the app is for version 1, I want to be able to share it as an exe, and I want users to be able to feed it two files, the nasku.csv, and the drivelog.csv The drivelog will contain many columns which are not neccessary, so I want the be able to do no work to the input. Meaning it can ingest a file with many useless columns. The csv below is what header and first row of the drivelog. 

OBJECTID	Inverter	Row	Table_	UPN	Drive_Time_MIN	Drive_Time_SEC	As_Built_Northing	Design_Northing	Top_of_P_in_Northing_Tolerance	As_Built_Easting	Design_Easting	Easting_In_Tolerance	As_Built_Top_Elev	Design_Elevation	Pile_Length	As_Built_Reveal_ft	Design_Min_Reveal_ft	Design_Max_Reveal_ft	Reveal_in_Spec	As_Built_Embed	Design_Min_Embed	Min_Embd_Met	Pile_Twist	Twist_in_Tol	East_deg_Lean	North_Deg_Lean	Remediation_Complete	Remediation_Type	N_Dy	E_Dx	Elv_Dz	GlobalID	CreationDate	Creator	EditDate	Editor	Letter	Color	Damper	Pile_Type	Table_Ready_for_Racking	Symbology	Tracker_Slope_Deg	Cumulative_Slope	Pile_Installed	Elevation_In_Tolerance	East_Deg_Lean_In_Spec	North_Deg_Lean_in_Spec	Remediation_Approved	Pull_Test_Passed	Is_Pull_Test_Needed	Remediation_Performed	Random_Pull_Test	Cumulative_Tracker_Slope_in_Spe	Date_Installed	Date_of_Pull_Test	Date_of_Random_Pull_Test	Date_Remediation_Completed	Date_Remediation_Approved	Display	Drive_Finished_At	Drive_Machine	Hammering_Status	Hammering_Flag	Design_Bottom_of_Pile	Remediation_Reccomendation	Symbology_S02	UFN	Num_Helicals_In_Frame	Helical_Oreintation	Helical_PIle_Position	Frame_Des_Northing	Frame_Des_Easting	Frame_Des_Elv	Helical_or_W_Section	Helical_Clocking	Pile_Size	Pile_Shape
2	1	40	360	41659				374440.4921	N/A		2265509.864			871.9375044	14.5		3.746008848	5.75			8			Yes					4493285.978	27186118.37		{3b9b599f-0319-484d-8057-235dca195ea3}	2025-09-04 21:25:00	HNemerov_westwood	2025-12-17 17:34:36	HNemerov_westwood	B	Dark Blue		Array		0			No																				867.1895													W6x10.4

The purpose of the drivelog is to store information on piles that have been driven already. So What I'm picuturing is, a drivelog is the document that the program should reference, and when the user feeds in a nasku.csv to the program, the program should update the drivelog with the relevant piles. In the drivelog Hammering_Status and Hammering_Flag corraspond with hammeringStatus and hammeringFlag in Nasku.csv

For now this process is manual, depending on a user to feed in csv's. But in the future the Nasku drivelogs should come from a API source. So there needs functionality in the part of the app that ingests the nasku.csv to periodically check a location or endpoint for new data. 

