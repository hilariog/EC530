run npm install on all the dependencies that get imported.
In one terminal run 'node server.js', and in another go to A1/client and run 'npm start'

This will create the React app on your local host on port 3000. navigate to (http://localhost:3000/)[http://localhost:3000/] to see it if it doesn't open automatically.

The interface allows you to upload a csv file and to populate your arrays how you like. Either by providing a column index for the csv or by manually entering the arrays. 

The program works with latitude and longitude coordinates and uses +/- instead of E/W, it will ignore csv cells that have non numeric characters in it.
