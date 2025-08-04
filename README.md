# palmetto automated transfer
Automation for data transfer to palmetto cluster

Designed to handle larges amount of biofilm oct scan data. maintains a transfers and deletes local data after a transfer if completed.


Globus refresh is the main code base update paths and provide globus ID to enable transfer and folder monitoring loop.



The script watches a designated folder and when new sensor data is generated it will transfer it via globus and remove local data after the transfer is complete
