Documentaion For GC Leaderboard API
1>
""" For Adding A New GC """
data must Sent in the form 

{
    "name": " ",
    "type": null
}

where name is the name of the GC Being Added(e.g - Running) 
and type is int keys from {1 : "Tech" , 2 : "Sports ", 3 : "Cult"}

to the URL : /gcleaderboard/postGC

""" For Updating Points Of A Hostel in A Particular GC """

Data must be sent in the form 
{
    "points": null
}

int points that have to be added or subtracted from points of that GC 
should be sent using this api.


on the URL : /gcleaderboard/updateGC/<pk>/
where <pk> is the uuid of the corresponding row in the GC_Hostel_Points