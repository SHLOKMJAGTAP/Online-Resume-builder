# 🏛️ The Gilded Archive: Luxury Resume & Portfolio Engine

A sophisticated full-stack web application that transforms professional data into a high-end, interactive digital portfolio. Built with Python, Flask, and MySQL.

## ✨ Features

* **Secure Authentication**: User registration and login using `Werkzeug` for password hashing and session management.
* **Dynamic Profile Management**: Custom profile photo uploads with secure filename handling.
* **Synchronized Resume Builder**: A unified form to manage Education, Skills, Professional Experience, and Notable Works.
* **Interactive Portfolio**: A "Gilded Noir" themed portfolio featuring:
    * **Parallax Hero Section**: Smooth header animations based on scroll depth.
    * **Auto-Link Detection**: Integration of the `urlize` filter to turn project text into clickable hyperlinks.
    * **Bento-Style Layout**: A modern, responsive grid for showcasing competencies and chronology.
    * **Scroll Reveal Animations**: Elegant UI elements that animate into view as the user explores.

## 🛠️ Tech Stack

* **Backend**: Python 3.x, Flask
* **Database**: MySQL (via PyMySQL)
* **Security**: Werkzeug (Password Hashing)
* **Frontend**: Jinja2 Templates, CSS3 (Custom Variables & Keyframes), Vanilla JavaScript (Intersection Observer API)

## 🚀 Getting Started

### 1. Prerequisites
* Python 3.8+
* MySQL Server
* Pip (Python Package Manager)

### 2. Database Setup
Create a database named `resume_db` and execute the following schema:

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    photo VARCHAR(255) DEFAULT 'default.png'
);

CREATE TABLE resumes (
    resume_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    education TEXT,
    skills TEXT,
    experience TEXT,
    projects TEXT,
    template VARCHAR(50) DEFAULT 'classic',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
