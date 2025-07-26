# Use the official Golang base image
FROM golang:1.24.3-alpine

# Set necessary environment variables
ENV GO111MODULE=on \
    APP_PORT=8088 \
    APP_MODE=http \
    APP_HOST=0.0.0.0

# Install git and other dependencies
RUN apk update && apk add --no-cache git bash curl

# Set the working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/zerodha/kite-mcp-server . 

# Copy .env file if needed
# You can mount it later using a volume or pass env variables at runtime
COPY .env .env

# Download Go modules
RUN go mod download

# Build the server binary
RUN go build -o kite-mcp-server

# Expose port
EXPOSE ${APP_PORT}

# Run the server
CMD ["./kite-mcp-server"]
