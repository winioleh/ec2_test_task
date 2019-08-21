# Start the application:
- Build Docker image using **docker build -t ec2_pyramid:latest .**
- Run docker container from terminal **docker run -e AWS_ACCESS_KEY_ID=YOUR_ID -e AWS_SECRET_ACCESS_KEY=YOUR_KEY -dp 6543:6543 ec2_pyramid**
- Open 0.0.0.0:6543 in your web browser
