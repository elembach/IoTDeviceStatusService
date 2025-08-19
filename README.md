
This project is a Flask-based backend service that works to store and serve data to the specified internal systems.

Setup Instructions:
1. Unzip the project folder and open it in your preferred IDE
2. Create/activate a virtual environment using:\
On Mac:\
bash\
python3 -m venv .venv source .venv/bin/activate\     
On Windows:\
.venv\Scripts\activate
3. Install the required packages through:\
pip install -r requirements.txt


How to Run:\
Not using Docker:
1. After activating the virtual environment, either use run.py within the chosen IDE or in terminal:\
    flask run
2. The API is available at http://127.0.0.1:5000 with Authorization key:\
supertopsecretkey!
3. In order to test, either run testing.py or \
bash\
pytest

Using Docker:
1. Make sure Docker Desktop is downloaded(can be found at https://www.docker.com/products/docker-desktop/)
2. Verify installation with:\
docker --version
3. Run app with:\
docker compose up --build 
4. The app should be available at http://localhost:5001 and can be viewed through Docker Desktop


Design Decisions:
Architecture:\
I used Flask App development because that is the method I have the most experience with, and thus feel the most comfortable
with. Furthermore, it is quite lightweight and easy to use. This makes it a good fit for a simple API. I was also able to learn
about and utilize Blueprints, which helped modularize the code and make it cleaner.\
I utilized SQLite because, like Flask, I feel quite comfortable with it. Given the scale of this project, I deemed it a good fit,
and it was easy to set up since it is file-based.

Security and Validation:\
I used marshmallow as a tool to assist with validation. As I originally attempted to hard-code validation, I did some
research to find a cleaner and more effective validation and sterilization tool. Marshmallow specifically helped monitor the
schema of the data when being taken in as a JSON payload.
I used an API Key as a way to elevate the security of this project and provide a user authentication element. This key 
prevents unauthorized requests and helps control the internal services.

Testing:\
I utilized pytest in order to perform testing functionality as it is a clean way to test when developing with Python.
It makes the code easier and repeatable at times. I also researched an implemented fixtures as a way isolate and utilize a test database.


Routing:\
Upon the addition of the bonus task to "Track historical status updates per device (instead of just the last one)", I had to adjust
some routing functionality and database set up. I have several of these changes documented within comments, but key changes include 
a PRIMARY KEY change within database.py, a change of INSERT into the post_status route, and the addition of a get_status_history functionality.

How Testing and Validation Could be Integrated into CI/CD:\
In order to integrate the testing and validation into a CI pipeline, you could define a CI workflow that
is able to run the testing suite every time that code is pushed into a repo, opened as a pull request, or merged into a mian branch.
In CD deployment, you would only want to deploy the service once testing is through and complete. Further integration testing would be needed.

Sources:
https://www.geeksforgeeks.org/python/flask-blueprints/
https://auth0.com/blog/developing-restful-apis-with-python-and-flask/
https://www.geeksforgeeks.org/python/python-build-a-rest-api-using-flask/
https://www.youtube.com/watch?app=desktop&v=7dgQRVqF1N0&t=1558s
https://www.youtube.com/watch?v=Y5CA79rHEYQ