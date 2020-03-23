Rove - Scooter rental web app
Synopsis:
Rove is inspired by "Bounce" which is an Indian origin transportation network company, and the only dockless scooter-sharing service in India. 
Here is how Rove works:
What the user sees-
A customer needs to register by providing details such as name, username, address, password, etc. He needs to add enough money to his RoveMoney wallet before booking a ride. 
On the main page the user can book a ride. He needs to select the starting location and the destination location from the two dropdowns. Once selected, he needs to click on "book ride". The distance along with the cost will be displayed to the user. Then he needs to click on "confirm booking" to confirm the ride. A 4-digit OTP will be displayed which the user has to enter on the OTP keypad fixed to the scooter. Once the ride is complete, he needs to click on "finish ride". The cost of the ride will be subtracted from the user's wallet.
What happens in the background-
When the user books a ride, the cost needs to be calculated. Each location is assigned x and y coordinates. Distance is calculated by using the formula for finding distance between two points. This distance is multiplied by the cost per km to get the final cost.
Also, an OTP needs to be generated and sent to the user. Money must be deducted after the completion of the ride.

How its’s built:
Rove is built using Flask: A python microframework. Its database is present in Heroku. The front end is built using Bootstrap 4 and the back end is built using PostgreSQL and Heroku database.
