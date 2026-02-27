# Bingo Card Generator

A customizable bingo card generator that creates interactive HTML bingo cards from CSV data with background images and celebration effects. Now available as both a CLI tool and a Flask web application deployable on AWS free tier.

## Installation

### Prerequisites

This application requires Python 3.11 or higher and uses [uv](https://github.com/astral-sh/uv) for fast, reliable package management.

#### Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Option 1: Install from Source (Recommended)

Install the bingo card generator from the project directory:

```bash
# Clone or navigate to the project directory
cd bingo-app

# Install the package and all dependencies
uv sync

# The CLI commands are now available
uv run create-bingo-card
uv run create-spooky-bingo
```

### Option 2: Development Mode

For active development where you want changes to be immediately reflected:

```bash
# Install in development mode
uv pip install -e .

# Run commands directly (no 'uv run' prefix needed)
create-bingo-card
create-spooky-bingo
```

## Running the Bingo Card Generator

### Web Application (New!)

You can now run the bingo card generator as a web application:

```bash
# Start the Flask web server
uv run python app.py

# Or using Flask directly
uv run flask --app app run --host 0.0.0.0 --port 8080
```

Then visit `http://localhost:8080` in your browser to:
- Select a theme (alien, ghost, thanksgiving, christmas, new_year)
- Choose grid size (3x3, 5x5, 7x7)
- Generate and play bingo cards directly in your browser

### CLI Tool (Original)

### Using uv run (Recommended)

```bash
# Use the CLI command with uv run
uv run create-bingo-card

# Or use the alias
uv run create-spooky-bingo
```

### If you installed in development mode:

```bash
# Run commands directly
create-bingo-card
create-spooky-bingo
```

### Running from source:

```bash
# Run the Python script directly with uv
uv run python create_bingo_card.py
```

### Usage Options

You can run the generator in two ways:

1. **Interactive Mode**: Run the command with no arguments, and the CLI will walk you through all configuration options.

    ```bash
    # Using uv run
    uv run create-bingo-card

    # If installed in dev mode
    create-bingo-card

    # Running from source
    uv run python create_bingo_card.py
    ```

2. **Command-line Arguments**: Provide specific options directly as arguments.

    ```bash
    # Using uv run
    uv run create-bingo-card --csv-file my_tiles.csv --image-path background.jpg

    # If installed in dev mode
    create-bingo-card --csv-file my_tiles.csv --image-path background.jpg

    # Running from source
    uv run python create_bingo_card.py --csv-file my_tiles.csv --image-path background.jpg
    ```

### Command-line Options

Generate a bingo card HTML file from a CSV of tile values and a background image.

| Option | Type | Description |
|--------|------|-------------|
| `--csv-file` | PATH | Path to the CSV file with bingo tile values |
| `--image-path` | PATH | Path to the background image to reveal on the board |
| `--h-bingo-image-path` | PATH | Path to the image used for H-bingo celebration |
| `--celebration-image-path` | PATH | Path to the image used for double and super bingo celebrations |
| `--tile-size` | INTEGER | Number of rows and columns in the bingo grid (if not specified, 5x5 and 7x7 will be generated) |
| `--free-center` | FLAG | Set center tile as FREE (only works with odd tile size) |
| `--output` | TEXT | Output HTML file path (will be appended with _5x5 or _7x7 if tile-size is not specified) |
| `--no-down-scaling` | FLAG | Disable automatic image scaling (images > 250KB will be scaled down by default) |
| `--background-color` | TEXT | Hex color for the background and tiles (e.g. #0a0a30) |
| `--theme` | TEXT | Theme to use (alien or ghost) - default: alien |
| `--no-interactive` | FLAG | Skip interactive prompts and use specified arguments + defaults |
| `--help` | FLAG | Show this message and exit |

## Examples

Generate a standard 5×5 bingo card with a free center:

```bash
# Using uv run
uv run create-bingo-card --csv-file data/my_terms.csv --free-center --output my_bingo_card

# If installed in dev mode
create-bingo-card --csv-file data/my_terms.csv --free-center --output my_bingo_card

# Running from source
uv run python create_bingo_card.py --csv-file data/my_terms.csv --free-center --output my_bingo_card
```

Generate a custom 7×7 bingo card with a background image:

```bash
# Using uv run
uv run create-bingo-card --csv-file data/lots_of_terms.csv --tile-size 7 --image-path images/background.jpg

# If installed in dev mode
create-bingo-card --csv-file data/lots_of_terms.csv --tile-size 7 --image-path images/background.jpg

# Running from source
uv run python create_bingo_card.py --csv-file data/lots_of_terms.csv --tile-size 7 --image-path images/background.jpg
```

Generate a ghost hunt themed bingo card:

```bash
# Using uv run
uv run create-spooky-bingo --theme ghost --csv-file ghost_hunt_tiles.csv --output ghost_hunt

# If installed in dev mode
create-spooky-bingo --theme ghost --csv-file ghost_hunt_tiles.csv --output ghost_hunt

# Running from source
uv run python create_bingo_card.py --theme ghost --csv-file ghost_hunt_tiles.csv --output ghost_hunt
```

## Themes

The bingo card generator supports multiple themes:

### Alien Theme (Default)
- Space/alien themed with purple and cyan colors
- UFO and alien emojis
- Neon glow effects
- Messages: "BINGO!", "DOUBLE BINGO!", "H BINGO!", "You are a God Gamer"

### Ghost Theme
- Spooky ghost hunt theme with dark purple and orange colors
- Ghost, bat, and pumpkin emojis
- Eerie font styles (Creepster, Nosifer, Eater)
- Messages: "GHOST CAPTURED!", "DOUBLE CAPTURE!", "HAUNTED PATTERN!", "Master Ghost Hunter!"

To use a theme, add the `--theme` option:

```bash
uv run create-bingo-card --theme ghost
```

## Updating Google Sites

After generating your bingo cards, follow these steps to update the Google Sites page:

1. **Generate the bingo HTML files**
   ```bash
   # Using uv run
   uv run create-bingo-card

   # If installed in dev mode
   create-bingo-card

   # Running from source
   uv run python create_bingo_card.py
   ```
   This will create your bingo HTML files (e.g., `bingo_5x5.html` and `bingo_7x7.html`)

2. **Go to Google Sites**
   - Navigate to https://sites.google.com
   - Click on "Spooky Saturday Bingo"

3. **Update the 5×5 bingo card**
   - Open the `bingo_5x5.html` file in a text editor
   - Select all content (Ctrl+A or Cmd+A) and copy it
   - On the Google Sites page, click on the 5×5 bingo card element to select it
   - Click the edit button (pencil icon)
   - Delete all existing content in the embed element
   - Paste the copied HTML content
   - Click "Insert" or "Update" to save

4. **Update the 7×7 bingo card**
   - Repeat step 3 for the `bingo_7x7.html` file and the bigger bingo tab/element

## AWS Deployment

Deploy the web application to AWS free tier using Docker on an EC2 t2.micro instance.

### Prerequisites

- AWS CLI installed and configured (`aws configure`)
- An SSH key pair for EC2 access

### Step 1: Create AWS Infrastructure

```bash
# Set your region
REGION=us-west-1

# Create an EC2 key pair (save the .pem file securely)
aws ec2 create-key-pair --key-name bingo-app-key --region $REGION \
  --query 'KeyMaterial' --output text > ~/.ssh/bingo-app-key.pem
chmod 600 ~/.ssh/bingo-app-key.pem

# Create a security group (allow HTTP on 8080 and SSH)
VPC_ID=$(aws ec2 describe-vpcs --region $REGION --query 'Vpcs[0].VpcId' --output text)
SG_ID=$(aws ec2 create-security-group \
  --group-name bingo-app-sg \
  --description "Bingo App" \
  --vpc-id $VPC_ID \
  --region $REGION \
  --query 'GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8080 --cidr 0.0.0.0/0 --region $REGION
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0 --region $REGION

# Launch a t2.micro instance (free tier) with Docker pre-installed
AMI_ID=$(aws ec2 describe-images --region $REGION --owners amazon \
  --filters "Name=name,Values=al2023-ami-2023*-x86_64" "Name=state,Values=available" \
  --query 'sort_by(Images,&CreationDate)[-1].ImageId' --output text)

INSTANCE_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t2.micro \
  --key-name bingo-app-key \
  --security-group-ids $SG_ID \
  --region $REGION \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=bingo-app}]' \
  --user-data '#!/bin/bash
yum update -y
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user' \
  --query 'Instances[0].InstanceId' --output text)

# Wait for the instance to be ready
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION
PUBLIC_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --region $REGION \
  --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
echo "Instance ready at: $PUBLIC_IP"
```

### Step 2: Deploy the App

```bash
# Wait ~60 seconds for Docker to install via user-data, then:

# Copy project files to EC2
rsync -avz --exclude='.venv' --exclude='__pycache__' --exclude='.git' \
  -e "ssh -i ~/.ssh/bingo-app-key.pem -o StrictHostKeyChecking=no" \
  . ec2-user@$PUBLIC_IP:~/bingo-app/

# SSH in, build, and run
ssh -i ~/.ssh/bingo-app-key.pem ec2-user@$PUBLIC_IP "
  cd ~/bingo-app
  sudo docker build -t bingo-app .
  sudo docker run -d --name bingo-app --restart unless-stopped \
    -p 8080:8080 -e FLASK_DEBUG=False -e PORT=8080 -e HOST=0.0.0.0 \
    bingo-app
"
```

The app will be available at `http://<PUBLIC_IP>:8080`

### Step 3: Manage the Instance

```bash
# Stop the instance (to avoid charges when not in use)
aws ec2 stop-instances --instance-ids $INSTANCE_ID --region $REGION

# Start it again later (note: public IP will change unless you use an Elastic IP)
aws ec2 start-instances --instance-ids $INSTANCE_ID --region $REGION

# Re-deploy after code changes
rsync -avz --exclude='.venv' --exclude='__pycache__' --exclude='.git' \
  -e "ssh -i ~/.ssh/bingo-app-key.pem" . ec2-user@$PUBLIC_IP:~/bingo-app/
ssh -i ~/.ssh/bingo-app-key.pem ec2-user@$PUBLIC_IP "
  cd ~/bingo-app
  sudo docker build -t bingo-app .
  sudo docker stop bingo-app && sudo docker rm bingo-app
  sudo docker run -d --name bingo-app --restart unless-stopped \
    -p 8080:8080 -e FLASK_DEBUG=False bingo-app
"

# Terminate the instance entirely (deletes it)
aws ec2 terminate-instances --instance-ids $INSTANCE_ID --region $REGION
```

### Optional: Custom Domain + HTTPS

1. Allocate an **Elastic IP** (free while attached) so the IP survives reboots
2. Register a domain via Route 53 or Cloudflare
3. Point an A record to the Elastic IP
4. Install nginx + Let's Encrypt on the EC2 for HTTPS

### Local Docker Testing

```bash
docker build -t bingo-app .
docker run -p 8080:8080 bingo-app
# Visit http://localhost:8080
```

## Architecture

- **CLI Tool**: Original Python CLI using Click, Rich, and Questionary
- **Web App**: Flask server that reuses CLI logic for bingo generation
- **Themes**: 5 built-in themes with customizable colors, fonts, and emojis
- **Templates**: Jinja2 templates for both HTML bingo cards and landing page
- **Images**: Automatic processing and base64 embedding for self-contained HTML
- **Deployment**: Dockerized for easy AWS deployment

## Notes

- If you don't specify a tile size, the script will automatically generate both 5×5 and 7×7 cards
- The FREE center option only works with odd-numbered tile sizes (5×5, 7×7, etc.)
- Large background images (>250KB) will be automatically scaled down unless you use the `--no-down-scaling` option
- Themes automatically set appropriate colors, fonts, and messages - you can still override the background color with `--background-color`
- The web app maintains full backward compatibility with the CLI tool