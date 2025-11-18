from flask import Flask, jsonify # Import Flask and jsonify for creating the web application and returning JSON responses

# Initialize the Flask application 
# Creates the web application instance
app=Flask(__name__) 

#Root endpoint: returns a welcome message. 
@app.route('/', methods=['GET']) # Deffines an http endpoint, when a client sends a GET request to the root URL ('/'), the home function is executed. 
def home(): # retruns a json response with status 200 
    return jsonify({'message': 'Welcome to Ivos SRE Flask App!'}), 200

# Health check endpoint: returns the health status of the application. - Later used by k8s and monitoring 
@app.route('/health', methods=['GET']) # Healthcheck endpoint - Kubernetes can use this later to see if the app is still alive. 
def health():
    return jsonify({'status': 'ok'}), 200

#Only used when running this script directly on apyton app.py
if __name__ == '__main__':
    # Makes is accesible from outside the container 
    app.run(host="0.0.0.0", port=5001, debug=True)  
            

