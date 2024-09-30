Network Intrusion Detection

This project was designed to use the dataset from The Third International Knowledge Discovery and Data Mining Tools Competition to train a machine learning model with the capabilities to distingish between "good" and "bad" connections. Bad connections are classified as any connection that presents a threat of intrusion, mainly from smurf or neptune attacks. Good connections are classified as any connection that does not present a threat to the security of the network. 

To run this project, simply run the NetworkIntrusionDetection.ipynb file alongside the data.csv file. This python notebook will process the data through scaling and encoding categorical features, extract the most important features, and then test its accuracy.
