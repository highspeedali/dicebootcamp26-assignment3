# Assignment 3 - GitHub Actions Assignment

## Live Render Cloud deployment URL: https://dicebootcamp26-assignment3.onrender.com
&nbsp;
&nbsp;
### Application Description

This sample **FastAPI** application demonstrates a simple REST API for managing products/items. It includes health monitoring, version tracking through environment variables, and basic CRUD functionality (Create and Read operations). Items are stored in an in-memory dictionary, making it a lightweight application suitable for learning FastAPI, API testing, Dockerization, and CI/CD pipeline demonstrations.

### Available Endpoints

| Method | Endpoint           | Description                                                           |
| ------ | ------------------ | --------------------------------------------------------------------- |
| `GET`  | `/`                | Returns a welcome message and the current application version.        |
| `GET`  | `/health`          | Health check endpoint used to verify that the application is running. |
| `POST` | `/items/{item_id}` | Creates a new item with a specified ID, name, and price.              |
| `GET`  | `/items/{item_id}` | Retrieves an existing item by its ID.                                 |


### main.py

```
import os

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

APP_VERSION = os.getenv("APP_VERSION", "0.1.0") or os.getenv(
    "GITHUB_REF_NAME",
    "0.1.0",
)

app = FastAPI(title="CI/CD Lab", version=APP_VERSION)


class Item(BaseModel):
    name: str
    price: float


items: dict[int, Item] = {}


@app.get("/")
def read_root():
    return {
        "message": "Hello from CI/CD lab!",
        "version": APP_VERSION,
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/items/{item_id}", status_code=status.HTTP_201_CREATED)
def create_item(item_id: int, item: Item):
    if item_id in items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Item already exists"
        )
    items[item_id] = item
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Item created successfully"},
    )


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found"
        )
    return items[item_id]


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

### Dockerfile

```
FROM python:3.13-slim

ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
```

### CICD Workflow using GitHub Actions (GHA)

Lint → Test → Build Docker Image → Push to Docker Hub → Deploy to Render

This sequence ensures that only code that passes linting, testing, and image build verification is deployed to the production environment.

On every push to main branch of this repo:
-  Linting and Code Formatting job is executed by using Ruff
- Unit testing is done as the next step using PyTest.
- A docker image is then build and its image with latest tag is stored in DockerHub.
- As a final step, Render Cloud webhook is used to  deploy the latest image on its free model. 

<img width="1833" height="439" alt="CICD Workflow png" src="https://github.com/user-attachments/assets/6f589f01-8d73-42fc-8c93-46725b66cd8b" />


```
name: CI Build and Deploy to Render Cloud

on:
  push:
    branches: [ "main" ]
    
permissions:
  contents: read

