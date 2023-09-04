# Path_Validation
A Python program for transit On-Board Survey path validation purpose

Who can use this tool? If you have an on-board survey database, this tool can perform automatic checks on OBAD (origin-boarding-alighting-destination) locations in conjunction with the reported transfer route sequence to make sure that the records show valid travel paths.  
What does this tool do? The tool developed in ArcGIS performs automatic checks for path validation and outputs maps for records that do not pass the automatic checks (rules described below). The key inputs for the tool are the raw survey data file with certain format and the transit route GIS shape file for the study area. The tool was developed with Python (a script language for ArcGIS). For Sunrise Boulevard project with 1,260 survey data records, it took roughly half hour for the tool to identify the problematic survey records and export the corresponding maps. The tool provides two key outputs for the data analysts (1) A table showing number of records based on their transfer pattern (see Table 2), and (2) Maps showing riders’ trip activities for all records that do not pass the automatic checks. 

Sunrise Blvd Route 36 OD interview survey included 1,260 raw survey records. Majority of the riders (95%) walk to/from their first/last bus. Table 1 shows the number of survey records by access/egress modes. 
Table 1: Number of Raw OD Survey Records by Access Mode and Egress Mode
	Egress
Access	Walk	Bike	KNR	Others	Total
Walk	1,197	1	9	6	1,213
Bike	1	15	-	-	16
KNR	23	-	1	-	24
Others	6	-	-	1	7
Total	1,227	16	10	7	1,260

The survey records were classified into one of the following ten patterns depending on the reported transfer activity. All records that included a non-walk access or egress mode were grouped in a separate category (#10). The validation tool performs automatic checks on records that were classified into categories 1-5 and 8. The automatic tests are defined below. The records that do not pass the automatic checks are flagged and the program outputs maps showing the details of the riders’ activities similar to shown in Figure 1. The records falling in categories 6-7 or 9-10 (5% of the total records) were manually checked for reasonableness using the maps created by the program. 

Table 2: Number of OD Survey Records by Transfer Pattern 
Transfer Pattern #	Number of Records	Automatic Verification?
1- No transfer	823	Yes
2- One bus transfer at access end	142	Yes
3- One bus transfer at egress end	157	Yes
4- Two transfers at the access end and no transfer at the egress end	32	Yes
5- Two transfers at the egress end and no transfer at the access end	28	Yes
6- Two transfers at the access end and one transfer at the egress end	1	No
7- Two transfers at the egress end and one transfer at the access end	0	No
8- One transfer at both access and egress end	13	Yes
9-Two transfers at both access and egress end	1	No
10-At least one end of the trip involves non-walk access/egress mode	63	No
Total	1,260	--

 
Figure 1: Example of a Map Created by the Tool if the Record does not Pass Automatic Test
 
The map shows OBAD locations, transfer routes (colored routes) and access/egress modes
Figure 2: Exhibit Showing Nomenclatures Mentioned in Table 3




 
Table 3: Definition of valid records for different transfer patterns
Transfer Pattern #	Automatic Validation Test(s) Performed by the Tool
1- No transfer	•	If BA distance is more than 0.25 mile; AND
•	If OB distance is less than 0.25 mile; AND
•	If AD distance is less than 0.25 mile.
2- One bus transfer at access end	•	If the transfer route, F1, is within 0.25 mile buffer around the boarding stop; AND
•	If the transfer route is within 0.25 mile buffer around the origin location. 
3- One bus transfer at egress end	•	If the transfer route is within 0.25 mile buffer around the alighting stop; AND
•	If the transfer route is within 0.25 mile buffer around the destination location. 
4- Two transfers at the access end and no transfer at the egress end	•	If the transfer route, F1, is within 0.25 mile buffer around the boarding stop; AND
•	If F1 and F2 are within 0.25 mile buffer; AND
•	If the second transfer route (F2) is within 0.25 mile buffer around the origin location. 
5- Two transfers at the egress end and no transfer at the access end	•	If the transfer route, T1, is within 0.25 mile buffer around the alighting stop; AND
•	If T1 and T2 are within 0.25 mile buffer; AND
•	If the second transfer route (T2) is within 0.25 mile buffer around the destination location. 
6- Two transfers at the access end and one transfer at the egress end Manually checked in Route 36 instance	•	If the transfer route, F1, is within 0.25 mile buffer around the boarding stop; AND
•	If F1 and F2 are within 0.25 mile buffer; AND
•	If the second transfer route (F2) is within 0.25 mile buffer around the origin location; AND 
•	If the transfer route is within 0.25 mile buffer around the alighting stop; AND
•	If the transfer route is within 0.25 mile buffer around the destination location.
7- Two transfers at the egress end and one transfer at the access end Manually checked in Route 36 instance 	•	If the transfer route, T1, is within 0.25 mile buffer around the alighting stop; AND
•	If T1 and T2 are within 0.25 mile buffer; AND
•	If the second transfer route (T2) is within 0.25 mile buffer around the destination location; AND 
•	If the transfer route is within 0.25 mile buffer around the alighting stop; AND
•	If the transfer route is within 0.25 mile buffer around the destination location. 
8- One transfer at both access and egress end	•	If the transfer route, F1, is within 0.25 mile buffer around the boarding stop; AND
•	If the transfer route is within 0.25 mile buffer around the origin location ; AND
•	If the transfer route, T1, is within 0.25 mile buffer around the boarding stop; AND
•	If the transfer route is within 0.25 mile buffer around the destination location. 
9-Two transfers at both access and egress end 	•	Manually Checked
10-At least one end of the trip involves non-walk access/egress mode(s)	•	Manually Checked


