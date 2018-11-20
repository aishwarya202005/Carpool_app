TEAM PRIME
----------

--> All the forms have Validation.

Login 
-->Password Encryption using bcrypt


Registration
--> User id, User name, email id is unique
--> Email Authentication with link
--> Authentication with OTP


Profile
-->Update Profile Details
-->Update Profile Picture
-->View all your rides ( Upcoming and Completed)
-->Can Cancel an Offered Ride
-->Check Ride Request and can Accept or Reject them


Find Ride
-->Search ride for desired Source,Destination,Date
-->Select any ride from offered choices,check the details and Book Ride.
   Notification of request is sent to the Driver.
-->Can view all the details related to searched ride like Source,Destination,Date,Time,No.of Vacant Seats,Car Details.
-->When Driver accepts the request,User is notified via email about Ride Confirmation.
-->User can Search Rides without login but can only book a ride after login.

Offer Ride
-->Only Logged In user can offer a ride
-->One user can offer multiple rides
-->User receives all the requests for offered ride and can Accept or Reject them.


Accept/Reject Ride:
-->When Driver Accept the ride, no of vacant seats is reduced.
   The corresponding User is notified that driver has accepted the request.
-->When Driver Reject a ride, User is notified that driver has rejected the request.
-->If all seats are filled up,User cannot request ride.


Delete Ride
-->User can Cancel offered ride.
   All riders who has requested that ride will be notified via email about ride cancellation.
   All users who has already confirmed that ride will also recieve notification via email about ride cancellation.


