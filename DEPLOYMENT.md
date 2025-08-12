# Deployment Guide - Airline Market Analyzer

This guide provides step-by-step instructions for deploying the Airline Market Analyzer web application.

## Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)
- Internet connection for API access

## Quick Start (Local Development)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd airline-market-analyzer
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys (optional for basic functionality)
# The app works with sample data even without API keys
```

### 4. Run the Application
```bash
python app.py
```

### 5. Access the Application
Open your browser and navigate to: `http://localhost:5000`

## Environment Configuration

### Required Environment Variables
Create a `.env` file with the following variables:

```env
# Flask Configuration
FLASK_DEBUG=True
PORT=5000

# Optional API Keys (app works without these using sample data)
OPENAI_API_KEY=your_openai_api_key_here
RAPIDAPI_KEY=your_rapidapi_key_here
AMADEUS_CLIENT_ID=your_amadeus_client_id_here
AMADEUS_CLIENT_SECRET=your_amadeus_client_secret_here

# Data Collection Settings
MAX_REQUESTS_PER_MINUTE=60
CACHE_DURATION_HOURS=24
LOG_LEVEL=INFO
```

### API Keys (Optional)

1. **OpenAI API** (for AI insights)
   - Sign up at: https://platform.openai.com/
   - Get API key from: https://platform.openai.com/api-keys
   - Free tier available with usage limits

2. **RapidAPI** (for flight data)
   - Sign up at: https://rapidapi.com/
   - Subscribe to Skyscanner API
   - Free tier available with limited requests

3. **Amadeus API** (alternative flight data)
   - Sign up at: https://developers.amadeus.com/
   - Create application to get client ID and secret
   - Free tier available

## Production Deployment

### Option 1: Heroku Deployment

1. **Install Heroku CLI**
   ```bash
   # Download from: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set FLASK_DEBUG=False
   heroku config:set OPENAI_API_KEY=your_key_here
   # Add other environment variables as needed
   ```

4. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### Option 2: Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .
   EXPOSE 5000

   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
   ```

2. **Build and Run**
   ```bash
   docker build -t airline-analyzer .
   docker run -p 5000:5000 --env-file .env airline-analyzer
   ```

### Option 3: VPS/Cloud Server

1. **Server Setup**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Python and pip
   sudo apt install python3 python3-pip python3-venv -y

   # Install nginx (optional, for reverse proxy)
   sudo apt install nginx -y
   ```

2. **Application Setup**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd airline-market-analyzer

   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

   # Configure environment
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run with Gunicorn**
   ```bash
   # Install gunicorn
   pip install gunicorn

   # Run application
   gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
   ```

4. **Setup Systemd Service (Optional)**
   ```bash
   # Create service file
   sudo nano /etc/systemd/system/airline-analyzer.service
   ```

   ```ini
   [Unit]
   Description=Airline Market Analyzer
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/airline-market-analyzer
   Environment="PATH=/path/to/airline-market-analyzer/venv/bin"
   ExecStart=/path/to/airline-market-analyzer/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   # Enable and start service
   sudo systemctl enable airline-analyzer
   sudo systemctl start airline-analyzer
   ```

## Testing the Deployment

### 1. Run Unit Tests
```bash
python test_app.py
```

### 2. Test Web Interface
1. Navigate to the application URL
2. Test the dashboard page
3. Try searching for flights (SYD → MEL)
4. Check market trends page
5. Verify charts and visualizations load

### 3. Test API Endpoints
```bash
# Test API endpoint
curl http://localhost:5000/api/data

# Should return JSON with sample data
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Change port in .env file
   PORT=8000
   ```

2. **Missing Dependencies**
   ```bash
   # Reinstall requirements
   pip install -r requirements.txt --force-reinstall
   ```

3. **Permission Errors**
   ```bash
   # Fix file permissions
   chmod +x app.py
   ```

4. **API Key Issues**
   - The app works without API keys using sample data
   - Check API key format and validity
   - Verify API quotas and limits

### Performance Optimization

1. **Enable Caching**
   - Data is automatically cached for 24 hours
   - Adjust `CACHE_DURATION_HOURS` in environment

2. **Use Production WSGI Server**
   ```bash
   # Use gunicorn instead of Flask dev server
   gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
   ```

3. **Database Optimization**
   - Consider using Redis for caching
   - Implement database for persistent storage

## Monitoring and Maintenance

### 1. Log Monitoring
```bash
# View application logs
tail -f logs/app.log

# Monitor system resources
htop
```

### 2. Health Checks
```bash
# Simple health check
curl http://localhost:5000/

# API health check
curl http://localhost:5000/api/data
```

### 3. Updates
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
sudo systemctl restart airline-analyzer
```

## Security Considerations

1. **Environment Variables**
   - Never commit `.env` file to version control
   - Use secure methods to store API keys in production

2. **HTTPS**
   - Use SSL/TLS certificates in production
   - Configure nginx or load balancer for HTTPS

3. **Firewall**
   - Only expose necessary ports
   - Use security groups in cloud environments

4. **Updates**
   - Keep dependencies updated
   - Monitor for security vulnerabilities

## Support

For issues or questions:
- Check the troubleshooting section above
- Review application logs
- Test with sample data first
- Verify API key configuration

## Performance Metrics

Expected performance:
- **Load Time**: < 3 seconds for dashboard
- **Search Results**: < 5 seconds for flight analysis
- **Memory Usage**: < 512MB for basic deployment
- **Concurrent Users**: 10-50 users (depending on server specs)

## Backup and Recovery

1. **Data Backup**
   ```bash
   # Backup cached data
   tar -czf backup-$(date +%Y%m%d).tar.gz data/
   ```

2. **Configuration Backup**
   ```bash
   # Backup environment and config
   cp .env .env.backup
   ```

3. **Recovery**
   ```bash
   # Restore from backup
   tar -xzf backup-YYYYMMDD.tar.gz
   ```
