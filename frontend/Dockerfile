FROM nginx:alpine

# Step 2: Delete default config and copy our site
RUN rm -rf /usr/share/nginx/html/*
COPY . /usr/share/nginx/html

# Step 3: Expose the port
EXPOSE 80

# NGINX starts automatically as default CMD
