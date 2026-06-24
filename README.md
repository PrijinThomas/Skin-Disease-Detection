
# Skin Disease Detection System

A web-based application designed for the preliminary identification of skin conditions using deep learning. This project implements a full-stack solution using Django, featuring role-based access control for Administrators, Doctors, and Patients.

## Table of Contents

* [About the Project]
* [Key Features]
* [Project Structure]
* [Prerequisites]
* [Installation & Setup]
* [Usage]
* [Disclaimer]
## About the Project

This system facilitates the automated analysis of skin images to assist in medical screening. By utilizing a Convolutional Neural Network (CNN), the platform allows patients to upload images for prediction, while doctors can manage diagnostics and patient history through a dedicated interface.

## Key Features

* **Role-Based Access:** Specialized dashboards for Administrators, Doctors, and Patients.
* **Automated Screening:** Uses deep learning to analyze skin lesion images.
* **Medical Record Management:** Secure handling of patient data and medical histories.
* **Image Uploads:** Custom media management for handling patient-submitted diagnostic images.

## Project Structure

* `administrator/`: Logic for site administration and system management.
* `doctor/`: Modules for doctors to view records and provide consultations.
* `patient/`: Functionality for patients to register and submit images.
* `skin_diseases/`: Core project configuration files (settings, urls, wsgi).
* `static/` & `template/`: UI assets and frontend templates.
* `train_skin_model.py`: Script to train the CNN model.
* `predict_new.py`: Utility for generating predictions on new images.
* `seed_diseases.py`: Script for populating initial disease data.

## Prerequisites

* Python 3.x
* pip (Python package manager)
* A local environment with sufficient memory to handle model processing.

## Installation & Setup

1. **Clone the repository:**
```bash

```



git clone https://github.com/PrijinThomas/Skin-Disease-Detection.git
cd Skin-Disease-Detection

```

2. **Install dependencies:**
   ```bash
pip install -r requirements.txt

```

3. **Prepare the Dataset:**
The training dataset is excluded from this repository due to its large size. Please create a `dataset/` folder in the root directory and place your training images (e.g., HAM10000) inside before running the training script.
4. **Initialize the database:**
```bash

```



python manage.py migrate

```

5. **Start the development server:**
   ```bash
python manage.py runserver

```

## Usage

1. **Model Training:** After placing your dataset, run `python train_skin_model.py` to generate the model weights.
2. **Web Portal:** Access the application at `[http://127.0.0.1:8000/](http://127.0.0.1:8000/)`.
3. **Diagnostics:** Patients upload images through the patient dashboard, which are then analyzed by the model via `predict_new.py`.

## Disclaimer

This project is intended for educational purposes and preliminary screening only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a dermatologist or qualified medical professional with any questions regarding a medical condition.