jobs:
  lint:
    name: Lint Code via Ruff
    runs-on: ubuntu-slim
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v7
        with:
            python-version: "3.13"
            cache: pip

      - name: Install Ruff
        run: pip install ruff

      - name: Check code via Ruff
        run: ruff check .

      - name: Code formatting via Ruff
        run: ruff format --check .

  test:
    name: Test the code using pytest
    needs: lint
    runs-on: ubuntu-slim
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v7
        with:
            python-version: "3.13"
            cache: pip

      - name: Install FastAPI
        run: pip install fastapi 

      - name: Install httpx2
        run: pip install httpx2 

      - name: Install uvicorn
        run: pip install uvicorn

      - name: Install PyTest
        run: pip install pytest

      - name: Run the tests
        run: python -m pytest -v

  build:
    name: Build the Docker Image
    needs: [lint,test]
    runs-on: ubuntu-latest

    steps:
    - name: Checkout the code
      uses: actions/checkout@v7

    - name: Setup Docker Buildx
      uses: docker/setup-buildx-action@v4

    - name: Login to Docker Hub
      uses: docker/login-action@v4
      with:
        username: ${{ vars.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
        
    - name: Build the Docker image
      run: docker build . --file Dockerfile --tag highspeedali/dicebootcamp26-assignment3:${{ vars.APP_VERSION }}

    - name: Push the Docker Image
      run: docker push highspeedali/dicebootcamp26-assignment3:${{ vars.APP_VERSION }}
  
  deploy:
    name: Deploy latest image on Render Cloud
    needs: [lint,test,build]
    runs-on: ubuntu-latest
    steps:
    - name: Use Render WebHook to deploy dicebootcamp26-assignment3:latest 
      env:
        HOOK_URL: ${{ secrets.RENDER_DEPLOY_HOOK_URL }}
      run: |
        curl -fsS -X POST "${HOOK_URL}"
```

### Linting job in GHA

##### Workflow Steps

1. **Checkout Code**
    
    - Downloads the repository source code into the workflow runner.
2. **Setup Python**
    
    - Installs Python 3.13 and enables pip dependency caching for faster workflow execution.
3. **Install Ruff**
    
    - Installs the Ruff linter and formatter.
4. **Lint Code**
    
    - Runs `ruff check .` to identify syntax errors, code quality issues, and style violations.
5. **Validate Formatting**
    
    - Runs `ruff format --check .` to verify that the code adheres to the configured formatting standards without modifying files.

<img width="1865" height="772" alt="image" src="https://github.com/user-attachments/assets/66b4d606-ff9e-4865-8733-12e950f1e68b" />

&nbsp;
&nbsp;

### Testing job in GHA

This GitHub Actions workflow stage executes automated tests for the FastAPI application using **PyTest**. It runs only after the **lint** job completes successfully, ensuring that code quality checks pass before testing begins. The workflow prepares a Python 3.13 environment, installs the required application and testing dependencies, and then runs the test suite to validate the application's functionality.

##### Workflow Steps

1. **Checkout Code**
    
    - Downloads the repository source code onto the workflow runner.
2. **Setup Python**
    
    - Configures Python 3.13 and enables pip package caching to improve workflow performance.
3. **Install Application Dependencies**
    
    - Installs FastAPI, HTTPX, and Uvicorn, which are required for the application and API testing.
4. **Install PyTest**
    
    - Installs the PyTest framework used for automated testing.
5. **Run Tests**
    
    - Executes all test cases using below command. `-v` flag is for verbose.
```
python -m pytest -v
```

### Build stage in GHA

This GitHub Actions workflow stage builds and publishes a Docker image for the application. It runs only after both the **lint** and **test** jobs complete successfully, ensuring that the code meets quality standards and passes all automated tests before creating a deployable artifact. The workflow authenticates with Docker Hub, builds a versioned Docker image, and pushes it to a Docker Hub repository for later deployment.

##### Workflow Steps

1. **Checkout Code**
    
    - Downloads the latest source code from the repository.
2. **Setup Docker Buildx**
    
    - Configures Docker Buildx, enabling advanced Docker image build capabilities.
3. **Login to Docker Hub**
    
    - Authenticates with Docker Hub using repository variables and secrets.
    - Uses:
        - `DOCKERHUB_USERNAME`
        - `DOCKERHUB_TOKEN`
4. **Build Docker Image**
    
    - Builds the application image using the project's `Dockerfile`.
    - Tags the image using the application version stored in `APP_VERSION`.
    
	```
	docker build . --file Dockerfile --tag highspeedali/dicebootcamp26-assignment3:${APP_VERSION}
	```
1. **Push Docker Image**
    
    - Uploads the newly built image to Docker Hub.
    
```
docker push highspeedali/dicebootcamp26-assignment3:${APP_VERSION}
```

### Deploy job in GHA

This GitHub Actions workflow stage automates the deployment of the application to **Render Cloud**. It runs only after the **lint**, **test**, and **build** jobs have completed successfully, ensuring that the application has passed quality checks, testing, and Docker image creation before deployment. The workflow triggers a Render deployment using a secure deployment webhook stored as a GitHub secret.

### Workflow Steps

1. **Verify Previous Jobs**
    
    - Waits for the **lint**, **test**, and **build** stages to complete successfully.
2. **Trigger Render Deployment**
    
    - Retrieves the Render deployment webhook URL from the `RENDER_DEPLOY_HOOK_URL` GitHub secret.
    - Sends an HTTP POST request using `curl` to initiate a new deployment on Render.
```
curl -fsS -X POST "$HOOK_URL"
```
