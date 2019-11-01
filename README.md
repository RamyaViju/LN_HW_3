##     Linux Networking HW-3 Question 1 
###    Team 9:  Ramya Vijayakumar (rvijaya4) , Prashanth Mallyampatti (pmallya)


Question 1 has 2 parts and each of these parts have been implemeted as separate python scripts.

## **1) q1.py :**  
	A script that:
		a. lists all MAC addresses and IP addresses of the all interfaces of running VMs
		b. resolves all IP and MAC conﬂicts and update the conﬁguration of each VM
			
## **Execution:**		
      python q1.py

## **Sample Execution:**

```
root@t11_vm8:~/HW_3# python q1.py
Domain: VM6
MAC: 52:54:00:0a:a4:33


Domain: VM7
MAC: 52:54:00:10:fc:d5


Domain: AnsibleVM1
MAC: 52:54:00:8a:43:1e
MAC: 52:54:00:a4:91:10


Domain: VM5
MAC: 52:54:00:67:0b:2b


Domain: AnsibleVM2
MAC: 52:54:00:02:ce:91
MAC: 52:54:00:51:eb:8e


There are no conflicting MAC and IP addresses
root@t11_vm8:~/HW_3#
```



## **1) mul_hyp.py :**  
	A script that:
		a. Takes a list of hypervisors as input
		b. Indentify duplicate MAC and IP addresses of all running VMs
			
## **Execution:**		
      python mul_hyp.py
      
## **Execution notes:**
The code takes a list of hypervisors as input and also the respective username and password to do an ssh later in the code.
This was not succesfully tested as we were unable to get a hypervisor with correct username and password values. The code reuses the logic of q1.py as this is just an extension of it.

