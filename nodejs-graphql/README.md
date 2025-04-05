# Ad Management System

## Overview

A comprehensive ad management system built with Node.js, GraphQL, and PostgreSQL, supporting multi-app ad campaigns with advanced targeting capabilities.

## Features

- Multi-app support
- Detailed campaign management
- Advanced ad group targeting
- Performance tracking
- GraphQL API

## Prerequisites

- Node.js (v18+)
- PostgreSQL
- Prisma
- GraphQL

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/mwahba/showcase.git
cd nodejs-graphql
```

### 3. Install/Activate Conda Environment

1. To establish the Conda environment: `conda env create --file=environment.yml`
1. To update the Conda environment: 11. `conda activate showcase_nodejs_env` 11. `conda env update --file=environment.yml --prune` to take in the changes and uninstall removed dependencies.
1. To run commands with sudo in a conda environment: 11. `conda activate showcase_nodejs_env` 11. Replacing `python` with the executable name: `sudo $(which python) script_name.py`

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Database

1. Create a `.env` file in the root directory
1. Add your PostgreSQL connection string:

```
POSTGRES_USER="postgres_user"
POSTGRES_PASSWORD="somepassword123!"
POSTGRES_DB="ad_management_db"
POSTGRES_PORT=5432
POSTGRES_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:${POSTGRES_PORT}/${POSTGRES_DB}?schema=public"
POSTGRES_PATH="pgdata"
POSTGRES_LOGFILE_PATH="${POSTGRES_PATH}/logfile"
```

1. Load environment variables into command line session (BASH, ZSH, possibly others): `source .env`
1. Initialize the DB cluster if not already done: `initdb -D ${POSTGRES_PATH} -U ${POSTGRES_USER}`
1. Start the PostgreSQL server: `pg_ctl -D ${POSTGRES_PATH} -l ${POSTGRES_LOGFILE_PATH} start`
1. Create the DB: `createdb -h localhost ${POSTGRES_DB} -U ${POSTGRES_USER}`
1. Edit with new password if not done: `psql -d ${POSTGRES_DB} -U ${POSTGRES_USER} -c "ALTER USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';"`
1. To launch PSQL shell: `psql -d ${POSTGRES_DB} -U ${POSTGRES_USER}`
1. To stop the database when you're done: `pg_ctl -D ${POSTGRES_PATH} stop`

### 4. Generate Prisma Client

```bash
npx prisma generate
```

### 5. Run Migrations

```bash
npx prisma migrate dev --name init
```

### 6. Start the Development Server

```bash
npm run dev
```

### 7. Access GraphQL Playground

Open `http://localhost:4000/graphql` in your browser

## Key Concepts

- **Apps**: Top-level containers for ad activities
- **Campaigns**: Marketing initiatives within an app
- **Ad Groups**: Logically grouped ads with shared targeting
- **Ads**: Individual advertisement units

## Targeting Options

- Keywords
- Location
- Gender
- Device Type
- Age Range

## Example Queries

### Create an App

```graphql
mutation {
  createApp(
    input: { name: "My Mobile App", description: "Awesome mobile application" }
  ) {
    id
    name
    apiKey
  }
}
```

### Create a Campaign

```graphql
mutation {
  createCampaign(
    input: {
      appId: "app-id-from-previous-step"
      name: "Summer Promotion"
      startDate: "2025-06-01"
      endDate: "2025-08-31"
      budget: 500.00
    }
  ) {
    id
    name
    budget
  }
}
```
