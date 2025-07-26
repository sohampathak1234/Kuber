# Use the official Go image as the base image
FROM golang:1.23-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the entire project into the container
COPY . .

# Install dependencies
RUN go mod tidy

# Build the Go application
RUN go build -o fi-mcp-dev main.go

# Expose the port the server will run on
EXPOSE 8080

# Set environment variable for the port (as per the repository instructions)
ENV FI_MCP_PORT=8080

# Command to run the server
CMD ["./fi-mcp-dev"]